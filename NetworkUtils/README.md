# HISAuto_web - 住院部HIS Agent应用

## 项目简介

HISAuto_web是一款专为医院住院部设计的HIS（医院信息系统）Agent应用，采用现代化的Web技术栈构建，提供直观的用户界面和强大的AI辅助功能。

## 功能特性

### 🔐 安全登录系统
- 用户名/密码认证
- 会话管理
- 安全退出功能

### 🏥 患者管理
- 多科室患者列表
- 患者基本信息展示
- 实时数据更新

### 🤖 AI智能功能
- 智能诊断分析
- 治疗方案推荐
- 用药安全监测
- 预后评估
- 护理计划制定

### ⚙️ 系统设置
- 密码修改
- 用户偏好设置

## 技术架构

### 后端技术
- **Python 3.8+**
- **Flask** - Web框架
- **SQLite** - 数据库（当前使用硬编码数据）

### 前端技术
- **HTML5** - 页面结构
- **CSS3** - 样式设计
- **JavaScript** - 交互逻辑
- **响应式设计** - 适配多种设备

### 设计特点
- 现代化UI设计
- 流畅的动画效果
- 直观的用户体验
- 专业的医疗系统风格

## 安装和运行

### 环境要求
- Python 3.8 或更高版本
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd HISAuto_web1.0
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   ```

3. **激活虚拟环境**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **运行应用**
   ```bash
   python start.py
   ```

6. **访问应用**
   打开浏览器访问：`http://localhost:5001`

### 端口管理

如果遇到"端口5001已被占用"的错误，可以使用以下方法解决：

#### 方法1：自动清理（推荐）
启动脚本已包含自动端口清理功能，会自动尝试释放被占用的端口。

#### 方法2：手动清理
运行清理脚本：
```bash
python cleanup.py
```

#### 方法3：使用批处理文件（Windows用户）
双击运行以下文件：
- `start.bat` - 启动应用
- `cleanup.bat` - 清理端口占用

#### 方法4：手动命令
```bash
# 查看占用端口的进程
netstat -ano | findstr :5001

# 终止指定进程（替换<PID>为实际的进程ID）
taskkill /PID <PID> /F
```

### 登录信息
- **用户名**: admin
- **密码**: admin

## 项目结构

```
HISAuto_web1.0/
├── app.py                 # Flask应用主文件
├── data_display.py        # 数据管理模块
├── requirements.txt       # Python依赖
├── README.md             # 项目说明
├── templates/            # HTML模板
│   ├── login.html        # 登录页面
│   └── dashboard.html    # 主工作台页面
└── static/              # 静态资源
    ├── css/             # 样式文件
    │   ├── login.css    # 登录页面样式
    │   └── dashboard.css # 工作台样式
    ├── js/              # JavaScript文件
    │   ├── login.js     # 登录页面脚本
    │   └── dashboard.js # 工作台脚本
    ├── icons/           # 图标文件
    └── fonts/           # 字体文件
```

## 功能模块说明

### 1. 登录模块
- 用户身份验证
- 表单验证
- 错误提示
- 安全会话管理

### 2. 工作台模块
- **左侧面板**：患者列表管理
  - Excel文件更新
  - 科室选择
  - 患者列表显示

- **右侧面板**：信息展示和AI功能
  - 基本信息：患者详细信息
  - AI功能区：AI功能选择和配置
  - AI结果区：运行结果和进度监控

### 3. 设置模块
- 密码修改功能
- 系统配置选项

## AI功能说明

### 智能诊断
基于患者症状和检查结果进行智能诊断分析，包含数据预处理、症状分析、检查结果解读、诊断推理和报告生成等步骤。

### 治疗方案推荐
根据诊断结果推荐个性化治疗方案，包括诊断结果分析、治疗方案匹配、风险评估、个性化调整和治疗建议生成。

### 用药安全监测
监测患者用药安全性和药物相互作用，包括用药清单分析、药物相互作用检查、剂量合理性评估、不良反应预测和安全建议生成。

### 预后评估
评估患者疾病预后和康复情况，包括病情严重程度评估、治疗效果分析、并发症风险评估、康复时间预测和预后报告生成。

### 护理计划制定
制定个性化的护理计划和注意事项，包括护理需求评估、护理风险识别、护理措施制定、护理效果评估和护理计划生成。

## 开发说明

### 数据管理
当前版本使用硬编码的示例数据，所有数据存储在 `data_display.py` 文件中，包括：
- 科室信息
- 患者数据
- AI功能配置

### API接口
应用提供以下RESTful API接口：
- `GET /api/departments` - 获取科室列表
- `GET /api/patients/<department>` - 获取指定科室的患者列表
- `GET /api/patient/<patient_id>` - 获取患者详细信息
- `GET /api/ai-functions` - 获取AI功能列表
- `GET /api/ai-workflow/<function_name>` - 获取AI功能工作流程
- `POST /api/run-ai` - 运行AI功能

### 扩展开发
- 数据库集成：可替换硬编码数据为SQLite或其他数据库
- TCP传输：可添加TCP通信功能
- 更多AI功能：可扩展AI功能模块
- 用户管理：可添加用户注册、权限管理等功能

## 浏览器兼容性

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 许可证

本项目仅供学习和演示使用。

## 联系方式

如有问题或建议，请联系开发团队。

---

**HISAuto_web** - 让医疗管理更智能、更高效！ 