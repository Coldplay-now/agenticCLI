"""
对话管理模块

管理多轮对话流程，收集用户需求。
"""

from typing import List, Dict, Optional
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .ai_client import AIClient

console = Console()


class ProjectType(Enum):
    """项目类型枚举"""
    PYTHON_CLI = "python_cli"
    FASTAPI = "fastapi"


class ConversationManager:
    """对话管理器"""
    
    def __init__(self, ai_client: AIClient):
        """初始化对话管理器
        
        Args:
            ai_client: AI 客户端
        """
        self.ai_client = ai_client
        self.conversation_history: List[Dict[str, str]] = []
        self.requirements: Dict[str, str] = {}
    
    def add_message(self, role: str, content: str):
        """添加消息到对话历史
        
        Args:
            role: 角色（user/assistant）
            content: 消息内容
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def ask_project_type(self) -> Optional[ProjectType]:
        """询问项目类型
        
        Returns:
            项目类型
        """
        console.print(Panel.fit(
            "[bold cyan]请问你想创建什么类型的项目？[/bold cyan]\n\n"
            "[green]A)[/green] Python CLI 工具\n"
            "[green]B)[/green] Python Web API (FastAPI)",
            title="项目类型"
        ))
        
        choice = Prompt.ask(
            "\n请选择",
            choices=["A", "B", "a", "b"],
            default="A"
        ).upper()
        
        project_type = None
        if choice == "A":
            project_type = ProjectType.PYTHON_CLI
            self.requirements["project_type"] = "Python CLI 工具"
        elif choice == "B":
            project_type = ProjectType.FASTAPI
            self.requirements["project_type"] = "Python Web API (FastAPI)"
        
        # 记录到对话历史
        self.add_message("user", choice)
        
        return project_type
    
    def ask_project_purpose(self) -> str:
        """询问项目用途
        
        Returns:
            项目用途描述
        """
        project_type = self.requirements.get("project_type", "项目")
        
        console.print(f"\n[cyan]这个{project_type}的主要用途是什么？[/cyan]")
        console.print("[dim]（请简单描述项目要实现的核心功能）[/dim]")
        
        purpose = Prompt.ask("\n请描述")
        
        self.requirements["purpose"] = purpose
        self.add_message("user", purpose)
        
        return purpose
    
    def ask_database_support(self) -> str:
        """询问是否需要数据库支持（仅 FastAPI）
        
        Returns:
            数据库选择
        """
        console.print(Panel.fit(
            "[bold cyan]需要数据库支持吗？[/bold cyan]\n\n"
            "[green]A)[/green] 需要（SQLite - 适合开发和小型项目）\n"
            "[green]B)[/green] 需要（PostgreSQL - 适合生产环境）\n"
            "[green]C)[/green] 暂时不需要",
            title="数据库配置"
        ))
        
        choice = Prompt.ask(
            "\n请选择",
            choices=["A", "B", "C", "a", "b", "c"],
            default="A"
        ).upper()
        
        db_choice = ""
        if choice == "A":
            db_choice = "SQLite"
            self.requirements["database"] = "SQLite"
        elif choice == "B":
            db_choice = "PostgreSQL"
            self.requirements["database"] = "PostgreSQL"
        elif choice == "C":
            db_choice = "不需要"
            self.requirements["database"] = "不需要"
        
        self.add_message("user", choice)
        
        return db_choice
    
    def ask_docker_support(self) -> bool:
        """询问是否需要 Docker 配置（仅 FastAPI）
        
        Returns:
            是否需要 Docker
        """
        console.print(Panel.fit(
            "[bold cyan]需要 Docker 配置吗？[/bold cyan]\n\n"
            "[green]A)[/green] 需要\n"
            "[green]B)[/green] 不需要",
            title="Docker 配置"
        ))
        
        choice = Prompt.ask(
            "\n请选择",
            choices=["A", "B", "a", "b"],
            default="A"
        ).upper()
        
        needs_docker = choice == "A"
        self.requirements["docker"] = "需要" if needs_docker else "不需要"
        self.add_message("user", choice)
        
        return needs_docker
    
    def ask_project_name(self) -> str:
        """询问项目名称
        
        Returns:
            项目名称
        """
        console.print("\n[cyan]请输入项目名称（用于创建目录）[/cyan]")
        console.print("[dim]（建议使用小写字母和连字符，如: my-project）[/dim]")
        
        project_name = Prompt.ask("\n项目名称", default="my-project")
        
        # 验证项目名称
        project_name = project_name.lower().strip()
        project_name = project_name.replace(" ", "-")
        
        self.requirements["project_name"] = project_name
        self.add_message("user", project_name)
        
        return project_name
    
    def collect_requirements(self) -> Dict[str, str]:
        """收集项目需求
        
        Returns:
            需求字典
        """
        # 1. 询问项目类型
        project_type = self.ask_project_type()
        if not project_type:
            return {}
        
        # 2. 询问项目用途
        self.ask_project_purpose()
        
        # 3. 根据项目类型询问特定需求
        if project_type == ProjectType.FASTAPI:
            self.ask_database_support()
            self.ask_docker_support()
        
        # 4. 询问项目名称
        self.ask_project_name()
        
        return self.requirements
    
    def show_requirements_summary(self):
        """显示需求总结"""
        console.print("\n")
        console.print(Panel.fit(
            "\n".join([f"[cyan]{k}[/cyan]: {v}" for k, v in self.requirements.items()]),
            title="[bold green]需求总结[/bold green]",
            border_style="green"
        ))
    
    def is_ready_for_generation(self) -> bool:
        """判断是否收集了足够的信息
        
        Returns:
            是否可以生成任务清单
        """
        required_fields = ["project_type", "purpose", "project_name"]
        return all(field in self.requirements for field in required_fields)


if __name__ == "__main__":
    # 测试对话管理器
    from .config import load_config
    from .ai_client import AIClient
    
    try:
        config = load_config()
        ai_client = AIClient(config)
        manager = ConversationManager(ai_client)
        
        console.print("[bold green]欢迎使用 AgentCLI！[/bold green]\n")
        console.print("我将帮助你创建项目。让我们开始吧！\n")
        
        # 收集需求
        requirements = manager.collect_requirements()
        
        if requirements:
            manager.show_requirements_summary()
            console.print("\n[green]需求收集完成！[/green]")
        else:
            console.print("\n[yellow]需求收集未完成[/yellow]")
    
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")

