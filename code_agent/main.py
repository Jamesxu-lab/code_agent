#!/usr/bin/env python3
"""Code Agent 入口脚本"""
import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_agent.main import main

if __name__ == "__main__":
    main()