"""
任务生成器模块

基于 CoT 推理生成任务清单。
"""

import json
import re
from typing import List, Dict, Optional

from pydantic import BaseModel, Field, validator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .ai_client import AIClient

console = Console()


class Task(BaseModel):
    """任务模型"""
    id: int = Field(..., description="任务 ID")
    name: str = Field(..., description="任务名称")
    description: str = Field(..., description="任务描述")
    type: str = Field(..., description="任务类型: create_directory/create_file/execute_command")
    params: Dict = Field(..., description="任务参数")
    
    @validator('type')
    def validate_type(cls, v):
        """验证任务类型"""
        valid_types = ["create_directory", "create_file", "execute_command"]
        if v not in valid_types:
            raise ValueError(f"任务类型必须是: {', '.join(valid_types)}")
        return v


class TaskList(BaseModel):
    """任务清单模型"""
    reasoning: str = Field(..., description="CoT 推理过程")
    project_name: str = Field(..., description="项目名称")
    tasks: List[Task] = Field(..., description="任务列表")
    
    @validator('tasks')
    def validate_task_count(cls, v):
        """验证任务数量"""
        if len(v) > 10:
            raise ValueError("任务数量不能超过 10 个")
        if len(v) == 0:
            raise ValueError("任务列表不能为空")
        return v


class TaskGenerator:
    """任务生成器"""
    
    def __init__(self, ai_client: AIClient):
        """初始化任务生成器
        
        Args:
            ai_client: AI 客户端
        """
        self.ai_client = ai_client
    
    def extract_task_list_json(self, response: str) -> Optional[str]:
        """从响应中提取任务清单 JSON
        
        Args:
            response: AI 响应内容
            
        Returns:
            JSON 字符串，如果未找到返回 None
        """
        # 查找 [TASK_LIST_START] 和 [TASK_LIST_END] 之间的内容
        pattern = r'\[TASK_LIST_START\](.*?)\[TASK_LIST_END\]'
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # 如果没有找到标记，尝试直接查找 JSON
        # 寻找以 { 开头，} 结尾的内容
        json_pattern = r'\{[\s\S]*\}'
        match = re.search(json_pattern, response)
        
        if match:
            return match.group(0)
        
        return None
    
    def extract_reasoning(self, response: str) -> str:
        """从响应中提取推理过程
        
        Args:
            response: AI 响应内容
            
        Returns:
            推理过程文本
        """
        # 提取 [TASK_LIST_START] 之前的内容
        parts = response.split('[TASK_LIST_START]')
        if len(parts) > 1:
            return parts[0].strip()
        return ""
    
    def generate_tasks(
        self,
        requirements: Dict[str, str],
        conversation_history: List[Dict[str, str]]
    ) -> Optional[TaskList]:
        """生成任务清单
        
        Args:
            requirements: 需求字典
            conversation_history: 对话历史
            
        Returns:
            任务清单对象，失败返回 None
        """
        console.print("\n[bold cyan]🤖 AI 正在分析需求并生成任务清单...[/bold cyan]\n")
        console.print("[dim]（以下内容为 AI 实时推理过程）[/dim]\n")
        
        # 调用 AI 生成任务清单（使用流式输出）
        response = self.ai_client.generate_task_list(
            requirements,
            conversation_history,
            stream=True  # 启用流式输出
        )
        
        if not response:
            console.print("\n[red]生成任务清单失败[/red]")
            return None
        
        console.print()  # 空行分隔
        
        # 提取 JSON
        json_str = self.extract_task_list_json(response)
        if not json_str:
            console.print("[red]无法从响应中提取任务清单 JSON[/red]")
            console.print("\n[dim]响应内容：[/dim]")
            console.print(response[:500] + "..." if len(response) > 500 else response)
            return None
        
        # 解析 JSON
        try:
            data = json.loads(json_str)
            task_list = TaskList(**data)
            return task_list
        
        except json.JSONDecodeError as e:
            console.print(f"[red]JSON 解析失败: {e}[/red]")
            console.print("\n[dim]JSON 内容：[/dim]")
            console.print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
            return None
        
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]任务清单验证失败: {error_msg}[/red]")
            
            # 如果是任务数量超限，提供更详细的提示
            if "任务数量不能超过 10 个" in error_msg:
                console.print("\n[yellow]提示：[/yellow]")
                console.print("AI 生成了超过 10 个任务。建议：")
                console.print("1. 重新运行，AI 会尝试合并相似任务")
                console.print("2. 或者简化项目需求，分阶段实现")
                console.print("3. 相似任务可以合并：")
                console.print("   - 多个 .py 文件 → 合并为一个任务")
                console.print("   - 多个目录 → 合并为一个任务")
                console.print("   - 配置文件 → 合并为一个任务")
            
            return None
    
    def show_task_list(self, task_list: TaskList):
        """显示任务清单
        
        Args:
            task_list: 任务清单对象
        """
        console.print("\n")
        console.print(Panel.fit(
            f"[bold]项目名称:[/bold] {task_list.project_name}\n"
            f"[bold]任务数量:[/bold] {len(task_list.tasks)}",
            title="[bold green]任务清单[/bold green]",
            border_style="green"
        ))
        
        # 创建表格
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=3)
        table.add_column("任务名称", style="cyan")
        table.add_column("描述", style="white")
        table.add_column("类型", style="yellow", width=18)
        
        for task in task_list.tasks:
            table.add_row(
                str(task.id),
                task.name,
                task.description,
                task.type
            )
        
        console.print(table)
    
    def confirm_task_list(self, task_list: TaskList) -> bool:
        """确认任务清单
        
        Args:
            task_list: 任务清单对象
            
        Returns:
            是否确认执行
        """
        from rich.prompt import Confirm
        
        self.show_task_list(task_list)
        
        console.print("\n")
        confirmed = Confirm.ask(
            "[bold]确认执行以上任务？[/bold]",
            default=True
        )
        
        return confirmed


if __name__ == "__main__":
    # 测试任务生成器
    from .config import load_config
    from .ai_client import AIClient
    
    try:
        config = load_config()
        ai_client = AIClient(config)
        generator = TaskGenerator(ai_client)
        
        # 测试数据
        requirements = {
            "project_type": "Python CLI 工具",
            "purpose": "文件批量重命名工具",
            "project_name": "file-renamer"
        }
        
        conversation_history = [
            {"role": "user", "content": "A"},
            {"role": "user", "content": "文件批量重命名工具"}
        ]
        
        console.print("[cyan]测试任务生成器...[/cyan]\n")
        
        task_list = generator.generate_tasks(requirements, conversation_history)
        
        if task_list:
            generator.show_task_list(task_list)
            console.print("\n[green]任务生成成功！[/green]")
        else:
            console.print("\n[red]任务生成失败[/red]")
    
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")

