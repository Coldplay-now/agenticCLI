"""
DeepSeek API 客户端

封装 OpenAI SDK 调用 DeepSeek API。
"""

from typing import List, Dict, Optional
import time

from openai import OpenAI, OpenAIError
from rich.console import Console

from .config import Config

console = Console()


class AIClient:
    """DeepSeek API 客户端"""
    
    def __init__(self, config: Config):
        """初始化 AI 客户端
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.client = OpenAI(
            api_key=config.deepseek_api_key,
            base_url=config.deepseek_base_url
        )
        self.system_prompt = config.system_prompt
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        retry_count: int = 3,
        stream: bool = False
    ) -> Optional[str]:
        """调用聊天 API
        
        Args:
            messages: 对话历史
            temperature: 温度参数（0-1）
            max_tokens: 最大 token 数
            retry_count: 重试次数
            stream: 是否使用流式输出
            
        Returns:
            AI 响应内容，失败返回 None
        """
        # 确保第一条消息是系统提示词
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages
        
        for attempt in range(retry_count):
            try:
                if stream:
                    return self._chat_stream(full_messages, temperature, max_tokens)
                else:
                    response = self.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=full_messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    content = response.choices[0].message.content
                    return content
            
            except OpenAIError as e:
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    console.print(
                        f"[yellow]API 调用失败，{wait_time}秒后重试... "
                        f"({attempt + 1}/{retry_count})[/yellow]"
                    )
                    time.sleep(wait_time)
                else:
                    console.print(f"[red]API 调用失败: {e}[/red]")
                    console.print("\n可能的原因：")
                    console.print("1. API Key 无效或已过期")
                    console.print("2. 网络连接问题")
                    console.print("3. API 服务暂时不可用")
                    console.print("\n请检查配置后重试。")
                    return None
            
            except Exception as e:
                console.print(f"[red]未知错误: {e}[/red]")
                return None
        
        return None
    
    def _chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """流式调用聊天 API
        
        Args:
            messages: 完整消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            AI 响应内容，失败返回 None
        """
        try:
            stream = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            full_content = ""
            # 流式输出内容
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    # 实时输出内容，使用淡青色，不解析 markdown
                    console.print(content, end="", style="cyan", markup=False, highlight=False)
            
            console.print()  # 换行
            return full_content
            
        except Exception as e:
            console.print(f"\n[red]流式输出错误: {e}[/red]")
            return None
    
    def chat_with_context(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Optional[str]:
        """带上下文的聊天
        
        Args:
            user_message: 用户消息
            conversation_history: 历史对话记录
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否使用流式输出
            
        Returns:
            AI 响应内容
        """
        messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]
        
        return self.chat(messages, temperature, max_tokens, stream=stream)
    
    def generate_task_list(
        self,
        requirements: Dict[str, str],
        conversation_history: List[Dict[str, str]],
        stream: bool = True
    ) -> Optional[str]:
        """生成任务清单
        
        Args:
            requirements: 需求信息字典
            conversation_history: 对话历史
            stream: 是否使用流式输出（默认 True）
            
        Returns:
            包含任务清单的响应（JSON格式）
        """
        # 构建生成任务清单的提示
        prompt = """
现在，基于我们的对话，请进行 Chain of Thought 推理分析，然后生成项目初始化任务清单。

需求总结：
"""
        for key, value in requirements.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += """
请按照以下步骤：
1. 【需求理解】：总结用户的核心需求
2. 【技术选型】：基于需求推荐技术栈
3. 【项目结构】：规划项目目录结构
4. 【任务分解】：生成具体的任务清单（**严格限制：≤10项，必须合并相似任务**）

**任务数量限制（重要）**：
- 任务总数必须 ≤ 10 项
- 如果任务过多，请合并相似的任务：
  * 多个 .py 文件可以合并为一个任务（在 description 中说明要创建哪些文件）
  * 多个目录创建可以合并为一个任务
  * 配置文件（README、requirements.txt、setup.py 等）可以合并为一个任务
  * 测试文件可以合并为一个任务
- 优先保留核心功能任务，次要任务可以合并或简化

**关键要求 - 任务规划阶段（重要变更）：**

1. **对于所有 .py 代码文件任务**：
   - **不需要**在任务规划阶段生成具体的代码内容（`content` 字段）
   - 只需要在 `description` 中清晰说明该文件要实现什么功能
   - 可以在 `params` 中添加 `code_description` 字段，提供更详细的代码生成说明
   - 例如：
     ```json
     {
       "id": 5,
       "name": "生成核心逻辑文件",
       "description": "实现游戏主循环逻辑，包含蛇的移动、食物生成、碰撞检测等功能",
       "type": "create_file",
       "params": {
         "path": "snake2/snake2/game.py",
         "code_description": "实现贪吃蛇游戏的核心逻辑，包括游戏状态管理、蛇的移动、食物生成、碰撞检测等"
       }
     }
     ```
   - 代码内容将在执行阶段由 AI 根据项目上下文动态生成

2. **对于配置文件**（README.md、requirements.txt、setup.py 等）：
   - 使用 `template` + `variables`
   - 必须提供所有必需的变量值（project_name、module_name、description 等）
   - 变量值应该是实际字符串，不是 {{variable_name}} 格式

3. **变量替换**：
   - 在 JSON 中，所有变量值应该是实际字符串
   - 例如：`"project_name": "file-renamer"` 而不是 `"project_name": "{{project_name}}"`

最后，请在 [TASK_LIST_START] 和 [TASK_LIST_END] 标记之间输出 JSON 格式的任务清单。
注意：JSON 中的字符串内容需要使用转义字符（\n 表示换行，\" 表示引号）。
"""
        
        return self.chat_with_context(
            prompt,
            conversation_history,
            temperature=0.3,  # 降低温度以获得更确定的输出
            max_tokens=3000,
            stream=stream
        )
    
    def generate_code_content(
        self,
        file_path: str,
        task_description: str,
        code_description: str,
        requirements: Dict[str, str],
        conversation_history: List[Dict[str, str]],
        created_files: Dict[str, str],
        project_structure: List[str],
        stream: bool = True
    ) -> Optional[str]:
        """生成代码文件内容
        
        Args:
            file_path: 文件路径
            task_description: 任务描述
            code_description: 代码生成说明
            requirements: 需求信息字典
            conversation_history: 对话历史
            created_files: 已创建的文件内容（路径 -> 内容）
            project_structure: 项目结构（已创建的文件和目录列表）
            stream: 是否使用流式输出（默认 True）
            
        Returns:
            生成的代码内容，失败返回 None
        """
        # 构建代码生成提示
        prompt = f"""
现在需要为项目生成代码文件内容。

**文件信息：**
- 文件路径: {file_path}
- 任务描述: {task_description}
- 代码说明: {code_description}

**项目需求：**
"""
        for key, value in requirements.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += "\n**已创建的文件内容（供参考）：**\n"
        if created_files:
            for path, content in created_files.items():
                # 显示文件的完整内容（但限制长度，避免过长）
                if len(content) > 2000:
                    content_preview = content[:2000] + "\n... (文件过长，已截断) ..."
                else:
                    content_preview = content
                prompt += f"\n文件: {path}\n```python\n{content_preview}\n```\n"
        else:
            prompt += "（暂无已创建的文件）\n"
        
        # 添加已创建文件的函数/类列表，方便导入验证
        if created_files:
            prompt += "\n**已创建文件中的可导入内容（用于验证导入）：**\n"
            for path, content in created_files.items():
                # 提取函数和类定义
                import re
                functions = re.findall(r'^def\s+(\w+)\s*\(', content, re.MULTILINE)
                classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                variables = re.findall(r'^__version__\s*=', content, re.MULTILINE)
                
                if functions or classes or variables:
                    prompt += f"\n文件 {path} 包含：\n"
                    if variables:
                        prompt += f"  - 变量: __version__\n"
                    if classes:
                        prompt += f"  - 类: {', '.join(classes)}\n"
                    if functions:
                        prompt += f"  - 函数: {', '.join(functions)}\n"
        
        prompt += "\n**项目结构：**\n"
        for item in project_structure:
            prompt += f"- {item}\n"
        
        prompt += """
**代码生成要求：**

1. **代码格式要求**：
   - 直接输出纯 Python 代码，不要包含 markdown 代码块标记（如 ```python 或 ```）
   - 不要包含任何 markdown 格式的说明文字
   - 代码应该从第一行开始就是有效的 Python 代码

2. **代码内容要求**：
   - 根据任务描述和代码说明，生成完整的、可运行的 Python 代码
   - 代码应该包含：
     * 必要的导入语句
     * 完整的函数/类定义
     * 实际的功能实现，不要只有 TODO 注释
     * 符合 Python 最佳实践和代码规范

3. **导入验证要求**（非常重要）：
   - **必须检查已创建的文件列表**，确保导入的模块和函数确实存在
   - 如果导入的模块不存在，不要生成该导入语句
   - 如果导入的函数不存在，使用已创建文件中实际存在的函数名
   - 例如：如果已创建的文件是 `game.py`，里面有 `main_game_loop()` 函数，不要导入不存在的 `core.main_function()`
   - 使用相对导入时（如 `from .game import ...`），确保被导入的模块确实存在

4. **Python 包结构要求**：
   - 如果生成的是包内的模块（如 `package_name/module.py`），确保：
     * 包目录下有 `__init__.py` 文件（如果还没有创建）
     * 导入时使用正确的相对导入路径（如 `from .module import function`）
   - 如果生成的是 CLI 入口文件，确保：
     * 导入的版本号来自 `__init__.py` 中的 `__version__`
     * 导入的函数来自实际存在的模块

5. **代码应该可以直接运行或至少提供完整的功能框架**

**重要提示**：
- 输出时只输出纯 Python 代码，不要有任何 markdown 格式
- 仔细检查已创建的文件列表，确保所有导入都是有效的
- 如果不确定某个导入是否存在，查看已创建的文件内容来确认
"""
        
        # 使用流式输出显示生成过程
        console.print(f"\n[bold cyan]正在生成代码: {file_path}[/bold cyan]")
        console.print("[dim]（以下内容为 AI 实时生成过程）[/dim]\n")
        
        response = self.chat_with_context(
            prompt,
            conversation_history,
            temperature=0.5,  # 适中的温度，平衡创造性和准确性
            max_tokens=4000,  # 代码可能较长，增加 token 限制
            stream=stream
        )
        
        if response:
            console.print()  # 空行分隔
            # 清理代码：移除可能的 markdown 代码块标记
            cleaned_response = self._clean_generated_code(response)
            return cleaned_response
        else:
            console.print(f"[red]生成代码失败: {file_path}[/red]")
            return None
    
    def _clean_generated_code(self, code: str) -> str:
        """清理生成的代码，移除 markdown 代码块标记等
        
        Args:
            code: 原始生成的代码
            
        Returns:
            清理后的代码
        """
        import re
        
        # 移除所有 markdown 代码块标记（包括单独一行的 ```）
        # 匹配开头的 ```python, ```py, ``` 等
        code = re.sub(r'^```(?:python|py|)?\s*\n?', '', code, flags=re.MULTILINE)
        # 匹配结尾的 ```
        code = re.sub(r'\n?```\s*$', '', code, flags=re.MULTILINE)
        # 匹配单独一行的 ```（不在开头或结尾）
        code = re.sub(r'\n```\s*\n', '\n', code)
        
        # 移除开头的多余空行
        code = code.lstrip('\n')
        
        # 移除结尾的多余空行（保留一个换行符）
        code = code.rstrip('\n') + '\n'
        
        return code


if __name__ == "__main__":
    # 测试 AI 客户端
    from .config import load_config
    
    try:
        config = load_config()
        client = AIClient(config)
        
        console.print("[cyan]测试 AI 客户端...[/cyan]\n")
        
        # 简单对话测试
        response = client.chat([
            {"role": "user", "content": "你好，请简单介绍一下你的功能。"}
        ])
        
        if response:
            console.print("[green]AI 响应:[/green]")
            console.print(response)
        else:
            console.print("[red]测试失败[/red]")
    
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")

