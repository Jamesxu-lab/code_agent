"""调试工具"""
import subprocess
import os
from langchain_core.tools import tool


@tool
def run_tests(pattern: str = "*", verbose: bool = True) -> str:
    """
    运行测试。

    Args:
        pattern: 测试文件模式（如 "test_*.py", "tests/"）
        verbose: 是否显示详细输出，默认 True

    Returns:
        测试执行结果
    """
    # 检查 pytest 是否可用
    try:
        subprocess.run(
            ["pytest", "--version"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "错误：pytest 未安装，请运行: pip install pytest"

    # 构建 pytest 命令
    cmd = ["pytest"]
    if verbose:
        cmd.append("-v")

    # 添加测试模式
    if pattern:
        cmd.append(pattern)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.getcwd(),
        )

        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(result.stderr)

        return f"测试完成 (退出码: {result.returncode})\n" + "\n".join(output)

    except subprocess.TimeoutExpired:
        return "错误：测试执行超时"
    except Exception as e:
        return f"错误：执行失败: {str(e)}"