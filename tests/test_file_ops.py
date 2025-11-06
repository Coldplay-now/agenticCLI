"""
文件操作测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from agentcli.utils.file_ops import (
    validate_path,
    create_directory,
    create_file,
    read_file,
    file_exists,
    sanitize_project_name
)


@pytest.fixture
def temp_dir():
    """临时目录 fixture"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # 清理
    if temp_path.exists():
        shutil.rmtree(temp_path)


def test_create_directory(temp_dir):
    """测试创建目录"""
    test_dir = temp_dir / "test_project" / "src"
    
    success = create_directory(test_dir)
    assert success == True
    assert test_dir.exists()
    assert test_dir.is_dir()


def test_create_file(temp_dir):
    """测试创建文件"""
    test_file = temp_dir / "test.txt"
    content = "Hello, World!"
    
    success = create_file(test_file, content)
    assert success == True
    assert test_file.exists()
    
    # 验证内容
    with open(test_file, "r") as f:
        assert f.read() == content


def test_create_file_with_parent_dir(temp_dir):
    """测试创建文件（自动创建父目录）"""
    test_file = temp_dir / "nested" / "dir" / "test.txt"
    content = "Test content"
    
    success = create_file(test_file, content)
    assert success == True
    assert test_file.exists()
    assert test_file.parent.exists()


def test_read_file(temp_dir):
    """测试读取文件"""
    test_file = temp_dir / "read_test.txt"
    content = "Test content for reading"
    
    # 先创建文件
    create_file(test_file, content)
    
    # 读取并验证
    read_content = read_file(test_file)
    assert read_content == content


def test_file_exists(temp_dir):
    """测试文件存在检查"""
    existing_file = temp_dir / "existing.txt"
    create_file(existing_file, "content")
    
    assert file_exists(existing_file) == True
    assert file_exists(temp_dir / "nonexistent.txt") == False


def test_sanitize_project_name():
    """测试项目名称清理"""
    test_cases = [
        ("My Project", "my-project"),
        ("project@name", "projectname"),
        ("Multiple   Spaces", "multiple-spaces"),
        ("123-valid", "123-valid"),
        ("UPPERCASE", "uppercase"),
        ("--trimmed--", "trimmed")
    ]
    
    for input_name, expected_output in test_cases:
        assert sanitize_project_name(input_name) == expected_output

