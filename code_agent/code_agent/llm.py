"""LLM 客户端封装 - 支持千问/Kimi"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI


class LLMClient:
    """LLM 客户端封装"""

    def __init__(
        self,
        provider: str = "qwen",
        model: str = "qwen3.5-plus",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0,
    ):
        """
        初始化 LLM 客户端

        Args:
            provider: 提供商 ("qwen" 或 "kimi")
            model: 模型名称
            api_key: API Key
            base_url: API 基础 URL
            temperature: 温度参数
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature

        # 获取 API Key
        if api_key is None:
            if provider == "qwen":
                api_key = os.getenv("DASHSCOPE_API_KEY")
            else:
                api_key = os.getenv("KIMI_API_KEY")

        if not api_key:
            raise ValueError(f"未设置 {provider.upper()}_API_KEY 环境变量")

        # 设置 base_url
        if base_url is None:
            if provider == "qwen":
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            elif provider == "kimi":
                base_url = "https://api.moonshot.cn/v1"

        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
        )

    def bind_tools(self, tools: list):
        """绑定工具到 LLM"""
        return self.llm.bind_tools(tools)

    def invoke(self, messages):
        """调用 LLM"""
        return self.llm.invoke(messages)


def create_llm(
    provider: str = "qwen",
    model: str = "qwen3.5-plus",
    temperature: float = 0,
) -> LLMClient:
    """创建 LLM 客户端的便捷函数"""
    return LLMClient(provider=provider, model=model, temperature=temperature)