import json

def extract_message(response: str) -> str:
    """
    解析后端返回的json字符串，优先取data.content，其次message，否则原样返回
    :param response: 后端返回的json字符串
    :return: message内容（若解析失败则原样返回）
    """
    try:
        data = json.loads(response)
        # 优先取data.content
        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict) and "content" in data["data"]:
                return data["data"]["content"]
            if "message" in data:
                return data["message"]
        return response
    except Exception:
        return response
