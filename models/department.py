from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import BaseModel
class Department(BaseModel):
    """科室模型"""
    
    __tablename__ = "departments"
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    name = Column(String(50), nullable=False)
    code = Column(String(20), unique=True, nullable=False)  # 科室代码
    description = Column(String(200))
    
    # 关联关系
    users = relationship("User", back_populates="department")
    action_groups = relationship("ActionGroup", back_populates="department")
    action_debug_groups = relationship("ActionsDebugGroup", back_populates="department")
    action_suit_groups = relationship("ActionsSuitGroup", back_populates="department")
    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name})>" 