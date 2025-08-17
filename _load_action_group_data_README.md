# _load_action_group_data 函数说明

## 功能概述

`_load_action_group_data` 函数是一个用于为Treeview控件填充树形结构数据的通用函数。该函数可以根据不同的数据源类型，自动加载相应的数据并构建层次化的树形结构。

## 函数签名

```python
@classmethod
def _load_action_group_data(cls, workTreeview, treeDatatxt):
```

## 参数说明

### workTreeview
- **类型**: tkinter.ttk.Treeview
- **说明**: 要填充数据的Treeview控件
- **必需**: 是

### treeDatatxt
- **类型**: str
- **说明**: 数据源类型标识符，用于确定要加载的数据类型
- **必需**: 是
- **可选值**:
  - `"ActionList"` - 行为列表数据
  - `"ActionsGroupHierarchy"` - 行为组层级数据
  - `"ActionSuitList"` - 行为套件列表数据
  - `"ActionsSuitGroupHierarchy"` - 行为套件组层级数据
  - `"ActionDebugList"` - 调试行为列表数据
  - `"ActionsDebugGroupHierarchy"` - 调试行为组层级数据

## 返回值

- **类型**: bool
- **说明**: 
  - `True` - 数据加载成功
  - `False` - 数据加载失败

## 功能特性

### 1. 智能数据分组
函数会根据不同的数据源类型，自动选择合适的分组字段：
- **列表类型** (`ActionList`, `ActionSuitList`, `ActionDebugList`): 使用 `list_rank` 字段进行分组
- **层级类型** (`ActionsGroupHierarchy`, `ActionsSuitGroupHierarchy`, `ActionsDebugGroupHierarchy`): 使用 `group_rank` 字段进行分组

### 2. 自动排序
- **列表类型**: 按 `action_sort_num` 字段排序
- **层级类型**: 按 `sort_num` 字段排序

### 3. 层次化结构
函数支持最多5级的层次结构，使用 `A_B_C_D_E_` 格式的命名规则：
- **A级别**: 代表总体分层（个人、科室、全局）
- **B-E级别**: 代表具体的层级编号

### 4. 智能图标显示
- **📁**: 表示组/文件夹类型
- **📄**: 表示文件/动作类型

## 使用示例

### 基本用法

```python
from utils.hometab_funcdata import hometab_funcData
import tkinter as tk
from tkinter import ttk

# 创建Treeview控件
root = tk.Tk()
tree = ttk.Treeview(root)

# 加载ActionList数据
result = hometab_funcData._load_action_group_data(tree, "ActionList")

# 加载ActionsGroupHierarchy数据
result = hometab_funcData._load_action_group_data(tree, "ActionsGroupHierarchy")
```

### 在GUI应用中使用

```python
class MyApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.tree = ttk.Treeview(self.root)
        self.tree.pack()
        
        # 创建菜单或按钮来切换不同的数据源
        self.create_controls()
    
    def create_controls(self):
        # 创建按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack()
        
        # 创建不同的数据加载按钮
        ttk.Button(button_frame, text="加载行为列表", 
                  command=lambda: self.load_data("ActionList")).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="加载行为组层级", 
                  command=lambda: self.load_data("ActionsGroupHierarchy")).pack(side=tk.LEFT)
    
    def load_data(self, data_type):
        """加载指定类型的数据"""
        result = hometab_funcData._load_action_group_data(self.tree, data_type)
        if result:
            print(f"{data_type} 数据加载成功")
        else:
            print(f"{data_type} 数据加载失败")
```

## 数据字段映射

### ActionList/ActionSuitList/ActionDebugList
- **iid**: `list_rank` 字段解析后的值
- **text**: 根据 `action_type` 显示 📁 或 📄
- **values**: (`action_name`, `action_note`, `id`)

### ActionsGroupHierarchy/ActionsSuitGroupHierarchy/ActionsDebugGroupHierarchy
- **iid**: `group_rank` 字段解析后的值
- **text**: 根据 `group_type` 显示 📁 或 📄
- **values**: (`group_name`, `group_note`, `id`)

## 注意事项

1. **数据库连接**: 函数会自动管理数据库会话，无需手动处理
2. **错误处理**: 函数包含完整的异常处理，失败时会记录日志
3. **内存管理**: 函数会自动清理数据库会话，避免内存泄漏
4. **树控件清理**: 每次调用函数时会自动清空树控件，然后重新填充数据

## 依赖项

- `tkinter.ttk.Treeview` - GUI树控件
- `parse_group_rank` 函数 - 用于解析rank字段
- 相应的ORM模型类 - 用于数据库查询
- 数据库连接管理器 - 用于获取数据库会话

## 测试

可以使用提供的测试脚本 `test_load_action_group_data.py` 来验证函数功能：

```bash
python test_load_action_group_data.py
```

测试脚本会创建一个GUI界面，允许您测试不同的数据加载功能。
