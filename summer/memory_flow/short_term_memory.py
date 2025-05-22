# 短期记忆管理模块，容量有限，随时可丢弃
from collections import deque
from config import SHORT_TERM_MEMORY_SIZE

class ShortTermMemory:
    def __init__(self):
        self.memory = deque(maxlen=SHORT_TERM_MEMORY_SIZE)
    def add(self, chunk):
        self.memory.append(chunk)
    def recall(self, query, k=3, theme=None):
        results = [c for c in self.memory if query in c.get('text','')]
        if theme:
            results = [c for c in results if c.get('theme') == theme]
        return results[-k:] if k else results
