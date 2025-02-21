import boto3
from typing import Dict, List
from decimal import Decimal
import random
from datetime import datetime, timedelta
from tqdm import tqdm

class RestrictionTables:
    def __init__(self):
        """Initialize DynamoDB client and table names"""
        self.dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        
        # Table names
        self.availability_table_name = 'AvailabilityRestrictions'
        self.detail_table_name = 'RestrictionDetail'
        self.combined_table_name = 'AvailabilityRestrictionsCombined'
        
        # Get table objects
        self.availability_table = self.dynamodb.Table(self.availability_table_name)
        self.detail_table = self.dynamodb.Table(self.detail_table_name)
        self.combined_table = self.dynamodb.Table(self.combined_table_name)

    def create_tables(self) -> Dict:
        """Create DynamoDB tables if they don't exist"""
        try:
            # Create AvailabilityRestrictions table
            self.dynamodb.create_table(
                TableName=self.availability_table_name,
                KeySchema=[
                    {'AttributeName': 'availabilityId', 'KeyType': 'HASH'},
                    {'AttributeName': 'stayDate', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'availabilityId', 'AttributeType': 'S'},
                    {'AttributeName': 'stayDate', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )

            # Create RestrictionDetail table
            self.dynamodb.create_table(
                TableName=self.detail_table_name,
                KeySchema=[
                    {'AttributeName': 'restrictionDetailId', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'restrictionDetailId', 'AttributeType': 'N'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )

            # Create AvailabilityRestrictionsCombined table
            self.dynamodb.create_table(
                TableName=self.combined_table_name,
                KeySchema=[
                    {'AttributeName': 'availabilityId', 'KeyType': 'HASH'},
                    {'AttributeName': 'stayDate', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'availabilityId', 'AttributeType': 'S'},
                    {'AttributeName': 'stayDate', 'AttributeType': 'S'},
                    {'AttributeName': 'restrictionDetailId', 'AttributeType': 'N'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'RestrictionDetailIndex',
                        'KeySchema': [
                            {'AttributeName': 'restrictionDetailId', 'KeyType': 'HASH'}
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

            return {
                'success': True,
                'message': 'Tables created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating tables: {str(e)}'
            }

    def generate_test_data(self, num_records: int = 1000) -> Dict:
        """Generate test data that maintains consistency across all tables"""
        try:
            # First, generate availability data with restrictions
            availability_data = []
            
            # Define the three fixed restriction combinations
            fixed_restrictions = [
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

            # Create restriction details mapping
            restriction_details = {}
            for i, restriction in enumerate(fixed_restrictions, 1):
                restriction_key = tuple(restriction.items())
                restriction_details[restriction_key] = {
                    'restrictionDetailId': i,
                    **dict(restriction_key)
                }

            print("\nGenerating test data...")
            with tqdm(total=num_records, desc="Generating records") as pbar:
                for i in range(num_records):
                    # Generate availability record
                    stay_date = (datetime.now() + timedelta(days=i % 30)).strftime('%Y-%m-%d')
                    availability_id = f"PROP_{i // 30 + 1:03d}"
                    
                    # Select one of the three fixed restrictions
                    restriction = fixed_restrictions[i % len(fixed_restrictions)]
                    restriction_key = tuple(restriction.items())
                    restriction_detail_id = restriction_details[restriction_key]['restrictionDetailId']

                    # Create records for all three tables
                    availability_record = {
                        'availabilityId': availability_id,
                        'stayDate': stay_date,
                        **restriction
                    }

                    combined_record = {
                        'availabilityId': availability_id,
                        'stayDate': stay_date,
                        'restrictionDetailId': restriction_detail_id,
                        'cutOffDays': random.randint(0, 7),
                        'versionId': str(random.randint(1, 100)),
                        'updateTpId': str(random.randint(1, 10)),
                        'updateTuId': str(random.randint(1, 5)),
                        'updateDate': datetime.now().isoformat(),
                        'changeRequestSourceId': str(random.randint(1, 3)),
                        'availabilityLevel': random.randint(0, 100)
                    }

                    availability_data.append((availability_record, combined_record))
                    pbar.update(1)

            # Insert data into RestrictionDetail table
            print("\nInserting restriction details...")
            with tqdm(total=len(restriction_details), desc="Inserting restriction details") as pbar:
                with self.detail_table.batch_writer() as writer:
                    for detail in restriction_details.values():
                        writer.put_item(Item=detail)
                        pbar.update(1)

            # Insert data into AvailabilityRestrictions and AvailabilityRestrictionsCombined tables
            print("\nInserting availability data...")
            with tqdm(total=len(availability_data), desc="Inserting availability data") as pbar:
                for i in range(0, len(availability_data), 25):
                    batch = availability_data[i:i+25]
                    
                    # Write to AvailabilityRestrictions
                    with self.availability_table.batch_writer() as writer:
                        for avail_record, _ in batch:
                            writer.put_item(Item=avail_record)
                    
                    # Write to AvailabilityRestrictionsCombined
                    with self.combined_table.batch_writer() as writer:
                        for _, combined_record in batch:
                            writer.put_item(Item=combined_record)
                    
                    pbar.update(len(batch))

            return {
                'success': True,
                'message': f'Successfully generated {num_records} records',
                'data': {
                    'total_records': num_records,
                    'unique_restrictions': len(restriction_details)
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating test data: {str(e)}'
            }

    def calculate_table_size(self, table_name: str) -> Dict:
        """Calculate the size of all data in the specified table"""
        try:
            total_items = 0
            total_size = 0
            size_distribution = {}  # Record the number of items in different size ranges
            
            # Scan the entire table
            table = self.dynamodb.Table(table_name)
            response = table.scan()
            
            while True:
                for item in response.get('Items', []):
                    size = self.calculate_item_size(item)
                    total_items += 1
                    total_size += size
                    
                    # Record size distribution (grouped by 100 bytes)
                    size_range = f"{(size // 100) * 100}-{(size // 100 + 1) * 100} bytes"
                    size_distribution[size_range] = size_distribution.get(size_range, 0) + 1
                
                # Check if there is more data
                if 'LastEvaluatedKey' not in response:
                    break
                    
                response = table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
            
            # Calculate average size
            avg_size = total_size / total_items if total_items > 0 else 0
            
            # Sort size distribution by size range
            sorted_distribution = dict(sorted(size_distribution.items(), 
                key=lambda x: int(x[0].split('-')[0])))
            
            return {
                'success': True,
                'message': 'Calculation completed',
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
                'message': f'Error calculating table size: {str(e)}'
            }

    def calculate_item_size(self, item: Dict) -> int:
        """Calculate the size of a single item (in bytes)"""
        size = 0
        for key, value in item.items():
            # Attribute name size
            size += len(key.encode('utf-8'))
            
            # Attribute value size
            if isinstance(value, str):
                size += len(value.encode('utf-8'))
            elif isinstance(value, (int, float, Decimal)):
                size += 8  # Numeric types use 8 bytes
            elif isinstance(value, bool):
                size += 1
            elif value is None:
                size += 1
                
        return size

    def count_by_restriction_detail(self) -> Dict:
        """Count the distribution of restriction combinations in the AvailabilityRestrictionsCombined table"""
        try:
            # Use GSI to count by restrictionDetailId
            counts = {}
            
            # Scan all data
            response = self.combined_table.scan(
                ProjectionExpression='restrictionDetailId'
            )
            
            while True:
                for item in response.get('Items', []):
                    detail_id = item.get('restrictionDetailId')
                    if detail_id is not None:
                        counts[detail_id] = counts.get(detail_id, 0) + 1
                
                if 'LastEvaluatedKey' not in response:
                    break
                    
                response = self.combined_table.scan(
                    ProjectionExpression='restrictionDetailId',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
            
            # Get detailed information for each restrictionDetailId
            details = {}
            for detail_id in counts.keys():
                response = self.detail_table.get_item(
                    Key={'restrictionDetailId': detail_id}
                )
                if 'Item' in response:
                    details[detail_id] = response['Item']
            
            return {
                'success': True,
                'message': 'Counting completed',
                'data': {
                    'counts': counts,
                    'details': details,
                    'total': sum(counts.values())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error counting restriction combinations: {str(e)}'
            }

    def count_fixed_restrictions_in_availability(self):
        """Count different restriction combinations in AvailabilityRestrictions table"""
        try:
            # Scan the entire table
            response = self.availability_table.scan()
            items = response['Items']
            
            # Continue scanning if there are more items
            while 'LastEvaluatedKey' in response:
                response = self.availability_table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response['Items'])

            # Count different combinations
            combinations = {}
            restriction_fields = [
                'sellState', 'advancePurchaseMin', 'advancePurchaseMax',
                'closedToArrival', 'closedToDeparture', 'doaCostPriceChangeBool',
                'fullPartnerLosArrival', 'fullPartnerLosStayThrough'
            ]

            for item in items:
                # Create key for restriction combination
                restriction = {field: item[field] for field in restriction_fields}
                key = tuple(sorted(restriction.items()))
                combinations[key] = combinations.get(key, 0) + 1

            # Print statistics
            print("\nRestriction Combinations Statistics in AvailabilityRestrictions table:")
            print("-" * 80)
            for key in sorted(combinations.keys()):
                restriction_dict = dict(key)
                print("\nCombination Details:")
                print(f"  Sell State: {restriction_dict['sellState']}")
                print(f"  Advance Purchase Min: {restriction_dict['advancePurchaseMin']}")
                print(f"  Advance Purchase Max: {restriction_dict['advancePurchaseMax']}")
                print(f"  Closed To Arrival: {restriction_dict['closedToArrival']}")
                print(f"  Closed To Departure: {restriction_dict['closedToDeparture']}")
                print(f"  DOA Cost Price Change: {restriction_dict['doaCostPriceChangeBool']}")
                print(f"  Full Partner LOS Arrival: {restriction_dict['fullPartnerLosArrival']}")
                print(f"  Full Partner LOS Stay Through: {restriction_dict['fullPartnerLosStayThrough']}")
                print(f"  Occurrence Count: {combinations[key]}")
                print("-" * 80)

            return {
                'success': True,
                'message': f'Successfully counted restriction combinations',
                'data': {
                    'total_records': len(items),
                    'unique_combinations': len(combinations),
                    'combinations': combinations
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error counting combinations: {str(e)}'
            }

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            self.dynamodb.Table(table_name).table_status
            return True
        except:
            return False

    def clear_table(self, table_name: str) -> Dict:
        """Clear all data from a table"""
        try:
            table = self.dynamodb.Table(table_name)
            
            # Get the key schema
            key_schema = table.key_schema
            
            # Scan the table
            response = table.scan()
            items = response['Items']
            
            # Delete all items
            with table.batch_writer() as batch:
                for item in items:
                    key = {attr['AttributeName']: item[attr['AttributeName']] 
                          for attr in key_schema}
                    batch.delete_item(Key=key)
            
            return {
                'success': True,
                'message': f'Successfully cleared {table_name} table'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error clearing {table_name} table: {str(e)}'
            }

    def calculate_compression_ratio(self):
        """Calculate the compression ratio between tables"""
        try:
            # Calculate sizes for each table
            restriction_detail_size = self.calculate_table_size(self.detail_table_name)['data']['total_size_bytes']
            combined_size = self.calculate_table_size(self.combined_table_name)['data']['total_size_bytes']
            availability_size = self.calculate_table_size(self.availability_table_name)['data']['total_size_bytes']

            # Calculate total size of split tables
            split_tables_size = restriction_detail_size + combined_size

            # Calculate compression ratio
            compression_ratio = (split_tables_size / availability_size) * 100 if availability_size > 0 else 0

            print("\nTable Size Comparison:")
            print("-" * 80)
            print(f"RestrictionDetail Table Size: {restriction_detail_size:,} bytes")
            print(f"AvailabilityRestrictionsCombined Table Size: {combined_size:,} bytes")
            print(f"AvailabilityRestrictions Table Size: {availability_size:,} bytes")
            print("-" * 80)
            print(f"Split Tables Total Size: {split_tables_size:,} bytes")
            print(f"Compression Ratio: {compression_ratio:.2f}%")
            print(f"Space Saving: {100 - compression_ratio:.2f}%")
            print("-" * 80)

            return {
                'success': True,
                'message': 'Successfully calculated compression ratio',
                'data': {
                    'restriction_detail_size': restriction_detail_size,
                    'combined_size': combined_size,
                    'availability_size': availability_size,
                    'compression_ratio': compression_ratio
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error calculating compression ratio: {str(e)}'
            }

def main():
    # Initialize
    tables = RestrictionTables()
    
    # 1. Check and create tables
    print("\n1. Checking table status:")
    tables_to_create = []
    if not tables.table_exists(tables.availability_table_name):
        tables_to_create.append(tables.availability_table_name)
    if not tables.table_exists(tables.detail_table_name):
        tables_to_create.append(tables.detail_table_name)
    if not tables.table_exists(tables.combined_table_name):
        tables_to_create.append(tables.combined_table_name)
        
    if tables_to_create:
        print(f"Tables to create: {', '.join(tables_to_create)}")
        create_result = tables.create_tables()
        print(create_result['message'])
    else:
        print("Tables already exist, skipping creation")
        
        # Clear existing data
        print("\n2. Clearing existing data:")
        for table_name in [tables.availability_table_name, tables.detail_table_name, tables.combined_table_name]:
            clear_result = tables.clear_table(table_name)
            print(clear_result['message'])
    
    # 3. Generate test data
    print("\n3. Generating test data:")
    data_result = tables.generate_test_data(1000)  # Generate 1000 records
    if data_result['success']:
        print(data_result['message'])
        print(f"Generated {data_result['data']['total_records']} records")
        print(f"Created {data_result['data']['unique_restrictions']} unique restriction combinations")

        # 4. Calculate table sizes
        print("\n4. Calculating table sizes:")
        
        # Calculate AvailabilityRestrictions size
        print("\nAvailabilityRestrictions Table:")
        size_result = tables.calculate_table_size(tables.availability_table_name)
        if size_result['success']:
            data = size_result['data']
            print(f"Total Records: {data['total_items']:,}")
            print(f"Total Size: {data['total_size_bytes']:,} bytes")
            print(f"        = {data['total_size_kb']:.2f} KB")
            print(f"        = {data['total_size_mb']:.2f} MB")
            print(f"Average Record Size: {data['avg_item_size_bytes']:.2f} bytes")
        
        # Calculate RestrictionDetail size
        print("\nRestrictionDetail Table:")
        size_result = tables.calculate_table_size(tables.detail_table_name)
        if size_result['success']:
            data = size_result['data']
            print(f"Total Records: {data['total_items']:,}")
            print(f"Total Size: {data['total_size_bytes']:,} bytes")
            print(f"        = {data['total_size_kb']:.2f} KB")
            print(f"        = {data['total_size_mb']:.2f} MB")
            print(f"Average Record Size: {data['avg_item_size_bytes']:.2f} bytes")
        
        # Calculate AvailabilityRestrictionsCombined size
        print("\nAvailabilityRestrictionsCombined Table:")
        size_result = tables.calculate_table_size(tables.combined_table_name)
        if size_result['success']:
            data = size_result['data']
            print(f"Total Records: {data['total_items']:,}")
            print(f"Total Size: {data['total_size_bytes']:,} bytes")
            print(f"        = {data['total_size_kb']:.2f} KB")
            print(f"        = {data['total_size_mb']:.2f} MB")
            print(f"Average Record Size: {data['avg_item_size_bytes']:.2f} bytes")

        # 5. Calculate compression ratio
        print("\n5. Calculating compression ratio:")
        compression_result = tables.calculate_compression_ratio()
        if compression_result['success']:
            print(compression_result['message'])

        # 6. Analyze restriction combinations
        print("\n6. Analyzing restriction combinations:")
        distribution_result = tables.count_by_restriction_detail()
        if distribution_result['success']:
            data = distribution_result['data']
            print(f"\nTotal Records: {data['total']:,}")
            print("\nDistribution by Restriction Combination:")
            for detail_id, count in sorted(data['counts'].items()):
                detail = data['details'].get(detail_id, {})
                print(f"\nRestrictionDetail {detail_id}: {count:,} records")
                if detail:
                    print("Combination Details:")
                    print(f"  sellState: {detail.get('sellState')}")
                    print(f"  advancePurchaseMin: {detail.get('advancePurchaseMin')}")
                    print(f"  advancePurchaseMax: {detail.get('advancePurchaseMax')}")
                    print(f"  closedToArrival: {detail.get('closedToArrival')}")
                    print(f"  closedToDeparture: {detail.get('closedToDeparture')}")
                    print(f"  doaCostPriceChangeBool: {detail.get('doaCostPriceChangeBool')}")
        
        # Count restriction combinations in AvailabilityRestrictions
        print("\nCounting restriction combinations in AvailabilityRestrictions...")
        result = tables.count_fixed_restrictions_in_availability()
        print(result['message'])

    else:
        print(data_result['message'])

if __name__ == "__main__":
    main()
