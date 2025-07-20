#!/usr/bin/env python3
"""
测试filter语法修复
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟缺失的模块
sys.modules['pynput'] = Mock()
sys.modules['pynput.mouse'] = Mock()
sys.modules['pynput.keyboard'] = Mock()
sys.modules['win32gui'] = Mock()
sys.modules['win32api'] = Mock()
sys.modules['pyautogui'] = Mock()

# 创建测试模型
Base = declarative_base()

class TestHierarchy(Base):
    __tablename__ = 'test_hierarchy'
    
    id = Column(Integer, primary_key=True)
    group_rank = Column(String(50))
    sort_num = Column(Integer)

class TestGroup(Base):
    __tablename__ = 'test_group'
    
    id = Column(Integer, primary_key=True)
    group_rank_id = Column(Integer)
    sort_num = Column(Integer)


class TestFilterSyntax(unittest.TestCase):
    """测试filter语法修复"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # 创建数据库引擎和会话
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
        
        # 创建测试数据
        self.create_test_data()
        
    def tearDown(self):
        """测试后的清理工作"""
        # 关闭数据库连接
        if hasattr(self, 'engine'):
            self.engine.dispose()
        
        # 删除临时数据库文件
        try:
            if os.path.exists(self.db_path):
                os.unlink(self.db_path)
        except PermissionError:
            pass
    
    def create_test_data(self):
        """创建测试数据"""
        session = self.Session()
        
        try:
            # 创建层次结构测试数据
            hierarchy1 = TestHierarchy(group_rank="A1B2C3", sort_num=1)
            hierarchy2 = TestHierarchy(group_rank="A1B2C4", sort_num=2)
            hierarchy3 = TestHierarchy(group_rank="A1B2C5", sort_num=3)
            
            session.add_all([hierarchy1, hierarchy2, hierarchy3])
            session.commit()
            
            # 创建行为组测试数据
            group1 = TestGroup(group_rank_id=1, sort_num=1)
            group2 = TestGroup(group_rank_id=1, sort_num=2)
            group3 = TestGroup(group_rank_id=2, sort_num=1)
            
            session.add_all([group1, group2, group3])
            session.commit()
            
            self.hierarchy_ids = [hierarchy1.id, hierarchy2.id, hierarchy3.id]
            self.group_ids = [group1.id, group2.id, group3.id]
            
        finally:
            session.close()
    
    def test_filter_syntax_with_contains_and_condition(self):
        """测试使用contains和条件的filter语法"""
        session = self.Session()
        
        try:
            # 测试修复后的语法：使用filter()方法
            results = session.query(TestHierarchy).filter(
                TestHierarchy.group_rank.contains("A1B2") & 
                (TestHierarchy.sort_num == 2)
            ).all()
            
            # 验证结果
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].group_rank, "A1B2C4")
            self.assertEqual(results[0].sort_num, 2)
            
            print("✓ filter语法测试通过")
            
        finally:
            session.close()
    
    def test_filter_syntax_with_multiple_conditions(self):
        """测试多个条件的filter语法"""
        session = self.Session()
        
        try:
            # 测试多个条件的filter语法
            results = session.query(TestGroup).filter(
                (TestGroup.group_rank_id == 1) & 
                (TestGroup.sort_num == 2)
            ).all()
            
            # 验证结果
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].group_rank_id, 1)
            self.assertEqual(results[0].sort_num, 2)
            
            print("✓ 多条件filter语法测试通过")
            
        finally:
            session.close()
    
    def test_filter_by_syntax(self):
        """测试filter_by的正确语法"""
        session = self.Session()
        
        try:
            # 测试filter_by的正确语法（只用于简单相等条件）
            results = session.query(TestHierarchy).filter_by(sort_num=1).all()
            
            # 验证结果
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].sort_num, 1)
            
            print("✓ filter_by语法测试通过")
            
        finally:
            session.close()
    
    def test_invalid_filter_by_syntax(self):
        """测试无效的filter_by语法（应该失败）"""
        session = self.Session()
        
        try:
            # 这个应该会失败，因为filter_by不支持复杂表达式
            with self.assertRaises(Exception):
                session.query(TestHierarchy).filter_by(
                    TestHierarchy.group_rank.contains("A1B2") and TestHierarchy.sort_num == 2
                ).all()
            
            print("✓ 无效filter_by语法测试通过（正确抛出异常）")
            
        finally:
            session.close()


if __name__ == '__main__':
    print("开始运行filter语法测试...")
    print("=" * 50)
    
    # 运行测试
    unittest.main(verbosity=2)
    
    print("=" * 50)
    print("测试完成！") 