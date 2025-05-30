# NagaAgent 2.2beta 

> 智能对话助手，支持多MCP服务、流式语音交互、主题树检索、极致精简代码风格。

---

## ⚡ 快速开始
1. 克隆项目
   ```powershell
   git clone [项目地址]
   cd NagaAgent
   ```
2. 一键配置
   ```powershell
   .\setup.ps1
   ```
   - 自动创建虚拟环境并安装依赖
   - 检查/下载中文向量模型
   - 配置支持toolcall的LLM，推荐DeepSeekV3
3. 启动
   ```powershell
   .\start.bat
   ```

---

## 🖥️ 系统要求
- Windows 10/11
- Python 3.13+
- PowerShell 5.1+

---

## 🛠️ 依赖安装与环境配置
- 所有依赖见`requirements.txt`
- 如遇`greenlet`、`pyaudio`等安装失败，需先装[Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)，勾选C++ build tools，重启命令行后再`pip install -r requirements.txt`
- 浏览器自动化需`playwright`，首次用需`python -m playwright install chromium`
- 依赖安装命令：
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate
  pip install -r requirements.txt
  python -m playwright install chromium
  ```

---

## 🌟 主要特性
- **全局变量/路径/密钥统一`config.py`管理**，支持.env和环境变量，所有变量唯一、无重复定义
- DeepSeek流式对话，支持上下文召回与主题树分片检索
- faiss向量数据库，HNSW+PQ混合索引，异步加速，动态调整深度，权重动态调整，自动清理
- MCP服务集成，Agent Handoff智能分发，支持自定义过滤器与回调
- **多Agent能力扩展：浏览器、文件、代码等多种Agent即插即用，所有Agent均可通过handoff机制统一调用**
- 代码极简，注释全中文，组件解耦，便于扩展
- PyQt5动画与UI，支持PNG序列帧，loading动画极快
- 日志/检索/索引/主题/参数全部自动管理
- 记忆权重动态调整，支持AI/人工标记important，权重/阈值/清理策略全部在`config.py`统一管理
- **所有前端UI与后端解耦，前端只需解析后端JSON，自动适配message/data.content等多种返回结构**
- **前端换行符自动适配，无论后端返回`\n`还是`\\n`，PyQt界面都能正确分行显示**
- **所有Agent的handoff schema和注册元数据已集中在`mcpserver/mcp_registry.py`，主流程和管理器极简，扩展维护更方便。只需维护一处即可批量注册/扩展所有Agent服务。**
- **自动注册/热插拔Agent机制，新增/删除Agent只需增删py文件，无需重启主程序**

---

## 🗂️ 目录结构
```
NagaAgent/
├── main.py                     # 主入口
├── config.py                   # 全局配置
├── conversation_core.py        # 对话核心（含兼容模式主逻辑）
├── mcp_manager.py              # MCP服务管理
├── requirements.txt            # 依赖
├── summer/                     # faiss与向量相关
│   ├── memory_manager.py       # 记忆管理主模块
│   ├── summer_faiss.py         # faiss相关操作
│   ├── faiss_index.py          # faiss索引管理
│   ├── embedding.py            # 向量编码
│   ├── memory_flow/            # 记忆分层相关
│   └── summer_upgrade/         # 兼容升级相关脚本
│       └── compat_txt_to_faiss.py # 历史对话兼容主脚本
├── logs/                       # 日志（含历史txt对话）
│   ├── 2025-04-27.txt
│   ├── 2025-05-05.txt
│   ├── ...
│   └── faiss/                  # faiss索引与元数据
├── voice/                      # 语音相关
│   ├── voice_config.py
│   └── voice_handler.py
├── ui/                         # 前端UI
│   ├── pyqt_chat_window.py     # PyQt聊天窗口
│   └── response_utils.py       # 前端通用响应解析工具
├── models/                     # 向量模型等
├── README.md                   # 项目说明
└── ...
```

---

## 🌐 多Agent与MCP服务
- **所有Agent的注册、schema、描述均集中在`mcpserver/mcp_registry.py`，批量管理，极简扩展**
- 支持浏览器、文件、代码等多种Agent，全部可通过handoff机制统一调用
- Agent能力即插即用，自动注册/热插拔，无需重启主程序
- 典型用法示例：

```python
# 读取文件内容
await s.mcp.handoff(
  service_name="file",
  task={"action": "read", "path": "test.txt"}
)
# 运行Python代码
await s.mcp.handoff(
  service_name="coder",
  task={"action": "run", "file": "main.py"}
)
```

---

## 📝 前端UI与响应适配
- **所有后端返回均为结构化JSON，前端通过`ui/response_utils.py`的`extract_message`方法自动适配多种返回格式**
- 优先显示`data.content`，其次`message`，最后原样返回，兼容所有Agent
- PyQt前端自动将所有`\n`和`\\n`换行符转为`<br>`，多行内容显示无障碍
- UI动画、主题、昵称、透明度等全部可在`config.py`和`pyqt_chat_window.py`灵活配置

---

## 🔊 流式语音交互
- 支持语音输入（流式识别，自动转文字）与语音输出（流式合成，边播边出）
- 依赖与配置详见`voice/voice_config.py`和README相关章节

---

## 📝 其它亮点
- 记忆权重、遗忘阈值、冗余去重、短期/长期记忆容量等全部在`config.py`统一管理，便于灵活调整
- 主题归类、召回、权重提升、清理等全部自动化，AI/人工可标记important内容，重要内容一年内不会被清理
- 检索日志自动记录，参数可调，faiss配置示例见`config.py`
- 聊天窗口背景透明度、用户名、主题树召回、流式输出、侧栏动画等全部可自定义
- 支持历史对话一键导入AI多层记忆系统，兼容主题、分层、embedding等所有新特性
- 多Agent分步流水线自动执行机制，支持plan结构自动解析与多步执行

---

如需详细功能/API/扩展说明，见各模块注释与代码，所有变量唯一、注释中文、极致精简。

## 🆙 历史对话兼容升级
- 支持将旧版txt对话内容一键导入AI多层记忆系统，兼容主题、分层、embedding等所有新特性。
- 激活指令：
  ```
  #夏园系统兼容升级
  ```
  - 系统会自动遍历logs目录下所有txt日志，列出所有历史对话内容并编号，输出到终端和`summer/summer_upgrade/history_dialogs.json`。
- 用户可查看编号后，选择导入方式：
  - 全部导入：
    ```
    python summer/summer_upgrade/compat_txt_to_faiss.py import all
    ```
  - 选择性导入（如第1、3、5-8条）：
    ```
    python summer/summer_upgrade/compat_txt_to_faiss.py import 1,3,5-8
    ```
- 兼容过程自动判重，已入库内容不会重复导入，支持断点续跑。
- 兼容内容全部走AI自动主题归类与分层，完全与新系统一致。
- 详细进度、结果和异常均有反馈，安全高效。

## 📚 目录结构
```
NagaAgent/
├── main.py                     # 主入口
├── config.py                   # 全局配置
├── conversation_core.py        # 对话核心（含兼容模式主逻辑）
├── mcp_manager.py              # MCP服务管理
├── requirements.txt            # 依赖
├── summer/                     # faiss与向量相关
│   ├── memory_manager.py       # 记忆管理主模块
│   ├── summer_faiss.py         # faiss相关操作
│   ├── faiss_index.py          # faiss索引管理
│   ├── embedding.py            # 向量编码
│   ├── memory_flow/            # 记忆分层相关
│   └── summer_upgrade/         # 兼容升级相关脚本
│       └── compat_txt_to_faiss.py # 历史对话兼容主脚本
├── logs/                       # 日志（含历史txt对话）
│   ├── 2025-04-27.txt
│   ├── 2025-05-05.txt
│   ├── ...
│   └── faiss/                  # faiss索引与元数据
├── voice/                      # 语音相关
│   ├── voice_config.py
│   └── voice_handler.py
├── ui/                         # 前端UI
│   └── pyqt_chat_window.py     # PyQt聊天窗口
├── models/                     # 向量模型等
├── README.md                   # 项目说明
└── ...
```

## ❓ 常见问题
- Python版本/依赖/虚拟环境/浏览器驱动等问题，详见`setup.ps1`与本README
- IDE报import错误，重启并选择正确解释器
- 语音依赖安装失败，先装C++ Build Tools
- 浏览器无法启动，检查playwright安装与网络
- 主题树/索引/参数/密钥全部在`config.py`统一管理

## 📝 开发模式
- 聊天输入`#devmode`进入开发者模式，后续对话不写入faiss，仅用于MCP测试

## 📝 许可证
MIT License

---

如需详细功能/API/扩展说明，见各模块注释与代码，所有变量唯一、注释中文、极致精简。

## 聊天窗口自定义
1. 聊天窗口背景透明度由`config.BG_ALPHA`统一控制，取值0~1，默认0.4。
2. 用户名自动识别电脑名，变量`config.USER_NAME`，如需自定义可直接修改该变量。

## 智能历史召回机制
1. 默认按主题分片检索历史，极快且相关性高。
2. 若分片查不到，自动兜底遍历所有主题分片模糊检索（faiss_fuzzy_recall），话题跳跃也能召回历史。
3. faiss_fuzzy_recall支持直接调用，返回全局最相关历史。
4. 兜底逻辑已集成主流程，无需手动切换。

## ⚡️ 全新流式输出机制
- AI回复支持前后端全链路流式输出，边生成边显示，极致丝滑。
- 后端采用async生成器yield分段内容，前端Worker线程streaming信号实时追加到对话框。
- 彻底无终端print污染，支持大文本不卡顿。
- 如遇依赖包冲突，建议彻底清理全局PYTHONPATH和环境变量，仅用虚拟环境。

## 侧栏与主聊天区动画优化说明
- 侧栏点击切换时，侧栏宽度、主聊天区宽度、输入框高度均采用同步动画，提升视觉流畅度。
- 输入框隐藏采用高度动画，动画结束后自动清除焦点，避免输入法残留。
- 线程处理增加自动释放，避免内存泄漏。
- 相关动画效果可在`ui/pyqt_chat_window.py`的`toggle_full_img`方法中自定义。

### 使用方法
- 点击侧栏即可切换立绘展开/收起，主聊天区和输入框会自动让位并隐藏/恢复。
- 动画时长、缓动曲线等可根据需要调整源码参数。

## 多Agent分步流水线自动执行机制

系统支持LLM输出plan结构时自动解析并依次执行每一步：
- 每步可包含action结构，指明agent和params参数
- 系统自动调用对应agent，支持上下文在多步间传递
- 每步执行结果实时反馈，全部完成后汇总
- 其它无action的步骤仅输出描述，不自动执行

示例plan结构：
```json
{
  "plan": {
    "goal": "完成复杂多步任务",
    "steps": [
      {"desc": "第一步描述", "action": {"agent": "file", "params": {"action": "read", "path": "test.txt"}}},
      {"desc": "第二步描述", "action": {"agent": "coder", "params": {"action": "edit", "file": "test.py", "code": "print('hello')"}}}
    ]
  }
}
```

如需自定义Agent或扩展plan协议，请参考`mcpserver/agent_xxx/`和`mcp_registry.py`。
