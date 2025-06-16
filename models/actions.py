from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import BaseModel

class ActionMouse(BaseModel):
    """行为操作表_鼠标"""
    __tablename__ = 'action_mouse'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    mouse_action = Column(Integer, nullable=False)  # 鼠标动作(1:左击,2:右击,3:左键按下,4:右键按下,5:左键释放,6:右键释放,7:滚轮动作)
    mouse_size = Column(Float)  # 鼠标动作大小(用于记录滚轮动作的大小)
    x = Column(Integer)  # 鼠标X坐标
    y = Column(Integer)  # 鼠标Y坐标
    time_diff = Column(Float)  # 与上一个动作的时间差
    action_list_id = Column(Integer, ForeignKey('action_list.id'))  # 外键，与ActionList中的ID关联

    # 关系
    action_list = relationship("ActionList", back_populates="mouse_actions")


    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionMouse).filter_by(action_list_id=group_id).first()
        session.close()
        return action

    def __repr__(self):
        return f"<ActionMouse(id={self.id}, action_list_id={self.action_list_id})>"

class ActionKeyboard(BaseModel):
    """行为操作表_键盘"""
    __tablename__ = 'action_keyboard'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    keyboard_type = Column(Integer, nullable=False)  # 键盘类型(1:按下,2:释放,3:单击,4:文本)
    keyboard_value = Column(String(500))  # 按键值或文本内容
    time_diff = Column(Float)  # 与上一个动作的时间差
    action_list_id = Column(Integer, ForeignKey('action_list.id'))  # 外键，与ActionList中的ID关联

    # 关系
    action_list = relationship("ActionList", back_populates="keyboard_actions")

    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionKeyboard).filter_by(action_list_id=group_id).first()
        session.close()
        return action
    def __repr__(self):
        return f"<ActionKeyboard(id={self.id}, action_list_id={self.action_list_id})>"

class ActionCodeTxt(BaseModel):
    """行为操作表_密码文本"""
    __tablename__ = 'action_codetxt'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    code_text = Column(String(500))  # 密码文本(SHA256保存)
    code_tips = Column(String(500))  # 密码文本的提示文本内容
    time_diff = Column(Float)  # 与上一个动作的时间差
    action_list_id = Column(Integer, ForeignKey('action_list.id'))  # 外键，与ActionList中的ID关联

    # 关系
    action_list = relationship("ActionList", back_populates="code_text_actions")

    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionCodeTxt).filter_by(action_list_id=group_id).first()
        session.close()
        return action
    def __repr__(self):
        return f"<ActionCodeTxt(id={self.id}, action_list_id={self.action_list_id})>"

class ActionPrintscreen(BaseModel):
    """截屏操作表"""
    __tablename__ = 'action_printscreen'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    lux = Column(Integer)  # 截屏左上角x坐标
    luy = Column(Integer)  # 截屏左上角y坐标
    rdx = Column(Integer)  # 截屏右下角x坐标
    rdy = Column(Integer)  # 截屏右下角y坐标
    pic_name = Column(String(200))  # 图片名称
    match_picture_name = Column(String(200))  # 匹配的图片文件名
    match_text = Column(String(500))  # 匹配的文本信息
    mouse_action = Column(Integer, default=0)  # 鼠标动作(0:无,1:左击,2:右击,3:左键按下,4:右键按下,5:左键释放,6:右键释放,7:滚轮动作)
    time_diff = Column(Float)  # 与上一个动作的时间差
    action_list_id = Column(Integer, ForeignKey('action_list.id'))  # 外键，与ActionList中的ID关联

    # 关系
    action_list = relationship("ActionList", back_populates="printscreen_actions")

    def get_action_by_group_id(group_id):
        from database.db_manager import DatabaseManager 
        from config.config_manager import ConfigManager

        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        dp_encryption_key = config.get_value('System', 'dbencryptionkey')
        db_manager = DatabaseManager(db_path, dp_encryption_key)
        db_manager.initialize()
        session = db_manager.get_session()
        action = session.query(ActionPrintscreen).filter_by(action_list_id=group_id).first()
        session.close()
        return action
    def __repr__(self):
        return f"<ActionPrintscreen(id={self.id}, action_list_id={self.action_list_id})>"

class ActionAI(BaseModel):
    """AI模型的行为操作表"""
    __tablename__ = 'action_ai'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    train_group_name = Column(String(200))  # 训练库名称
    train_long_name = Column(String(200))  # 记录名称
    long_txt_name = Column(String(200))  # 长文本名称
    ai_illustration = Column(String(1000))  # AI网页输入框输入的文本内容
    ai_note = Column(String(500))  # 备注信息
    time_diff = Column(Float)  # 与上一个动作的时间差
    action_list_id = Column(Integer, ForeignKey('action_list.id'))  # 外键，与ActionList中的ID关联

    # 关系
    action_list = relationship("ActionList", back_populates="ai_actions")

    def get_action_by_group_id(group_id, action_name):
        return ActionAI.query.filter_by(action_list_id=group_id, action_name=action_name).first()
    def __repr__(self):
        return f"<ActionAI(id={self.id}, action_list_id={self.action_list_id})>"

class ActionFunction(BaseModel):
    """其他操作函数表"""
    __tablename__ = 'action_function'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    function_name = Column(String(200), nullable=False)  # 函数名称
    args1 = Column(String(500))  # 函数参数1
    args2 = Column(String(500))  # 函数参数2
    args_list = Column(String(500))  # 函数参数列表所在位置
    time_diff = Column(Float)  # 与上一个动作的时间差
    action_list_id = Column(Integer, ForeignKey('action_list.id'))  # 外键，与ActionList中的ID关联

    # 关系
    action_list = relationship("ActionList", back_populates="function_actions")

    def get_action_by_group_id(group_id, action_name):
        return ActionFunction.query.filter_by(action_list_id=group_id, action_name=action_name).first()
    def __repr__(self):
        return f"<ActionFunction(id={self.id}, action_list_id={self.action_list_id})>"

class ActionClass(BaseModel):
    """检验列表_类"""
    __tablename__ = 'action_class'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    class_name = Column(String(200))  # 类名
    windows_title = Column(String(500))  # 窗体名
    time_diff = Column(Float)  # 与上一个动作的时间差
    action_list_id = Column(Integer, ForeignKey('action_list.id'))  # 外键，与ActionList中的ID关联

    # 关系
    action_list = relationship("ActionList", back_populates="class_actions")

    def get_action_by_group_id(group_id, action_name):
        return ActionClass.query.filter_by(action_list_id=group_id, action_name=action_name).first()
    def __repr__(self):
        return f"<ActionClass(id={self.id}, action_list_id={self.action_list_id})>"

class ActionList(BaseModel):
    """行为组记录表"""
    __tablename__ = 'action_list'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    group_id = Column(Integer,ForeignKey('action_list_group.id'))  # 行为组的编号
    action_type = Column(String(50), nullable=False)  # 行为类型
    action_name = Column(String(200))  # 行为名称
    next_id = Column(Integer)  # 下一步ID
    debug_group_id = Column(Integer)  # Debug调试用ID
    action_note = Column(String(500))  # 行为元备注

    # 关系
    mouse_actions = relationship("ActionMouse", back_populates="action_list")
    keyboard_actions = relationship("ActionKeyboard", back_populates="action_list")
    code_text_actions = relationship("ActionCodeTxt", back_populates="action_list")
    printscreen_actions = relationship("ActionPrintscreen", back_populates="action_list")
    ai_actions = relationship("ActionAI", back_populates="action_list")
    function_actions = relationship("ActionFunction", back_populates="action_list")
    class_actions = relationship("ActionClass", back_populates="action_list")
    action_list_group = relationship("ActionGroup", back_populates="action_list")

    def __repr__(self):
        return f"<ActionList(id={self.id}, name={self.action_name})>"

class ActionGroup(BaseModel):
    """行为组表"""
    __tablename__ = 'action_list_group'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    sort_num = Column(Integer)
    action_list_group_name = Column(String(200))
    group_rank_id = Column(Integer,ForeignKey('actions_group_hierarchy.id'))
    excel_name = Column(String(200))
    excel_sheet_num = Column(Integer)
    excel_column = Column(Integer)
    last_circle_local = Column(Integer)
    last_circle_node = Column(Integer)
    about_time = Column(String(50))
    user_id = Column(String(50), ForeignKey('users.user_id'))
    department_id = Column(Integer, ForeignKey('departments.code'))
    action_list_group_note = Column(String(500))
    is_auto = Column(Boolean, default=False)
    auto_time = Column(String(20))

    # 关系
    action_list = relationship("ActionList", back_populates="action_list_group")
    action_group_hierarchy = relationship("ActionsGroupHierarchy", back_populates="action_groups")
    task_list = relationship("TaskList", back_populates="action_group")
    user = relationship("User", back_populates="action_groups")
    department = relationship("Department", back_populates="action_groups")
    task_list_finished = relationship("TaskListFinished", back_populates="action_group")
    auto_task = relationship("AutoTask", back_populates="action_group")

    def __repr__(self):
        return f"<ActionGroup(id={self.id}, name={self.action_list_group_name})>"

class ActionsGroupHierarchy(BaseModel):
    """行为组分层"""
    __tablename__ = 'actions_group_hierarchy'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    group_name = Column(String(200))  # 组名称
    group_rank = Column(String(50))  # 组级别
    sort_num = Column(Integer)  # 排序编码
    doctor_id = Column(Integer, ForeignKey('users.id'))  # 医生ID
    department_id = Column(Integer, ForeignKey('departments.id'))  # 科室ID
    group_note = Column(String(500))  # 组备注

    # 关系
    action_groups = relationship("ActionGroup", back_populates="action_group_hierarchy")

    def __repr__(self):
        return f"<ActionsGroupHierarchy(id={self.id}, name={self.group_name})>" 