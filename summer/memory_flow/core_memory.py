# 核心记忆管理模块，极高优先级，极难遗忘
import json, os, time
from config import LOG_DIR

class CoreMemory:
    def __init__(self):
        self.path = f'{LOG_DIR}/faiss/core_memory.json'
        self._load()
    def _load(self):
        try:
            with open(self.path, encoding='utf-8') as f:
                self.data = json.load(f)
        except:
            self.data = {}
    def add(self, chunk):
        key = self._get_key(chunk)
        now = time.time()
        self.data[key] = {**chunk, 'last_used': now, 'weight': 999, 'level': 'core'}
        self._save()
    def recall(self, query, k=3, theme=None):
        results = [v for v in self.data.values() if query in v.get('text','')]
        if theme:
            results = [v for v in results if v.get('theme') == theme]
        results = sorted(results, key=lambda x: (-x.get('weight',999), -x.get('last_used',0)))
        return results[:k]
    def _get_key(self, chunk):
        import hashlib
        return hashlib.md5(f"core_{chunk.get('file','')}_{chunk.get('time','')}_{chunk.get('role','')}_{chunk['text']}".encode()).hexdigest()
    def _save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=0, indent=1)
