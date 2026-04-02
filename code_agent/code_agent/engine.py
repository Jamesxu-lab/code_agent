"""ReAct 执行引擎"""
import os
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

from .llm import create_llm
from .prompt import build_system_prompt
from .tools import read_file, write_file, list_directory, search_files, run_command, run_tests


# 工具映射
TOOLS_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "search_files": search_files,
    "run_command": run_command,
    "run_tests": run_tests,
}


def create_agent(
    provider: str = "qwen",
    model: str = "qwen3.5-plus",
    temperature: float = 0,
):
    """创建带有工具的 Agent"""
    llm = create_llm(provider=provider, model=model, temperature=temperature)

    # 绑定所有工具
    all_tools = [
        read_file,
        write_file,
        list_directory,
        search_files,
        run_command,
        run_tests,
    ]
    return llm.bind_tools(all_tools)


def run_react_loop(
    agent,
    user_query: str,
    max_iterations: int = 20,
    verbose: bool = True,
) -> str:
    """
    运行 ReAct 循环

    Args:
        agent: 配置好工具的 LLM
        user_query: 用户请求
        max_iterations: 最大迭代次数
        verbose: 是否显示详细输出

    Returns:
        最终结果
    """
    # 构建系统提示
    system_prompt = build_system_prompt(user_query)
    messages = [HumanMessage(content=system_prompt)]

    if verbose:
        print("=" * 60)
        print("开始 ReAct 循环")
        print(f"任务: {user_query}")
        print("=" * 60)

    for iteration in range(max_iterations):
        if verbose:
            print(f"\n--- 迭代 {iteration + 1}/{max_iterations} ---")

        # 1. 调用 LLM
        try:
            response = agent.invoke(messages)
        except Exception as e:
            return f"LLM 调用失败: {str(e)}"

        # 获取响应内容
        content = response.content if hasattr(response, 'content') else str(response)

        if verbose:
            print(f"思考: {content[:200] if content else '(无)'}...")

        # 2. 检查工具调用
        has_tool_call = False

        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get('name')
                    args = tool_call.get('args', {})
                else:
                    tool_name = getattr(tool_call, 'name', None)
                    args = getattr(tool_call, 'args', {})

                if verbose:
                    print(f"行动: {tool_name}")
                    print(f"参数: {args}")

                # 执行工具
                if tool_name in TOOLS_MAP:
                    tool_func = TOOLS_MAP[tool_name]
                    try:
                        observation = tool_func.invoke(args)
                    except Exception as e:
                        observation = f"工具执行失败: {str(e)}"

                    if verbose:
                        obs_display = observation[:300] if len(observation) > 300 else observation
                        print(f"观察: {obs_display}...")

                    # 添加到消息历史
                    messages.append(AIMessage(content=content))
                    messages.append(HumanMessage(content=f"工具 [{tool_name}] 返回:\n{observation}"))
                    has_tool_call = True
                else:
                    if verbose:
                        print(f"警告: 未知工具 {tool_name}")

        # 3. 检查是否完成
        if not has_tool_call:
            if verbose:
                print("\n任务完成!")
            return content

    return "达到最大迭代次数限制"


def run(
    user_query: str,
    provider: str = "qwen",
    model: str = "qwen3.5-plus",
    max_iterations: int = 20,
    verbose: bool = True,
) -> str:
    """
    运行 Agent 处理任务

    Args:
        user_query: 用户请求
        provider: LLM 提供商 ("qwen" 或 "kimi")
        model: 模型名称
        max_iterations: 最大迭代次数
        verbose: 是否显示详细输出

    Returns:
        执行结果
    """
    agent = create_agent(provider=provider, model=model)
    return run_react_loop(
        agent,
        user_query=user_query,
        max_iterations=max_iterations,
        verbose=verbose,
    )
