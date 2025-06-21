        def confirm_module():
            self.relate_location_selected = local_mode_var.get()
            select_mode.destroy()
            return self.relate_location_selected
            
        select_mode = tk.Toplevel(root)
        select_mode.title("选择模式")
        select_mode.geometry("400x300")
        select_mode.resizable(False, False)

        select_mode.transient(root)
        select_mode.grab_set()
        select_mode.focus_set()

        local_mode_frame = ttk.Frame(select_mode)
        local_mode_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        local_mode_var = tk.IntVar()
        
        label_local = ttk.Label(local_mode_frame, text='选择插入位置:', font=("Arial", 12))
        label_local.pack(pady=10)
        
        # 根据当前选中的节点类型显示不同的选项
        selected = self.action_tree.selection()[0]
        if not selected:
            messagebox.showwarning("警告", "请选择节点")
            local_mode_var.set(5)
            select_mode.destroy()
            return
        elif selected.startswith("group_"):
            ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
        elif selected.startswith("A") and not selected.endswith("E"):
            ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text ='插入子项', variable=local_mode_var, value=3).pack(pady=5)
        else:
            messagebox.showwarning("警告", "节点的内容出现错误，请修�?)
            local_mode_var.set(5)
            select_mode.destroy()
            return
            
        confirm_btn = ttk.Button(local_mode_frame, text="确定", command=confirm_module)
        confirm_btn.pack(pady=10)
        root.wait_window(select_mode)

    def _set_home_controls_state(self, state):
        """设置首页控件状�?""
        for ctrl in [
            self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
            self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
            self.is_auto_check, self.auto_time_entry, self.group_desc_entry
        ]:
            ctrl.config(state=state)
        self.group_user_name_entry.config(state='disabled')
        self.department_id_entry.config(state='disabled')
    def _set_action_group_entry_controls_state(self, state): 
        """设置行为组输入框控件状�?""
        for ctrl in [
            self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
            self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
            self.is_auto_check, self.auto_time_entry, self.group_desc_entry
        ]:
            ctrl.config(state=state) 
        self.group_user_name_entry.config(state='disabled')
        self.department_id_entry.config(state='disabled')
    def _set_action_group_button_controls_state(self, state):
        """设置行为组按钮控件状�?""
        for ctrl in [
            self.btn_new_action_group, self.btn_edit_action_group, self.btn_delete_action_group,
            self.btn_capture_image, self.btn_save_action_group, self.btn_refresh_action_group
        ]:
            ctrl.config(state=state)
    
    # =============================================================================
    # 行为元操作辅助方�?    # =============================================================================
    
    def _set_action_controls_state(self, state):
        """设置行为元控件状�?""
        for ctrl in [
            self.action_name_entry, self.next_action_entry, self.action_type_combo,
            self.debug_group_id_entry, self.action_note_entry
        ]:
            ctrl.config(state=state)
    
    def _set_action_button_state(self):
        """设置行为元按钮状�?""
        if self.action_operation_type in [1, 2]:  # 创建或修改状�?            self.btn_create_action.config(state='disabled')
            self.btn_record_action.config(state='disabled')
            self.btn_modify_action.config(state='disabled')
            self.btn_delete_action.config(state='disabled')
            self.btn_save_action.config(state='normal')
            self.btn_use_suit.config(state='disabled')
        else:  # 正常状�?            self.btn_create_action.config(state='normal')
            self.btn_record_action.config(state='normal')
            self.btn_modify_action.config(state='normal')
            self.btn_delete_action.config(state='normal')
            self.btn_save_action.config(state='disabled')
            self.btn_use_suit.config(state='normal')
    
    def _clear_action_detail_controls(self):
        """清空行为详情控件"""
        # 清空基本信息
        if hasattr(self, 'action_name_var'):
            self.action_name_var.set("")
        if hasattr(self, 'action_note_var'):
            self.action_note_var.set("")
        if hasattr(self, 'next_action_var'):
            self.next_action_var.set("")
            
        # 清空鼠标控件
        if hasattr(self, 'action_mouse_action_type_var'):
            self.action_mouse_action_type_var.set("")
        if hasattr(self, 'action_mouse_x_var'):
            self.action_mouse_x_var.set("")
        if hasattr(self, 'action_mouse_y_var'):
            self.action_mouse_y_var.set("")
        if hasattr(self, 'action_mouse_size_var'):
            self.action_mouse_size_var.set("")
        if hasattr(self, 'action_mouse_time_diff_var'):
            self.action_mouse_time_diff_var.set("")
            
        # 清空键盘控件
        if hasattr(self, 'action_keyboard_type_var'):
            self.action_keyboard_type_var.set("")
        if hasattr(self, 'action_keyboard_value_var'):
            self.action_keyboard_value_var.set("")
        if hasattr(self, 'action_keyboard_time_diff_var'):
            self.action_keyboard_time_diff_var.set("")
            
        # 清空类控�?        if hasattr(self, 'action_class_name_var'):
            self.action_class_name_var.set("")
        if hasattr(self, 'action_window_title_var'):
            self.action_window_title_var.set("")
        if hasattr(self, 'action_class_time_diff_var'):
            self.action_class_time_diff_var.set("")
            
        # 清空AI控件
        if hasattr(self, 'action_ai_training_group_var'):
            self.action_ai_training_group_var.set("")
        if hasattr(self, 'action_ai_record_name_var'):
            self.action_ai_record_name_var.set("")
        if hasattr(self, 'action_ai_long_text_name_var'):
            self.action_ai_long_text_name_var.set("")
        if hasattr(self, 'action_ai_illustration_var'):
            self.action_ai_illustration_var.set("")
        if hasattr(self, 'action_ai_note_var'):
            self.action_ai_note_var.set("")
        if hasattr(self, 'action_ai_time_diff_var'):
            self.action_ai_time_diff_var.set("")
            
        # 清空图像控件
        if hasattr(self, 'action_image_left_top_x_var'):
            self.action_image_left_top_x_var.set("")
        if hasattr(self, 'action_image_left_top_y_var'):
            self.action_image_left_top_y_var.set("")
        if hasattr(self, 'action_image_right_bottom_x_var'):
            self.action_image_right_bottom_x_var.set("")
        if hasattr(self, 'action_image_right_bottom_y_var'):
            self.action_image_right_bottom_y_var.set("")
        if hasattr(self, 'action_image_names_var'):
            self.action_image_names_var.set("")
        if hasattr(self, 'action_image_match_criteria_var'):
            self.action_image_match_criteria_var.set("")
        if hasattr(self, 'image_mouse_action_var'):
            self.image_mouse_action_var.set("")
        if hasattr(self, 'image_time_diff_var'):
            self.image_time_diff_var.set("")
            
        # 清空函数控件
        if hasattr(self, 'action_function_name_var'):
            self.action_function_name_var.set("")
        if hasattr(self, 'action_function_parameters_var'):
            self.action_function_parameters_var.set("")
        if hasattr(self, 'action_function_arguments_var'):
            self.action_function_arguments_var.set("")
        if hasattr(self, 'function_time_diff_var'):
            self.function_time_diff_var.set("")
                
    def _refresh_action_list(self):
        """刷新行为列表"""
        if not self.current_action_group_id:
            return
            
        try:
            # 使用ActionManager的方法刷新行为列�?            self.action_manager._refresh_action_list()
        except Exception as e:
            messagebox.showerror("错误", f"刷新行为列表失败: {str(e)}")
    
    def _update_action_buttons_state(self):
        """更新行为按钮状�?""
        # 根据是否有选中项来设置按钮状�?        selected = self.action_list.selection()
        has_selection = len(selected) > 0
        
        if has_selection and not self.action_operation_type:
            # 有选中项且不在编辑状�?            self.btn_modify_action.config(state='normal')
            self.btn_delete_action.config(state='normal')
        else:
            # 无选中项或在编辑状�?            self.btn_modify_action.config(state='disabled')
            self.btn_delete_action.config(state='disabled')
    
    # 行为操作方法  
    def _create_action(self):
        """创建行为�?""
        try:
            if self.action_manager.create_action():
                # 启用相关控件 - 使用ActionManager的方�?                self.action_manager._set_action_controls_state('normal')
                # 修改按钮状�?- 使用ActionManager的方�?                self.action_manager._set_action_button_state()
                return True
            else:
                return False
        except Exception as e:
            messagebox.showerror("错误", f"创建行为元时发生异常: {str(e)}")
            return False
