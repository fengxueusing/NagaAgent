# agent_app_launcher.py # 应用启动与管理Agent
import os
import platform
import subprocess
import asyncio
import json
from .app_cache import get_cached_apps, preload_apps  # 应用缓存模块
from .app_name_matcher import update_alias, find_best_app_with_llm

class AppLauncherAgent(object):
    """应用启动与管理Agent，支持打开、列出本机应用"""  # 类注释
    name = "AppLauncher Agent"  # Agent名称

    def __init__(self):
        from .app_cache import preload_apps, get_cached_apps
        preload_apps()  # 初始化时同步预加载
        import sys
        sys.stderr.write(f'✅ AppLauncherAgent初始化完成，预加载应用数: {len(get_cached_apps())}\n')

    def get_system_prompt_with_apps(self):
        """获取包含应用列表的系统提示词"""
        app_list = get_cached_apps()
        app_names = [app['name'] for app in app_list]
        app_list_str = "\n".join([f"- {name}" for name in app_names])
        
        base_prompt = """你是一个智能应用启动助手。你的任务是理解用户的需求，从本地应用列表中选择最合适的应用并启动它。

你的能力：
1. 理解用户的各种表达方式（如'我想写文档'、'打开浏览器'、'启动微信'等）
2. 智能匹配应用名称（如'word'匹配'Microsoft Word'、'浏览器'匹配'Chrome'等）
3. 支持中文和英文应用名称
4. 记录用户偏好，提高下次选择的准确性

可用应用列表：
{app_list}

当用户需要启动应用时，请：
1. 分析用户需求
2. 从应用列表中选择最合适的应用
3. 执行启动操作
4. 返回启动结果

如果找不到合适的应用，请告知用户并建议替代方案。

请用中文回复，保持友好和专业的语调。"""
        
        return base_prompt.format(app_list=app_list_str)

    def run(self, action, app=None, args=None):
        """
        action: 操作类型（open/list/refresh）
        app: 应用名或路径
        args: 启动参数
        """
        if action == "open":
            return self.open_app(app, args)  # 打开应用
        elif action == "list":
            return {"status": "success", "apps": get_cached_apps()}  # 返回缓存应用列表
        elif action == "refresh":
            asyncio.create_task(preload_apps())  # 异步刷新
            return {"status": "success", "message": "正在刷新应用列表，请稍后再试"}
        else:
            return {"status": "error", "message": f"未知操作: {action}"}  # 错误处理

    async def open_app_async(self, app, args=None):
        """异步打开指定应用（使用LLM智能选择）"""
        print(f"open_app_async收到app参数: {app}")
        print(f"缓存应用名: {[item['name'] for item in get_cached_apps()]}")
        
        exe_path = None
        app_list = get_cached_apps()
        
        # 1. 支持绝对路径
        if app and os.path.exists(app):
            exe_path = app
        else:
            # 2. 使用LLM智能选择
            match = await find_best_app_with_llm(app, app_list) if app else None
            if match:
                exe_path = match["path"]
                # 动态学习
                update_alias(app, match["name"])
                print(f"LLM智能选择结果: {match['name']}")
        
        if not exe_path or not os.path.exists(exe_path):
            return {"status": "error", "message": f"未找到应用: {app}"}
        
        try:
            if exe_path.lower().endswith('.lnk'):
                os.startfile(exe_path)  # 用系统方式打开快捷方式
            else:
                cmd = [exe_path]
                if args:
                    if isinstance(args, str):
                        cmd += args.split()
                    elif isinstance(args, list):
                        cmd += args
                subprocess.Popen(cmd, shell=False)
            return {"status": "success", "message": f"已启动: {exe_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def open_app(self, app, args=None):
        """同步打开指定应用（保持向后兼容）"""
        print(f"open_app收到app参数: {app}")
        print(f"缓存应用名: {[item['name'] for item in get_cached_apps()]}")
        exe_path = None
        app_list = get_cached_apps()
        
        # 1. 支持绝对路径
        if app and os.path.exists(app):
            exe_path = app
        else:
            # 2. 使用LLM智能选择（同步版本）
            import asyncio
            try:
                match = asyncio.run(find_best_app_with_llm(app, app_list)) if app else None
                if match:
                    exe_path = match["path"]
                    # 动态学习
                    update_alias(app, match["name"])
                    print(f"LLM智能选择结果: {match['name']}")
            except Exception as e:
                print(f"LLM选择失败: {e}")
        
        if not exe_path or not os.path.exists(exe_path):
            return {"status": "error", "message": f"未找到应用: {app}"}
        try:
            if exe_path.lower().endswith('.lnk'):
                os.startfile(exe_path)  # 用系统方式打开快捷方式
            else:
                cmd = [exe_path]
                if args:
                    if isinstance(args, str):
                        cmd += args.split()
                    elif isinstance(args, list):
                        cmd += args
                subprocess.Popen(cmd, shell=False)
            return {"status": "success", "message": f"已启动: {exe_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def handle_handoff(self, task):
        """
        MCP标准接口，处理handoff请求
        :param task: dict，包含action/app/args等
        """
        action = (
            task.get("action") or
            task.get("operation") or
            task.get("task") or
            ("open" if any(k in task for k in ["app", "app_name", "check_running", "wait_for", "report"]) else None)
        )
        app = (
            task.get("app") or
            task.get("app_name") or
            task.get("check_running") or
            task.get("wait_for") or
            task.get("report")
        )
        args = task.get("args")
        
        # 使用异步版本以获得更好的LLM智能选择
        if action == "open":
            return await self.open_app_async(app, args)
        else:
            return self.run(action, app, args)

    async def process_user_request(self, user_request: str) -> str:
        """处理用户请求（Agent模式）"""
        try:
            # 分析用户请求
            if "列表" in user_request or "查看" in user_request or "显示" in user_request:
                # 用户想查看应用列表
                app_list = get_cached_apps()
                app_names = [app['name'] for app in app_list]
                return f"当前可用的应用有：\n" + "\n".join([f"- {name}" for name in app_names])
            
            elif "刷新" in user_request or "更新" in user_request:
                # 用户想刷新应用列表
                asyncio.create_task(preload_apps())
                return "正在刷新应用列表，请稍后再试"
            
            else:
                # 用户想启动应用
                app_list = get_cached_apps()
                match = await find_best_app_with_llm(user_request, app_list)
                
                if match:
                    # 启动应用
                    result = await self.open_app_async(match['name'])
                    if result['status'] == 'success':
                        return f"✅ 已成功启动 {match['name']}"
                    else:
                        return f"❌ 启动失败：{result['message']}"
                else:
                    return f"抱歉，我没有找到与'{user_request}'匹配的应用。请尝试更具体的描述，或者查看可用应用列表。"
                    
        except Exception as e:
            return f"处理请求时出现错误：{str(e)}"

# 工厂函数：动态创建Agent实例
def create_app_launcher_agent():
    """创建AppLauncherAgent实例"""
    return AppLauncherAgent()

# 获取Agent元数据
def get_agent_metadata():
    """获取Agent元数据"""
    import os
    manifest_path = os.path.join(os.path.dirname(__file__), "agent-manifest.json")
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载元数据失败: {e}")
        return None

# 验证配置
def validate_agent_config(config):
    """验证Agent配置"""
    return True

# 获取依赖
def get_agent_dependencies():
    """获取Agent依赖"""
    return ["app_cache", "app_name_matcher"]
