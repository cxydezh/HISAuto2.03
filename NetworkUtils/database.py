#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HISAuto_web 数据库模型
用于存储AI运行结果和患者信息
"""

import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='his_auto.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建AI运行结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_run_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                ai_function TEXT NOT NULL,
                run_mode TEXT NOT NULL,
                run_status TEXT NOT NULL,
                run_result TEXT,
                run_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                workflow_data TEXT
            )
        ''')
        
        # 创建患者信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                department TEXT,
                admission_date TEXT,
                admission_days INTEGER,
                attending_doctor TEXT,
                resident_doctor TEXT,
                chief_doctor TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_ai_result(self, patient_id, patient_name, ai_function, run_mode, run_status, run_result, workflow_data=None):
        """保存AI运行结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_run_results 
            (patient_id, patient_name, ai_function, run_mode, run_status, run_result, workflow_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, patient_name, ai_function, run_mode, run_status, run_result, workflow_data))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_patient_ai_results(self, patient_id):
        """获取指定患者的AI运行结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, ai_function, run_mode, run_status, run_result, run_time, workflow_data
            FROM ai_run_results 
            WHERE patient_id = ?
            ORDER BY run_time DESC
        ''', (patient_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'ai_function': row[1],
                'run_mode': row[2],
                'run_status': row[3],
                'run_result': row[4],
                'run_time': row[5],
                'workflow_data': row[6]
            }
            for row in results
        ]
    
    def get_ai_result_detail(self, result_id):
        """获取AI运行结果详情"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM ai_run_results WHERE id = ?
        ''', (result_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'patient_id': row[1],
                'patient_name': row[2],
                'ai_function': row[3],
                'run_mode': row[4],
                'run_status': row[5],
                'run_result': row[6],
                'run_time': row[7],
                'workflow_data': row[8]
            }
        return None
    
    def save_patient(self, patient_data):
        """保存患者信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO patients 
            (id, name, age, gender, department, admission_date, admission_days, 
             attending_doctor, resident_doctor, chief_doctor, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient_data['id'], patient_data['name'], patient_data['age'],
            patient_data['gender'], patient_data['department'], patient_data['admission_date'],
            patient_data['admission_days'], patient_data['attending_doctor'],
            patient_data['resident_doctor'], patient_data['chief_doctor'], patient_data['notes']
        ))
        
        conn.commit()
        conn.close()
    
    def get_patient(self, patient_id):
        """获取患者信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM patients WHERE id = ?
        ''', (patient_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'age': row[2],
                'gender': row[3],
                'department': row[4],
                'admission_date': row[5],
                'admission_days': row[6],
                'attending_doctor': row[7],
                'resident_doctor': row[8],
                'chief_doctor': row[9],
                'notes': row[10]
            }
        return None

# 全局数据库实例
db = Database() 