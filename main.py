import os
import sys
import globalvariable
# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
import tkinter as tk
from config.config_manager import ConfigManager
from utils.logger import Logger,logger
from database.db_manager import DatabaseManager



def initialize_system():
    """初始化系统"""
    # 获取配置管理器实例
    config_manager = ConfigManager()
    
    # 设置日志
    logger.info("系统初始化开始")

    
    try:
        # 创建必要的目录
        sys_folder = config_manager.get_value('System', 'SysFolder', 'D:/HISAuto/')
        required_dirs = [
            os.path.join(sys_folder, 'DataSource'),
            os.path.join(sys_folder, 'PatientsSource'),
            os.path.join(sys_folder, 'ActionsGroup'),
            os.path.join(sys_folder, 'ActionsDebugGroup'),
            os.path.join(sys_folder, 'LongTxt'),
            os.path.join(sys_folder, 'outputTxt'),
            os.path.join(sys_folder, 'function'),
            os.path.join(sys_folder, 'logs')
        ]
        
        for directory in required_dirs:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"创建目录: {directory}")
            
        # 初始化数据库
        db_path = config_manager.get_value('System', 'DataSource')
        encryption_key = config_manager.get_value('Security', 'DBEncryptionKey')
        
        if not encryption_key:
            raise ValueError("未找到数据库加密密钥配置")
            
        logger.info("正在初始化数据库...")
        db_manager = DatabaseManager(
            db_path=db_path,
            encryption_key=encryption_key
        )
        db_manager.initialize()
        
        # 验证数据库加密
        logger.info("正在验证数据库加密...")
        if not db_manager.verify_encryption():
            raise Exception("数据库加密验证失败，请检查加密密钥是否正确")
            
        db_manager.create_tables()
        logger.info("数据库初始化完成")
        
        logger.info("系统初始化完成")
        return config_manager, logger, db_manager
        
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        raise
    finally:
        #  确保在程序退出时释放数据库资源
        del db_manager
        db_manager = None
def handle_login(username: str, password: str):
    """处理登录事件"""
    # TODO: 实现实际的登录验证逻辑
    # 这里暂时使用一个简单的验证
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.user import User
    from models.department import Department
    from config.config_manager import ConfigManager
    config = ConfigManager()
    db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    if user:
        if user.password == password:
            globalvariable.USER_NAME = user.username
            globalvariable.USER_ID = user.user_id
            globalvariable.USER_DEPARTMENT_ID = user.department_id
            globalvariable.USER_DEPARTMENT = session.query(Department).filter_by(code=globalvariable.USER_DEPARTMENT_ID).first().name
            if user.role == "system_admin":
                globalvariable.USER_IS_ADMIN = True
            else:
                globalvariable.USER_IS_ADMIN = False
            if user.username == "admin":
                globalvariable.USER_IS_SUPER_ADMIN = True
            else:
                globalvariable.USER_IS_SUPER_ADMIN = False
            session.close()
            return True, globalvariable.USER_IS_SUPER_ADMIN
        else:
            return False, False
    else:
        return False, False
    #if username == "admin" and password == "admin":
    #    return True, True  # 返回 (登录成功, 是否为超级管理员)
    #elif username == "user" and password == "user":
    #    return True, False  # 返回 (登录成功, 是否为超级管理员)
    #else:
    #    raise Exception("用户名或密码错误")
def main():
    """主程序入口"""
    try:
        # 初始化系统
        config_manager, logger, db_manager = initialize_system()
        
        # 创建登录窗口
        from gui import LoginWindow
        login_window = LoginWindow(handle_login)
        
        # 显示登录窗口
        login_window.show()
        
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"原因: {str(e.__cause__)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 