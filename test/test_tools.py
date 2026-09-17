import tools.calculator  # noqa: F401
import tools.search  # noqa: F401
import tools.weather  # noqa: F401
from tools.registry import registry


class TestCalculator:
    def test_normal(self):
        calc = registry.get("calculator")
        result = calc.func(expression="1+1")
        assert "1+1" in result
        assert "2" in result

    def test_multiply(self):
        calc = registry.get("calculator")
        result = calc.func(expression="2*4")
        assert "2*4" in result
        assert "8" in result

    def test_illegal_char(self):
        calc = registry.get("calculator")
        result = calc.func(expression="abc")
        assert "非法字符" in result

    def test_division_by_zero(self):
        calc = registry.get("calculator")
        result = calc.func(expression="1/0")
        assert "计算错误" in result


class TestSearch:
    def test_normal(self):
        s = registry.get("search")
        result = s.func(query="Python")
        assert "Python" in result
        assert "第一个结果" in result
        assert "第二个结果" in result
        assert "第三个结果" in result


class TestWeather:
    def test_normal(self):
        w = registry.get("weather")
        result = w.func(location="北京")
        assert "北京" in result
        assert "晴天" in result
