"""文件操作工具"""
import os
import glob
from typing import Optional
from langchain_core.tools import tool


@tool
def read_file(path: str, encoding: str = "utf-8") -> str:
    """
    读取文件内容。

    Args:
        path: 文件路径（支持绝对路径和相对路径）
        encoding: 文件编码，默认 utf-8

    Returns:
        文件内容
    """
    expanded_path = os.path.expanduser(path)

    if not os.path.isabs(expanded_path):
        expanded_path = os.path.abspath(expanded_path)

    if not os.path.exists(expanded_path):
        return f"错误：文件不存在: {expanded_path}"

    if not os.path.isfile(expanded_path):
        return f"错误：不是文件: {expanded_path}"

    try:
        with open(expanded_path, 'r', encoding=encoding) as f:
            content = f.read()
        return f"文件: {expanded_path}\n内容:\n{content}"
    except Exception as e:
        return f"错误：读取失败: {str(e)}"


@tool
def write_file(path: str, content: str, encoding: str = "utf-8") -> str:
    """
    写入内容到文件。

    Args:
        path: 文件路径
        content: 要写入的内容
        encoding: 文件编码，默认 utf-8

    Returns:
        操作结果
    """
    file_path = os.path.expanduser(path)

    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return f"成功写入文件: {file_path}"
    except Exception as e:
        return f"错误：写入失败: {str(e)}"


@tool
def list_directory(path: str = ".") -> str:
    """
    列出目录内容。

    Args:
        path: 目录路径，默认当前目录

    Returns:
        目录内容列表
    """
    dir_path = os.path.expanduser(path)

    if not os.path.isabs(dir_path):
        dir_path = os.path.abspath(dir_path)

    if not os.path.exists(dir_path):
        return f"错误：目录不存在: {dir_path}"

    if not os.path.isdir(dir_path):
        return f"错误：不是目录: {dir_path}"

    try:
        items = os.listdir(dir_path)
        result = f"目录: {dir_path}\n"
        for item in sorted(items):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                result += f"[DIR]  {item}/\n"
            else:
                size = os.path.getsize(item_path)
                result += f"[FILE] {item} ({size} bytes)\n"
        return result
    except Exception as e:
        return f"错误：列出失败: {str(e)}"


@tool
def search_files(pattern: str, root_dir: Optional[str] = None) -> str:
    """
    搜索文件。

    Args:
        pattern: 文件模式（如 "*.py", "**/*.py"）
        root_dir: 搜索根目录，默认当前目录

    Returns:
        匹配的文件列表
    """
    if root_dir is None:
        root_dir = os.getcwd()
    else:
        root_dir = os.path.expanduser(root_dir)

    if not os.path.exists(root_dir):
        return f"错误：目录不存在: {root_dir}"

    try:
        # 使用 glob 搜索
        search_pattern = os.path.join(root_dir, pattern)
        matches = glob.glob(search_pattern, recursive=True)

        if not matches:
            return f"未找到匹配的文件: {pattern}"

        result = f"找到 {len(matches)} 个文件:\n"
        for f in sorted(matches):
            rel_path = os.path.relpath(f, root_dir)
            result += f"  {rel_path}\n"
        return result
    except Exception as e:
        return f"错误：搜索失败: {str(e)}"