from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from models.base import BaseModel

class ActionDebugMouse(BaseModel):
    """Debug行为操作表_鼠标"""
    __tablename__ = 'action_debug_mouse'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    mouse_action = Column(Integer, nullable=False)  # 鼠标动作(1:左击,2:右击,3:左键按下,4:右键按下,5:左键释放,6:右键释放,7:滚轮动作)
    mouse_size = Column(Float)  # 鼠标动作大小(用于记录滚轮动作的大小)
    action_list_id = Column(Integer, ForeignKey('action_debug_list.id'))  # 外键，与ActionDebugList中的ID关联

    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionDebugMouse).filter_by(id=group_id).first()
        session.close()
        return action
    # 关系
    action_list = relationship("ActionDebugList", back_populates="mouse_actions")

class ActionDebugKeyboard(BaseModel):
    """Debug行为操作表_键盘"""
    __tablename__ = 'action_debug_keyboard'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    keyboard_type = Column(Integer, nullable=False)  # 键盘类型(1:按下,2:释放,3:单击,4:文本)
    keyboard_value = Column(String(500))  # 按键值或文本内容
    action_list_id = Column(Integer, ForeignKey('action_debug_list.id'))  # 外键，与ActionDebugList中的ID关联

    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionDebugKeyboard).filter_by(id=group_id).first()
        session.close()
        return action
    # 关系
    action_list = relationship("ActionDebugList", back_populates="keyboard_actions")

class ActionDebugCodeTxt(BaseModel):
    """Debug行为操作表_密码文本"""
    __tablename__ = 'action_debug_codetxt'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    code_text = Column(String(500))  # 密码文本(SHA256保存)
    code_tips = Column(String(500))  # 密码文本的提示文本内容
    action_list_id = Column(Integer, ForeignKey('action_debug_list.id'))  # 外键，与ActionDebugList中的ID关联

    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionDebugCodeTxt).filter_by(id=group_id).first()
        session.close()
        return action
    # 关系
    action_list = relationship("ActionDebugList", back_populates="code_text_actions")

class ActionDebugPrintscreen(BaseModel):
    """Debug截屏操作表"""
    __tablename__ = 'action_debug_printscreen'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    lux = Column(Integer)  # 截屏左上角x坐标
    luy = Column(Integer)  # 截屏左上角y坐标
    rdx = Column(Integer)  # 截屏右下角x坐标
    rdy = Column(Integer)  # 截屏右下角y坐标
    pic_location = Column(String(200))  # 图片位置
    mouse_action = Column(Integer, default=0)  # 鼠标动作(0:无,1:左击,2:右击,3:左键按下,4:右键按下,5:左键释放,6:右键释放,7:滚轮动作)
    action_list_id = Column(Integer, ForeignKey('action_debug_list.id'))  # 外键，与ActionDebugList中的ID关联

    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionDebugPrintscreen).filter_by(id=group_id).first()
        session.close()
        return action
    # 关系
    action_list = relationship("ActionDebugList", back_populates="printscreen_actions")

class ActionDebugFunction(BaseModel):
    """Debug其他操作函数表"""
    __tablename__ = 'action_debug_function'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    function_name = Column(String(200), nullable=False)  # 函数名称
    args1 = Column(String(500))  # 函数参数1
    args2 = Column(String(500))  # 函数参数2
    args_list = Column(String(500))  # 函数参数列表所在位置
    action_list_id = Column(Integer, ForeignKey('action_debug_list.id'))  # 外键，与ActionDebugList中的ID关联

    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionDebugFunction).filter_by( id=group_id).first()
        session.close()
        return action
    # 关系
    action_list = relationship("ActionDebugList", back_populates="function_actions")

class ActionDebugClass(BaseModel):
    """Debug检验列表_类"""
    __tablename__ = 'action_debug_class'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    class_name = Column(String(200))  # 类名
    windows_title = Column(String(500))  # 窗体名
    action_list_id = Column(Integer, ForeignKey('action_debug_list.id'))  # 外键，与ActionDebugList中的ID关联

    def get_action_by_group_id(group_id):   
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionDebugClass).filter_by(id=group_id).first()
        session.close()
        return action
        # 关系
    action_list = relationship("ActionDebugList", back_populates="class_actions")

class ActionDebugList(BaseModel):
    """Debug行为组记录表"""
    __tablename__ = 'action_debug_list'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    group_id = Column(Integer, ForeignKey('actions_debug_group.id'))  # 行为组的编号
    action_type = Column(String(50), nullable=False)  # 行为类型
    action_name = Column(String(200))  # 行为名称
    next_id = Column(Integer)  # 下一步的行为ID
    back_id = Column(Integer)  # 返回ID
    action_note = Column(String(500))  # 行为元备注

    # 关系
    mouse_actions = relationship("ActionDebugMouse", back_populates="action_list")
    keyboard_actions = relationship("ActionDebugKeyboard", back_populates="action_list")
    code_text_actions = relationship("ActionDebugCodeTxt", back_populates="action_list")
    printscreen_actions = relationship("ActionDebugPrintscreen", back_populates="action_list")
    function_actions = relationship("ActionDebugFunction", back_populates="action_list")
    class_actions = relationship("ActionDebugClass", back_populates="action_list")
    debug_group = relationship("ActionsDebugGroup", back_populates="action_lists", foreign_keys=[group_id])

class ActionsDebugGroup(BaseModel):
    """Debug行为组表"""
    __tablename__ = 'actions_debug_group'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    sort_num = Column(Integer)  # 排序编码
    action_list_group_name = Column(String(200))  # 行为组名称
    group_rank = Column(String(50))  # 组级别
    excel_name = Column(String(200))  # Excel文件名
    excel_sheet_num = Column(Integer)  # Sheet编号
    excel_column = Column(Integer)  # 列编号
    last_circle_local = Column(Integer)  # 上一次循环位置
    last_circle_node = Column(Integer)  # 上一次循环节点
    back_id = Column(Integer)  # 返回ID
    user_id = Column(Integer, ForeignKey('users.id'))  # 用户ID
    department_id = Column(Integer, ForeignKey('departments.code'))  # 科室code 
    action_list_group_note = Column(String(500))  # 行为组备注
    action_debug_group_hierarchy_id = Column(Integer, ForeignKey('actions_debug_group_hierarchy.id'))  # 外键，与ActionsDebugGroupHierarchy中的ID关联

    # 关系
    action_lists = relationship("ActionDebugList", back_populates="debug_group", foreign_keys="[ActionDebugList.group_id]")
    action_debug_group_hierarchy = relationship("ActionsDebugGroupHierarchy", back_populates="action_debug_groups")
    user = relationship("User", back_populates="action_debug_groups")
    department = relationship("Department", back_populates="action_debug_groups")

class ActionsDebugGroupHierarchy(BaseModel):
    """Debug行为组分层"""
    __tablename__ = 'actions_debug_group_hierarchy'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    group_name = Column(String(200))  # 组名称
    group_rank = Column(String(50))  # 组级别
    sort_num = Column(Integer)  # 排序编码
    doctor_id = Column(Integer, ForeignKey('users.id'))  # 医生ID
    department_id = Column(Integer, ForeignKey('departments.id'))  # 科室ID
    group_note = Column(String(500))  # 组备注

    # 关系
    action_debug_groups = relationship("ActionsDebugGroup", back_populates="action_debug_group_hierarchy") 