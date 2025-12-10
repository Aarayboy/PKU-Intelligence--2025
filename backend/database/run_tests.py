#!/usr/bin/env python3
"""
运行测试脚本
"""
import subprocess
import sys

def run_tests():
    """运行所有测试"""
    commands = [
        ["pytest", "test_database.py", "-v"],
    ]
    
    for cmd in commands:
        print(f"\n{'='*60}")
        print(f"运行: {' '.join(cmd)}")
        print(f"{'='*60}")
        
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"测试失败: {cmd}")
            return result.returncode
    
    return 0

if __name__ == "__main__":
    sys.exit(run_tests())