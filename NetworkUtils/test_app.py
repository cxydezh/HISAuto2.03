#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HISAuto_web 应用测试文件
"""

import unittest
import json
from app import app
from data_display import get_departments, get_patients_by_department, get_patient_info, get_ai_functions, get_ai_workflow

class HISAutoWebTestCase(unittest.TestCase):
    """HISAuto_web 应用测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.app = app.test_client()
        self.app.testing = True
        
    def test_login_page(self):
        """测试登录页面"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'HISAuto_web', response.data)
        
    def test_login_success(self):
        """测试登录成功"""
        response = self.app.post('/login', data={
            'username': 'admin',
            'password': 'admin'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
    def test_login_failure(self):
        """测试登录失败"""
        response = self.app.post('/login', data={
            'username': 'admin',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        
    def test_dashboard_access_without_login(self):
        """测试未登录访问工作台"""
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
        
    def test_api_departments(self):
        """测试科室API"""
        response = self.app.get('/api/departments')
        self.assertEqual(response.status_code, 302)  # 需要登录
        
    def test_data_functions(self):
        """测试数据管理函数"""
        # 测试获取科室
        departments = get_departments()
        self.assertIsInstance(departments, list)
        self.assertGreater(len(departments), 0)
        
        # 测试获取患者
        patients = get_patients_by_department('personal')
        self.assertIsInstance(patients, list)
        self.assertGreater(len(patients), 0)
        
        # 测试获取患者信息
        if patients:
            patient_info = get_patient_info(patients[0]['id'])
            self.assertIsNotNone(patient_info)
            self.assertIn('name', patient_info)
            
        # 测试获取AI功能
        ai_functions = get_ai_functions()
        self.assertIsInstance(ai_functions, list)
        self.assertGreater(len(ai_functions), 0)
        
        # 测试获取AI工作流程
        if ai_functions:
            workflow = get_ai_workflow(ai_functions[0])
            self.assertIsNotNone(workflow)
            self.assertIn('workflow', workflow)

class DataValidationTestCase(unittest.TestCase):
    """数据验证测试类"""
    
    def test_department_data_structure(self):
        """测试科室数据结构"""
        departments = get_departments()
        for dept in departments:
            self.assertIn('id', dept)
            self.assertIn('name', dept)
            self.assertIsInstance(dept['id'], str)
            self.assertIsInstance(dept['name'], str)
            
    def test_patient_data_structure(self):
        """测试患者数据结构"""
        departments = get_departments()
        for dept in departments:
            patients = get_patients_by_department(dept['id'])
            for patient in patients:
                required_fields = ['id', 'name', 'admission_date', 'age', 'gender', 
                                 'department', 'admission_days', 'attending_doctor', 
                                 'resident_doctor', 'chief_doctor', 'notes']
                for field in required_fields:
                    self.assertIn(field, patient)
                    
    def test_ai_function_data_structure(self):
        """测试AI功能数据结构"""
        ai_functions = get_ai_functions()
        for func_name in ai_functions:
            workflow = get_ai_workflow(func_name)
            self.assertIn('description', workflow)
            self.assertIn('workflow', workflow)
            self.assertIsInstance(workflow['workflow'], list)
            
            for step in workflow['workflow']:
                self.assertIn('name', step)
                self.assertIn('description', step)
                self.assertIn('delay', step)
                self.assertIsInstance(step['delay'], int)

def run_performance_test():
    """运行性能测试"""
    print("开始性能测试...")
    
    import time
    
    # 测试数据加载性能
    start_time = time.time()
    departments = get_departments()
    dept_load_time = time.time() - start_time
    
    start_time = time.time()
    patients = get_patients_by_department('personal')
    patient_load_time = time.time() - start_time
    
    start_time = time.time()
    ai_functions = get_ai_functions()
    ai_load_time = time.time() - start_time
    
    print(f"科室数据加载时间: {dept_load_time:.4f}秒")
    print(f"患者数据加载时间: {patient_load_time:.4f}秒")
    print(f"AI功能加载时间: {ai_load_time:.4f}秒")
    
    # 测试数据完整性
    total_patients = sum(len(get_patients_by_department(dept['id'])) for dept in departments)
    print(f"总科室数: {len(departments)}")
    print(f"总患者数: {total_patients}")
    print(f"总AI功能数: {len(ai_functions)}")

def run_functionality_test():
    """运行功能测试"""
    print("开始功能测试...")
    
    # 测试所有科室的患者数据
    departments = get_departments()
    for dept in departments:
        patients = get_patients_by_department(dept['id'])
        print(f"科室 {dept['name']}: {len(patients)} 名患者")
        
        # 测试每个患者的信息完整性
        for patient in patients:
            patient_info = get_patient_info(patient['id'])
            if patient_info is None:
                print(f"警告: 患者 {patient['id']} 信息获取失败")
                
    # 测试AI功能
    ai_functions = get_ai_functions()
    for func_name in ai_functions:
        workflow = get_ai_workflow(func_name)
        if workflow is None:
            print(f"警告: AI功能 {func_name} 工作流程获取失败")
        else:
            print(f"AI功能 {func_name}: {len(workflow['workflow'])} 个步骤")

if __name__ == '__main__':
    print("=" * 50)
    print("HISAuto_web 应用测试")
    print("=" * 50)
    
    # 运行功能测试
    run_functionality_test()
    print()
    
    # 运行性能测试
    run_performance_test()
    print()
    
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(verbosity=2) 