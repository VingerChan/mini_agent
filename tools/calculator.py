from tools.registry import tool


@tool
def calculator(expression: str) -> str:
    """
    计算数学表达式，支持加减乘除，例如 1+1=2、2*4=8
    Args:
        expression: 数学表达式字符串，仅允许数字和运算符(+-*/.)，例如"1+1"、"3*(2+4)"
    """
    allowed_chars = set("0123456789+-*/().% ")
    if not all(c in allowed_chars for c in expression):
        return "错误：表达式包含非法字符"
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"
