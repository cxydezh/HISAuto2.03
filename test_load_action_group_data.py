#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试_load_action_group_data函数的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.hometab_funcdata import hometab_funcData
import tkinter as tk
from tkinter import ttk

def test_load_action_group_data():
    """测试_load_action_group_data函数"""
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("测试_load_action_group_data函数")
    root.geometry("800x600")
    
    # 创建Treeview控件
    tree_frame = ttk.Frame(root)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 创建Treeview
    columns = ("名称", "备注", "ID")
    tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings")
    
    # 设置列标题
    tree.heading("#0", text="层级")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    
    # 添加滚动条
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    # 布局
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    
    # 创建控制按钮
    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def load_action_list():
        """加载ActionList数据"""
        print("正在加载ActionList数据...")
        result = hometab_funcData._load_action_group_data(tree, "ActionList")
        print(f"ActionList加载结果: {result}")
    
    def load_actions_group_hierarchy():
        """加载ActionsGroupHierarchy数据"""
        print("正在加载ActionsGroupHierarchy数据...")
        result = hometab_funcData._load_action_group_data(tree, "ActionsGroupHierarchy")
        print(f"ActionsGroupHierarchy加载结果: {result}")
    
    def load_action_suit_list():
        """加载ActionSuitList数据"""
        print("正在加载ActionSuitList数据...")
        result = hometab_funcData._load_action_group_data(tree, "ActionSuitList")
        print(f"ActionSuitList加载结果: {result}")
    
    def load_actions_suit_group_hierarchy():
        """加载ActionsSuitGroupHierarchy数据"""
        print("正在加载ActionsSuitGroupHierarchy数据...")
        result = hometab_funcData._load_action_group_data(tree, "ActionsSuitGroupHierarchy")
        print(f"ActionsSuitGroupHierarchy加载结果: {result}")
    
    def load_action_debug_list():
        """加载ActionDebugList数据"""
        print("正在加载ActionDebugList数据...")
        result = hometab_funcData._load_action_group_data(tree, "ActionDebugList")
        print(f"ActionDebugList加载结果: {result}")
    
    def load_actions_debug_group_hierarchy():
        """加载ActionsDebugGroupHierarchy数据"""
        print("正在加载ActionsDebugGroupHierarchy数据...")
        result = hometab_funcData._load_action_group_data(tree, "ActionsDebugGroupHierarchy")
        print(f"ActionsDebugGroupHierarchy加载结果: {result}")
    
    def clear_tree():
        """清空树控件"""
        tree.delete(*tree.get_children())
        print("树控件已清空")
    
    # 创建按钮
    ttk.Button(button_frame, text="加载ActionList", command=load_action_list).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="加载ActionsGroupHierarchy", command=load_actions_group_hierarchy).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="加载ActionSuitList", command=load_action_suit_list).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="加载ActionsSuitGroupHierarchy", command=load_actions_suit_group_hierarchy).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="加载ActionDebugList", command=load_action_debug_list).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="加载ActionsDebugGroupHierarchy", command=load_actions_debug_group_hierarchy).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="清空", command=clear_tree).pack(side=tk.LEFT, padx=5)
    
    # 添加说明标签
    info_label = ttk.Label(root, text="点击按钮测试不同的数据加载功能。函数会根据不同的treeDatatxt参数加载相应的数据到树控件中。", 
                          wraplength=750, justify=tk.CENTER)
    info_label.pack(pady=10)
    
    print("测试窗口已创建，请点击按钮测试函数功能")
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    test_load_action_group_data()
