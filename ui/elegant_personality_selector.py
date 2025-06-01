"""
优雅的性格选择器组件
使用动画效果和现代化设计的性格选择界面
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
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

class PersonalityCard(QWidget):
    """单个性格卡片"""
    clicked = pyqtSignal(str, dict)
    
    def __init__(self, personality_code, personality_data, parent=None):
        super().__init__(parent)
        self.personality_code = personality_code
        self.personality_data = personality_data
        self.is_selected = False
        self.setup_ui()
        
    def setup_ui(self):
        """初始化卡片UI"""
        self.setFixedHeight(60)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        # 性格名称和代码
        name_layout = QHBoxLayout()
        
        if self.personality_code == "DEFAULT":
            code_label = QLabel("●")
            name_label = QLabel("默认娜迦")
        else:
            code_label = QLabel(self.personality_code)
            name_label = QLabel(self.personality_data.get('name', ''))
            
        code_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 150);
                font: 10pt 'Lucida Console';
                font-weight: bold;
                background: transparent;
                border: none;
                min-width: 40px;
            }
        """)
        
        name_label.setStyleSheet("""
            QLabel {
                color: #fff;
                font: 12pt 'Lucida Console';
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        
        name_layout.addWidget(code_label)
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        layout.addLayout(name_layout)
        
        # 描述
        desc_label = QLabel(self.personality_data.get('description', ''))
        desc_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 100);
                font: 9pt 'Lucida Console';
                background: transparent;
                border: none;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        self.update_style()
        
    def update_style(self):
        """更新卡片样式"""
        if self.is_selected:
            self.setStyleSheet("""
                PersonalityCard {
                    background: rgba(255, 255, 255, 20);
                    border: 1px solid rgba(255, 255, 255, 60);
                    border-radius: 8px;
                    border-left: 3px solid #64C8FF;
                }
            """)
        else:
            self.setStyleSheet("""
                PersonalityCard {
                    background: rgba(255, 255, 255, 5);
                    border: 1px solid rgba(255, 255, 255, 20);
                    border-radius: 8px;
                }
                PersonalityCard:hover {
                    background: rgba(255, 255, 255, 15);
                    border: 1px solid rgba(255, 255, 255, 40);
                }
            """)
    
    def set_selected(self, selected):
        """设置选中状态"""
        self.is_selected = selected
        self.update_style()
        
    def mousePressEvent(self, event):
        """处理点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.personality_code, self.personality_data)

class ElegantPersonalitySelector(QWidget):
    """优雅的性格选择器"""
    
    personality_changed = pyqtSignal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_personality = "DEFAULT"
        self.is_expanded = False
        self.cards = {}
        self.setup_ui()
        
    def setup_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 主控制按钮
        self.main_button = QPushButton()
        self.main_button.setFixedHeight(50)
        self.main_button.clicked.connect(self.toggle_expansion)
        self.update_main_button()
        
        main_layout.addWidget(self.main_button)
        
        # 展开区域容器
        self.expand_container = QFrame()
        self.expand_container.setFixedHeight(0)  # 初始高度为0
        self.expand_container.setStyleSheet("""
            QFrame {
                background: rgba(17, 17, 17, 150);
                border: 1px solid rgba(255, 255, 255, 30);
                border-top: none;
                border-radius: 0 0 10px 10px;
            }
        """)
        
        # 滚动区域
        scroll_area = QScrollArea(self.expand_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: rgba(17, 17, 17, 150);
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: rgba(17, 17, 17, 150);
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 20);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 60);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 80);
            }
        """)
        
        # 滚动内容
        scroll_content = QWidget()
        scroll_content.setStyleSheet("""
            QWidget {
                background: rgba(17, 17, 17, 150);
                border: none;
            }
        """)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(8, 8, 8, 8)
        scroll_layout.setSpacing(2)
        
        # 添加性格卡片
        self.create_personality_cards(scroll_layout)
        
        scroll_area.setWidget(scroll_content)
        
        # 设置展开容器布局
        container_layout = QVBoxLayout(self.expand_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll_area)
        
        main_layout.addWidget(self.expand_container)
        
        # 展开动画
        self.expand_animation = QPropertyAnimation(self.expand_container, b"maximumHeight")
        self.expand_animation.setDuration(300)
        self.expand_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def create_personality_cards(self, layout):
        """创建性格卡片"""
        # 添加默认选项
        default_card = PersonalityCard("DEFAULT", {"name": "默认娜迦", "description": "标准娜迦，保持原有对话风格"})
        default_card.clicked.connect(self.on_personality_selected)
        default_card.set_selected(True)  # 默认选中
        self.cards["DEFAULT"] = default_card
        layout.addWidget(default_card)
        
        # 按组添加MBTI性格
        for group_name, personalities in PERSONALITY_GROUPS.items():
            if group_name != "默认":
                # 添加分组标题
                group_label = QLabel(f"─── {group_name} ───")
                group_label.setStyleSheet("""
                    QLabel {
                        color: rgba(255, 255, 255, 80);
                        font: 10pt 'Lucida Console';
                        font-style: italic;
                        background: transparent;
                        border: none;
                        padding: 8px 0 4px 0;
                        text-align: center;
                    }
                """)
                group_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(group_label)
                
                # 添加该组的性格卡片
                for personality_code in personalities:
                    if personality_code in MBTI_PERSONALITIES:
                        card = PersonalityCard(personality_code, MBTI_PERSONALITIES[personality_code])
                        card.clicked.connect(self.on_personality_selected)
                        self.cards[personality_code] = card
                        layout.addWidget(card)
        
        layout.addStretch()
    
    def update_main_button(self):
        """更新主按钮显示"""
        if self.current_personality == "DEFAULT":
            text = "● 默认娜迦"
            desc = "标准娜迦，保持原有对话风格"
        else:
            personality_data = MBTI_PERSONALITIES.get(self.current_personality, {})
            text = f"{self.current_personality} - {personality_data.get('name', '')}"
            desc = personality_data.get('description', '')
        
        # 截断过长的描述
        if len(desc) > 30:
            desc = desc[:27] + "..."
            
        button_text = f"{text}\n{desc}"
        
        self.main_button.setText(button_text)
        self.main_button.setStyleSheet(f"""
            QPushButton {{
                background: rgba(17,17,17,180);
                color: #fff;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 10px;
                padding: 8px 12px;
                font: 11pt 'Lucida Console';
                text-align: left;
            }}
            QPushButton:hover {{
                border: 1px solid rgba(255, 255, 255, 80);
                background: rgba(17,17,17,200);
            }}
            QPushButton:pressed {{
                background: rgba(17,17,17,220);
            }}
        """)
    
    def toggle_expansion(self):
        """切换展开/收起状态"""
        if self.is_expanded:
            # 收起
            self.expand_animation.setStartValue(250)
            self.expand_animation.setEndValue(0)
            self.main_button.setText(self.main_button.text().replace("▲", "▼"))
        else:
            # 展开
            self.expand_animation.setStartValue(0)
            self.expand_animation.setEndValue(250)
            self.main_button.setText(self.main_button.text().replace("▼", "▲"))
        
        self.is_expanded = not self.is_expanded
        self.expand_animation.start()
        
    def on_personality_selected(self, personality_code, personality_config):
        """处理性格选择"""
        # 更新选中状态
        for code, card in self.cards.items():
            card.set_selected(code == personality_code)
        
        # 更新当前性格
        self.current_personality = personality_code
        self.update_main_button()
        
        # 发送信号
        self.personality_changed.emit(personality_code, personality_config)
        
        # 延迟收起（给用户时间看到选择效果）
        QTimer.singleShot(500, self.collapse_if_expanded)
        
    def collapse_if_expanded(self):
        """如果展开则收起"""
        if self.is_expanded:
            self.toggle_expansion()
    
    def set_personality(self, personality_code):
        """程序设置性格（不触发信号）"""
        if personality_code in self.cards or personality_code == "DEFAULT":
            # 更新选中状态
            for code, card in self.cards.items():
                card.set_selected(code == personality_code)
            
            self.current_personality = personality_code
            self.update_main_button()
    
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
    test_window.resize(400, 600)
    
    layout = QVBoxLayout(test_window)
    
    # 添加性格选择器
    selector = ElegantPersonalitySelector()
    selector.personality_changed.connect(
        lambda code, config: print(f"性格切换到: {code} - {config.get('name', '')}")
    )
    
    layout.addWidget(selector)
    layout.addStretch()
    
    test_window.show()
    app.exec_() 