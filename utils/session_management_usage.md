# Session 管理功能使用指南

## 问题背景

在数据库表结构更新后，现有的 SQLAlchemy session 可能不会自动感知到这些变化，导致使用过期的元数据。

## 解决方案

### 1. 修改后的 `_get_session()` 方法

```python
def _get_session(self, force_refresh=False):
    """获取数据库会话
    
    Args:
        force_refresh: 是否强制刷新session，用于数据库表结构更新后重新创建session
        
    Returns:
        session: 数据库会话对象，失败时返回None
    """
```

### 2. 新增的方法

#### `refresh_session()`
强制刷新数据库会话
```python
# 使用示例
action_group_manager = ActionGroupManager(home_tab)
if action_group_manager.refresh_session():
    print("Session refreshed successfully")
else:
    print("Failed to refresh session")
```

#### `is_session_valid()`
检查当前 session 是否有效
```python
# 使用示例
if not action_group_manager.is_session_valid():
    print("Session is invalid, refreshing...")
    action_group_manager.refresh_session()
```

#### `handle_database_schema_update()`
处理数据库表结构更新后的操作
```python
# 使用示例
if action_group_manager.handle_database_schema_update():
    print("Database schema update handled successfully")
else:
    print("Failed to handle database schema update")
```

## 使用场景

### 场景1：数据库表结构更新后
```python
# 当数据库表结构发生变化时
action_group_manager = ActionGroupManager(home_tab)

# 方法1：直接刷新session
action_group_manager.refresh_session()

# 方法2：使用专门的更新处理方法
action_group_manager.handle_database_schema_update()
```

### 场景2：定期检查session有效性
```python
# 在关键操作前检查session有效性
def perform_critical_operation():
    if not action_group_manager.is_session_valid():
        action_group_manager.refresh_session()
    
    # 执行关键操作
    result = action_group_manager.get_action_group_data(group_id)
    return result
```

### 场景3：异常处理中的自动恢复
```python
# 在异常处理中自动刷新session
try:
    data = action_group_manager.get_action_group_data(group_id)
except Exception as e:
    if "session" in str(e).lower() or "connection" in str(e).lower():
        action_group_manager.refresh_session()
        # 重试操作
        data = action_group_manager.get_action_group_data(group_id)
```

## 最佳实践

1. **在数据库表结构更新后立即调用** `refresh_session()` 或 `handle_database_schema_update()`

2. **在关键操作前检查session有效性**，特别是在长时间运行的应用中

3. **在异常处理中识别session相关错误**，并自动刷新session

4. **定期监控session状态**，特别是在多用户环境中

5. **在应用启动时验证session**，确保初始状态正确

## 注意事项

1. 刷新session会关闭现有连接，确保没有未提交的事务
2. 刷新后需要重新验证session有效性
3. 在并发环境中要注意session的线程安全性
4. 建议在日志中记录session刷新操作，便于调试 