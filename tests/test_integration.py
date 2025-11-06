"""
集成测试

测试完整的工作流程。
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from agentcli.task_generator import TaskList, Task
from agentcli.task_executor import TaskExecutor


@pytest.fixture
def temp_dir():
    """临时目录"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_templates_dir(temp_dir):
    """模拟模板目录"""
    templates_dir = temp_dir / "templates"
    templates_dir.mkdir()
    
    # 创建 python_cli 模板目录
    cli_template = templates_dir / "python_cli" / "files"
    cli_template.mkdir(parents=True)
    
    # 创建一个简单的模板文件
    readme_template = cli_template / "README.md"
    with open(readme_template, "w") as f:
        f.write("# {{project_name}}\n\n{{description}}")
    
    return templates_dir


def test_task_executor_create_directory(temp_dir, mock_templates_dir):
    """测试任务执行器 - 创建目录"""
    executor = TaskExecutor(mock_templates_dir, temp_dir)
    
    task = Task(
        id=1,
        name="创建目录",
        description="创建测试目录",
        type="create_directory",
        params={"path": "test-project"}
    )
    
    success = executor.execute_single_task(task)
    assert success == True
    assert (temp_dir / "test-project").exists()


def test_task_executor_create_file(temp_dir, mock_templates_dir):
    """测试任务执行器 - 创建文件"""
    executor = TaskExecutor(mock_templates_dir, temp_dir)
    
    # 先创建目录
    (temp_dir / "test-project").mkdir()
    
    task = Task(
        id=2,
        name="创建文件",
        description="创建README",
        type="create_file",
        params={
            "path": "test-project/README.md",
            "content": "# Test Project\n\nThis is a test."
        }
    )
    
    success = executor.execute_single_task(task)
    assert success == True
    assert (temp_dir / "test-project" / "README.md").exists()


def test_task_executor_with_template(temp_dir, mock_templates_dir):
    """测试任务执行器 - 使用模板"""
    executor = TaskExecutor(mock_templates_dir, temp_dir)
    
    (temp_dir / "test-project").mkdir()
    
    task = Task(
        id=2,
        name="从模板创建README",
        description="使用模板创建README",
        type="create_file",
        params={
            "path": "test-project/README.md",
            "template": "python_cli/README.md",
            "variables": {
                "project_name": "Test Project",
                "description": "A test project"
            }
        }
    )
    
    success = executor.execute_single_task(task)
    assert success == True
    
    # 验证变量替换
    readme_path = temp_dir / "test-project" / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()
    
    assert "Test Project" in content
    assert "A test project" in content


def test_task_executor_full_workflow(temp_dir, mock_templates_dir):
    """测试完整工作流程"""
    executor = TaskExecutor(mock_templates_dir, temp_dir)
    
    # 创建任务清单
    task_list = TaskList(
        reasoning="测试工作流程",
        project_name="test-project",
        tasks=[
            Task(
                id=1,
                name="创建项目目录",
                description="创建根目录",
                type="create_directory",
                params={"path": "test-project"}
            ),
            Task(
                id=2,
                name="创建README",
                description="创建项目文档",
                type="create_file",
                params={
                    "path": "test-project/README.md",
                    "content": "# Test Project"
                }
            ),
            Task(
                id=3,
                name="创建src目录",
                description="创建源码目录",
                type="create_directory",
                params={"path": "test-project/src"}
            )
        ]
    )
    
    # 执行任务
    success = executor.execute(task_list)
    assert success == True
    
    # 验证结果
    assert (temp_dir / "test-project").exists()
    assert (temp_dir / "test-project" / "README.md").exists()
    assert (temp_dir / "test-project" / "src").exists()


def test_task_executor_failure_handling(temp_dir, mock_templates_dir):
    """测试任务执行失败处理"""
    executor = TaskExecutor(mock_templates_dir, temp_dir)
    
    # 创建一个会失败的任务（无效路径）
    task = Task(
        id=1,
        name="无效任务",
        description="这个任务会失败",
        type="create_directory",
        params={"path": "../../../invalid/path"}
    )
    
    success = executor.execute_single_task(task)
    assert success == False

