"""
模板加载器模块

负责读取和管理项目模板。
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console

console = Console()


class TemplateLoader:
    """模板加载器"""
    
    def __init__(self, templates_dir: Path):
        """初始化模板加载器
        
        Args:
            templates_dir: 模板目录路径
        """
        self.templates_dir = templates_dir
        self.templates: Dict[str, Dict] = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载所有模板的元数据"""
        if not self.templates_dir.exists():
            console.print(f"[yellow]警告: 模板目录不存在: {self.templates_dir}[/yellow]")
            return
        
        # 遍历模板目录
        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                template_yaml = template_dir / "template.yaml"
                if template_yaml.exists():
                    try:
                        with open(template_yaml, "r", encoding="utf-8") as f:
                            metadata = yaml.safe_load(f)
                        
                        self.templates[metadata["type"]] = {
                            "name": metadata["name"],
                            "description": metadata["description"],
                            "type": metadata["type"],
                            "variables": metadata.get("variables", []),
                            "files": metadata.get("files", []),
                            "path": template_dir
                        }
                    except Exception as e:
                        console.print(f"[yellow]加载模板失败 {template_dir.name}: {e}[/yellow]")
    
    def get_template(self, template_type: str) -> Optional[Dict]:
        """获取模板信息
        
        Args:
            template_type: 模板类型
            
        Returns:
            模板信息字典，不存在返回 None
        """
        return self.templates.get(template_type)
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板
        
        Returns:
            模板类型列表
        """
        return list(self.templates.keys())
    
    def get_template_file_path(self, template_type: str, file_name: str) -> Optional[Path]:
        """获取模板文件路径
        
        Args:
            template_type: 模板类型
            file_name: 文件名
            
        Returns:
            文件路径，不存在返回 None
        """
        template = self.get_template(template_type)
        if not template:
            return None
        
        file_path = template["path"] / "files" / file_name
        if file_path.exists():
            return file_path
        
        return None
    
    def read_template_file(self, template_type: str, file_name: str) -> Optional[str]:
        """读取模板文件内容
        
        Args:
            template_type: 模板类型
            file_name: 文件名
            
        Returns:
            文件内容，不存在返回 None
        """
        file_path = self.get_template_file_path(template_type, file_name)
        if not file_path:
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            console.print(f"[red]读取模板文件失败: {e}[/red]")
            return None
    
    def get_required_variables(self, template_type: str) -> List[str]:
        """获取模板所需的变量
        
        Args:
            template_type: 模板类型
            
        Returns:
            变量名列表
        """
        template = self.get_template(template_type)
        if template:
            return template.get("variables", [])
        return []


if __name__ == "__main__":
    # 测试模板加载器
    from pathlib import Path
    
    # 假设从项目根目录运行
    templates_dir = Path(__file__).parent.parent / "templates"
    loader = TemplateLoader(templates_dir)
    
    console.print("[cyan]测试模板加载器...[/cyan]\n")
    
    # 列出所有模板
    console.print("[bold]可用模板:[/bold]")
    for template_type in loader.list_templates():
        template = loader.get_template(template_type)
        console.print(f"- {template['name']} ({template_type})")
        console.print(f"  {template['description']}")
    
    # 测试读取模板文件
    console.print("\n[bold]测试读取 python_cli 的 README 模板:[/bold]")
    readme_content = loader.read_template_file("python_cli", "README.md")
    if readme_content:
        console.print(f"成功读取，长度: {len(readme_content)} 字符")
        console.print(f"前 100 字符: {readme_content[:100]}...")
    else:
        console.print("[red]读取失败[/red]")
    
    console.print("\n[green]测试完成！[/green]")

