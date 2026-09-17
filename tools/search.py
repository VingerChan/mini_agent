from tools.registry import tool


@tool
def search(query: str) -> str:
    """
    根据关键词搜索信息
    Args:
        query: 搜索关键词，例如"今日新闻"、“国际新闻”
    """
    results = [
        f"第一个结果：关于「{query}」的百科介绍，这是一篇详细的说明文章。",
        f"第二个结果：关于「{query}」的最新新闻报道，内容丰富值得关注。",
        f"第三个结果：关于「{query}」的相关讨论，社区热议话题。",
    ]
    return "\n".join(results)
