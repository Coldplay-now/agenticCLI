"""
任务执行引擎模块

执行任务清单中的各项任务。
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

from .task_generator import Task, TaskList
from .ai_client import AIClient
from .utils.file_ops import (
    create_directory,
    create_file,
    execute_command,
    validate_path
)
from .utils.code_validator import (
    validate_generated_code,
    check_package_structure
)

console = Console()


class TaskExecutor:
    """任务执行器"""
    
    def __init__(
        self,
        templates_dir: Path,
        output_dir: Path = Path("."),
        ai_client: Optional[AIClient] = None,
        requirements: Optional[Dict[str, str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        """初始化任务执行器
        
        Args:
            templates_dir: 模板目录路径
            output_dir: 输出目录（默认为当前目录）
            ai_client: AI 客户端（用于生成代码文件内容）
            requirements: 需求信息字典（用于代码生成）
            conversation_history: 对话历史（用于代码生成）
        """
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        self.ai_client = ai_client
        self.requirements = requirements or {}
        self.conversation_history = conversation_history or []
        self.executed_tasks: List[Task] = []
        self.created_paths: List[Path] = []
        self.project_name: Optional[str] = None
        self.project_variables: Dict[str, str] = {}
    
    def replace_variables(self, text: str, variables: Dict[str, str]) -> str:
        """替换文本中的变量
        
        Args:
            text: 原始文本
            variables: 变量字典
            
        Returns:
            替换后的文本
        """
        result = text
        for key, value in variables.items():
            # 替换 {{variable_name}} 格式
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
            # 也替换 {variable_name} 格式（单层大括号）
            placeholder2 = f"{{{key}}}"
            result = result.replace(placeholder2, str(value))
        return result
    
    def ensure_variables_replaced(self, content: str, file_path: Path) -> str:
        """确保所有变量都被替换
        
        Args:
            content: 文件内容
            file_path: 文件路径
            
        Returns:
            处理后的内容
        """
        # 检查是否还有未替换的变量
        import re
        pattern = r'\{\{?(\w+)\}?\}'
        matches = re.findall(pattern, content)
        
        if matches:
            # 使用项目变量或推断默认值
            project_name = self.project_name or (self.output_dir.name if self.output_dir.name != "." else "")
            module_name = project_name.replace("-", "_").replace(" ", "_") if project_name else ""
            
            defaults = {
                "project_name": project_name or "my-project",
                "module_name": module_name or "my_project",
                "description": self.project_variables.get("description", "项目描述"),
                "author_name": self.project_variables.get("author_name", "开发者"),
                "author_email": self.project_variables.get("author_email", "developer@example.com")
            }
            
            # 合并项目变量
            defaults.update(self.project_variables)
            
            for var_name in matches:
                if var_name in defaults:
                    # 替换 {{variable_name}} 格式
                    placeholder = f"{{{{{var_name}}}}}"
                    content = content.replace(placeholder, str(defaults[var_name]))
                    # 替换 {variable_name} 格式
                    placeholder2 = f"{{{var_name}}}"
                    content = content.replace(placeholder2, str(defaults[var_name]))
        
        return content
    
    def load_template(self, template_path: str, variables: Dict[str, str] = None) -> Optional[str]:
        """加载模板文件
        
        Args:
            template_path: 模板文件相对路径（如 "python_cli/cli.py"）
            variables: 变量字典
            
        Returns:
            模板内容，失败返回 None
        """
        # 如果路径不包含 files/，自动添加
        if "/files/" not in template_path:
            parts = template_path.split("/")
            if len(parts) >= 2:
                template_path = f"{parts[0]}/files/{'/'.join(parts[1:])}"
        
        full_path = self.templates_dir / template_path
        
        if not full_path.exists():
            console.print(f"[yellow]警告: 找不到模板文件 {template_path}[/yellow]")
            return None
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 替换变量
            if variables:
                content = self.replace_variables(content, variables)
            
            return content
        
        except Exception as e:
            console.print(f"[red]读取模板文件失败: {e}[/red]")
            return None
    
    def execute_create_directory(self, task: Task) -> bool:
        """执行创建目录任务
        
        Args:
            task: 任务对象
            
        Returns:
            是否成功
        """
        path_str = task.params.get("path", "")
        if not path_str:
            console.print(f"[red]任务 {task.id} 缺少 path 参数[/red]")
            return False
        
        # 验证路径
        if not validate_path(path_str):
            console.print(f"[red]无效的路径: {path_str}[/red]")
            return False
        
        full_path = self.output_dir / path_str
        
        success = create_directory(full_path)
        if success:
            self.created_paths.append(full_path)
        
        return success
    
    def _is_code_file(self, task: Task) -> bool:
        """判断任务是否为代码文件生成任务
        
        Args:
            task: 任务对象
            
        Returns:
            是否为代码文件任务
        """
        if task.type != "create_file":
            return False
        
        path_str = task.params.get("path", "")
        if not path_str:
            return False
        
        # 判断是否为代码文件（.py）
        if path_str.endswith(".py"):
            # 如果有 code_description 或没有 content/template，则是代码文件任务
            if "code_description" in task.params:
                return True
            if "content" not in task.params and "template" not in task.params:
                return True
        
        return False
    
    def _collect_project_context(self) -> Tuple[Dict[str, str], List[str]]:
        """收集已创建的文件内容和项目结构
        
        Returns:
            (已创建的文件内容字典, 项目结构列表)
        """
        created_files: Dict[str, str] = {}
        project_structure: List[str] = []
        
        # 收集已创建的文件内容
        for path in self.created_paths:
            if path.is_file():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    # 使用相对路径作为键
                    rel_path = str(path.relative_to(self.output_dir))
                    created_files[rel_path] = content
                    project_structure.append(f"文件: {rel_path}")
                except Exception as e:
                    console.print(f"[yellow]警告: 无法读取文件 {path}: {e}[/yellow]")
            elif path.is_dir():
                rel_path = str(path.relative_to(self.output_dir))
                project_structure.append(f"目录: {rel_path}")
        
        return created_files, project_structure
    
    def execute_create_file(self, task: Task, generated_content: Optional[str] = None) -> bool:
        """执行创建文件任务
        
        Args:
            task: 任务对象
            generated_content: 已生成的代码内容（用于代码文件任务）
            
        Returns:
            是否成功
        """
        path_str = task.params.get("path", "")
        if not path_str:
            console.print(f"[red]任务 {task.id} 缺少 path 参数[/red]")
            return False
        
        # 验证路径
        if not validate_path(path_str):
            console.print(f"[red]无效的路径: {path_str}[/red]")
            return False
        
        full_path = self.output_dir / path_str
        
        # 获取内容
        content = generated_content  # 优先使用生成的代码内容
        if not content:
            content = task.params.get("content")
        
        template = task.params.get("template")
        variables = task.params.get("variables", {})
        
        if content:
            # 直接使用提供的内容或生成的代码内容
            if variables:
                content = self.replace_variables(content, variables)
            # 确保所有变量都被替换
            content = self.ensure_variables_replaced(content, full_path)
        elif template:
            # 从模板加载
            content = self.load_template(template, variables)
            if content is None:
                return False
            # 确保所有变量都被替换
            content = self.ensure_variables_replaced(content, full_path)
        else:
            console.print(f"[red]任务 {task.id} 缺少 content、template 或 code_description 参数[/red]")
            return False
        
        success = create_file(full_path, content)
        if success:
            self.created_paths.append(full_path)
        
        return success
    
    def execute_command_task(self, task: Task) -> bool:
        """执行命令任务
        
        Args:
            task: 任务对象
            
        Returns:
            是否成功
        """
        command = task.params.get("command", "")
        if not command:
            console.print(f"[red]任务 {task.id} 缺少 command 参数[/red]")
            return False
        
        cwd = task.params.get("cwd")
        if cwd:
            cwd = self.output_dir / cwd
        else:
            cwd = self.output_dir
        
        return execute_command(command, cwd)
    
    def execute_single_task(self, task: Task, generated_content: Optional[str] = None) -> bool:
        """执行单个任务
        
        Args:
            task: 任务对象
            generated_content: 已生成的代码内容（用于代码文件任务）
            
        Returns:
            是否成功
        """
        if task.type == "create_directory":
            return self.execute_create_directory(task)
        elif task.type == "create_file":
            return self.execute_create_file(task, generated_content)
        elif task.type == "execute_command":
            return self.execute_command_task(task)
        else:
            console.print(f"[red]未知的任务类型: {task.type}[/red]")
            return False
    
    def execute(self, task_list: TaskList) -> bool:
        """执行任务清单
        
        Args:
            task_list: 任务清单对象
            
        Returns:
            是否全部成功
        """
        # 设置项目信息，用于变量替换
        self.project_name = task_list.project_name
        # 从任务中提取变量信息
        for task in task_list.tasks:
            if task.type == "create_file":
                variables = task.params.get("variables", {})
                if variables:
                    self.project_variables.update(variables)
        
        # 将任务分为两类：非代码任务和代码文件任务
        non_code_tasks: List[Task] = []
        code_file_tasks: List[Task] = []
        
        for task in task_list.tasks:
            if self._is_code_file(task):
                code_file_tasks.append(task)
            else:
                non_code_tasks.append(task)
        
        console.print("\n[bold cyan]开始执行任务...[/bold cyan]\n")
        console.print(f"[dim]任务分类: {len(non_code_tasks)} 个非代码任务, {len(code_file_tasks)} 个代码文件任务[/dim]\n")
        
        # 第一阶段：执行所有非代码任务（目录、配置文件、命令等）
        console.print("[bold yellow]阶段 1: 执行非代码任务[/bold yellow]\n")
        
        total_non_code = len(non_code_tasks)
        success_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task_progress = progress.add_task(
                "[cyan]执行非代码任务",
                total=total_non_code
            )
            
            for task in non_code_tasks:
                progress.update(
                    task_progress,
                    description=f"[cyan]正在执行: {task.name}"
                )
                
                success = self.execute_single_task(task)
                
                if success:
                    console.print(f"[green]✓[/green] {task.name}")
                    success_count += 1
                    self.executed_tasks.append(task)
                else:
                    console.print(f"[red]✗[/red] {task.name} - 执行失败")
                    console.print(f"[yellow]任务执行中止（已完成 {success_count}/{total_non_code} 个非代码任务）[/yellow]")
                    return False
                
                progress.update(task_progress, advance=1)
        
        console.print(f"\n[green]非代码任务执行完成！（{success_count}/{total_non_code}）[/green]\n")
        
        # 第二阶段：批量生成所有代码文件内容
        if code_file_tasks:
            console.print("[bold yellow]阶段 2: 生成代码文件内容[/bold yellow]\n")
            
            # 收集已创建的文件内容和项目结构
            created_files, project_structure = self._collect_project_context()
            
            # 批量生成所有代码文件内容
            code_contents: Dict[int, str] = {}  # task.id -> generated content
            
            for task in code_file_tasks:
                path_str = task.params.get("path", "")
                task_description = task.description
                code_description = task.params.get("code_description", task_description)
                
                if not self.ai_client:
                    console.print(f"[red]错误: 无法生成代码文件 {path_str}，缺少 AI 客户端[/red]")
                    return False
                
                # 生成代码内容
                generated_content = self.ai_client.generate_code_content(
                    file_path=path_str,
                    task_description=task_description,
                    code_description=code_description,
                    requirements=self.requirements,
                    conversation_history=self.conversation_history,
                    created_files=created_files,
                    project_structure=project_structure,
                    stream=True
                )
                
                if generated_content:
                    # 验证生成的代码
                    is_valid, issues = validate_generated_code(
                        generated_content,
                        path_str,
                        self.output_dir,
                        created_files
                    )
                    
                    if issues:
                        console.print(f"[yellow]代码验证警告 ({path_str}):[/yellow]")
                        for issue in issues:
                            console.print(f"  {issue}")
                    
                    if not is_valid:
                        console.print(f"[red]✗[/red] 生成的代码验证失败: {path_str}")
                        console.print("[yellow]请检查代码语法错误[/yellow]")
                        return False
                    
                    code_contents[task.id] = generated_content
                    # 更新已创建的文件列表（用于后续代码生成）
                    created_files[path_str] = generated_content
                else:
                    console.print(f"[red]✗[/red] 生成代码失败: {path_str}")
                    return False
            
            console.print(f"\n[green]代码生成完成！（{len(code_contents)}/{len(code_file_tasks)}）[/green]\n")
            
            # 第三阶段：创建所有代码文件
            console.print("[bold yellow]阶段 3: 创建代码文件[/bold yellow]\n")
            
            total_code = len(code_file_tasks)
            code_success_count = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                
                task_progress = progress.add_task(
                    "[cyan]创建代码文件",
                    total=total_code
                )
                
                for task in code_file_tasks:
                    progress.update(
                        task_progress,
                        description=f"[cyan]正在创建: {task.name}"
                    )
                    
                    generated_content = code_contents.get(task.id)
                    if generated_content:
                        success = self.execute_create_file(task, generated_content)
                        
                        if success:
                            console.print(f"[green]✓[/green] {task.name}")
                            code_success_count += 1
                            self.executed_tasks.append(task)
                        else:
                            console.print(f"[red]✗[/red] {task.name} - 创建失败")
                            console.print(f"[yellow]任务执行中止（已完成 {code_success_count}/{total_code} 个代码文件）[/yellow]")
                            return False
                    else:
                        console.print(f"[red]✗[/red] {task.name} - 缺少生成的代码内容")
                        return False
                    
                    progress.update(task_progress, advance=1)
            
            console.print(f"\n[green]代码文件创建完成！（{code_success_count}/{total_code}）[/green]\n")
        
        total_tasks = len(task_list.tasks)
        total_success = len(self.executed_tasks)
        console.print(f"[bold green]所有任务执行完成！（{total_success}/{total_tasks}）[/bold green]")
        
        # 验证包结构
        if self.project_name:
            is_complete, missing_files = check_package_structure(
                self.output_dir,
                self.project_name,
                {str(p.relative_to(self.output_dir)): "" for p in self.created_paths if p.is_file()}
            )
            
            if missing_files:
                console.print(f"\n[yellow]⚠️  包结构检查: 发现缺失的文件[/yellow]")
                for missing in missing_files:
                    console.print(f"  - {missing}")
                console.print("[dim]提示: 这些文件可能需要手动创建或在下一次生成时添加[/dim]")
        
        return True
    
    def show_next_steps(self, task_list: TaskList):
        """显示后续步骤
        
        Args:
            task_list: 任务清单对象
        """
        project_path = self.output_dir / task_list.project_name
        
        next_steps = f"""
[bold cyan]项目创建成功！[/bold cyan]

[bold]项目位置:[/bold] {project_path}

[bold]下一步:[/bold]
1. 进入项目目录
   [green]cd {task_list.project_name}[/green]

2. 查看 README 了解项目详情
   [green]cat README.md[/green]

3. 安装依赖（如果有 requirements.txt）
   [green]pip install -r requirements.txt[/green]

4. 开始开发！
"""
        
        console.print(Panel(next_steps, border_style="green"))
    
    def rollback(self):
        """回滚已执行的任务（删除创建的文件和目录）
        
        注意：这个功能在 MVP 中暂不实现（P2 需求）
        """
        console.print("[yellow]回滚功能暂未实现（P2需求）[/yellow]")
        pass


if __name__ == "__main__":
    # 测试任务执行器
    from .config import load_config, get_templates_dir
    from .task_generator import Task, TaskList
    
    try:
        config = load_config()
        templates_dir = get_templates_dir(config)
        
        executor = TaskExecutor(templates_dir)
        
        # 测试数据
        task_list = TaskList(
            reasoning="测试任务清单",
            project_name="test-project",
            tasks=[
                Task(
                    id=1,
                    name="创建项目目录",
                    description="创建测试项目目录",
                    type="create_directory",
                    params={"path": "test-project"}
                ),
                Task(
                    id=2,
                    name="创建 README",
                    description="创建 README 文件",
                    type="create_file",
                    params={
                        "path": "test-project/README.md",
                        "content": "# Test Project\n\nThis is a test project."
                    }
                )
            ]
        )
        
        console.print("[cyan]测试任务执行器...[/cyan]\n")
        
        success = executor.execute(task_list)
        
        if success:
            executor.show_next_steps(task_list)
        else:
            console.print("\n[red]任务执行失败[/red]")
    
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        import traceback
        traceback.print_exc()

