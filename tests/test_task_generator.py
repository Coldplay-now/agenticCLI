"""
任务生成器测试
"""

import pytest
import json
from agentcli.task_generator import Task, TaskList, TaskGenerator


def test_task_model():
    """测试任务模型"""
    task = Task(
        id=1,
        name="测试任务",
        description="这是一个测试任务",
        type="create_directory",
        params={"path": "test-project"}
    )
    
    assert task.id == 1
    assert task.name == "测试任务"
    assert task.type == "create_directory"


def test_task_invalid_type():
    """测试无效的任务类型"""
    with pytest.raises(ValueError):
        Task(
            id=1,
            name="测试",
            description="测试",
            type="invalid_type",
            params={}
        )


def test_task_list_model():
    """测试任务清单模型"""
    tasks = [
        Task(
            id=1,
            name="任务1",
            description="描述1",
            type="create_directory",
            params={"path": "dir1"}
        ),
        Task(
            id=2,
            name="任务2",
            description="描述2",
            type="create_file",
            params={"path": "file1.txt", "content": "test"}
        )
    ]
    
    task_list = TaskList(
        reasoning="测试推理",
        project_name="test-project",
        tasks=tasks
    )
    
    assert task_list.project_name == "test-project"
    assert len(task_list.tasks) == 2


def test_task_list_too_many_tasks():
    """测试任务数量超限"""
    tasks = [
        Task(
            id=i,
            name=f"任务{i}",
            description=f"描述{i}",
            type="create_directory",
            params={"path": f"dir{i}"}
        )
        for i in range(11)  # 11个任务，超过限制
    ]
    
    with pytest.raises(ValueError, match="任务数量不能超过 10 个"):
        TaskList(
            reasoning="测试",
            project_name="test",
            tasks=tasks
        )


def test_extract_task_list_json():
    """测试提取任务清单 JSON"""
    # 模拟 AI 响应
    response = """
    这是推理过程...
    
    [TASK_LIST_START]
    {
        "reasoning": "测试推理",
        "project_name": "test-project",
        "tasks": [
            {
                "id": 1,
                "name": "创建目录",
                "description": "创建项目目录",
                "type": "create_directory",
                "params": {"path": "test-project"}
            }
        ]
    }
    [TASK_LIST_END]
    """
    
    # 需要 AI 客户端，这里使用 Mock
    from unittest.mock import Mock
    
    ai_client = Mock()
    generator = TaskGenerator(ai_client)
    
    json_str = generator.extract_task_list_json(response)
    assert json_str is not None
    
    # 验证 JSON 可以解析
    data = json.loads(json_str)
    assert data["project_name"] == "test-project"
    assert len(data["tasks"]) == 1

