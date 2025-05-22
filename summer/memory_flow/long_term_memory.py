# 长期记忆管理模块，faiss主库，权重动态管理
from summer.summer_faiss import faiss_add, faiss_recall
from config import LONG_TERM_CONSOLIDATE_WEIGHT
import time

class LongTermMemory:
    def __init__(self, meta, usage):
        self.meta = meta
        self.usage = usage
    def add(self, chunk):
        key = chunk.get('key')
        now = time.time()
        meta = self.meta.get(key, {})
        # 只有权重高/被标记/AI判定重要才写入faiss
        if meta.get('weight', 0) >= LONG_TERM_CONSOLIDATE_WEIGHT or meta.get('important', False):
            faiss_add([chunk])
            self.meta[key] = {**chunk, 'weight': meta.get('weight', 1), 'last_used': now, 'level': 'long_term'}
            self.usage[key] = now
        else:
            # 只更新meta和usage，不写入faiss
            self.meta[key] = {**chunk, 'weight': meta.get('weight', 1), 'last_used': now, 'level': 'long_term'}
            self.usage[key] = now
    def recall(self, query, k=3, theme=None):
        ltm_future = faiss_recall(query, k)
        ltm_results = ltm_future.result() if hasattr(ltm_future, 'result') else []
        if theme:
            ltm_results = [c for c in ltm_results if c.get('theme') == theme]
        return ltm_results[:k]
