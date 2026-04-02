# code_agent：coding agent的最小可行方案

---

## 背景

本项目希望通过使用Agent来构建一个最小可行的coding agent产品，试图回答：**coding agent怎么展开工作；以及协作中人类开发者（特别是产品经理视角）的核心价值是什么？**

基于已有对LLM及Agent原理的理解，我通过 **Claude Code** 指挥 **MiniMax 2.5** 构建了这个 Coding Agent。它展示了如何通过简单的 ReAct 循环，让模型具备“手”和“眼”，去处理真实的文件系统任务。

---

## 运行原理：ReAct 循环

项目核心逻辑遵循 **Thought -> Action -> Observation** 的自主循环。

代码段


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

---

## 项目结构与 AI 协作记录

本项目 90% 的底层架构由 AI 生成，由人类进行工程化调优与环境适配。

Plaintext

```
code_agent/
├── code_agent/             # 主逻辑包
│   ├── main.py            # CLI 入口 (argparse 解析)
│   ├── llm.py             # LLM 客户端 (适配 ChatOpenAI 接口)
│   ├── engine.py          # ReAct 执行引擎 (核心循环所在)
│   ├── prompt.py          # 系统提示词模板 (Agent 的性格与边界)
│   └── tools/             # 智能体工具箱
│       ├── file.py        # 读写/搜索/列表
│       ├── command.py     # Shell 命令执行
│       └── debug.py       # Pytest 集成测试
├── pyproject.toml         # 项目元数据与依赖管理
└── main.py                # 根目录启动脚本
```

### 协作分工表

|**组件**|**AI 的贡献 (MiniMax 2.5)**|**人类调试 (PM 视角)**|
|---|---|---|
|**架构设计**|自动生成 `engine.py` 的迭代骨架|给出需求和工具边界，防止 Agent 陷入死循环|
|**模型适配**|实现基础的 OpenAI 兼容接口|针对国产模型（Qwen/Kimi）的 Prompt 优化|
|**环境兼容**|编写基础 Python 逻辑|解决 Python 3.14 下 Pydantic V2 的兼容性告警|

---

## 快速开始

### 1. 环境准备

Bash

```
# 克隆仓库
git clone https://github.com/Jamesxu-lab/code_agent.git
cd code_agent

# 安装依赖 (推荐使用开发者模式)
pip install langchain langchain-openai openai
```

### 2. 配置环境变量

在根目录创建 `.env` 文件或直接导出：

Bash

```
export QWEN_API_KEY="your_key_here"
export KIMI_API_KEY="your_key_here"
```

### 3. 开始交互

Bash

```
# 场景 1：文件自动化
python3 main.py "在当前目录创建一个测试文件 hello.txt，内容为 Hello World"

# 场景 2：跨模型调用 (使用 Kimi)
python3 main.py -p kimi -m kimi-latest "分析当前目录结构并给出总结"

# 场景 3：执行 Shell 指令
python3 main.py "查找当前目录下所有 .py 文件并统计行数"
```

---

## 💡 启发与刻意练习

本项目非常适合以下“实验性”练习：

1. **观察思考路径**：查看控制台输出，对比 Kimi 和 Qwen 在面对同一个逻辑错误（如文件不存在）时，谁的“反思（Reflection）”能力更强？
    
2. **工具扩展**：试着在 `tools/` 下增加一个 `git_tool.py`，看看 Agent 是否能自主完成 `git commit`。
    
3. **极限测试**：将 `-i` (iterations) 参数设为 3，观察 Agent 在受限步数内能否完成复杂任务。
    

---

## 注意事项

- **安全性提示**：本 Agent 具备执行 Shell 命令的权限。**请勿在包含敏感数据的生产环境运行。**
    
- **API 成本**：ReAct 模式会产生多次往返对话，请留意你的 Token 消耗。
    

---

## 后续拓展

- [ ] 支持流式输出 (Streaming)
    
- [ ] 接入网页搜索工具 (Web Search)
    
- [ ] 增加基于本地向量库的“长短期记忆”
    
- [ ] 集成代码审查 (Code Review) 自动反馈流程
