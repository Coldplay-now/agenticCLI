"""
配置模块测试
"""

import pytest
from pathlib import Path
from agentcli.utils.file_ops import validate_path, sanitize_project_name


def test_validate_path_safe():
    """测试安全路径验证"""
    # 安全路径
    assert validate_path("project/src") == True
    assert validate_path("my-project") == True
    assert validate_path("project_name") == True


def test_validate_path_unsafe():
    """测试不安全路径验证"""
    # 不安全路径
    assert validate_path("../../../etc/passwd") == False
    assert validate_path("/absolute/path") == False
    assert validate_path("path/$(command)") == False


def test_sanitize_project_name():
    """测试项目名称清理"""
    assert sanitize_project_name("My Project") == "my-project"
    assert sanitize_project_name("project@#$%name") == "projectname"
    assert sanitize_project_name("Multiple---Hyphens") == "multiple-hyphens"
    assert sanitize_project_name("123-valid-name") == "123-valid-name"


def test_project_name_edge_cases():
    """测试项目名称边界情况"""
    # 全部特殊字符
    assert sanitize_project_name("@#$%^&*()") == ""
    
    # 首尾连字符
    assert sanitize_project_name("---project---") == "project"
    
    # 空格
    assert sanitize_project_name("my project name") == "my-project-name"

