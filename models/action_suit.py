from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from models.base import BaseModel

class ActionSuitMouse(BaseModel):
    """Suit行为操作表_鼠标"""
    __tablename__ = 'action_suit_mouse'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    mouse_action = Column(Integer, nullable=False)  # 鼠标动作(1:左击,2:右击,3:左键按下,4:右键按下,5:左键释放,6:右键释放,7:滚轮动作)
    mouse_size = Column(Float)  # 鼠标动作大小(用于记录滚轮动作的大小)
    action_list_id = Column(Integer, ForeignKey('actions_suit_list.id'))  # 外键，与ActionsSuitList中的ID关联

    # 关系
    action_list = relationship("ActionsSuitList", back_populates="mouse_actions")

class ActionSuitKeyboard(BaseModel):
    """Suit行为操作表_键盘"""
    __tablename__ = 'action_suit_keyboard'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    keyboard_type = Column(Integer, nullable=False)  # 键盘类型(1:按下,2:释放,3:单击,4:文本)
    keyboard_value = Column(String(500))  # 按键值或文本内容
    action_list_id = Column(Integer, ForeignKey('actions_suit_list.id'))  # 外键，与ActionsSuitList中的ID关联

    # 关系
    action_list = relationship("ActionsSuitList", back_populates="keyboard_actions")

class ActionSuitCodeTxt(BaseModel):
    """Suit行为操作表_密码文本"""
    __tablename__ = 'action_suit_codetxt'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    code_text = Column(String(500))  # 密码文本(SHA256保存)
    code_tips = Column(String(500))  # 密码文本的提示文本内容
    action_list_id = Column(Integer, ForeignKey('actions_suit_list.id'))  # 外键，与ActionsSuitList中的ID关联

    # 关系
    action_list = relationship("ActionsSuitList", back_populates="code_text_actions")

class ActionSuitPrintscreen(BaseModel):
    """Suit截屏操作表"""
    __tablename__ = 'action_suit_printscreen'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    lux = Column(Integer)  # 截屏左上角x坐标
    luy = Column(Integer)  # 截屏左上角y坐标
    rdx = Column(Integer)  # 截屏右下角x坐标
    rdy = Column(Integer)  # 截屏右下角y坐标
    pic_name = Column(String(200))  # 图片名称
    match_picture_name = Column(String(200))  # 匹配的图片文件名
    match_text = Column(String(500))  # 匹配的文本信息
    mouse_action = Column(Integer, default=0)  # 鼠标动作(0:无,1:左击,2:右击,3:左键按下,4:右键按下,5:左键释放,6:右键释放,7:滚轮动作)
    action_list_id = Column(Integer, ForeignKey('actions_suit_list.id'))  # 外键，与ActionsSuitList中的ID关联

    # 关系
    action_list = relationship("ActionsSuitList", back_populates="printscreen_actions")

class ActionSuitAI(BaseModel):
    """SuitAI模型的行为操作表"""
    __tablename__ = 'action_suit_ai'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    train_group_name = Column(String(200))  # 训练库名称
    train_long_name = Column(String(200))  # 记录名称
    long_txt_name = Column(String(200))  # 长文本名称
    ai_illustration = Column(String(1000))  # AI网页输入框输入的文本内容
    ai_note = Column(String(500))  # 备注信息
    action_list_id = Column(Integer, ForeignKey('actions_suit_list.id'))  # 外键，与ActionsSuitList中的ID关联

    # 关系
    action_list = relationship("ActionsSuitList", back_populates="ai_actions")

class ActionSuitFunction(BaseModel):
    """其他Suit操作函数表"""
    __tablename__ = 'action_suit_function'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    function_name = Column(String(200), nullable=False)  # 函数名称
    args1 = Column(String(500))  # 函数参数1
    args2 = Column(String(500))  # 函数参数2
    args_list = Column(String(500))  # 函数参数列表所在位置
    action_list_id = Column(Integer, ForeignKey('actions_suit_list.id'))  # 外键，与ActionsSuitList中的ID关联

    # 关系
    action_list = relationship("ActionsSuitList", back_populates="function_actions")

class ActionSuitClass(BaseModel):
    """Suit检验列表_类"""
    __tablename__ = 'action_suit_class'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    class_name = Column(String(200))  # 类名
    windows_title = Column(String(500))  # 窗体名
    action_list_id = Column(Integer, ForeignKey('actions_suit_list.id'))  # 外键，与ActionsSuitList中的ID关联

    # 关系
    action_list = relationship("ActionsSuitList", back_populates="class_actions")

class ActionsSuitList(BaseModel):
    """Suit行为组记录表"""
    __tablename__ = 'actions_suit_list'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    group_id = Column(Integer,ForeignKey('actions_suit_group.id'))  # 行为组的编号
    action_type = Column(String(50), nullable=False)  # 行为类型
    action_name = Column(String(200))  # 行为名称
    next_id = Column(Integer)  # 下一步ID
    debug_group_id = Column(Integer)  # Debug调试用ID
    setup_time = Column(DateTime)  # 设置时间
    update_time = Column(DateTime)  # 更新时间
    action_note = Column(String(500))  # 行为元备注

    # 关系
    mouse_actions = relationship("ActionSuitMouse", back_populates="action_list")
    keyboard_actions = relationship("ActionSuitKeyboard", back_populates="action_list")
    code_text_actions = relationship("ActionSuitCodeTxt", back_populates="action_list")
    printscreen_actions = relationship("ActionSuitPrintscreen", back_populates="action_list")
    ai_actions = relationship("ActionSuitAI", back_populates="action_list")
    function_actions = relationship("ActionSuitFunction", back_populates="action_list")
    class_actions = relationship("ActionSuitClass", back_populates="action_list")
    action_list_group = relationship("ActionsSuitGroup", back_populates="action_lists")

class ActionsSuitGroup(BaseModel):
    """Suit行为组表"""
    __tablename__ = 'actions_suit_group'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    sort_num = Column(Integer)  # 排序编码
    action_list_group_name = Column(String(200))  # 行为组名称
    group_rank_id = Column(Integer,ForeignKey('actions_suit_group_hierarchy.id'))  # 组级别
    excel_name = Column(String(200))  # Excel文件名
    excel_sheet_num = Column(Integer)  # Sheet编号
    excel_column = Column(Integer)  # 列编号
    last_circle_local = Column(Integer)  # 上一次循环位置
    last_circle_node = Column(Integer)  # 上一次循环节点
    about_time = Column(String(50))  # 预计时间
    setup_time = Column(DateTime)  # 设置时间
    update_time = Column(DateTime)  # 更新时间
    department_id = Column(Integer, ForeignKey('departments.code'))  # 科室code 
    user_id = Column(Integer, ForeignKey('users.id'))  # 用户ID
    action_list_group_note = Column(String(500))  # 行为组备注
    is_auto = Column(Boolean, default=False)  # 是否自动执行
    auto_time = Column(String(20))  # 自动执行时间

    # 关系
    action_lists = relationship("ActionsSuitList", back_populates="action_list_group")
    action_suit_group_hierarchy = relationship("ActionsSuitGroupHierarchy", back_populates="action_suit_groups")
    user = relationship("User", back_populates="action_suit_groups")
    department = relationship("Department", back_populates="action_suit_groups")

class ActionsSuitGroupHierarchy(BaseModel):
    """行为组套"""
    __tablename__ = 'actions_suit_group_hierarchy'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    group_name = Column(String(200))  # 组名称
    group_rank = Column(String(50))  # 组级别
    sort_num = Column(Integer)  # 排序编码
    doctor_id = Column(Integer, ForeignKey('users.id'))  # 医生ID
    department_id = Column(Integer, ForeignKey('departments.id'))  # 科室ID
    group_note = Column(String(500))  # 组备注

    # 关系
    action_suit_groups = relationship("ActionsSuitGroup", back_populates="action_suit_group_hierarchy") 