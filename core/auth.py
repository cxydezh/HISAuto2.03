from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.user import User
from models.department import Department
from utils.crypto_utils import CryptoUtils
from utils.logs import log_manager

class AuthManager:
    """用户认证管理器"""
    
    def __init__(self, session: Session):
        """初始化认证管理器
        
        Args:
            session: 数据库会话
        """
        self.session = session
        self.max_login_attempts = 5
        self.login_attempts: Dict[str, int] = {}
    
    def register(self, user_id: str, username: str, department_id: int, 
                password: str, phone: str) -> Dict[str, Any]:
        """注册新用户
        
        Args:
            user_id: 用户ID
            username: 用户名
            department_id: 科室ID
            password: 密码
            phone: 电话
            
        Returns:
            Dict[str, Any]: 注册结果
        """
        # 验证用户ID长度
        if len(user_id) < 5:
            return {"success": False, "message": "用户ID至少需要5位"}
            
        # 验证密码长度
        if len(password) < 6:
            return {"success": False, "message": "密码至少需要6位"}
            
        # 检查用户ID是否已存在
        if self.session.query(User).filter_by(user_id=user_id).first():
            return {"success": False, "message": "用户ID已存在"}
            
        # 检查科室是否存在
        department = self.session.query(Department).filter_by(id=department_id).first()
        if not department:
            return {"success": False, "message": "科室不存在"}
            
        try:
            # 创建新用户
            hashed_password = CryptoUtils.hash_password(password)
            user = User(
                user_id=user_id,
                username=username,
                department_id=department_id,
                password=hashed_password,
                phone=phone,
                role="doctor",  # 默认角色为医生
                ai_capacity=100,  # 默认AI容量
                is_active=True
            )
            
            self.session.add(user)
            self.session.commit()
            
            log_manager.log_system("info", f"用户 {user_id} 注册成功")
            return {"success": True, "message": "注册成功"}
            
        except Exception as e:
            self.session.rollback()
            log_manager.log_system("error", f"用户注册失败: {str(e)}")
            return {"success": False, "message": "注册失败"}
    
    def login(self, user_id: str, password: str, ip: str) -> Dict[str, Any]:
        """用户登录
        
        Args:
            user_id: 用户ID
            password: 密码
            ip: 登录IP
            
        Returns:
            Dict[str, Any]: 登录结果
        """
        # 检查登录尝试次数
        if user_id in self.login_attempts and self.login_attempts[user_id] >= self.max_login_attempts:
            return {"success": False, "message": "登录失败次数过多，请稍后再试"}
            
        try:
            # 查找用户
            user = self.session.query(User).filter_by(user_id=user_id).first()
            if not user:
                self._increment_login_attempts(user_id)
                return {"success": False, "message": "用户不存在"}
                
            # 验证密码
            if not CryptoUtils.verify_password(password, user.password):
                self._increment_login_attempts(user_id)
                return {"success": False, "message": "密码错误"}
                
            # 检查用户状态
            if not user.is_active:
                return {"success": False, "message": "用户已被禁用"}
                
            # 更新登录信息
            user.last_login = datetime.now()
            user.last_ip = ip
            self.session.commit()
            
            # 重置登录尝试次数
            self.login_attempts[user_id] = 0
            
            log_manager.log_user_action(user.id, "login")
            return {
                "success": True,
                "message": "登录成功",
                "user": {
                    "id": user.id,
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role,
                    "department_id": user.department_id
                }
            }
            
        except Exception as e:
            self.session.rollback()
            log_manager.log_system("error", f"用户登录失败: {str(e)}")
            return {"success": False, "message": "登录失败"}
    
    def change_password(self, user_id: str, old_password: str, 
                       new_password: str) -> Dict[str, Any]:
        """修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            Dict[str, Any]: 修改结果
        """
        try:
            user = self.session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return {"success": False, "message": "用户不存在"}
                
            if not CryptoUtils.verify_password(old_password, user.password):
                return {"success": False, "message": "旧密码错误"}
                
            if len(new_password) < 6:
                return {"success": False, "message": "新密码至少需要6位"}
                
            user.password = CryptoUtils.hash_password(new_password)
            self.session.commit()
            
            log_manager.log_user_action(user.id, "change_password")
            return {"success": True, "message": "密码修改成功"}
            
        except Exception as e:
            self.session.rollback()
            log_manager.log_system("error", f"修改密码失败: {str(e)}")
            return {"success": False, "message": "修改密码失败"}
    
    def update_user_info(self, user_id: str, username: Optional[str] = None,
                        department_id: Optional[int] = None,
                        phone: Optional[str] = None) -> Dict[str, Any]:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            username: 新用户名
            department_id: 新科室ID
            phone: 新电话
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            user = self.session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return {"success": False, "message": "用户不存在"}
                
            if department_id:
                department = self.session.query(Department).filter_by(id=department_id).first()
                if not department:
                    return {"success": False, "message": "科室不存在"}
                    
            if username:
                user.username = username
            if department_id:
                user.department_id = department_id
            if phone:
                user.phone = phone
                
            self.session.commit()
            
            log_manager.log_user_action(user.id, "update_info")
            return {"success": True, "message": "用户信息更新成功"}
            
        except Exception as e:
            self.session.rollback()
            log_manager.log_system("error", f"更新用户信息失败: {str(e)}")
            return {"success": False, "message": "更新用户信息失败"}
    
    def _increment_login_attempts(self, user_id: str):
        """增加登录尝试次数
        
        Args:
            user_id: 用户ID
        """
        if user_id not in self.login_attempts:
            self.login_attempts[user_id] = 0
        self.login_attempts[user_id] += 1 