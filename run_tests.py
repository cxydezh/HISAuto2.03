#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本 - 运行所有自动化测试
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行自动化测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试模块
    try:
        # 导入测试模块
        from test_integration import TestHomeTabFuncIntegration, TestStandaloneFunctions, TestDatabaseOperations
        from test_gui_integration import TestHomeTabGUIIntegration, TestErrorHandling
        
        # 添加测试类
        test_suite.addTest(unittest.makeSuite(TestHomeTabFuncIntegration))
        test_suite.addTest(unittest.makeSuite(TestStandaloneFunctions))
        test_suite.addTest(unittest.makeSuite(TestDatabaseOperations))
        test_suite.addTest(unittest.makeSuite(TestHomeTabGUIIntegration))
        test_suite.addTest(unittest.makeSuite(TestErrorHandling))
        
        print("✓ 成功加载所有测试模块")
        
    except ImportError as e:
        print(f"✗ 导入测试模块失败: {e}")
        return False
    
    # 运行测试
    print("\n开始执行测试...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"运行测试数: {result.testsRun}")
    print(f"失败测试数: {len(result.failures)}")
    print(f"错误测试数: {len(result.errors)}")
    print(f"跳过测试数: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n失败测试详情:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n错误测试详情:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # 返回测试是否全部通过
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n测试{'全部通过' if success else '有失败'}")
    
    return success

def run_specific_test(test_name):
    """运行特定测试"""
    print(f"运行特定测试: {test_name}")
    
    if test_name == "integration":
        from test_integration import TestHomeTabFuncIntegration
        suite = unittest.makeSuite(TestHomeTabFuncIntegration)
    elif test_name == "gui":
        from test_gui_integration import TestHomeTabGUIIntegration
        suite = unittest.makeSuite(TestHomeTabGUIIntegration)
    elif test_name == "error":
        from test_gui_integration import TestErrorHandling
        suite = unittest.makeSuite(TestErrorHandling)
    else:
        print(f"未知测试类型: {test_name}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"测试{'通过' if success else '失败'}")
    
    return success

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行特定测试
        test_type = sys.argv[1]
        run_specific_test(test_type)
    else:
        # 运行所有测试
        run_all_tests() 