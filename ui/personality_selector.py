"""
MBTI性格选择组件
提供美观的下拉框界面来选择不同的性格模式
"""

from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import sys
import os

# 添加项目根目录到path，以便导入mbti配置
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

try:
    from mbti_personalities import MBTI_PERSONALITIES, PERSONALITY_GROUPS
except ImportError:
    # 如果导入失败，使用备用的简单配置
    MBTI_PERSONALITIES = {
        "INTJ": {"name": "建筑师", "description": "独立思考的战略家"},
        "DEFAULT": {"name": "默认", "description": "标准的娜迦性格"}
    }
    PERSONALITY_GROUPS = {"默认": ["DEFAULT", "INTJ"]}

class PersonalitySelector(QWidget):
    """性格选择器组件"""
    
    # 性格改变信号
    personality_changed = pyqtSignal(str, dict)  # 发送性格代码和配置
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_personality = "DEFAULT"  # 默认性格
        self.setup_ui()
        
    def setup_ui(self):
        """初始化UI"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(6)
        
        # 标题标签 - 优化风格，与现有UI保持一致
        title_label = QLabel("● 性格模式")
        title_label.setStyleSheet("""
            QLabel {
                color: #fff;
                font: 12pt 'Lucida Console';
                font-weight: normal;
                background: transparent;
                border: none;
                margin-bottom: 2px;
            }
        """)
        layout.addWidget(title_label)
        
        # 下拉框 - 使用与现有UI一致的样式
        self.personality_combo = QComboBox()
        self.personality_combo.setStyleSheet("""
            QComboBox {
                background: rgba(17,17,17,180);
                color: #fff;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 10px;
                padding: 6px 10px;
                font: 11pt 'Lucida Console';
                min-height: 20px;
            }
            QComboBox:hover {
                border: 1px solid rgba(255, 255, 255, 80);
                background: rgba(17,17,17,200);
            }
            QComboBox:focus {
                border: 1px solid rgba(255, 255, 255, 100);
                background: rgba(17,17,17,220);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid rgba(255, 255, 255, 150);
                margin-right: 6px;
            }
            QComboBox::down-arrow:hover {
                border-top: 6px solid #fff;
            }
            QComboBox QAbstractItemView {
                background: rgba(17,17,17,240);
                color: #fff;
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 10px;
                padding: 4px;
                selection-background-color: rgba(255, 255, 255, 30);
                outline: none;
                font: 11pt 'Lucida Console';
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                border-radius: 6px;
                margin: 1px;
                color: #fff;
            }
            QComboBox QAbstractItemView::item:selected {
                background: rgba(255, 255, 255, 40);
                color: #fff;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(255, 255, 255, 20);
            }
            QComboBox QAbstractItemView::item[text*="───"] {
                color: rgba(255, 255, 255, 100);
                background: rgba(0, 0, 0, 50);
                font-style: italic;
                text-align: center;
            }
        """)
        
        # 填充下拉框选项
        self.populate_combo()
        
        layout.addWidget(self.personality_combo)
        
        # 描述标签 - 优化样式
        self.description_label = QLabel()
        self.description_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 120);
                font: 9pt 'Lucida Console';
                background: transparent;
                border: none;
                padding: 2px 0;
                margin-top: 2px;
                line-height: 14px;
            }
        """)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        
        # 连接信号
        self.personality_combo.currentTextChanged.connect(self.on_personality_changed)
        
        # 设置默认描述
        self.update_description()
        
    def populate_combo(self):
        """填充下拉框选项"""
        # 添加默认选项
        self.personality_combo.addItem("默认娜迦", "DEFAULT")
        
        # 按组添加MBTI性格
        for group_name, personalities in PERSONALITY_GROUPS.items():
            # 添加分组分隔符
            if group_name != "默认":
                separator_text = f"─── {group_name} ───"
                self.personality_combo.addItem(separator_text, "SEPARATOR")
                
                # 添加该组的性格类型
                for personality_code in personalities:
                    if personality_code in MBTI_PERSONALITIES:
                        personality_data = MBTI_PERSONALITIES[personality_code]
                        display_text = f"{personality_code} - {personality_data['name']}"
                        self.personality_combo.addItem(display_text, personality_code)
    
    def on_personality_changed(self, text):
        """处理性格切换"""
        # 获取当前选择的数据
        current_data = self.personality_combo.currentData()
        
        # 忽略分隔符选项
        if current_data == "SEPARATOR":
            # 恢复到之前的选择
            self.personality_combo.setCurrentText(self.get_current_display_text())
            return
            
        if current_data and current_data != self.current_personality:
            self.current_personality = current_data
            self.update_description()
            
            # 获取性格配置
            if current_data == "DEFAULT":
                personality_config = {"name": "默认娜迦", "description": "标准的娜迦AI助手"}
            else:
                personality_config = MBTI_PERSONALITIES.get(current_data, {})
            
            # 发送信号
            self.personality_changed.emit(current_data, personality_config)
    
    def update_description(self):
        """更新描述文本"""
        if self.current_personality == "DEFAULT":
            description = "标准娜迦，保持原有对话风格"
        else:
            personality_data = MBTI_PERSONALITIES.get(self.current_personality, {})
            description = personality_data.get('description', '暂无描述')
        
        self.description_label.setText(description)
    
    def get_current_display_text(self):
        """获取当前性格的显示文本"""
        if self.current_personality == "DEFAULT":
            return "默认娜迦"
        else:
            personality_data = MBTI_PERSONALITIES.get(self.current_personality, {})
            return f"{self.current_personality} - {personality_data.get('name', '')}"
    
    def set_personality(self, personality_code):
        """程序设置性格（不触发信号）"""
        if personality_code in MBTI_PERSONALITIES or personality_code == "DEFAULT":
            self.current_personality = personality_code
            
            # 找到对应的下拉框索引并设置
            display_text = self.get_current_display_text()
            index = self.personality_combo.findText(display_text)
            if index >= 0:
                self.personality_combo.setCurrentIndex(index)
            
            self.update_description()
    
    def get_current_personality(self):
        """获取当前选择的性格"""
        return self.current_personality


if __name__ == "__main__":
    # 测试组件
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication([])
    
    # 创建测试窗口
    test_window = QWidget()
    test_window.setStyleSheet("""
        QWidget {
            background: rgba(25, 25, 25, 220);
            color: white;
        }
    """)
    test_window.resize(300, 200)
    
    layout = QVBoxLayout(test_window)
    
    # 添加性格选择器
    selector = PersonalitySelector()
    selector.personality_changed.connect(
        lambda code, config: print(f"性格切换到: {code} - {config.get('name', '')}")
    )
    
    layout.addWidget(selector)
    
    test_window.show()
    app.exec_() 