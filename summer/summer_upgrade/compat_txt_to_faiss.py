import os, hashlib, json, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from summer.memory_manager import MemoryManager # 导入记忆管理器

LOG_DIR = 'logs' # 日志目录
HISTORY_JSON = os.path.join(os.path.dirname(__file__), 'history_dialogs.json') # 历史对话缓存文件

# 列出所有历史对话内容并编号
def list_history_dialogs():
    # 先列出所有以时间命名的txt文件
    txt_files = [fn for fn in os.listdir(LOG_DIR) if fn.endswith('.txt') and fn[:4].isdigit() and fn[4] == '-' and fn[7] == '-']
    txt_files.sort()
    print('找到以下历史对话日志：')
    for idx, fn in enumerate(txt_files, 1):
        print(f'{idx}. {fn}')
    print('-'*40)
    # 遍历内容但不打印
    all_chunks = []
    idx = 1
    for fn in txt_files:
        with open(os.path.join(LOG_DIR, fn), encoding='utf-8') as f:
            t = None
            for l in f:
                if l.strip().startswith('时间:'):
                    t = l.split(':', 1)[1].strip()
                for role in ['用户', 'user', '娜迦', 'ai']:
                    if l.strip().startswith(f'{role}:'):
                        txt = l.split(':', 1)[1].strip()
                        key = hashlib.md5(f'{fn}_{t}_{role}_{txt}'.encode()).hexdigest()
                        chunk = {'idx': idx, 'role': 'user' if '用户' in role else 'ai', 'text': txt, 'time': t, 'file': fn, 'key': key}
                        all_chunks.append(chunk)
                        idx += 1
    with open(HISTORY_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=1)
    print(f"共{len(all_chunks)}条历史对话，已预热缓存到{HISTORY_JSON}")

# 根据用户输入的序号或all导入AI记忆系统
def import_selected_dialogs(indices):
    mm = MemoryManager()
    with open(HISTORY_JSON, encoding='utf-8') as f:
        all_chunks = json.load(f)
    selected = []
    if indices == 'all':
        selected = all_chunks
    else:
        idx_set = set()
        for part in indices.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                idx_set.update(range(start, end+1))
            else:
                idx_set.add(int(part))
        selected = [c for c in all_chunks if c['idx'] in idx_set]
    processed, skipped, failed = 0, 0, 0
    for chunk in selected:
        try:
            if chunk['key'] in mm.long_term_meta:
                skipped += 1
                continue
            mm.add_memory(chunk, level='auto') # 走AI分层
            processed += 1
        except Exception as e:
            failed += 1
    print(f'导入完成，成功:{processed} 跳过:{skipped} 失败:{failed}')
    # 自动删除中间缓存文件
    try:
        os.remove(HISTORY_JSON)
        print(f'已自动清理中间缓存文件: {HISTORY_JSON}')
    except Exception as e:
        print(f'清理中间缓存文件失败: {e}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python compat_txt_to_faiss.py list|import all|import 1,3,5-8')
        sys.exit(0)
    if sys.argv[1] == 'list':
        list_history_dialogs()
    elif sys.argv[1] == 'import':
        if len(sys.argv) < 3:
            print('用法: python compat_txt_to_faiss.py import all|import 1,3,5-8')
            sys.exit(0)
        import_selected_dialogs(sys.argv[2])
    else:
        print('未知命令') 