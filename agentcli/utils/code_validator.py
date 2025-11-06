"""
代码验证工具模块

提供代码语法验证、导入验证等功能。
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from rich.console import Console

console = Console()


class CodeValidationError(Exception):
    """代码验证错误"""
    pass


def validate_python_syntax(code: str, file_path: str = "") -> Tuple[bool, Optional[str]]:
    """验证 Python 代码语法
    
    Args:
        code: Python 代码内容
        file_path: 文件路径（用于错误提示）
        
    Returns:
        (是否有效, 错误信息)
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        error_msg = f"语法错误"
        if file_path:
            error_msg += f" ({file_path})"
        error_msg += f": {e.msg} at line {e.lineno}"
        if e.text:
            error_msg += f"\n  {e.text.strip()}"
        return False, error_msg
    except Exception as e:
        return False, f"代码验证失败: {e}"


def extract_imports(code: str) -> Dict[str, List[str]]:
    """提取代码中的导入语句
    
    Args:
        code: Python 代码内容
        
    Returns:
        {模块名: [导入的函数/类/变量列表]}
    """
    imports: Dict[str, List[str]] = {}
    
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    imports[module_name] = []
            
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                imported_names = [alias.name for alias in node.names]
                imports[module_name] = imported_names
    
    except SyntaxError:
        # 如果代码有语法错误，无法解析导入
        pass
    
    return imports


def validate_imports(
    code: str,
    file_path: str,
    project_root: Path,
    created_files: Dict[str, str]
) -> Tuple[bool, List[str]]:
    """验证代码中的导入是否有效
    
    Args:
        code: Python 代码内容
        file_path: 当前文件路径（相对路径）
        project_root: 项目根目录
        created_files: 已创建的文件字典 {路径: 内容}
        
    Returns:
        (是否有效, 错误列表)
    """
    errors: List[str] = []
    imports = extract_imports(code)
    
    # 获取当前文件所在目录
    current_dir = Path(file_path).parent
    
    for module_name, imported_names in imports.items():
        # 跳过标准库和第三方库（简单判断）
        if not module_name or module_name.split('.')[0] in ['os', 'sys', 'json', 're', 'typing', 'pathlib', 'click', 'rich']:
            continue
        
        # 处理相对导入
        if module_name.startswith('.'):
            # 相对导入：从当前目录开始查找
            module_path = current_dir / module_name.lstrip('.')
            
            # 尝试查找 .py 文件
            py_file = None
            for suffix in ['', '.py']:
                test_path = module_path.with_suffix(suffix)
                if test_path.exists():
                    py_file = test_path
                    break
            
            # 如果找不到，尝试作为包目录
            if not py_file:
                test_path = module_path / '__init__.py'
                if test_path.exists():
                    py_file = test_path
            
            if not py_file:
                # 检查是否在已创建的文件中
                rel_path = str(module_path.relative_to(project_root))
                if rel_path not in created_files:
                    errors.append(f"无法找到模块: {module_name} (相对导入)")
                    continue
            
            # 验证导入的函数/类是否存在
            if imported_names:
                # 从已创建的文件中查找
                target_file = None
                if py_file:
                    target_file = py_file
                else:
                    rel_path = str(module_path.relative_to(project_root))
                    if rel_path in created_files:
                        # 需要读取文件内容来验证
                        pass
                
                if target_file and target_file.exists():
                    try:
                        with open(target_file, 'r', encoding='utf-8') as f:
                            target_code = f.read()
                        
                        # 提取目标文件中的函数和类
                        target_tree = ast.parse(target_code)
                        available_names = set()
                        
                        for node in ast.walk(target_tree):
                            if isinstance(node, ast.FunctionDef):
                                available_names.add(node.name)
                            elif isinstance(node, ast.ClassDef):
                                available_names.add(node.name)
                            elif isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name) and target.id == '__version__':
                                        available_names.add('__version__')
                        
                        # 检查导入的名称是否存在
                        for name in imported_names:
                            if name not in available_names and name != '*':
                                errors.append(
                                    f"无法从 {module_name} 导入 {name} "
                                    f"(在 {target_file.relative_to(project_root)} 中不存在)"
                                )
                    except Exception as e:
                        # 如果无法读取或解析目标文件，跳过验证
                        pass
        
        # 处理绝对导入（项目内的模块）
        else:
            # 检查模块是否在已创建的文件中
            module_parts = module_name.split('.')
            module_path = project_root / Path(*module_parts)
            
            # 尝试查找 .py 文件或包目录
            py_file = None
            if (module_path.with_suffix('.py')).exists():
                py_file = module_path.with_suffix('.py')
            elif (module_path / '__init__.py').exists():
                py_file = module_path / '__init__.py'
            
            if not py_file:
                # 检查是否在已创建的文件中
                rel_path = str(module_path.relative_to(project_root))
                found = False
                for created_path in created_files.keys():
                    if created_path.startswith(rel_path) or rel_path.startswith(created_path):
                        found = True
                        break
                
                if not found:
                    errors.append(f"无法找到模块: {module_name}")
    
    return len(errors) == 0, errors


def check_package_structure(
    project_root: Path,
    package_name: str,
    created_files: Dict[str, str]
) -> Tuple[bool, List[str]]:
    """检查 Python 包结构是否完整
    
    Args:
        project_root: 项目根目录
        package_name: 包名称
        created_files: 已创建的文件字典
        
    Returns:
        (是否完整, 缺失的文件列表)
    """
    missing_files: List[str] = []
    
    # 检查包目录是否存在
    package_dir = project_root / package_name
    if not package_dir.exists():
        missing_files.append(f"{package_name}/ (包目录)")
        return False, missing_files
    
    # 检查 __init__.py
    init_file = package_dir / '__init__.py'
    if not init_file.exists():
        rel_path = f"{package_name}/__init__.py"
        if rel_path not in created_files:
            missing_files.append(rel_path)
    
    # 检查是否有 CLI 文件，如果有，检查是否需要 __main__.py
    cli_files = ['cli.py', 'main.py', '__main__.py']
    has_cli = any((package_dir / f).exists() for f in cli_files)
    has_main = (package_dir / '__main__.py').exists()
    
    if has_cli and not has_main:
        # 检查 README 中是否提到 python -m package_name
        readme_path = project_root / 'README.md'
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                    if f'python -m {package_name}' in readme_content:
                        missing_files.append(f"{package_name}/__main__.py (支持 python -m 运行)")
            except Exception:
                pass
    
    # 检查 setup.py（Python CLI 项目必需）
    setup_file = project_root / 'setup.py'
    if not setup_file.exists():
        setup_path = 'setup.py'
        if setup_path not in created_files:
            missing_files.append('setup.py (用于安装包，支持 pip install -e . 和 python -m 运行)')
    
    return len(missing_files) == 0, missing_files


def validate_generated_code(
    code: str,
    file_path: str,
    project_root: Path,
    created_files: Dict[str, str]
) -> Tuple[bool, List[str]]:
    """全面验证生成的代码
    
    Args:
        code: 生成的代码内容
        file_path: 文件路径（相对路径）
        project_root: 项目根目录
        created_files: 已创建的文件字典
        
    Returns:
        (是否有效, 错误/警告列表)
    """
    issues: List[str] = []
    
    # 1. 语法验证
    is_valid, syntax_error = validate_python_syntax(code, file_path)
    if not is_valid:
        issues.append(f"❌ {syntax_error}")
        return False, issues
    
    # 2. 检查是否还有 markdown 标记
    if re.search(r'```', code):
        issues.append(f"⚠️  代码中可能包含 markdown 代码块标记")
    
    # 3. 导入验证（仅对 .py 文件）
    if file_path.endswith('.py'):
        is_valid, import_errors = validate_imports(code, file_path, project_root, created_files)
        if not is_valid:
            for error in import_errors:
                issues.append(f"⚠️  {error}")
    
    return len([i for i in issues if i.startswith('❌')]) == 0, issues


if __name__ == "__main__":
    # 测试代码验证
    test_code = """
import os
from .game import main_game_loop
from . import __version__

def test():
    pass
"""
    
    console.print("[cyan]测试代码验证...[/cyan]\n")
    
    # 测试语法验证
    is_valid, error = validate_python_syntax(test_code, "test.py")
    console.print(f"语法验证: {'✓' if is_valid else '✗'} {error or '通过'}")
    
    # 测试导入提取
    imports = extract_imports(test_code)
    console.print(f"\n提取的导入: {imports}")

