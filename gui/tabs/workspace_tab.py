import tkinter as tk
from tkinter import ttk, messagebox
from gui.tabs.base_tab import BaseTab

class WorkspaceTab(BaseTab):
    def __init__(self, notebook, main_window):
        super().__init__(notebook, main_window, "工作区")
        
        # 创建界面
        self._create_widgets()
        
    def _create_widgets(self):
        """创建工作区标签页的控件"""
        # 创建三列布局
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # 创建左侧面板（在院患者）
        left_panel = ttk.LabelFrame(self.frame, text="在院患者")
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建中间按钮区域
        middle_panel = ttk.Frame(self.frame)
        middle_panel.grid(row=0, column=1, sticky=tk.NS, padx=5, pady=5)
        
        # 创建右侧面板（出院患者）
        right_panel = ttk.LabelFrame(self.frame, text="出院患者")
        right_panel.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建各个面板内容
        self._create_left_panel(left_panel)
        self._create_middle_panel(middle_panel)
        self._create_right_panel(right_panel)
        
    def _create_left_panel(self, parent):
        """创建左侧面板 - 在院患者"""
        # 创建在院患者树形视图
        self.in_hospital_tree = ttk.Treeview(parent, columns=("bed", "name", "id"), show="headings")
        self.in_hospital_tree.heading("bed", text="床号")
        self.in_hospital_tree.heading("name", text="姓名")
        self.in_hospital_tree.heading("id", text="病历号")
        
        self.in_hospital_tree.column("bed", width=100)
        self.in_hospital_tree.column("name", width=100)
        self.in_hospital_tree.column("id", width=150)
        
        # 添加滚动条
        in_hospital_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.in_hospital_tree.yview)
        self.in_hospital_tree.configure(yscrollcommand=in_hospital_scroll.set)
        
        # 布局
        self.in_hospital_tree.grid(row=0, column=0, sticky=tk.NSEW)
        in_hospital_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 配置grid权重
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # 添加示例数据
        self.in_hospital_tree.insert("", "end", values=("101", "张三", "2024001"))
        self.in_hospital_tree.insert("", "end", values=("102", "李四", "2024002"))
        
    def _create_middle_panel(self, parent):
        """创建中间面板 - 操作按钮"""
        # 创建按钮
        self.btn_patient_discharge = ttk.Button(parent, text="患者出院", command=self._patient_discharge)
        self.btn_patient_discharge.grid(row=0, column=0, pady=5)
        
        self.btn_patient_archive = ttk.Button(parent, text="患者归档", command=self._patient_archive)
        self.btn_patient_archive.grid(row=1, column=0, pady=5)
        
        self.btn_cancel_discharge = ttk.Button(parent, text="出院撤销", command=self._cancel_discharge)
        self.btn_cancel_discharge.grid(row=2, column=0, pady=5)
        
        self.btn_cancel_archive = ttk.Button(parent, text="归档撤销", command=self._cancel_archive)
        self.btn_cancel_archive.grid(row=3, column=0, pady=5)
        
        self.btn_refresh = ttk.Button(parent, text="刷新列表", command=self._refresh_patient_lists)
        self.btn_refresh.grid(row=4, column=0, pady=5)
        
    def _create_right_panel(self, parent):
        """创建右侧面板 - 出院患者"""
        # 创建出院患者树形视图
        self.out_hospital_tree = ttk.Treeview(parent, columns=("bed", "name", "id"), show="headings")
        self.out_hospital_tree.heading("bed", text="床号")
        self.out_hospital_tree.heading("name", text="姓名")
        self.out_hospital_tree.heading("id", text="病历号")
        
        self.out_hospital_tree.column("bed", width=100)
        self.out_hospital_tree.column("name", width=100)
        self.out_hospital_tree.column("id", width=150)
        
        # 添加滚动条
        out_hospital_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.out_hospital_tree.yview)
        self.out_hospital_tree.configure(yscrollcommand=out_hospital_scroll.set)
        
        # 布局
        self.out_hospital_tree.grid(row=0, column=0, sticky=tk.NSEW)
        out_hospital_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 配置grid权重
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
    def _patient_discharge(self):
        """处理患者出院"""
        selected_item = self.in_hospital_tree.selection()
        if not selected_item:
            self.show_message("警告", "请先选择要出院的患者", "warning")
            return
            
        # 获取选中的患者信息
        patient_info = self.in_hospital_tree.item(selected_item[0])
        bed_num = patient_info['values'][0]
        patient_name = patient_info['values'][1]
        patient_id = patient_info['values'][2]
        
        if self.show_question("确认", f"确定要为患者 {patient_name} 办理出院手续吗？"):
            # 移动到出院列表
            self.out_hospital_tree.insert("", "end", values=(bed_num, patient_name, patient_id))
            self.in_hospital_tree.delete(selected_item[0])
            self.show_message("成功", f"患者 {patient_name} 已成功出院")
            
    def _patient_archive(self):
        """处理患者归档"""
        self.show_message("提示", "归档功能开发中...")
        
    def _cancel_discharge(self):
        """撤销患者出院"""
        selected_item = self.out_hospital_tree.selection()
        if not selected_item:
            self.show_message("警告", "请先选择要撤销出院的患者", "warning")
            return
            
        # 获取选中的患者信息
        patient_info = self.out_hospital_tree.item(selected_item[0])
        bed_num = patient_info['values'][0]
        patient_name = patient_info['values'][1]
        patient_id = patient_info['values'][2]
        
        if self.show_question("确认", f"确定要撤销患者 {patient_name} 的出院手续吗？"):
            # 移动回在院列表
            self.in_hospital_tree.insert("", "end", values=(bed_num, patient_name, patient_id))
            self.out_hospital_tree.delete(selected_item[0])
            self.show_message("成功", f"患者 {patient_name} 已成功撤销出院")
            
    def _cancel_archive(self):
        """撤销患者归档"""
        self.show_message("提示", "归档撤销功能开发中...")
        
    def _refresh_patient_lists(self):
        """刷新患者列表"""
        # 清空现有列表
        self.in_hospital_tree.delete(*self.in_hospital_tree.get_children())
        self.out_hospital_tree.delete(*self.out_hospital_tree.get_children())
        
        # 重新加载示例数据
        self.in_hospital_tree.insert("", "end", values=("101", "张三", "2024001"))
        self.in_hospital_tree.insert("", "end", values=("102", "李四", "2024002"))
        self.in_hospital_tree.insert("", "end", values=("103", "王五", "2024003"))
        
        self.show_message("提示", "患者列表已刷新") 