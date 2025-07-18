# agent_weather_time.py # 天气和时间查询Agent
import json # 导入json模块
import aiohttp # 异步HTTP请求
from agents import Agent, ComputerTool # 导入Agent和工具基类
from config import DEBUG # 导入全局DEBUG配置
import requests # 用于同步获取IP和城市
import re # 用于正则解析
from datetime import datetime, timedelta # 用于日期处理
IPIP_URL = "https://myip.ipip.net/" # 统一配置
from .city_code_map import CITY_CODE_MAP # 导入城市编码表

class WeatherTimeTool:
    """天气和时间工具类"""
    def __init__(self):
        self._ip_info = None # 缓存IP信息
        self._local_ip = None # 本地IP
        self._local_city = None # 本地城市
        self._get_local_ip_and_city() # 初始化时获取本地IP和城市
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._preload_ip_info())
            else:
                self._ip_info = None # 不再异步获取IP
        except Exception:
            self._ip_info = None

    def _get_local_ip_and_city(self):
        """同步获取本地IP和城市"""
        try:
            resp = requests.get(IPIP_URL, timeout=5)
            resp.encoding = 'utf-8'
            html = resp.text
            match = re.search(r"当前 IP：([\d\.]+)\s+来自于：(.+?)\s{2,}", html)
            if match:
                self._local_ip = match.group(1)
                self._local_city = match.group(2)
            else:
                self._local_ip = None
                self._local_city = None
        except Exception as e:
            self._local_ip = None
            self._local_city = None

    async def _preload_ip_info(self):
        pass # 兼容保留，不再异步获取IP

    async def get_weather(self, province, city):
        """调用高德地图天气接口，city参数为编码，返回原始json并替换reporttime为系统时间"""  # 右侧注释
        url = f'https://restapi.amap.com/v3/weather/weatherInfo?city={city}&key=06e5619c6e787a67ae4b9f177ab48fe2'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json(content_type=None)
                # 替换reporttime为系统当前时间 # 右侧注释
                if data.get('lives') and isinstance(data['lives'], list):
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    for live in data['lives']:
                        if isinstance(live, dict):
                            live['reporttime'] = current_time
                return data

    async def handle(self, action=None, ip=None, city=None, query=None, format=None, **kwargs):
        """统一处理入口，自动查表获取城市编码，API用编码，返回原始数据"""  # 右侧注释
        # city为'auto'或空时自动用本地城市 # 右侧注释
        if city in [None, '', 'auto']:
            city_str = getattr(self, '_local_city', '') or ''
        else:
            city_str = city
        if city_str.startswith('中国'):
            city_str = city_str[2:].strip()
        province, city_name = city_str, city_str
        if city_str:
            match = re.match(r"^([\u4e00-\u9fa5]+) ([\u4e00-\u9fa5]+)$", city_str)
            if match:
                province = match.group(1)
                city_name = match.group(2)
            else:
                parts = city_str.split()
                if len(parts) >= 2:
                    province = parts[-2]
                    city_name = parts[-1]
                else:
                    province = city_str
                    city_name = city_str
        # 新增：查表获取编码 # 右侧注释
        city_code = CITY_CODE_MAP.get(city_name) or CITY_CODE_MAP.get(province)
        if not city_code:
            return {'status': 'error', 'message': f'未找到城市编码: {city_name}'}
        if action in ['weather', 'get_weather', 'current_weather', 'time', 'get_time', 'current_time']:
            weather = await self.get_weather(province, city_code)
            return {
                'status': 'ok',
                'message': 'API原始数据',
                'data': weather
            }
        else:
            return {'status': 'error', 'message': f'未知操作: {action}'}

class WeatherTimeAgent(Agent):
    """天气和时间Agent"""
    def __init__(self):
        self._tool = WeatherTimeTool() # 预加载
        super().__init__(
            name="WeatherTime Agent", # Agent名称
            instructions="天气和时间智能体", # 角色描述
            tools=[ComputerTool(self._tool)], # 注入工具
            model="weather-time-use-preview" # 使用统一模型
        )
        import sys
        ip_str = getattr(self._tool, '_local_ip', '未获取到IP')  # 直接用本地IP
        city_str = getattr(self._tool, '_local_city', '未知城市') # 获取本地城市
        sys.stderr.write(f'✅ WeatherTimeAgent初始化完成，登陆地址：{city_str}\n')

    async def handle_handoff(self, task: dict) -> str:
        try:
            # 兼容多种action字段
            action = (
                task.get("action") or
                task.get("operation") or
                task.get("task") or
                task.get("query_type") or
                task.get("type") or  # 新增对type字段的兼容
                (("weather" if "weather" in str(task).lower() else None) if any(k in task for k in ["city", "weather", "get_weather"]) else None) or
                (("time" if "time" in str(task).lower() else None) if any(k in task for k in ["time", "get_time"]) else None)
            )
            ip = task.get("ip")
            city = task.get("city") or task.get("location")  # 兼容location字段
            query = task.get("query")
            format = task.get("format")
            # 兜底：如果action还没有，尝试从query/format推断
            if not action:
                if query:
                    if 'time' in query or '时间' in query:
                        action = 'time'
                    elif 'weather' in query or '天气' in query:
                        action = 'weather'
                elif format:
                    if 'time' in format or '时间' in format:
                        action = 'time'
                    elif 'weather' in format or '天气' in format:
                        action = 'weather'
            result = await self._tool.handle(action, ip, city, query, format)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e), "data": {}}, ensure_ascii=False)