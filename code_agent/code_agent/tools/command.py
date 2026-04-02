"""命令执行工具"""
import subprocess
from langchain_core.tools import tool


@tool
def run_command(command: str, shell: bool = True, timeout: int = 60) -> str:
    """
    执行 shell 命令。

    Args:
        command: 要执行的命令
        shell: 是否使用 shell 执行，默认 True
        timeout: 超时时间（秒），默认 60

    Returns:
        命令执行结果
    """
    if shell:
        cmd = command
    else:
        cmd = command.split()

    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )

        output = []
        if result.stdout:
            output.append(f"stdout:\n{result.stdout}")
        if result.stderr:
            output.append(f"stderr:\n{result.stderr}")

        if result.returncode == 0:
            return f"命令执行成功 (退出码: 0)\n" + "\n".join(output)
        else:
            return f"命令执行失败 (退出码: {result.returncode})\n" + "\n".join(output)

    except subprocess.TimeoutExpired:
        return f"错误：命令执行超时 ({timeout}秒)"
    except Exception as e:
        return f"错误：执行失败: {str(e)}"


# 解决 os 导入问题
import os