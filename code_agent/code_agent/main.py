"""CLI 入口"""
import argparse
import sys

from code_agent.engine import run


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="Code Agent - CLI 编程助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m code_agent "创建一个测试文件 hello.txt"
  python -m code_agent "列出当前目录的文件"
  python -m code_agent "在 /tmp 目录创建一个 Python 项目"
        """
    )

    parser.add_argument(
        "task",
        nargs="?",
        help="要执行的任务",
    )

    parser.add_argument(
        "-m", "--model",
        default="qwen3.5-plus",
        help="使用的模型 (默认: qwen3.5-plus)",
    )

    parser.add_argument(
        "-p", "--provider",
        default="qwen",
        choices=["qwen", "kimi"],
        help="LLM 提供商 (默认: qwen)",
    )

    parser.add_argument(
        "-i", "--iterations",
        type=int,
        default=10,
        help="最大迭代次数 (默认: 10)",
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="安静模式，不显示详细输出",
    )

    args = parser.parse_args()

    # 检查任务参数
    if not args.task:
        parser.print_help()
        sys.exit(1)

    # 执行任务
    try:
        result = run(
            user_query=args.task,
            provider=args.provider,
            model=args.model,
            max_iterations=args.iterations,
            verbose=not args.quiet,
        )
        print("\n" + "=" * 60)
        print("最终结果:")
        print("=" * 60)
        print(result)
    except KeyboardInterrupt:
        print("\n\n任务已取消")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


__all__ = ["main"]