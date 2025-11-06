"""
核心模块测试
"""

import pytest
from {{module_name}}.core import main_function, helper_function


def test_main_function():
    """测试主函数"""
    result = main_function()
    assert result is not None
    assert isinstance(result, str)


def test_helper_function():
    """测试辅助函数"""
    test_data = "test"
    result = helper_function(test_data)
    assert result == test_data


# 更多测试用例...

