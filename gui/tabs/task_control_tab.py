import tkinter as tk
from tkinter import ttk, messagebox
from gui.tabs.base_tab import BaseTab
from models.task import TaskList, TaskListFinished
from models.actions import ActionGroup, ActionList
from gui.tabs.Hierarchyutils import parse_group_rank
from utils.home_tab_func import ActionGroupRun
from database.db_manager import DatabaseManager
from config.config_manager import ConfigManager
from datetime import datetime

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
                # 获取任务信息
                config_manager = ConfigManager()
                db_path = config_manager.get_value('System', 'DataSource')
                encryption_key = config_manager.get_value('Security', 'DBEncryptionKey')
                
                if not db_path or not encryption_key:
                    self.show_message("错误", "数据库配置信息不完整", "error")
                    return
                
                db_manager = DatabaseManager(db_path, encryption_key)
                db_manager.initialize()
                session = db_manager.Session()
                
                try:
                    # 获取任务记录
                    task = session.query(TaskList).filter_by(id=task_id).first()
                    if not task:
                        self.show_message("错误", f"找不到任务 {task_id}", "error")
                        return
                    
                    # 获取行为组ID
                    actions_group_id = task.actions_group_id
                    
                    if not actions_group_id:
                        self.show_message("错误", "该任务没有关联的行为组", "error")
                        return
                    
                    # 使用ActionGroupRun来执行行为组
                    # run_action_group方法会自动检查是否有Excel表格，如果有则遍历每一行执行，如果没有则只执行一次
                    from utils.home_tab_func import ActionGroupRun
                    action_runner = ActionGroupRun(None)  # 暂时传None，如果需要home_tab的功能，可以后续修改
                    
                    # 调用run_action_group方法，该方法会：
                    # 1. 检查行为组是否有Excel表格（excel_name、excel_sheet_num、excel_column）
                    # 2. 如果有表格，遍历每一行数据，每访问一行就执行一次行为组
                    # 3. 如果没有表格，只执行一次行为组
                    success = action_runner.run_action_group(actions_group_id)
                    
                    if success:
                        # 将任务移动到已完成列表
                        finished_task = task.move_to_finished(datetime.now())
                        session.add(finished_task)
                        session.delete(task)
                        session.commit()
                        
                        self.show_message("成功", f"任务 {task_id} 执行完成")
                        self._refresh_task_lists()
                    else:
                        self.show_message("错误", f"任务 {task_id} 执行失败", "error")
                        
                finally:
                    session.close()
                    
            except Exception as e:
                self.show_message("错误", f"任务执行失败: {str(e)}", "error")
                import traceback
                traceback.print_exc()
    
    def _get_ordered_actions_by_tree_structure(self, session, group_id):
        """根据树结构顺序获取ActionList
        
        排序规则（根据需求文档）：
        1. 先根据list_rank级别排序
        2. 然后根据sort_num排序
        3. 排除action_type为"hierarchy_list"的记录（这些只是目录节点）
        
        Args:
            session: 数据库会话
            group_id: 行为组ID
            
        Returns:
            list: 按树结构顺序排列的ActionList记录列表
        """
        try:
            # 获取所有行为元
            all_actions = session.query(ActionList).filter_by(group_id=group_id).all()
            
            # 过滤掉hierarchy_list类型的记录（这些只是目录节点，不执行）
            executable_actions = []
            for action in all_actions:
                action_type = getattr(action, 'action_type', None)
                if action_type and action_type not in ['hierarchy_list', 'list_hierarchy']:
                    # 只处理有list_rank的记录
                    if action.list_rank:
                        executable_actions.append(action)
            
            # 按照树结构顺序排序
            # 排序规则：先按list_rank排序，然后按sort_num排序
            def get_sort_key(action):
                """获取排序键"""
                if not action.list_rank:
                    # 如果没有list_rank，放到最后
                    return f"Z999_{action.sort_num or 0:06d}_{action.id}"
                
                # 解析list_rank
                rank_dict = parse_group_rank(action.list_rank)
                
                # 创建排序键：A级_B级_C级_D级_E级_sort_num_id
                sort_key = (
                    f"{rank_dict['A']:03d}_{rank_dict['B']:03d}_{rank_dict['C']:03d}_"
                    f"{rank_dict['D']:03d}_{rank_dict['E']:03d}_{action.sort_num or 0:06d}_{action.id}"
                )
                return sort_key
            
            # 排序
            ordered_actions = sorted(executable_actions, key=lambda x: get_sort_key(x))
            
            return ordered_actions
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []
    
    def _execute_actions_in_order(self, session, ordered_actions, action_runner):
        """按照顺序执行行为元
        
        Args:
            session: 数据库会话
            ordered_actions: 按树结构顺序排列的ActionList记录列表
            action_runner: ActionGroupRun实例，用于执行行为元
            
        Returns:
            bool: 是否成功执行
        """
        try:
            # 创建ID到记录的映射，用于快速查找
            action_map = {action.id: action for action in ordered_actions}
            
            # 记录已执行的action ID，避免循环
            executed_ids = set()
            
            # 从第一个action开始执行
            current_action_id = None
            if ordered_actions:
                current_action_id = ordered_actions[0].id
            
            # 按照树结构顺序执行，但如果next_id存在，优先跳转到next_id
            while current_action_id and current_action_id not in executed_ids:
                executed_ids.add(current_action_id)
                
                # 获取当前action
                current_action = action_map.get(current_action_id)
                if not current_action:
                    # 如果找不到当前action，尝试从数据库中查找
                    current_action = session.query(ActionList).filter_by(id=current_action_id, group_id=action_runner.group_id).first()
                    if not current_action:
                        break
                
                # 执行当前action
                action_result = self._execute_single_action(current_action, action_runner)
                
                if not action_result:
                    # 如果执行失败，可以进入Debug流程或终止
                    # 这里暂时返回False，后续可以根据需求添加Debug处理
                    return False
                
                # 确定下一个action
                if current_action.next_id:
                    # 如果有next_id，优先跳转到next_id对应的action
                    next_action = session.query(ActionList).filter_by(
                        id=current_action.next_id, 
                        group_id=action_runner.group_id
                    ).first()
                    
                    if next_action:
                        # 如果next_id指向的action在ordered_actions中，添加到map中
                        if next_action.id not in action_map:
                            action_map[next_action.id] = next_action
                        current_action_id = next_action.id
                    else:
                        # next_id指向的action不存在或不在当前group中，按顺序执行下一个
                        current_action_id = self._get_next_action_id_by_order(
                            current_action_id, ordered_actions
                        )
                else:
                    # 没有next_id，按树结构顺序执行下一个
                    current_action_id = self._get_next_action_id_by_order(
                        current_action_id, ordered_actions
                    )
            
            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def _get_next_action_id_by_order(self, current_action_id, ordered_actions):
        """根据树结构顺序获取下一个action的ID
        
        Args:
            current_action_id: 当前action的ID
            ordered_actions: 按树结构顺序排列的ActionList记录列表
            
        Returns:
            int or None: 下一个action的ID，如果没有则返回None
        """
        # 找到当前action在列表中的位置
        current_index = None
        for i, action in enumerate(ordered_actions):
            if action.id == current_action_id:
                current_index = i
                break
        
        # 如果找到当前位置，返回下一个action的ID
        if current_index is not None and current_index + 1 < len(ordered_actions):
            return ordered_actions[current_index + 1].id
        
        return None
    
    def _execute_single_action(self, action, action_runner):
        """执行单个行为元
        
        Args:
            action: ActionList记录
            action_runner: ActionGroupRun实例
            
        Returns:
            bool: 是否成功执行
        """
        try:
            action_type = getattr(action, 'action_type', None)
            
            if action_type == 'mouse':
                return action_runner.run_mouse_action(action.id)
            elif action_type == 'keyboard':
                return action_runner.run_keyboard_action(action.id)
            elif action_type == 'code_text' or action_type == 'code':
                return action_runner.run_code_action(action.id)
            elif action_type == 'class':
                return action_runner.run_class_action(action.id)
            elif action_type == 'ai' or action_type == 'AI':
                return action_runner.run_AI_action(action.id)
            elif action_type == 'printscreen' or action_type == 'image':
                return action_runner.run_image_action(action.id)
            elif action_type == 'function':
                return action_runner.run_function_action(action.id)
            else:
                # 未知的行为类型
                return False
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
        
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