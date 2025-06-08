# HISAuto - 医院智能自动化办公系统

## 项目简介
HISAuto是一个为医院住院部医生开发的智能自动化办公系统。该系统可以实现鼠标键盘行为录制、自动化任务执行、OCR文字识别、AI辅助等功能。

## 主要功能
1. 鼠标键盘行为录制与回放
2. 自动化任务执行
3. 屏幕截图与OCR文字识别
4. AI辅助功能
5. 局域网通信功能

## 系统要求
- Python 3.8+
- Windows 10/11

## 安装说明
1. 克隆项目到本地
2. 创建虚拟环境：`python -m venv .venv`
3. 激活虚拟环境：
   - Windows: `.venv\Scripts\activate`
4. 安装依赖：`pip install -r requirements.txt`

## 配置说明
系统配置文件位于 `config/HISAutoConfiguration.cfg`，首次运行时会自动创建。

## 使用说明
1. 运行主程序：`python main.py`
2. 使用默认账号登录：
   - 用户名：admin
   - 密码：admin123

## 开发说明
项目采用MVC架构，主要模块包括：
- config: 配置管理
- database: 数据库操作
- models: 数据模型
- utils: 工具类
- logs: 日志管理

## 许可证
本项目采用 MIT 许可证 