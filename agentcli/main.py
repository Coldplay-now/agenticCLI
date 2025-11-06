"""
AgentCLI 主程序入口

整合所有模块，提供完整的用户交互流程。
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from . import __version__
from .config import load_config, get_templates_dir
from .ai_client import AIClient
from .conversation import ConversationManager
from .task_generator import TaskGenerator
from .task_executor import TaskExecutor

console = Console()


def show_welcome():
    """显示欢迎信息"""
    welcome_text = f"""
[bold cyan]AgentCLI v{__version__}[/bold cyan]

[bold]智能项目初始化助手[/bold]

通过 AI 驱动的对话，快速创建规范的项目脚手架。

[dim]- 支持 Python CLI 工具模板
- 支持 FastAPI Web 项目模板
- CoT 推理分析需求
- 自动生成完整项目结构[/dim]
"""
    
    console.print(Panel.fit(
        welcome_text,
        border_style="cyan",
        padding=(1, 2)
    ))


def show_completion_message(project_name: str, project_path: Path):
    """显示完成信息
    
    Args:
        project_name: 项目名称
        project_path: 项目路径
    """
    completion_text = f"""
[bold green]项目创建成功！[/bold green]

[bold]项目位置:[/bold]
[cyan]{project_path}[/cyan]

[bold]下一步:[/bold]

1. 进入项目目录
   [green]cd {project_name}[/green]

2. 查看 README 了解项目详情
   [green]cat README.md[/green]

3. 开始开发！
"""
    
    console.print(Panel.fit(
        completion_text,
        border_style="green",
        padding=(1, 2)
    ))


@click.command()
@click.version_option(version=__version__)
@click.option('--output-dir', '-o', type=click.Path(), default=".",
              help='输出目录（默认为当前目录）')
def cli(output_dir):
    """AgentCLI - 智能项目初始化助手
    
    通过 AI 对话快速创建项目脚手架。
    """
    try:
        # 显示欢迎信息
        show_welcome()
        console.print()
        
        # 加载配置
        console.print("[cyan]正在加载配置...[/cyan]")
        try:
            config = load_config()
            console.print("[green]✓[/green] 配置加载成功\n")
        except Exception as e:
            console.print(f"[red]✗[/red] 配置加载失败: {e}\n")
            console.print("[yellow]请按照以下步骤配置 AgentCLI：[/yellow]")
            console.print("1. 确保 .env 文件存在并包含有效的 DEEPSEEK_API_KEY")
            console.print("2. 确保 systemprompt.md 文件存在\n")
            sys.exit(1)
        
        # 初始化 AI 客户端
        console.print("[cyan]正在连接 AI 服务...[/cyan]")
        ai_client = AIClient(config)
        console.print("[green]✓[/green] AI 服务连接成功\n")
        
        # 获取模板目录
        templates_dir = get_templates_dir(config)
        
        # 创建对话管理器
        conversation_manager = ConversationManager(ai_client)
        
        # 开始收集需求
        console.print(Panel.fit(
            "[bold]让我们开始创建你的项目！[/bold]\n\n"
            "我会通过几个问题来了解你的需求。",
            border_style="cyan"
        ))
        console.print()
        
        requirements = conversation_manager.collect_requirements()
        
        if not requirements or not conversation_manager.is_ready_for_generation():
            console.print("\n[yellow]需求收集未完成，程序退出。[/yellow]")
            sys.exit(0)
        
        # 显示需求总结
        conversation_manager.show_requirements_summary()
        
        # 生成任务清单
        console.print()
        task_generator = TaskGenerator(ai_client)
        
        task_list = task_generator.generate_tasks(
            requirements,
            conversation_manager.conversation_history
        )
        
        if not task_list:
            console.print("\n[red]任务清单生成失败，程序退出。[/red]")
            console.print("[yellow]提示: 请检查 AI 服务是否正常，或尝试重新运行。[/yellow]")
            sys.exit(1)
        
        # 确认任务清单
        confirmed = task_generator.confirm_task_list(task_list)
        
        if not confirmed:
            console.print("\n[yellow]任务已取消。[/yellow]")
            sys.exit(0)
        
        # 执行任务
        output_path = Path(output_dir).resolve()
        task_executor = TaskExecutor(
            templates_dir,
            output_path,
            ai_client=ai_client,
            requirements=requirements,
            conversation_history=conversation_manager.conversation_history
        )
        
        success = task_executor.execute(task_list)
        
        if success:
            # 显示完成信息
            console.print()
            project_path = output_path / task_list.project_name
            show_completion_message(task_list.project_name, project_path)
            
            # 显示额外的后续步骤
            task_executor.show_next_steps(task_list)
        else:
            console.print("\n[red]项目创建失败。[/red]")
            console.print("[yellow]部分文件可能已创建，请检查输出目录。[/yellow]")
            sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]程序被用户中断。[/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"\n[red]发生错误: {e}[/red]")
        
        # 调试模式下显示完整堆栈
        import os
        if os.getenv("DEBUG"):
            import traceback
            traceback.print_exc()
        
        sys.exit(1)


@click.group()
@click.version_option(version=__version__)
def main():
    """AgentCLI - 智能项目初始化助手"""
    pass


@main.command()
def init():
    """创建新项目（交互式）"""
    cli.callback()


@main.command()
def version():
    """显示版本信息"""
    rprint(f"[cyan]AgentCLI[/cyan] version [green]{__version__}[/green]")


@main.command()
def doctor():
    """检查环境配置"""
    console.print("[cyan]正在检查环境配置...[/cyan]\n")
    
    issues = []
    
    # 检查 .env 文件
    env_file = Path(".env")
    if env_file.exists():
        console.print("[green]✓[/green] .env 文件存在")
    else:
        console.print("[red]✗[/red] .env 文件不存在")
        issues.append("创建 .env 文件并配置 DEEPSEEK_API_KEY")
    
    # 检查 systemprompt.md
    prompt_file = Path("systemprompt.md")
    if prompt_file.exists():
        console.print("[green]✓[/green] systemprompt.md 文件存在")
    else:
        console.print("[red]✗[/red] systemprompt.md 文件不存在")
        issues.append("确保 systemprompt.md 文件在项目根目录")
    
    # 尝试加载配置
    try:
        from .config import load_config
        config = load_config()
        console.print("[green]✓[/green] 配置加载成功")
    except Exception as e:
        console.print(f"[red]✗[/red] 配置加载失败: {e}")
        issues.append(f"修复配置问题: {e}")
    
    # 显示结果
    console.print()
    if issues:
        console.print("[yellow]发现以下问题：[/yellow]")
        for i, issue in enumerate(issues, 1):
            console.print(f"{i}. {issue}")
    else:
        console.print("[green]所有检查通过！AgentCLI 已准备就绪。[/green]")


if __name__ == "__main__":
    cli()

