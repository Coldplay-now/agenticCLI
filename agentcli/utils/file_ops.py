"""
文件操作工具模块

提供安全的文件和目录操作功能。
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def validate_path(path_str: str) -> bool:
    """验证路径安全性（防止路径遍历攻击）
    
    Args:
        path_str: 路径字符串
        
    Returns:
        是否安全
    """
    # 不允许包含 ..
    if ".." in path_str:
        return False
    
    # 不允许绝对路径
    if path_str.startswith("/") or (len(path_str) > 1 and path_str[1] == ":"):
        return False
    
    # 不允许特殊字符
    dangerous_chars = ["<", ">", "|", "&", ";", "`", "$", "(", ")"]
    if any(char in path_str for char in dangerous_chars):
        return False
    
    return True


def create_directory(path: Path) -> bool:
    """创建目录
    
    Args:
        path: 目录路径
        
    Returns:
        是否成功
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        console.print(f"[red]创建目录失败 {path}: {e}[/red]")
        return False


def create_file(path: Path, content: str) -> bool:
    """创建文件
    
    Args:
        path: 文件路径
        content: 文件内容
        
    Returns:
        是否成功
    """
    try:
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return True
    except Exception as e:
        console.print(f"[red]创建文件失败 {path}: {e}[/red]")
        return False


def execute_command(command: str, cwd: Optional[Path] = None) -> bool:
    """执行命令
    
    Args:
        command: 命令字符串
        cwd: 工作目录
        
    Returns:
        是否成功
    """
    try:
        # 验证命令安全性
        dangerous_commands = ["rm -rf /", "del /f /q", "format"]
        if any(dangerous in command.lower() for dangerous in dangerous_commands):
            console.print(f"[red]拒绝执行危险命令: {command}[/red]")
            return False
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True
        else:
            console.print(f"[yellow]命令执行返回非零: {result.returncode}[/yellow]")
            if result.stderr:
                console.print(f"[dim]{result.stderr}[/dim]")
            return False
    
    except subprocess.TimeoutExpired:
        console.print(f"[red]命令执行超时: {command}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]命令执行失败: {e}[/red]")
        return False


def read_file(path: Path) -> Optional[str]:
    """读取文件内容
    
    Args:
        path: 文件路径
        
    Returns:
        文件内容，失败返回 None
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        console.print(f"[red]读取文件失败 {path}: {e}[/red]")
        return None


def file_exists(path: Path) -> bool:
    """检查文件是否存在
    
    Args:
        path: 文件路径
        
    Returns:
        是否存在
    """
    return path.exists()


def sanitize_project_name(name: str) -> str:
    """清理项目名称
    
    Args:
        name: 原始名称
        
    Returns:
        清理后的名称
    """
    # 转小写
    name = name.lower()
    
    # 替换空格为连字符
    name = name.replace(" ", "-")
    
    # 只保留字母、数字、连字符和下划线
    name = re.sub(r'[^a-z0-9\-_]', '', name)
    
    # 移除连续的连字符
    name = re.sub(r'-+', '-', name)
    
    # 移除首尾的连字符
    name = name.strip('-')
    
    return name


if __name__ == "__main__":
    # 测试文件操作
    from pathlib import Path
    
    console.print("[cyan]测试文件操作工具...[/cyan]\n")
    
    # 测试路径验证
    test_paths = [
        ("normal/path", True),
        ("../../../etc/passwd", False),
        ("/absolute/path", False),
        ("path/with/$(command)", False),
        ("valid-project_name", True)
    ]
    
    console.print("[bold]路径验证测试:[/bold]")
    for path, expected in test_paths:
        result = validate_path(path)
        status = "[green]✓[/green]" if result == expected else "[red]✗[/red]"
        console.print(f"{status} {path}: {result}")
    
    # 测试项目名称清理
    console.print("\n[bold]项目名称清理测试:[/bold]")
    test_names = [
        "My Project",
        "project@#$%name",
        "Multiple---Hyphens",
        "123-valid-name"
    ]
    
    for name in test_names:
        cleaned = sanitize_project_name(name)
        console.print(f"{name} → {cleaned}")
    
    console.print("\n[green]测试完成！[/green]")

