import threading
from conversation_core import NagaConversation
import os,asyncio
import sys
sys.path.append(os.path.dirname(__file__))
from ui.pyqt_chat_window import ChatWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from summer.memory_manager import MemoryManager
n=NagaConversation()
def show_help():print('系统命令: 清屏, 查看索引, 帮助, 退出')
def show_index():print('主题分片索引已集成，无需单独索引查看')
def clear():os.system('cls'if os.name=='nt'else'clear')
with open('./ui/progress.txt','w')as f:f.write('0')
mm = MemoryManager()
threading.Thread(target=mm.forget_long_term, daemon=True).start()  # 启动时异步清理一次
print('='*30+'\n娜迦对话系统已启动\n'+'='*30)
show_help()
loop=asyncio.new_event_loop()
threading.Thread(target=loop.run_forever,daemon=True).start()
class NagaAgentAdapter:
 def __init__(s):s.naga=NagaConversation()
 async def respond_stream(s,txt):resp=await s.naga.process(txt);yield "娜迦",resp,None,True,False
if __name__=="__main__":
 app=QApplication(sys.argv)
 icon_path = os.path.join(os.path.dirname(__file__), "ui", "window_icon.png")
 app.setWindowIcon(QIcon(icon_path))
 win=ChatWindow()
 win.setWindowTitle("NagaAgent")
 win.show()
 sys.exit(app.exec_())
