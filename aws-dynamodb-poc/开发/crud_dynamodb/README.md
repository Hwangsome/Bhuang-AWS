# DynamoDB CRUD Operations

这个项目提供了一个简单的Python类来执行DynamoDB的CRUD（创建、读取、更新、删除）操作。

## 前提条件

- Python 3.7 或更高版本
- 已配置AWS凭证（通过AWS CLI或环境变量）
- 已存在的DynamoDB表

## 安装

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置AWS凭证，可以通过以下方式之一:
   - 使用AWS CLI: `aws configure`
   - 设置环境变量:
     ```
     AWS_ACCESS_KEY_ID=你的访问密钥
     AWS_SECRET_ACCESS_KEY=你的秘密密钥
     AWS_DEFAULT_REGION=你的区域
     ```
   - 创建`.env`文件并包含相同的变量

## 使用方法

### 初始化

```python
from dynamodb_crud import DynamoDBCRUD

# 使用你的表名初始化
crud = DynamoDBCRUD('你的表名')
```

### 创建项目

```python
item = {
    'id': '1',
    'name': '张三',
    'email': 'zhangsan@example.com'
}
result = crud.create_item(item)
```

### 读取项目

```python
result = crud.read_item({'id': '1'})
```

### 更新项目

```python
update_result = crud.update_item(
    key={'id': '1'},
    update_expression="SET #n = :new_name",
    expression_values={':new_name': '李四'}
)
```

### 删除项目

```python
delete_result = crud.delete_item({'id': '1'})
```

### 扫描表

```python
# 扫描整个表
scan_result = crud.scan_table()

# 使用过滤器扫描
filter_result = crud.scan_table(
    filter_expression="age > :min_age",
    expression_values={':min_age': 25}
)
```

## 错误处理

所有方法都返回一个包含以下内容的字典:
- `success`: 布尔值，表示操作是否成功
- `message`: 如果操作失败，包含错误信息
- 其他特定于操作的数据（例如，检索到的项目、更新结果等）

## 示例

完整的示例代码可以在 `dynamodb_crud.py` 文件的 `main()` 函数中找到。运行示例:

```bash
python dynamodb_crud.py
```

## 注意事项

1. 确保你有适当的AWS权限来执行这些操作
2. 在生产环境中使用前，请确保正确处理错误和异常
3. 考虑实现重试机制以处理临时性故障
4. 对于大型表，考虑使用分页来处理scan操作
