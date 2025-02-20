import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
import os
from dotenv import load_dotenv
from decimal import Decimal

# Load environment variables
load_dotenv()

class DynamoDBCRUD:
    def __init__(self, table_name, endpoint_url='http://localhost:8000'):
        """
        Initialize DynamoDB client and table
        Args:
            table_name (str): The name of the DynamoDB table
            endpoint_url (str): DynamoDB endpoint URL (default: http://localhost:8000)
        """
        try:
            self.dynamodb = boto3.resource('dynamodb',
                endpoint_url=endpoint_url,
                region_name='us-west-2',  # 本地运行时这个值可以是任意的
                aws_access_key_id='dummy',  # 本地运行时使用虚拟凭证
                aws_secret_access_key='dummy'
            )
            self.table = self.dynamodb.Table(table_name)
            print(f"Successfully connected to local DynamoDB at {endpoint_url}")
        except EndpointConnectionError as e:
            print(f"Error connecting to local DynamoDB: {str(e)}")
            print("Please make sure your local DynamoDB is running")
            raise
        except Exception as e:
            print(f"Error initializing DynamoDB client: {str(e)}")
            raise

    def create_item(self, item):
        """
        Create a new item in the DynamoDB table
        """
        try:
            response = self.table.put_item(Item=item)
            return {
                'success': True,
                'message': 'Item created successfully',
                'response': response
            }
        except ClientError as e:
            return {
                'success': False,
                'message': f'Error creating item: {str(e)}'
            }

    def read_item(self, key):
        """
        Read an item from the DynamoDB table using its primary key
        """
        try:
            response = self.table.get_item(Key=key)
            item = response.get('Item')
            if item:
                return {
                    'success': True,
                    'item': item
                }
            return {
                'success': False,
                'message': 'Item not found'
            }
        except ClientError as e:
            return {
                'success': False,
                'message': f'Error reading item: {str(e)}'
            }

    def update_item(self, key, update_expression, expression_values):
        """
        Update an item in the DynamoDB table
        """
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="UPDATED_NEW"
            )
            return {
                'success': True,
                'message': 'Item updated successfully',
                'updated_attributes': response.get('Attributes')
            }
        except ClientError as e:
            return {
                'success': False,
                'message': f'Error updating item: {str(e)}'
            }

    def delete_item(self, key):
        """
        Delete an item from the DynamoDB table
        """
        try:
            response = self.table.delete_item(Key=key)
            return {
                'success': True,
                'message': 'Item deleted successfully',
                'response': response
            }
        except ClientError as e:
            return {
                'success': False,
                'message': f'Error deleting item: {str(e)}'
            }

    def scan_table(self, filter_expression=None, expression_values=None):
        """
        Scan the entire table, optionally with a filter
        """
        try:
            if filter_expression and expression_values:
                response = self.table.scan(
                    FilterExpression=filter_expression,
                    ExpressionAttributeValues=expression_values
                )
            else:
                response = self.table.scan()
            
            return {
                'success': True,
                'items': response.get('Items', []),
                'count': response.get('Count', 0)
            }
        except ClientError as e:
            return {
                'success': False,
                'message': f'Error scanning table: {str(e)}'
            }

    def create_table(self, key_schema, attribute_definitions, provisioned_throughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}):
        """
        创建DynamoDB表
        Args:
            key_schema (list): 主键模式，例如 [{'AttributeName': 'id', 'KeyType': 'HASH'}]
            attribute_definitions (list): 属性定义，例如 [{'AttributeName': 'id', 'AttributeType': 'S'}]
            provisioned_throughput (dict): 预置吞吐量设置
        Returns:
            dict: 包含操作结果的字典
        """
        try:
            table = self.dynamodb.create_table(
                TableName=self.table.name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput
            )
            # 等待表创建完成
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table.name)
            return {'success': True, 'message': f'表 {self.table.name} 创建成功'}
        except ClientError as e:
            return {'success': False, 'message': f'创建表时出错: {str(e)}'}

def main():
    try:
        # 初始化 DynamoDB 客户端
        table_name = "Movies"  # 替换为你的表名
        crud = DynamoDBCRUD(table_name)

        # 列出所有表
        tables = list(crud.dynamodb.tables.all())
        print("\n现有的表:")
        for table in tables:
            print(f"- {table.name}")

        # 测试表是否存在
        try:
            crud.table.table_status
            print(f"\n表 '{table_name}' 存在且可访问!")
            print(f"表状态: {crud.table.table_status}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"\n表 '{table_name}' 不存在。正在创建表...")
                
                # 定义表结构
                key_schema = [
                    {'AttributeName': 'year', 'KeyType': 'HASH'},  # 分区键
                    {'AttributeName': 'title', 'KeyType': 'RANGE'}  # 排序键
                ]
                
                attribute_definitions = [
                    {'AttributeName': 'year', 'AttributeType': 'N'},
                    {'AttributeName': 'title', 'AttributeType': 'S'}
                ]
                
                # 创建表
                result = crud.create_table(key_schema, attribute_definitions)
                print(result['message'])
                if not result['success']:
                    return
            else:
                print(f"\n访问表时出错: {str(e)}")
                return

        # 如果成功创建了表，添加一些示例数据
        if crud.table.table_status == 'ACTIVE':
            print("\n添加示例电影数据...")
            movies = [
                {
                    'year': 1994,
                    'title': '肖申克的救赎',
                    'info': {
                        'directors': ['弗兰克·德拉邦特'],
                        'rating': Decimal('9.3')
                    }
                },
                {
                    'year': 1994,
                    'title': '这个杀手不太冷',
                    'info': {
                        'directors': ['吕克·贝松'],
                        'rating': Decimal('9.1')
                    }
                }
            ]
            
            for movie in movies:
                result = crud.create_item(movie)
                if result['success']:
                    print(f"添加电影成功: {movie['title']}")
                else:
                    print(f"添加电影失败: {movie['title']} - {result['message']}")

    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
