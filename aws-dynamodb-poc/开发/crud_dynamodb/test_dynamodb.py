import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import json
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Union
from tqdm import tqdm
import random
import time

class DynamoDBTest:
    def __init__(self, table_name: str = "AvailabilityRestrictions", endpoint_url: str = 'http://localhost:8000'):
        """
        初始化DynamoDB客户端和表
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
        创建DynamoDB表
        """
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'availabilityId',
                        'KeyType': 'HASH'  # 分区键
                    },
                    {
                        'AttributeName': 'stayDate',
                        'KeyType': 'RANGE'  # 排序键
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'availabilityId',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'stayDate',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'sellState',
                        'AttributeType': 'N'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'StayDateIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'stayDate',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'sellState',
                                'KeyType': 'RANGE'
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
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            
            # 等待表创建完成
            waiter = self.dynamodb.meta.client.get_waiter('table_exists')
            waiter.wait(TableName=self.table_name)
            
            return {
                'success': True,
                'message': f'表 {self.table_name} 创建成功'
            }
        except ClientError as e:
            return {
                'success': False,
                'message': f'创建表失败: {str(e)}'
            }

    def create_item(self, item: Dict) -> Dict:
        """
        创建单条记录
        """
        try:
            response = self.table.put_item(Item=item)
            return {
                'success': True,
                'message': '记录创建成功',
                'response': response
            }
        except ClientError as e:
            return {
                'success': False,
                'message': f'创建记录失败: {str(e)}'
            }

    def get_item(self, availability_id: str, stay_date: str) -> Dict:
        """
        通过主键获取单条记录
        """
        try:
            response = self.table.get_item(
                Key={
                    'availabilityId': availability_id,
                    'stayDate': stay_date
                }
            )
            
            if 'Item' in response:
                # 将Decimal类型转换为int或float
                item = {}
                for key, value in response['Item'].items():
                    if isinstance(value, Decimal):
                        item[key] = int(value) if value % 1 == 0 else float(value)
                    else:
                        item[key] = value
                
                return {
                    'success': True,
                    'message': '记录获取成功',
                    'item': item
                }
            else:
                return {
                    'success': False,
                    'message': '记录不存在'
                }
        except ClientError as e:
            return {
                'success': False,
                'message': f'获取记录失败: {str(e)}'
            }

    # def query_by_stay_date(self, stay_date: str, sell_state: Optional[int] = None) -> Dict:
        """
        通过stayDate和可选的sellState查询记录
        """
        try:
            if sell_state is not None:
                # 使用stayDate和sellState查询
                response = self.table.query(
                    IndexName='StayDateIndex',
                    KeyConditionExpression='stayDate = :sd AND sellState = :ss',
                    ExpressionAttributeValues={
                        ':sd': stay_date,
                        ':ss': sell_state
                    }
                )
            else:
                # 只使用stayDate查询
                response = self.table.query(
                    IndexName='StayDateIndex',
                    KeyConditionExpression='stayDate = :sd',
                    ExpressionAttributeValues={
                        ':sd': stay_date
                    }
                )

            # 格式化结果
            items = []
            for item in response['Items']:
                formatted_item = {}
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        formatted_item[key] = int(value) if value % 1 == 0 else float(value)
                    else:
                        formatted_item[key] = value
                items.append(formatted_item)

            return {
                'success': True,
                'message': f'查询成功，找到 {len(items)} 条记录',
                'items': items
            }
        except ClientError as e:
            return {
                'success': False,
                'message': f'查询失败: {str(e)}'
            }

    def batch_write_items(self, items: List[Dict]) -> Dict:
        """
        批量写入数据
        """
        try:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
            return {
                'success': True,
                'message': f'成功批量写入 {len(items)} 条数据'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'批量写入失败: {str(e)}'
            }

    def generate_test_data(self, count: int) -> List[Dict]:
        """
        生成测试数据，使用多组固定值组合
        """
        items = []
        base_date = datetime(2025, 2, 1)
        
        # 定义多组固定值组合
        fixed_values_groups = [
            {
                "sellState": 1,
                "advancePurchaseMin": 7,
                "advancePurchaseMax": 30,
                "closedToArrival": 1,
                "closedToDeparture": 1,
                "doaCostPriceChangeBool": 1,
                "fullPartnerLosArrival": 268435455,
                "fullPartnerLosStayThrough": 268435455
            },
            {
                "sellState": 2,
                "advancePurchaseMin": 14,
                "advancePurchaseMax": 60,
                "closedToArrival": 0,
                "closedToDeparture": 1,
                "doaCostPriceChangeBool": 0,
                "fullPartnerLosArrival": 268435455,
                "fullPartnerLosStayThrough": 268435455
            },
            {
                "sellState": 3,
                "advancePurchaseMin": 1,
                "advancePurchaseMax": 90,
                "closedToArrival": 1,
                "closedToDeparture": 0,
                "doaCostPriceChangeBool": 1,
                "fullPartnerLosArrival": 268435455,
                "fullPartnerLosStayThrough": 268435455
            }
        ]
        
        # 计算每组应该生成多少条数据
        items_per_group = count // len(fixed_values_groups)
        remaining_items = count % len(fixed_values_groups)
        
        # 为每组生成对应数量的数据
        for group_index, fixed_values in enumerate(fixed_values_groups):
            # 计算这组需要生成的数据量
            group_count = items_per_group + (1 if group_index < remaining_items else 0)
            
            for _ in range(group_count):
                # 生成随机日期（在2025-02-01到2025-12-31之间）
                random_days = random.randint(0, 333)  # 最多11个月
                stay_date = (base_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
                
                # 生成随机时间
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                update_date = f"{stay_date} {hour:02d}:{minute:02d}:{second:02d}.345"

                # 创建基础数据
                item = {
                    "availabilityId": str(uuid.uuid4()),
                    "stayDate": stay_date,
                    "cutOffDays": random.randint(0, 30),
                    "versionId": random.randint(1, 100),
                    "updateTpId": random.randint(1, 10),
                    "updateTuId": random.randint(1, 10),
                    "updateDate": update_date,
                    "updateClientId": random.randint(1, 5)
                }
                
                # 添加固定值字段
                item.update(fixed_values)
                items.append(item)
        
        return items

    def batch_insert_with_progress(self, total_count: int, batch_size: int = 25) -> Dict:
        """
        分批插入大量数据，显示进度条
        """
        try:
            start_time = time.time()
            total_batches = (total_count + batch_size - 1) // batch_size
            success_count = 0
            error_count = 0
            
            with tqdm(total=total_count, desc="插入数据") as pbar:
                for i in range(0, total_count, batch_size):
                    # 生成这一批次的数据
                    current_batch_size = min(batch_size, total_count - i)
                    items = self.generate_test_data(current_batch_size)
                    
                    # 批量写入数据
                    result = self.batch_write_items(items)
                    if result['success']:
                        success_count += len(items)
                    else:
                        error_count += len(items)
                        print(f"\n批次 {i//batch_size + 1}/{total_batches} 失败: {result['message']}")
                    
                    # 更新进度条
                    pbar.update(len(items))
                    
                    # 每1000条数据后暂停一下，避免请求过快
                    if (i + batch_size) % 1000 == 0:
                        time.sleep(0.1)
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                'success': True,
                'message': (
                    f'批量插入完成\n'
                    f'总数据量: {total_count}\n'
                    f'成功: {success_count}\n'
                    f'失败: {error_count}\n'
                    f'耗时: {duration:.2f} 秒\n'
                    f'平均速率: {total_count/duration:.2f} 条/秒'
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'批量插入过程中出错: {str(e)}'
            }

    def calculate_item_size(self, item: Dict) -> int:
        """
        计算单个项目的大小（以字节为单位）
        参考: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/CapacityUnitCalculations.html
        """
        size = 0
        for key, value in item.items():
            # 属性名称的大小
            size += len(key.encode('utf-8'))
            
            # 属性值的大小
            if isinstance(value, str):
                size += len(value.encode('utf-8'))
            elif isinstance(value, (int, float, Decimal)):
                size += 8  # 数字类型固定使用8字节
            elif isinstance(value, bool):
                size += 1
            elif value is None:
                size += 1
                
        return size

    def calculate_table_size(self) -> Dict:
        """
        计算表中所有数据的大小
        """
        try:
            total_items = 0
            total_size = 0
            size_distribution = {}  # 记录不同大小范围的项目数量
            
            # 扫描整个表
            response = self.table.scan()
            items = response.get('Items', [])
            
            while True:
                for item in items:
                    size = self.calculate_item_size(item)
                    total_items += 1
                    total_size += size
                    
                    # 记录大小分布（按100字节分组）
                    size_range = f"{(size // 100) * 100}-{(size // 100 + 1) * 100}字节"
                    size_distribution[size_range] = size_distribution.get(size_range, 0) + 1
                
                # 检查是否还有更多数据
                if 'LastEvaluatedKey' not in response:
                    break
                    
                # 获取下一批数据
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items = response.get('Items', [])
            
            # 计算平均大小
            avg_size = total_size / total_items if total_items > 0 else 0
            
            # 按大小范围排序
            sorted_distribution = dict(sorted(size_distribution.items(), 
                key=lambda x: int(x[0].split('-')[0])))
            
            return {
                'success': True,
                'message': '计算完成',
                'data': {
                    'total_items': total_items,
                    'total_size_bytes': total_size,
                    'total_size_kb': total_size / 1024,
                    'total_size_mb': total_size / (1024 * 1024),
                    'avg_item_size_bytes': avg_size,
                    'size_distribution': sorted_distribution
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'计算表大小时出错: {str(e)}'
            }

    def table_exists(self) -> bool:
        """
        检查表是否存在
        """
        try:
            self.dynamodb.Table(self.table_name).table_status
            return True
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            return False

    def clear_table(self) -> Dict:
        """
        清空表中的所有数据
        """
        try:
            # 获取所有项目
            items_to_delete = []
            response = self.table.scan(
                ProjectionExpression='availabilityId, stayDate'
            )
            
            while True:
                items = response.get('Items', [])
                for item in items:
                    items_to_delete.append({
                        'DeleteRequest': {
                            'Key': {
                                'availabilityId': item['availabilityId'],
                                'stayDate': item['stayDate']
                            }
                        }
                    })
                
                if 'LastEvaluatedKey' not in response:
                    break
                    
                response = self.table.scan(
                    ProjectionExpression='availabilityId, stayDate',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
            
            # 批量删除项目
            if items_to_delete:
                with tqdm(total=len(items_to_delete), desc="删除数据") as pbar:
                    for i in range(0, len(items_to_delete), 25):
                        batch = items_to_delete[i:i+25]
                        self.dynamodb.batch_write_item(
                            RequestItems={
                                self.table_name: batch
                            }
                        )
                        pbar.update(len(batch))
                        
                return {
                    'success': True,
                    'message': f'成功删除 {len(items_to_delete)} 条数据'
                }
            else:
                return {
                    'success': True,
                    'message': '表中没有数据需要删除'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'清空表数据时出错: {str(e)}'
            }

    def count_fixed_value_groups(self) -> Dict:
        """
        统计每组固定值组合的数量
        """
        try:
            # 定义固定值组合的特征
            fixed_value_groups = {
                "Group1": {
                    "sellState": 1,
                    "advancePurchaseMin": 7,
                    "advancePurchaseMax": 30,
                    "closedToArrival": 1,
                    "closedToDeparture": 1,
                    "doaCostPriceChangeBool": 1,
                },
                "Group2": {
                    "sellState": 2,
                    "advancePurchaseMin": 14,
                    "advancePurchaseMax": 60,
                    "closedToArrival": 0,
                    "closedToDeparture": 1,
                    "doaCostPriceChangeBool": 0,
                },
                "Group3": {
                    "sellState": 3,
                    "advancePurchaseMin": 1,
                    "advancePurchaseMax": 90,
                    "closedToArrival": 1,
                    "closedToDeparture": 0,
                    "doaCostPriceChangeBool": 1,
                }
            }
            
            # 初始化计数器
            group_counts = {group: 0 for group in fixed_value_groups}
            unmatched = 0
            
            # 扫描表中的所有数据
            response = self.table.scan()
            
            while True:
                for item in response.get('Items', []):
                    # 检查每个项目属于哪个组
                    matched = False
                    for group_name, group_values in fixed_value_groups.items():
                        if all(item.get(key) == value for key, value in group_values.items()):
                            group_counts[group_name] += 1
                            matched = True
                            break
                    
                    if not matched:
                        unmatched += 1
                
                # 检查是否还有更多数据
                if 'LastEvaluatedKey' not in response:
                    break
                    
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
            
            return {
                'success': True,
                'message': '统计完成',
                'data': {
                    'group_counts': group_counts,
                    'unmatched': unmatched,
                    'total': sum(group_counts.values()) + unmatched
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'统计固定值组合时出错: {str(e)}'
            }

def main():
    # 初始化DynamoDB测试类
    dynamo_test = DynamoDBTest()

    # 1. 检查并创建表
    print("\n1. 检查表状态:")
    if dynamo_test.table_exists():
        print("表已存在，跳过创建步骤")
        
        # 清空现有数据
        print("\n2. 清空表中的数据:")
        clear_result = dynamo_test.clear_table()
        print(clear_result['message'])
    else:
        print("表不存在，开始创建表")
        create_result = dynamo_test.create_table()
        print(create_result['message'])

    # 批量插入1000条测试数据
    print("\n3. 批量插入1000条测试数据:")
    batch_result = dynamo_test.batch_insert_with_progress(1000)
    print(batch_result['message'])

    # 统计固定值组合的数量
    print("\n4. 统计固定值组合的数量:")
    group_result = dynamo_test.count_fixed_value_groups()
    if group_result['success']:
        data = group_result['data']
        print("\n各组数据统计:")
        for group, count in data['group_counts'].items():
            print(f"{group}: {count:,} 条")
        if data['unmatched'] > 0:
            print(f"不匹配任何组合: {data['unmatched']:,} 条")
        print(f"总计: {data['total']:,} 条")
    else:
        print(group_result['message'])

    # 计算数据大小
    print("\n5. 计算数据大小:")
    size_result = dynamo_test.calculate_table_size()
    if size_result['success']:
        data = size_result['data']
        print(f"总记录数: {data['total_items']:,} 条")
        print(f"总大小: {data['total_size_bytes']:,} 字节")
        print(f"      = {data['total_size_kb']:.2f} KB")
        print(f"      = {data['total_size_mb']:.2f} MB")
        print(f"平均每条记录大小: {data['avg_item_size_bytes']:.2f} 字节")
        print("\n数据大小分布:")
        for size_range, count in data['size_distribution'].items():
            print(f"{size_range}: {count:,} 条")
    else:
        print(size_result['message'])

    # 测试查询功能
    # print("\n6. 测试查询功能:")
    # # 查询2025-02-01的数据
    # query_result = dynamo_test.query_by_stay_date("2025-02-01")
    # if query_result['success']:
    #     print(f"2025-02-01的数据数量: {len(query_result['items'])}")
    #     if query_result['items']:
    #         print("第一条数据示例:")
    #         print(json.dumps(query_result['items'][0], indent=2, ensure_ascii=False))
    # else:
    #     print(query_result['message'])

    # 统计不同sellState的数据分布
    # print("\n7. 统计不同sellState的数据分布:")
    # for sell_state in [1, 2, 3]:
        query_result = dynamo_test.query_by_stay_date("2025-02-01", sell_state)
        if query_result['success']:
            print(f"sellState={sell_state} 的数据数量: {len(query_result['items'])}")
            if query_result['items']:
                print("示例数据的固定值字段:")
                first_item = query_result['items'][0]
                fixed_fields = [
                    "sellState",
                    "advancePurchaseMin",
                    "advancePurchaseMax",
                    "closedToArrival",
                    "closedToDeparture",
                    "doaCostPriceChangeBool",
                    "fullPartnerLosArrival",
                    "fullPartnerLosStayThrough"
                ]
                for field in fixed_fields:
                    if field in first_item:
                        print(f"  {field}: {first_item[field]}")
        else:
            print(f"查询 sellState={sell_state} 失败: {query_result['message']}")

if __name__ == "__main__":
    main()
