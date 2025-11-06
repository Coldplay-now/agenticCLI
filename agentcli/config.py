"""
配置管理模块

负责加载和验证环境变量配置、系统提示词等。
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from rich.console import Console

console = Console()


class Config(BaseModel):
    """应用配置模型"""
    
    deepseek_api_key: str = Field(..., description="DeepSeek API Key")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API Base URL"
    )
    system_prompt: str = Field(..., description="系统提示词内容")
    project_root: Path = Field(..., description="项目根目录")
    
    class Config:
        arbitrary_types_allowed = True
    
    @validator('deepseek_api_key')
    def validate_api_key(cls, v):
        """验证 API Key 不为空"""
        if not v or v == "your_deepseek_api_key_here":
            raise ValueError(
                "请在 .env 文件中设置有效的 DEEPSEEK_API_KEY"
            )
        return v


def load_system_prompt(project_root: Path) -> str:
    """加载系统提示词
    
    Args:
        project_root: 项目根目录
        
    Returns:
        系统提示词内容
        
    Raises:
        FileNotFoundError: 如果 systemprompt.md 不存在
    """
    prompt_file = project_root / "systemprompt.md"
    
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"找不到系统提示词文件: {prompt_file}\n"
            "请确保 systemprompt.md 文件存在于项目根目录"
        )
    
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if not content.strip():
            raise ValueError("系统提示词文件为空")
        
        return content
    except Exception as e:
        raise RuntimeError(f"读取系统提示词文件失败: {e}")


def load_config() -> Config:
    """加载应用配置
    
    Returns:
        配置对象
        
    Raises:
        ValueError: 配置验证失败
        FileNotFoundError: 找不到必要的文件
    """
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 加载 .env 文件
    env_file = project_root / ".env"
    if not env_file.exists():
        console.print("[yellow]警告: 找不到 .env 文件[/yellow]")
        console.print("\n请按照以下步骤配置：")
        console.print("1. 复制 .env.example 到 .env")
        console.print("   [cyan]cp .env.example .env[/cyan]")
        console.print("2. 编辑 .env 文件，填入你的 DeepSeek API Key")
        console.print("3. 重新运行 AgentCLI\n")
        raise FileNotFoundError("找不到 .env 文件")
    
    load_dotenv(env_file)
    
    # 获取环境变量
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # 加载系统提示词
    try:
        system_prompt = load_system_prompt(project_root)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        raise
    
    # 创建配置对象
    try:
        config = Config(
            deepseek_api_key=api_key,
            deepseek_base_url=base_url,
            system_prompt=system_prompt,
            project_root=project_root
        )
        return config
    except ValueError as e:
        console.print(f"[red]配置验证失败: {e}[/red]")
        console.print("\n请检查 .env 文件中的配置是否正确。")
        raise


def get_templates_dir(config: Config) -> Path:
    """获取模板目录路径
    
    Args:
        config: 配置对象
        
    Returns:
        模板目录路径
    """
    return config.project_root / "agentcli" / "templates"


if __name__ == "__main__":
    # 测试配置加载
    try:
        cfg = load_config()
        console.print("[green]配置加载成功！[/green]")
        console.print(f"API Base URL: {cfg.deepseek_base_url}")
        console.print(f"项目根目录: {cfg.project_root}")
        console.print(f"系统提示词长度: {len(cfg.system_prompt)} 字符")
    except Exception as e:
        console.print(f"[red]配置加载失败: {e}[/red]")

