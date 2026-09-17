from tools.registry import tool


@tool
def weather(location: str) -> str:
    """
    查询指定地区的天气详情
    Args:
        location: 需要查询天气的地区名称，例如"北京"、"上海"
    """
    return (
        f"{location}天气详情：\n"
        f"天气：晴天\n"
        f"温度：26°C\n"
        f"湿度：45%\n"
        f"风力：微风"
    )
