# CLI 编程 Agent 项目实现记录

## 背景

用户希望构建一个独立 CLI 编程 Agent，具备：
- **类型**: 独立 CLI 工具
- **后端**: 千问/Kimi
- **能力**: 代码读写、编写、调试修改
- **交互**: 单轮交互 + 完全自主执行

## 参考实现

参考项目: `/Users/a51nb/05-Development/01-Projects/react_file_agent/agent.py`

该实现包含:
- ReAct 循环 (思考→行动→观察)
- 千问 API 调用
- 基础文件工具 (read_local_file, write_file, list_directory)

## 设计方案

### 1. 项目结构

```
code_agent/
├── code_agent/              # 主包
│   ├── __init__.py
│   ├── main.py            # CLI 入口
│   ├── llm.py             # LLM 客户端封装
│   ├── tools/             # 工具模块
│   │   ├── __init__.py
│   │   ├── file.py        # 文件操作
│   │   ├── command.py     # 命令执行
│   │   └── debug.py       # 调试工具
│   ├── engine.py          # ReAct 执行引擎
│   └── prompt.py          # Prompt 模板
├── pyproject.toml
└── main.py                # 入口脚本
```

### 2. 核心组件

| 组件 | 职责 | 关键实现 |
|------|------|----------|
| `llm.py` | LLM 客户端 | 支持千问/Kimi，通过 `ChatOpenAI` 封装 |
| `tools/file.py` | 文件操作 | read, write, list, search |
| `tools/command.py` | 命令执行 | shell 命令封装 |
| `tools/debug.py` | 代码调试 | pytest 集成 |
| `engine.py` | ReAct 循环 | 迭代调用 LLM + 执行工具 |
| `main.py` | CLI 入口 | argparse + REPL 循环 |

### 3. 工具系统

使用 LangChain 的 `@tool` 装饰器定义工具：

```python
from langchain_core.tools import tool

@tool
def read_file(path: str) -> str:
    """读取文件内容"""
    expanded_path = os.path.expanduser(path)
    # ... 实现
    return content

@tool
def write_file(path: str, content: str) -> str:
    """写入文件内容"""
    # ... 实现
    return result

@tool
def run_command(command: str) -> str:
    """执行 shell 命令"""
    # ... 实现
    return result
```

### 4. LLM 支持

**千问 (DashScope)**:
```python
llm = ChatOpenAI(
    model="qwen3.5-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
```

**Kimi (Moonshot)**:
```python
llm = ChatOpenAI(
    model="kimi",
    api_key=os.getenv("KIMI_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
)
```

### 5. 执行流程

```
用户输入任务
    │
    ▼
┌─────────────────────────────────┐
│  1. 构建 System Prompt            │
│  2. 调用 LLM (绑定工具)         │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  3. 检测工具调用                │
│     ├── 有 → 执行工具 → 观察     │
│     └── 无 → 返回结果           │
└─────────────────────────────────┘
    │
    ▼
  是否达到迭代上限?
    │
   是 → 返回结果
```

## 实现步骤

### 1. 创建项目结构

```bash
mkdir -p code_agent/code_agent/tools
```

### 2. 创建 pyproject.toml

```toml
[project]
name = "code-agent"
version = "0.1.0"
dependencies = [
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "openai>=1.0.0",
]
```

### 3. 实现 LLM 客户端 (llm.py)

```python
class LLMClient:
    def __init__(self, provider="qwen", model="qwen3.5-plus", ...):
        if provider == "qwen":
            api_key = os.getenv("DASHSCOPE_API_KEY")
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        else:
            api_key = os.getenv("KIMI_API_KEY")
            base_url = "https://api.moonshot.cn/v1"

        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
        )
```

### 4. 实现工具 (tools/)

#### file.py - 文件操作
- `read_file(path)`: 读取文件
- `write_file(path, content)`: 写入文件
- `list_directory(path)`: 列出目录
- `search_files(pattern, root_dir)`: 搜索文件

#### command.py - 命令执行
- `run_command(command, shell, timeout)`: 执行 shell 命令

#### debug.py - 调试工具
- `run_tests(pattern, verbose)`: 运行 pytest

### 5. 实现 ReAct 引擎 (engine.py)

```python
def run_react_loop(agent, user_query, max_iterations=20, verbose=True):
    system_prompt = build_system_prompt(user_query)
    messages = [HumanMessage(content=system_prompt)]

    for iteration in range(max_iterations):
        # 1. 调用 LLM
        response = agent.invoke(messages)

        # 2. 检查工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                args = tool_call['args']

                # 执行工具
                tool_func = TOOLS_MAP[tool_name]
                observation = tool_func.invoke(args)

                # 添加到消息历史
                messages.append(AIMessage(content=response.content))
                messages.append(HumanMessage(content=f"工具返回: {observation}"))

        # 3. 检查是否完成
        if not has_tool_call:
            return response.content

    return "达到最大迭代次数限制"
```

### 6. 实现 CLI 入口 (main.py)

```python
def main():
    parser = argparse.ArgumentParser(description="Code Agent")
    parser.add_argument("task", nargs="?", help="要执行的任务")
    parser.add_argument("-m", "--model", default="qwen3.5-plus")
    parser.add_argument("-p", "--provider", default="qwen", choices=["qwen", "kimi"])
    parser.add_argument("-i", "--iterations", type=int, default=20)
    parser.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()

    result = run(
        user_query=args.task,
        provider=args.provider,
        model=args.model,
        max_iterations=args.iterations,
        verbose=not args.quiet,
    )
    print(result)
```

### 7. 安装依赖

```bash
pip install langchain langchain-openai openai
```

## 使用方式

```bash
# 基本使用
python3 main.py "在当前目录创建一个测试文件 hello.txt，内容为 Hello World"

# 列出当前目录文件
python3 main.py "列出当前目录的文件"

# 指定模型
python3 main.py -m qwen3.5-plus "创建文件 test.py"

# 使用 Kimi
python3 main.py -p kimi -m kimi "创建文件"

# 安静模式
python3 main.py -q "创建文件"
```

## 环境变量

```bash
# 千问
export DASHSCOPE_API_KEY="your-api-key"

# Kimi (可选)
export KIMI_API_KEY="your-api-key"
```

## 测试结果

```bash
$ python3 main.py "在当前目录创建一个测试文件 hello.txt，内容为 Hello World"

============================================================
开始 ReAct 循环
任务: 在当前目录创建一个测试文件 hello.txt，内容为 Hello World
============================================================

--- 迭代 1/10 ---
思考: (无)...
行动: write_file
参数: {'path': 'hello.txt', 'content': 'Hello World'}
观察: 成功写入文件: hello.txt...

--- 迭代 2/10 ---
思考: 任务已完成！

任务完成!

============================================================
最终结果:
============================================================
任务已完成！

**总结：**
- 在当前目录创建了测试文件 `hello.txt`
- 文件内容为 "Hello World"
- 文件写入成功
```

## 关键代码片段

### 工具定义

```python
from langchain_core.tools import tool

@tool
def read_file(path: str, encoding: str = "utf-8") -> str:
    """读取文件内容"""
    expanded_path = os.path.expanduser(path)
    if not os.path.exists(expanded_path):
        return f"错误：文件不存在: {expanded_path}"
    with open(expanded_path, 'r', encoding=encoding) as f:
        return f.read()
```

### Agent 创建

```python
from langchain_openai import ChatOpenAI

def create_agent(provider="qwen", model="qwen3.5-plus"):
    llm = ChatOpenAI(
        model=model,
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    return llm.bind_tools([read_file, write_file, list_directory, run_command])
```

### ReAct 循环

```python
from langchain_core.messages import HumanMessage, AIMessage

def run_react_loop(agent, user_query, max_iterations=20):
    messages = [HumanMessage(content=build_system_prompt(user_query))]

    for _ in range(max_iterations):
        response = agent.invoke(messages)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                result = TOOLS_MAP[tool_call['name']].invoke(tool_call['args'])
                messages.append(AIMessage(content=response.content))
                messages.append(HumanMessage(content=f"工具返回: {result}"))
        else:
            return response.content

    return "达到最大迭代次数限制"
```

## 注意事项

1. **Python 版本**: 需要 Python 3.10+，推荐 3.11
2. **依赖安装**: 确保使用正确的 Python 版本安装依赖
3. **API Key**: 必须设置对应的环境变量
4. **路径处理**: 使用 `os.path.expanduser()` 处理 `~` 路径
5. **目录创建**: 写入文件前确保父目录存在

## 后续扩展

- 添加更多工具 (git 操作、代码格式化等)
- 支持流式输出
- 添加 REPL 交互模式
- 集成代码审查功能
- 添加记忆/上下文管理