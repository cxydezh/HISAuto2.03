from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import datetime

class User(BaseModel):
    """用户模型"""
    
    __tablename__ = "users"
    
    user_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(50), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.code"), nullable=False)
    password = Column(String(100), nullable=False)
    phone = Column(String(20))
    role = Column(String(20), default="doctor")  # doctor, department_admin, system_admin, super_admin
    permission = Column(String(100))  # 权限列表，JSON格式
    ai_capacity = Column(Integer, default=100)
    last_login = Column(DateTime)
    last_ip = Column(String(50))
    
    # 关联关系
    department = relationship("Department", back_populates="users")
    action_groups = relationship("ActionGroup", back_populates="user")
    action_debug_groups = relationship("ActionsDebugGroup", back_populates="user")
    action_suit_groups = relationship("ActionsSuitGroup", back_populates="user")
    task_list = relationship("TaskList", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, username={self.username})>" 