from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class TaskList(BaseModel):
    """任务列表"""
    __tablename__ = 'task_list'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    task_start_time = Column(DateTime, nullable=False)  # 任务发起时间
    task_priority = Column(Integer, nullable=False)  # 任务优先级
    task_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 任务发起用户ID
    task_user_name = Column(String(100), nullable=False)  # 任务发起用户名
    task_ip = Column(String(50), nullable=False)  # 任务来源的IP地址
    task_is_auto = Column(Boolean, default=False)  # 任务是否为自动执行
    actions_group_id = Column(Integer, ForeignKey('action_list_group.id'), nullable=False)  # 要执行的任务的行为组ID号

    # 关系
    user = relationship("User", foreign_keys=[task_user_id],back_populates="task_list")
    action_group = relationship("ActionGroup", foreign_keys=[actions_group_id],back_populates="task_list")

    def move_to_finished(self, finished_time):
        """将任务移动到已完成列表"""
        from models.task import TaskListFinished
        finished_task = TaskListFinished(
            task_start_time=self.task_start_time,
            task_priority=self.task_priority,
            task_user_id=self.task_user_id,
            task_user_name=self.task_user_name,
            task_ip=self.task_ip,
            task_is_auto=self.task_is_auto,
            actions_group_id=self.actions_group_id,
            finished_time=finished_time
        )
        return finished_task

class TaskListFinished(BaseModel):
    """已完成的任务列表"""
    __tablename__ = 'task_list_finished'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    task_start_time = Column(DateTime, nullable=False)  # 任务发起时间
    task_priority = Column(Integer, nullable=False)  # 任务优先级
    task_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 任务发起用户ID
    task_user_name = Column(String(100), nullable=False)  # 任务发起用户名
    task_ip = Column(String(50), nullable=False)  # 任务来源的IP地址
    task_is_auto = Column(Boolean, default=False)  # 任务是否为自动执行
    actions_group_id = Column(Integer, ForeignKey('action_list_group.id'), nullable=False)  # 要执行的任务的行为组ID号
    finished_time = Column(DateTime, nullable=False)  # 运行完成的时间

    # 关系
    user = relationship("User", foreign_keys=[task_user_id])
    action_group = relationship("ActionGroup", foreign_keys=[actions_group_id],back_populates="task_list_finished")

class AutoTask(BaseModel):
    """自动执行任务列表"""
    __tablename__ = 'auto_task'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    task_start_time = Column(DateTime, nullable=False)  # 任务发起时间
    task_priority = Column(Integer, nullable=False)  # 任务优先级
    task_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 任务发起用户ID
    task_user_name = Column(String(100), nullable=False)  # 任务发起用户名
    task_ip = Column(String(50), nullable=False)  # 任务来源的IP地址
    task_is_auto = Column(Boolean, default=True)  # 任务是否为自动执行
    actions_group_id = Column(Integer, ForeignKey('action_list_group.id'), nullable=False)  # 要执行的任务的行为组ID号
    auto_time = Column(String(50), nullable=False)  # 自动执行的时间

    # 关系
    user = relationship("User", foreign_keys=[task_user_id])
    action_group = relationship("ActionGroup", foreign_keys=[actions_group_id],back_populates="auto_task")

    def create_task(self):
        """创建新的任务"""
        from models.task import TaskList
        new_task = TaskList(
            task_start_time=self.task_start_time,
            task_priority=self.task_priority,
            task_user_id=self.task_user_id,
            task_user_name=self.task_user_name,
            task_ip=self.task_ip,
            task_is_auto=True,
            actions_group_id=self.actions_group_id
        )
        return new_task 