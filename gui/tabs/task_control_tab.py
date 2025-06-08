import tkinter as tk
from tkinter import ttk, messagebox
from gui.tabs.base_tab import BaseTab
from models.task import TaskList, TaskListFinished
from models.actions import ActionGroup

class TaskControlTab(BaseTab):
    def __init__(self, notebook, main_window):
        super().__init__(notebook, main_window, "任务控制")
        
        # 创建界面
        self._create_widgets()
        
        # 初始化任务列表
        self._refresh_task_lists()
        
    def _create_widgets(self):
        """创建任务控制标签页的控件"""
        # 创建三列布局
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # 创建左侧面板（待执行任务）
        left_panel = ttk.LabelFrame(self.frame, text="待执行任务")
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建中间按钮区域
        middle_panel = ttk.Frame(self.frame)
        middle_panel.grid(row=0, column=1, sticky=tk.NS, padx=5, pady=5)
        
        # 创建右侧面板（已完成任务）
        right_panel = ttk.LabelFrame(self.frame, text="已完成任务")
        right_panel.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建各个面板内容
        self._create_left_panel(left_panel)
        self._create_middle_panel(middle_panel)
        self._create_right_panel(right_panel)
        
    def _create_left_panel(self, parent):
        """创建左侧面板 - 待执行任务"""
        # 创建待执行任务树形视图
        self.pending_task_tree = ttk.Treeview(parent, columns=("id", "time", "user", "priority", "auto", "group"), show="headings")
        self.pending_task_tree.heading("id", text="ID")
        self.pending_task_tree.heading("time", text="发起时间")
        self.pending_task_tree.heading("user", text="发起用户")
        self.pending_task_tree.heading("priority", text="优先级")
        self.pending_task_tree.heading("auto", text="自动执行")
        self.pending_task_tree.heading("group", text="行为组")
        
        self.pending_task_tree.column("id", width=50)
        self.pending_task_tree.column("time", width=150)
        self.pending_task_tree.column("user", width=100)
        self.pending_task_tree.column("priority", width=50)
        self.pending_task_tree.column("auto", width=50)
        self.pending_task_tree.column("group", width=100)
        
        # 添加滚动条
        pending_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.pending_task_tree.yview)
        self.pending_task_tree.configure(yscrollcommand=pending_scroll.set)
        
        # 布局
        self.pending_task_tree.grid(row=0, column=0, sticky=tk.NSEW)
        pending_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 配置grid权重
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
    def _create_middle_panel(self, parent):
        """创建中间面板 - 操作按钮"""
        # 创建按钮
        ttk.Button(parent, text="执行任务", command=self._execute_task).grid(row=0, column=0, pady=5)
        ttk.Button(parent, text="暂停任务", command=self._pause_task).grid(row=1, column=0, pady=5)
        ttk.Button(parent, text="删除任务", command=self._delete_task).grid(row=2, column=0, pady=5)
        ttk.Button(parent, text="刷新列表", command=self._refresh_task_lists).grid(row=3, column=0, pady=5)
        
    def _create_right_panel(self, parent):
        """创建右侧面板 - 已完成任务"""
        # 创建已完成任务树形视图
        self.finished_task_tree = ttk.Treeview(parent, columns=("id", "time", "user", "priority", "auto", "group", "finish_time"), show="headings")
        self.finished_task_tree.heading("id", text="ID")
        self.finished_task_tree.heading("time", text="发起时间")
        self.finished_task_tree.heading("user", text="发起用户")
        self.finished_task_tree.heading("priority", text="优先级")
        self.finished_task_tree.heading("auto", text="自动执行")
        self.finished_task_tree.heading("group", text="行为组")
        self.finished_task_tree.heading("finish_time", text="完成时间")
        
        self.finished_task_tree.column("id", width=50)
        self.finished_task_tree.column("time", width=150)
        self.finished_task_tree.column("user", width=100)
        self.finished_task_tree.column("priority", width=50)
        self.finished_task_tree.column("auto", width=50)
        self.finished_task_tree.column("group", width=100)
        self.finished_task_tree.column("finish_time", width=150)
        
        # 添加滚动条
        finished_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.finished_task_tree.yview)
        self.finished_task_tree.configure(yscrollcommand=finished_scroll.set)
        
        # 布局
        self.finished_task_tree.grid(row=0, column=0, sticky=tk.NSEW)
        finished_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 配置grid权重
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
    def _execute_task(self):
        """执行选中的任务"""
        selected_item = self.pending_task_tree.selection()
        if not selected_item:
            self.show_message("警告", "请先选择要执行的任务", "warning")
            return
        
        # 获取选中的任务信息
        task_info = self.pending_task_tree.item(selected_item[0])
        task_id = task_info['values'][0]
        
        if self.show_question("确认", f"确定要执行任务 {task_id} 吗？"):
            try:
                # 模拟任务执行
                # TODO: 实际的任务执行逻辑
                self.show_message("成功", f"任务 {task_id} 已开始执行")
                self._refresh_task_lists()
            except Exception as e:
                self.show_message("错误", f"任务执行失败: {str(e)}", "error")
        
    def _pause_task(self):
        """暂停选中的任务"""
        selected_item = self.pending_task_tree.selection()
        if not selected_item:
            self.show_message("警告", "请先选择要暂停的任务", "warning")
            return
        
        # 获取选中的任务信息
        task_info = self.pending_task_tree.item(selected_item[0])
        task_id = task_info['values'][0]
        
        if self.show_question("确认", f"确定要暂停任务 {task_id} 吗？"):
            try:
                # 模拟任务暂停
                # TODO: 实际的任务暂停逻辑
                self.show_message("成功", f"任务 {task_id} 已暂停")
                self._refresh_task_lists()
            except Exception as e:
                self.show_message("错误", f"任务暂停失败: {str(e)}", "error")
        
    def _delete_task(self):
        """删除选中的任务"""
        selected_item = self.pending_task_tree.selection()
        if not selected_item:
            self.show_message("警告", "请先选择要删除的任务", "warning")
            return
        
        # 获取选中的任务信息
        task_info = self.pending_task_tree.item(selected_item[0])
        task_id = task_info['values'][0]
        
        if self.show_question("确认", f"确定要删除任务 {task_id} 吗？"):
            try:
                # 模拟任务删除
                # TODO: 实际的任务删除逻辑
                self.pending_task_tree.delete(selected_item[0])
                self.show_message("成功", f"任务 {task_id} 已删除")
            except Exception as e:
                self.show_message("错误", f"任务删除失败: {str(e)}", "error")
        
    def _refresh_task_lists(self):
        """刷新任务列表"""
        try:
            # 清空现有列表
            self.pending_task_tree.delete(*self.pending_task_tree.get_children())
            self.finished_task_tree.delete(*self.finished_task_tree.get_children())
            
            # 添加示例数据
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 待执行任务示例数据
            self.pending_task_tree.insert("", "end", values=(
                "1", current_time, "admin", "高", "是", "数据处理组"
            ))
            self.pending_task_tree.insert("", "end", values=(
                "2", current_time, "doctor", "中", "否", "报告生成组"
            ))
            
            # 已完成任务示例数据
            self.finished_task_tree.insert("", "end", values=(
                "10", "2024-01-15 09:00:00", "admin", "高", "是", "数据备份组", current_time
            ))
            self.finished_task_tree.insert("", "end", values=(
                "11", "2024-01-15 10:30:00", "doctor", "中", "否", "统计分析组", current_time
            ))
            
        except Exception as e:
            print(f"刷新任务列表失败: {str(e)}")
            self.show_message("错误", f"刷新任务列表失败: {str(e)}", "error") 