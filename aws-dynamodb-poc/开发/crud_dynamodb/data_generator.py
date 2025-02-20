import random
from datetime import datetime, timedelta
from property_restrictions import DynamoDBCRUD
import uuid
import time
from typing import List, Dict
import concurrent.futures
from tqdm import tqdm

def generate_sample_data(num_records: int = 100000) -> List[Dict]:
    """
    生成示例数据
    """
    base_date = datetime(2025, 1, 1)
    property_ids = [str(i) for i in range(266270522, 266270532)]  # 10个不同的property
    
    data = []
    for _ in range(num_records):
        # 随机生成数据
        property_id = random.choice(property_ids)
        days_offset = random.randint(0, 365)
        stay_date = (base_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
        
        item = {
            "propertyId": property_id,
            "restrictionId": str(uuid.uuid4())[:8],  # 使用UUID前8位作为restrictionId
            "stayDate": stay_date,
            "sellState": random.randint(1, 5),
            "cutOffDays": random.randint(0, 7),
            "advancePurchaseMin": random.randint(1, 30),
            "advancePurchaseMax": random.randint(31, 90),
            "closedToArrival": random.randint(0, 1),
            "closedToDeparture": random.randint(0, 1),
            "fullPartnerLosArrival": 268435455,
            "fullPartnerLosStayThrough": 268435455,
            "doaCostPriceChangeBool": random.randint(0, 1),
            "versionId": 1,
            "updateTpId": random.randint(1, 100),
            "updateTuId": random.randint(1, 100),
            "updateDate": datetime.now().isoformat(),
            "changeRequestSourceId": random.randint(1, 5),
            "availabilityLevel": random.randint(1, 3)
        }
        data.append(item)
    
    return data

def batch_write_with_progress(crud: DynamoDBCRUD, items: List[Dict], batch_size: int = 25):
    """
    带进度条的批量写入
    """
    total_batches = len(items) // batch_size + (1 if len(items) % batch_size else 0)
    
    with tqdm(total=len(items), desc="写入数据") as pbar:
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            result = crud.batch_create_items(batch)
            if not result['success']:
                print(f"\n批次 {i//batch_size + 1}/{total_batches} 写入失败: {result['message']}")
            pbar.update(len(batch))

def perform_performance_tests(crud: DynamoDBCRUD):
    """
    执行性能测试
    """
    print("\n执行性能测试...")
    
    # 1. 测试按日期范围查询
    print("\n1. 测试按日期范围查询")
    start_time = time.time()
    result = crud.query_by_date_range("2025-01-01", "2025-12-31", limit=1000)
    query_time = time.time() - start_time
    print(f"查询耗时: {query_time:.2f}秒")
    if result['success']:
        print(f"返回记录数: {result['count']}")
    else:
        print(f"查询失败: {result.get('message', '未知错误')}")

    # 2. 测试按销售状态查询
    print("\n2. 测试按销售状态查询")
    start_time = time.time()
    result = crud.query_by_sell_state(1, "2025-01-01", "2025-12-31", limit=1000)
    query_time = time.time() - start_time
    print(f"查询耗时: {query_time:.2f}秒")
    if result['success']:
        print(f"返回记录数: {result['count']}")
    else:
        print(f"查询失败: {result.get('message', '未知错误')}")

    # 3. 测试分页查询
    print("\n3. 测试分页查询")
    start_time = time.time()
    page_size = 100
    last_key = None
    total_items = 0
    page_count = 0
    
    while True:
        result = crud.query_by_date_range(
            "2025-01-01", "2025-12-31",
            last_evaluated_key=last_key,
            limit=page_size
        )
        if not result['success']:
            print(f"查询失败: {result.get('message', '未知错误')}")
            break
            
        total_items += result['count']
        page_count += 1
        
        if 'lastEvaluatedKey' not in result:
            break
        last_key = result['lastEvaluatedKey']
        
        if page_count >= 10:  # 只测试前10页
            break
    
    query_time = time.time() - start_time
    print(f"分页查询耗时: {query_time:.2f}秒")
    print(f"查询了 {page_count} 页，总计 {total_items} 条记录")

    # 4. 测试不同的查询场景
    print("\n4. 测试特定属性组合查询")
    
    # 测试特定销售状态的查询
    print("\n4.1 查询特定销售状态 (sellState = 1)")
    start_time = time.time()
    result = crud.query_by_sell_state(1, limit=1000)
    query_time = time.time() - start_time
    print(f"查询耗时: {query_time:.2f}秒")
    if result['success']:
        print(f"返回记录数: {result['count']}")
    else:
        print(f"查询失败: {result.get('message', '未知错误')}")
    
    # 测试特定日期的查询
    print("\n4.2 查询特定日期 (2025-06-01)")
    start_time = time.time()
    result = crud.query_by_stay_date("2025-06-01", limit=1000)
    query_time = time.time() - start_time
    print(f"查询耗时: {query_time:.2f}秒")
    if result['success']:
        print(f"返回记录数: {result['count']}")
    else:
        print(f"查询失败: {result.get('message', '未知错误')}")

def main():
    try:
        # 初始化 DynamoDB 客户端
        table_name = "PropertyRestrictions"
        crud = DynamoDBCRUD(table_name)
        
        # 生成示例数据
        print("生成示例数据...")
        data = generate_sample_data(100000)  # 生成10万条数据
        
        # 批量写入数据
        print("\n开始批量写入数据...")
        start_time = time.time()
        batch_write_with_progress(crud, data)
        total_time = time.time() - start_time
        print(f"\n写入完成，总耗时: {total_time:.2f}秒")
        
        # 执行性能测试
        perform_performance_tests(crud)

    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
