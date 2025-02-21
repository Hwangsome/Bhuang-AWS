import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
import os
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime
import json
from typing import Dict, List, Optional, Union
import uuid

# Load environment variables
load_dotenv()

class DynamoDBCRUD:
    def __init__(self, table_name, endpoint_url='http://localhost:8000'):
        """
        Initialize DynamoDB client and table
        """
        try:
            self.dynamodb = boto3.resource('dynamodb',
                endpoint_url=endpoint_url,
                region_name='us-west-2',
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy'
            )
            self.table_name = table_name
            self.table = self.dynamodb.Table(table_name)
            print(f"Successfully connected to local DynamoDB at {endpoint_url}")
        except Exception as e:
            print(f"Error initializing DynamoDB client: {str(e)}")
            raise

    def create_table(self) -> Dict:
        """
        创建DynamoDB表，包含全局二级索引(GSI)和本地二级索引(LSI)
        """
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'propertyId',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'restrictionId',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'propertyId',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'restrictionId',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'stayDate',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'sellState',
                        'AttributeType': 'N'
                    },
                    {
                        'AttributeName': 'updateDate',
                        'AttributeType': 'S'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'StayDateIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'stayDate',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 10,
                            'WriteCapacityUnits': 10
                        }
                    },
                    {
                        'IndexName': 'SellStateIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'sellState',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 10,
                            'WriteCapacityUnits': 10
                        }
                    }
                ],
                LocalSecondaryIndexes=[
                    {
                        'IndexName': 'PropertyUpdateDateIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'propertyId',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'updateDate',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            
            return {
                'success': True,
                'message': f"表 '{self.table_name}' 创建成功"
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f"创建表时出错: {str(e)}"
            }

    def describe_table_indexes(self) -> Dict:
        """
        获取表的索引信息
        """
        try:
            table = self.dynamodb.Table(self.table_name)
            response = table.meta.client.describe_table(
                TableName=self.table_name
            )
            
            table_desc = response['Table']
            indexes_info = {
                'table_name': self.table_name,
                'primary_key': [k['AttributeName'] for k in table_desc['KeySchema']],
                'gsi': [],
                'lsi': []
            }
            
            # 获取GSI信息
            if 'GlobalSecondaryIndexes' in table_desc:
                for gsi in table_desc['GlobalSecondaryIndexes']:
                    indexes_info['gsi'].append({
                        'name': gsi['IndexName'],
                        'key_schema': [k['AttributeName'] for k in gsi['KeySchema']],
                        'projection_type': gsi['Projection']['ProjectionType']
                    })
            
            # 获取LSI信息
            if 'LocalSecondaryIndexes' in table_desc:
                for lsi in table_desc['LocalSecondaryIndexes']:
                    indexes_info['lsi'].append({
                        'name': lsi['IndexName'],
                        'key_schema': [k['AttributeName'] for k in lsi['KeySchema']],
                        'projection_type': lsi['Projection']['ProjectionType']
                    })
            
            return {
                'success': True,
                'message': '获取索引信息成功',
                'data': indexes_info
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f"获取表索引信息时出错: {str(e)}"
            }

    def create_item(self, item: Dict, transaction_id: Optional[str] = None) -> Dict:
        """
        创建新记录，支持事务日志
        """
        try:
            # 添加版本控制和审计字段
            item['versionId'] = item.get('versionId', 1)
            item['createdAt'] = datetime.now().isoformat()
            item['updatedAt'] = item['createdAt']
            
            # 如果提供了事务ID，添加到记录中
            if transaction_id:
                item['transactionId'] = transaction_id

            # 创建变更日志
            change_log = {
                'changeId': str(uuid.uuid4()),
                'tableName': self.table_name,
                'operationType': 'CREATE',
                'itemKey': {
                    'propertyId': item['propertyId'],
                    'restrictionId': item['restrictionId']
                },
                'newValue': item,
                'timestamp': item['createdAt'],
                'transactionId': transaction_id
            }

            # 使用事务写入主记录和变更日志
            with self.table.batch_writer() as batch:
                batch.put_item(Item=item)
                # 如果有单独的日志表，这里应该写入日志表
                # self.log_table.put_item(Item=change_log)

            return {'success': True, 'message': '记录创建成功', 'data': item}
        except ClientError as e:
            return {'success': False, 'message': f'创建记录失败: {str(e)}'}

    def get_item(self, key: Dict) -> Dict:
        """
        获取单个记录
        """
        try:
            response = self.table.get_item(Key=key)
            if 'Item' in response:
                return {'success': True, 'data': response['Item']}
            return {'success': False, 'message': '记录不存在'}
        except ClientError as e:
            return {'success': False, 'message': str(e)}

    def query_by_stay_date(self, stay_date: str, last_evaluated_key: Optional[Dict] = None, limit: int = 20) -> Dict:
        """
        按入住日期查询，支持分页
        """
        try:
            params = {
                'IndexName': 'StayDateIndex',
                'KeyConditionExpression': '#stay_date = :stay_date',
                'ExpressionAttributeNames': {
                    '#stay_date': 'stayDate'
                },
                'ExpressionAttributeValues': {
                    ':stay_date': stay_date
                },
                'Limit': limit
            }
            
            if last_evaluated_key:
                params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table.query(**params)
            
            result = {
                'success': True,
                'data': response['Items'],
                'count': response['Count']
            }
            
            if 'LastEvaluatedKey' in response:
                result['lastEvaluatedKey'] = response['LastEvaluatedKey']
            
            return result
        except ClientError as e:
            return {'success': False, 'message': str(e)}

    def query_by_sell_state(self, sell_state: int, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, limit: int = 20) -> Dict:
        """
        按销售状态查询，支持日期范围
        """
        try:
            key_condition = '#sell_state = :sell_state'
            expr_attr_names = {'#sell_state': 'sellState'}
            expr_attr_values = {':sell_state': sell_state}

            if start_date and end_date:
                key_condition += ' AND #stay_date BETWEEN :start_date AND :end_date'
                expr_attr_names['#stay_date'] = 'stayDate'
                expr_attr_values[':start_date'] = start_date
                expr_attr_values[':end_date'] = end_date

            response = self.table.query(
                IndexName='SellStateIndex',
                KeyConditionExpression=key_condition,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values,
                Limit=limit
            )

            return {
                'success': True,
                'data': response['Items'],
                'count': response['Count']
            }
        except ClientError as e:
            return {'success': False, 'message': str(e)}

    def update_item(self, key: Dict, update_data: Dict, transaction_id: Optional[str] = None) -> Dict:
        """
        更新记录，支持事务和版本控制
        """
        try:
            # 首先获取当前记录
            current_item = self.get_item(key)
            if not current_item['success']:
                return current_item

            # 准备更新表达式
            update_expr = 'SET '
            expr_attr_names = {}
            expr_attr_values = {}
            
            for field, value in update_data.items():
                update_expr += f'#{field} = :{field}, '
                expr_attr_names[f'#{field}'] = field
                expr_attr_values[f':{field}'] = value

            # 添加审计字段
            update_expr += '#updatedAt = :updatedAt, #versionId = :newVersion'
            expr_attr_names['#updatedAt'] = 'updatedAt'
            expr_attr_names['#versionId'] = 'versionId'
            expr_attr_values[':updatedAt'] = datetime.now().isoformat()
            expr_attr_values[':newVersion'] = current_item['data']['versionId'] + 1
            expr_attr_values[':currentVersion'] = current_item['data']['versionId']

            # 使用条件表达式确保版本号匹配
            condition_expr = '#versionId = :currentVersion'

            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expr.rstrip(', '),
                ConditionExpression=condition_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues='ALL_NEW'
            )

            return {'success': True, 'message': '更新成功', 'data': response['Attributes']}
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return {'success': False, 'message': '版本冲突，请重试'}
            return {'success': False, 'message': str(e)}

    def delete_item(self, key: Dict, transaction_id: Optional[str] = None) -> Dict:
        """
        删除记录，支持软删除
        """
        try:
            # 获取当前记录用于日志
            current_item = self.get_item(key)
            if not current_item['success']:
                return current_item

            # 软删除：更新状态而不是真正删除
            update_expr = 'SET #status = :deleted, #updatedAt = :updatedAt'
            expr_attr_names = {
                '#status': 'status',
                '#updatedAt': 'updatedAt'
            }
            expr_attr_values = {
                ':deleted': 'DELETED',
                ':updatedAt': datetime.now().isoformat()
            }

            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues='ALL_NEW'
            )

            return {'success': True, 'message': '记录已删除', 'data': response['Attributes']}
        except ClientError as e:
            return {'success': False, 'message': str(e)}

    def batch_create_items(self, items: List[Dict], transaction_id: Optional[str] = None) -> Dict:
        """
        批量创建记录
        """
        try:
            success_items = []
            failed_items = []
            
            # DynamoDB batch_writer 自动处理重试和分批
            with self.table.batch_writer() as batch:
                for item in items:
                    try:
                        # 添加审计字段
                        item['versionId'] = item.get('versionId', 1)
                        item['createdAt'] = datetime.now().isoformat()
                        item['updatedAt'] = item['createdAt']
                        if transaction_id:
                            item['transactionId'] = transaction_id
                        
                        batch.put_item(Item=item)
                        success_items.append(item)
                    except Exception as e:
                        failed_items.append({
                            'item': item,
                            'error': str(e)
                        })

            return {
                'success': len(failed_items) == 0,
                'message': f'成功添加 {len(success_items)} 条记录，失败 {len(failed_items)} 条',
                'successItems': success_items,
                'failedItems': failed_items
            }
        except Exception as e:
            return {'success': False, 'message': f'批量创建失败: {str(e)}'}

    def query_by_date_range(self, start_date: str, end_date: str, 
                          sell_state: Optional[int] = None,
                          last_evaluated_key: Optional[Dict] = None,
                          limit: int = 20) -> Dict:
        """
        按日期范围查询，可选择性过滤销售状态
        """
        try:
            # 基础查询条件
            key_condition = '#stay_date BETWEEN :start_date AND :end_date'
            expr_attr_names = {'#stay_date': 'stayDate'}
            expr_attr_values = {
                ':start_date': start_date,
                ':end_date': end_date
            }

            # 如果指定了销售状态，添加过滤条件
            filter_expression = None
            if sell_state is not None:
                filter_expression = '#sell_state = :sell_state'
                expr_attr_names['#sell_state'] = 'sellState'
                expr_attr_values[':sell_state'] = sell_state

            params = {
                'IndexName': 'StayDateIndex',
                'KeyConditionExpression': key_condition,
                'ExpressionAttributeNames': expr_attr_names,
                'ExpressionAttributeValues': expr_attr_values,
                'Limit': limit
            }

            if filter_expression:
                params['FilterExpression'] = filter_expression
            
            if last_evaluated_key:
                params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table.query(**params)
            
            result = {
                'success': True,
                'data': response['Items'],
                'count': response['Count']
            }
            
            if 'LastEvaluatedKey' in response:
                result['lastEvaluatedKey'] = response['LastEvaluatedKey']
            
            return result
        except ClientError as e:
            return {'success': False, 'message': str(e)}

    def batch_update_items(self, items: List[Dict], transaction_id: Optional[str] = None) -> Dict:
        """
        批量更新记录，支持版本控制
        """
        try:
            success_items = []
            failed_items = []
            
            for item in items:
                try:
                    key = {
                        'propertyId': item['propertyId'],
                        'restrictionId': item['restrictionId']
                    }
                    update_data = {k: v for k, v in item.items() 
                                 if k not in ['propertyId', 'restrictionId']}
                    
                    result = self.update_item(key, update_data, transaction_id)
                    if result['success']:
                        success_items.append(result['data'])
                    else:
                        failed_items.append({
                            'item': item,
                            'error': result['message']
                        })
                except Exception as e:
                    failed_items.append({
                        'item': item,
                        'error': str(e)
                    })

            return {
                'success': len(failed_items) == 0,
                'message': f'成功更新 {len(success_items)} 条记录，失败 {len(failed_items)} 条',
                'successItems': success_items,
                'failedItems': failed_items
            }
        except Exception as e:
            return {'success': False, 'message': f'批量更新失败: {str(e)}'}

    def get_items_by_property_id(self, property_id: str) -> Dict:
        """
        获取指定propertyId的所有数据
        """
        try:
            response = self.table.query(
                KeyConditionExpression='propertyId = :pid',
                ExpressionAttributeValues={
                    ':pid': property_id
                }
            )
            
            if 'Items' in response:
                # 将Decimal类型转换为int或float
                items = []
                for item in response['Items']:
                    formatted_item = {}
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            # 如果是整数，转换为int，否则转换为float
                            formatted_item[key] = int(value) if value % 1 == 0 else float(value)
                        else:
                            formatted_item[key] = value
                    items.append(formatted_item)
                
                return {
                    'success': True,
                    'message': f'找到 {len(items)} 条记录',
                    'items': items
                }
            else:
                return {
                    'success': False,
                    'message': '未找到数据'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'查询失败: {str(e)}'
            }

    def test_empty_string_behavior(self) -> Dict:
        """
        测试向DynamoDB插入空字符串的行为
        注意：DynamoDB 不允许在索引键（包括GSI和LSI）中使用空字符串
        """
        try:
            # 创建包含空字符串的测试数据，但避免在索引键中使用空字符串
            test_items = [
                {
                    "propertyId": "266270522",
                    "restrictionId": "empty_test_1",
                    "stayDate": "2025-02-21",  # 索引键不能为空
                    "sellState": 1,            # 索引键不能为空
                    "cutOffDays": None,        # 测试 None 值
                    "advancePurchaseMin": "",  # 测试空字符串
                    "advancePurchaseMax": 1,
                    "closedToArrival": "",     # 测试空字符串
                    "closedToDeparture": None, # 测试 None 值
                    "fullPartnerLosArrival": 268435455,
                    "fullPartnerLosStayThrough": "",  # 测试空字符串
                    "doaCostPriceChangeBool": 1,
                    "versionId": "",           # 测试空字符串
                    "updateTpId": None,        # 测试 None 值
                    "updateTuId": "",          # 测试空字符串
                    "updateDate": "2025-02-21",  # 索引键不能为空
                    "changeRequestSourceId": None, # 测试 None 值
                    "availabilityLevel": ""      # 测试空字符串
                }
            ]

            results = []
            # 插入测试数据
            for item in test_items:
                result = self.create_item(item)
                results.append(result)
                print(f"\n插入数据结果: {result['message']}")

            # 查询并验证插入的数据
            for item in test_items:
                response = self.table.get_item(
                    Key={
                        'propertyId': item['propertyId'],
                        'restrictionId': item['restrictionId']
                    }
                )
                if 'Item' in response:
                    print(f"\n成功检索到数据 {item['restrictionId']}:")
                    retrieved_item = response['Item']
                    print("\n空值字段的实际存储情况:")
                    test_fields = [
                        'cutOffDays',           # None 值
                        'advancePurchaseMin',   # 空字符串
                        'closedToArrival',      # 空字符串
                        'closedToDeparture',    # None 值
                        'fullPartnerLosStayThrough',  # 空字符串
                        'versionId',            # 空字符串
                        'updateTpId',           # None 值
                        'updateTuId',           # 空字符串
                        'changeRequestSourceId', # None 值
                        'availabilityLevel'     # 空字符串
                    ]
                    for key in test_fields:
                        if key in retrieved_item:
                            value = retrieved_item[key]
                            print(f"- {key}: '{value}' (类型: {type(value).__name__})")
                        else:
                            print(f"- {key}: 字段不存在")
                else:
                    print(f"\n未找到数据 {item['restrictionId']}")

            return {
                'success': True,
                'message': '空字符串测试完成',
                'results': results
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'测试空字符串时出错: {str(e)}'
            }

def main():
    try:
        # 初始化 DynamoDB 客户端
        table_name = "PropertyRestrictions"
        crud = DynamoDBCRUD(table_name)

        # 列出所有表
        tables = list(crud.dynamodb.tables.all())
        print("\n现有的表:")
        for table in tables:
            print(f"- {table.name}")

        # 测试表是否存在并创建（如果需要）
        try:
            crud.table.table_status
            print(f"\n表 '{table_name}' 存在且可访问!")
            print(f"表状态: {crud.table.table_status}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"\n表 '{table_name}' 不存在。正在创建表...")
                result = crud.create_table()
                print(result['message'])
                if not result['success']:
                    return
                
                # 等待表变为活动状态
                print("等待表变为活动状态...")
                waiter = crud.dynamodb.meta.client.get_waiter('table_exists')
                waiter.wait(TableName=table_name)
                print("表现在处于活动状态")
            else:
                print(f"\n访问表时出错: {str(e)}")
                return

        # 测试空字符串行为
        print("\n开始测试空字符串行为:")
        empty_string_test = crud.test_empty_string_behavior()
        if not empty_string_test['success']:
            print(empty_string_test['message'])

        # 查询指定propertyId的数据
        print("\n查询propertyId为266270522的数据:")
        result = crud.get_items_by_property_id("266270522")
        if result['success']:
            print(json.dumps(result['items'], indent=2, ensure_ascii=False))
        else:
            print(result['message'])

    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
