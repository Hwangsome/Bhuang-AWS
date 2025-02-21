import boto3
import uuid
from datetime import datetime
import json
from typing import Dict, List
from decimal import Decimal

class InventoryTable:
    def __init__(self):
        """Initialize DynamoDB client and table name"""
        self.dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        self.table_name = 'Inventory'
        self.table = self.dynamodb.Table(self.table_name)

    def create_table(self) -> Dict:
        """Create Inventory table if it doesn't exist"""
        try:
            self.dynamodb.create_table(
                TableName=self.table_name,
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
            return {'success': True, 'message': 'Inventory table created successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error creating Inventory table: {str(e)}'}

    def table_exists(self) -> bool:
        """Check if the table exists"""
        try:
            self.dynamodb.Table(self.table_name).table_status
            return True
        except Exception:
            return False

    def clear_table(self) -> Dict:
        """Clear all data from the table"""
        try:
            response = self.table.scan()
            items = response['Items']
            
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])
            
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(
                        Key={
                            'availabilityId': item['availabilityId'],
                            'stayDate': item['stayDate']
                        }
                    )
            
            return {
                'success': True,
                'message': f'Successfully cleared {len(items)} items from the table'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error clearing table: {str(e)}'
            }

    def insert_test_data(self) -> Dict:
        """Insert 5 test records with some empty stayDates"""
        try:
            items = [
                {
                    "availabilityId": str(uuid.uuid4()),
                    "stayDate": "NO_DATE",  # Special marker for empty stayDate
                    "sold": 0,
                    "available": "1",
                    "accumulativeBlock": 0,
                    "versionId": 1,
                    "updateTpid": 1,
                    "updateTuid": 1,
                    "updateDate": "2025-02-10 12:11:12.345",
                    "updateClientId": 1
                },
                {
                    "availabilityId": str(uuid.uuid4()),
                    "stayDate": "NO_DATE",  # Special marker for empty stayDate
                    "sold": 1,
                    "available": "0",
                    "accumulativeBlock": 1,
                    "versionId": 2,
                    "updateTpid": 2,
                    "updateTuid": 2,
                    "updateDate": "2025-02-11 13:14:15.678",
                    "updateClientId": 2
                },
                {
                    "availabilityId": str(uuid.uuid4()),
                    "stayDate": "2025-02-12",
                    "sold": 2,
                    "available": "3",
                    "accumulativeBlock": 0,
                    "versionId": 3,
                    "updateTpid": 1,
                    "updateTuid": 3,
                    "updateDate": "2025-02-12 09:08:07.890",
                    "updateClientId": 1
                },
                {
                    "availabilityId": str(uuid.uuid4()),
                    "stayDate": "NO_DATE",  # Special marker for empty stayDate
                    "sold": 0,
                    "available": "5",
                    "accumulativeBlock": 1,
                    "versionId": 4,
                    "updateTpid": 2,
                    "updateTuid": 1,
                    "updateDate": "2025-02-13 16:17:18.901",
                    "updateClientId": 3
                },
                {
                    "availabilityId": str(uuid.uuid4()),
                    "stayDate": "2025-02-14",
                    "sold": 1,
                    "available": "",
                    "accumulativeBlock": 0,
                    "versionId": 5,
                    "updateTpid": 3,
                    "updateTuid": 2,
                    "updateDate": "2025-02-14 20:21:22.345",
                    "updateClientId": 2
                }
            ]

            # Insert items
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)

            return {
                'success': True,
                'message': 'Successfully inserted 5 test records',
                'data': items
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inserting test data: {str(e)}'
            }

    def calculate_table_size(self) -> Dict:
        """Calculate the size of the table"""
        try:
            response = self.table.scan()
            items = response['Items']
            
            total_size_bytes = 0
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])
            
            for item in items:
                # Convert Decimal to int/float before JSON serialization
                converted_item = self._decimal_to_int(item)
                item_size = len(json.dumps(converted_item).encode('utf-8'))
                total_size_bytes += item_size
            
            return {
                'success': True,
                'message': 'Successfully calculated table size',
                'data': {
                    'total_size_bytes': total_size_bytes
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error calculating table size: {str(e)}'
            }

    def _decimal_to_int(self, obj):
        """Convert Decimal objects to int/float for JSON serialization"""
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        elif isinstance(obj, dict):
            return {k: self._decimal_to_int(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._decimal_to_int(item) for item in obj]
        return obj

    def query_items(self, limit: int = 5) -> Dict:
        """Query items from the table"""
        try:
            # First try to get all items
            response = self.table.scan()
            
            # Log the raw response
            print("\nRaw DynamoDB Response:")
            print("-" * 80)
            print(json.dumps(self._decimal_to_int(dict(response)), indent=2, ensure_ascii=False))
            print("-" * 80)
            
            items = response.get('Items', [])
            
            # Continue scanning if there are more items
            while 'LastEvaluatedKey' in response and len(items) < limit:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))
            
            # Limit the number of items
            items = items[:limit]
            
            # Print items in JSON format with custom sorting for better readability
            print("\nQuery Results:")
            print("-" * 80)
            for item in items:
                # Sort the item keys for consistent output and convert Decimals
                sorted_item = {
                    'availabilityId': item['availabilityId'],
                    'stayDate': item['stayDate'],
                    'sold': self._decimal_to_int(item['sold']),
                    'available': self._decimal_to_int(item['available']),
                    'accumulativeBlock': self._decimal_to_int(item['accumulativeBlock']),
                    'versionId': self._decimal_to_int(item['versionId']),
                    'updateTpid': self._decimal_to_int(item['updateTpid']),
                    'updateTuid': self._decimal_to_int(item['updateTuid']),
                    'updateDate': item['updateDate'],
                    'updateClientId': self._decimal_to_int(item['updateClientId'])
                }
                print(json.dumps(sorted_item, indent=2, ensure_ascii=False))
                print("-" * 80)

            return {
                'success': True,
                'message': f'Successfully retrieved {len(items)} items',
                'data': items
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error querying items: {str(e)}'
            }

class InventoryKeysCombined:
    def __init__(self):
        """Initialize DynamoDB client and table name"""
        self.dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        self.table_name = 'Inventory_Keys_Combined'
        self.table = self.dynamodb.Table(self.table_name)

    def create_table(self) -> Dict:
        """Create Inventory_Keys_Combined table if it doesn't exist"""
        try:
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'aid', 'KeyType': 'HASH'},
                    {'AttributeName': 'sd', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'aid', 'AttributeType': 'S'},
                    {'AttributeName': 'sd', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            return {'success': True, 'message': 'Inventory_Keys_Combined table created successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error creating Inventory_Keys_Combined table: {str(e)}'}

    def table_exists(self) -> bool:
        """Check if the table exists"""
        try:
            self.dynamodb.Table(self.table_name).table_status
            return True
        except Exception:
            return False

    def clear_table(self) -> Dict:
        """Clear all data from the table"""
        try:
            response = self.table.scan()
            items = response['Items']
            
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])
            
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(
                        Key={
                            'aid': item['aid'],
                            'sd': item['sd']
                        }
                    )
            
            return {
                'success': True,
                'message': f'Successfully cleared {len(items)} items from the table'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error clearing table: {str(e)}'
            }

    def insert_test_data(self, original_items: List[Dict]) -> Dict:
        """Insert compressed test records"""
        try:
            compressed_items = []
            for item in original_items:
                compressed_item = {
                    'aid': item['availabilityId'],  # availabilityId -> aid
                    'sd': item['stayDate'],         # stayDate -> sd
                    's': item['sold'],              # sold -> s
                    'a': item['available'],         # available -> a
                    'ab': item['accumulativeBlock'],# accumulativeBlock -> ab
                    'vid': item['versionId'],       # versionId -> vid
                    'tpid': item['updateTpid'],     # updateTpid -> tpid
                    'tuid': item['updateTuid'],     # updateTuid -> tuid
                    'ud': item['updateDate'],       # updateDate -> ud
                    'cid': item['updateClientId']   # updateClientId -> cid
                }
                compressed_items.append(compressed_item)

            with self.table.batch_writer() as batch:
                for item in compressed_items:
                    batch.put_item(Item=item)

            return {
                'success': True,
                'message': f'Successfully inserted {len(compressed_items)} compressed records',
                'data': compressed_items
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inserting compressed test data: {str(e)}'
            }

    def calculate_table_size(self) -> Dict:
        """Calculate the size of the table"""
        try:
            response = self.table.scan()
            items = response['Items']
            
            total_size_bytes = 0
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])
            
            for item in items:
                # Convert Decimal to int/float before JSON serialization
                converted_item = self._decimal_to_int(item)
                item_size = len(json.dumps(converted_item).encode('utf-8'))
                total_size_bytes += item_size
            
            return {
                'success': True,
                'message': 'Successfully calculated table size',
                'data': {
                    'total_size_bytes': total_size_bytes
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error calculating table size: {str(e)}'
            }

    def _decimal_to_int(self, obj):
        """Convert Decimal objects to int/float for JSON serialization"""
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        elif isinstance(obj, dict):
            return {k: self._decimal_to_int(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._decimal_to_int(item) for item in obj]
        return obj

    def query_all_items(self) -> Dict:
        """Query and display all items from the table"""
        try:
            # Scan all items
            response = self.table.scan()
            
            # Log the raw response
            print("\nRaw DynamoDB Response:")
            print(response)
            print("-" * 80)
            print("ResponseMetadata:", json.dumps(self._decimal_to_int(response.get('ResponseMetadata', {})), indent=2, ensure_ascii=False))
            print("Count:", response.get('Count'))
            print("ScannedCount:", response.get('ScannedCount'))
            print("Items:", json.dumps(self._decimal_to_int(response.get('Items', [])), indent=2, ensure_ascii=False))
            if 'LastEvaluatedKey' in response:
                print("LastEvaluatedKey:", json.dumps(self._decimal_to_int(response['LastEvaluatedKey']), indent=2, ensure_ascii=False))
            print("-" * 80)
         
            items = response['Items']
            
            # Continue scanning if there are more items
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])
            
            # Convert Decimal types and sort items for consistent display
            converted_items = []
            for item in items:
                converted_item = self._decimal_to_int(item)
                # Sort the item keys for consistent output
                sorted_item = {
                    'aid': converted_item['aid'],
                    'sd': converted_item['sd'],
                    's': converted_item['s'],
                    'a': converted_item['a'],
                    'ab': converted_item['ab'],
                    'vid': converted_item['vid'],
                    'tpid': converted_item['tpid'],
                    'tuid': converted_item['tuid'],
                    'ud': converted_item['ud'],
                    'cid': converted_item['cid']
                }
                converted_items.append(sorted_item)
            
            # Print items in a formatted way
            print("\nInventory_Keys_Combined Table Contents:")
            print("-" * 80)
            for item in converted_items:
                print(json.dumps(item, indent=2, ensure_ascii=False))
                print("-" * 80)
            
            return {
                'success': True,
                'message': f'Successfully retrieved {len(items)} items',
                'data': converted_items
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error querying items: {str(e)}'
            }

def calculate_compression_ratio(inventory_table: InventoryTable, combined_table: InventoryKeysCombined) -> Dict:
    """Calculate compression ratio between original and compressed tables"""
    try:
        # Get table sizes
        inventory_result = inventory_table.calculate_table_size()
        combined_result = combined_table.calculate_table_size()
        
        print("\nDebug info:")
        print(f"Inventory result: {inventory_result}")
        print(f"Combined result: {combined_result}")
        
        if not inventory_result['success']:
            raise Exception(f"Failed to calculate inventory table size: {inventory_result['message']}")
        if not combined_result['success']:
            raise Exception(f"Failed to calculate combined table size: {combined_result['message']}")
            
        inventory_size = inventory_result['data']['total_size_bytes']
        combined_size = combined_result['data']['total_size_bytes']

        # Calculate compression ratio
        compression_ratio = (combined_size / inventory_size) * 100 if inventory_size > 0 else 0

        print("\nTable Size Comparison:")
        print("-" * 80)
        print(f"Original Inventory Table Size: {inventory_size:,} bytes")
        print(f"Compressed Keys Combined Table Size: {combined_size:,} bytes")
        print("-" * 80)
        print(f"Compression Ratio: {compression_ratio:.2f}%")
        print(f"Space Saving: {100 - compression_ratio:.2f}%")
        print("-" * 80)

        return {
            'success': True,
            'message': 'Successfully calculated compression ratio',
            'data': {
                'inventory_size': inventory_size,
                'combined_size': combined_size,
                'compression_ratio': compression_ratio
            }
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error calculating compression ratio: {str(e)}'
        }

def test_item_sizes():
    """Test the size difference between items with and without empty string"""
    # Create two identical items except one has an empty string
    item_with_empty = {
        "availabilityId": "test-id-123",
        "stayDate": "2025-02-21",
        "sold": 0,
        "accumulativeBlock": 0,
        "versionId": 1,
        "updateTpid": 1,
        "updateTuid": 1,
        "updateDate": "2025-02-21 12:00:00",
        "updateClientId": 1
    }

    item_with_value = {
        "availabilityId": "test-id-123",
        "stayDate": "2025-02-21",
        "sold": 0,
        "available": "1",  # Non-empty string
        "accumulativeBlock": 0,
        "versionId": 1,
        "updateTpid": 1,
        "updateTuid": 1,
        "updateDate": "2025-02-21 12:00:00",
        "updateClientId": 1
    }

    # Calculate sizes
    size_with_empty = len(json.dumps(item_with_empty).encode('utf-8'))
    size_with_value = len(json.dumps(item_with_value).encode('utf-8'))

    print("\nItem Size Comparison:")
    print("-" * 80)
    print("Item with empty string:")
    print(json.dumps(item_with_empty, indent=2))
    print(f"Size: {size_with_empty} bytes")
    print("-" * 80)
    print("Item with value:")
    print(json.dumps(item_with_value, indent=2))
    print(f"Size: {size_with_value} bytes")
    print("-" * 80)
    print(f"Size difference: {size_with_value - size_with_empty} bytes")
    print(f"Percentage difference: {((size_with_value - size_with_empty) / size_with_empty * 100):.2f}%")
    print("-" * 80)

    return {
        'item_with_empty_size': size_with_empty,
        'item_with_value_size': size_with_value,
        'difference': size_with_value - size_with_empty,
        'percentage_difference': ((size_with_value - size_with_empty) / size_with_empty * 100)
    }

def main():
    # Run size comparison test
    print("\nRunning item size comparison test...")
    test_item_sizes()

    # Initialize both tables
    inventory = InventoryTable()
    combined = InventoryKeysCombined()

    # Handle Inventory table
    if inventory.table_exists():
        print("Inventory table exists, clearing all data...")
        clear_result = inventory.clear_table()
        print(clear_result['message'])
    else:
        print("Creating Inventory table...")
        create_result = inventory.create_table()
        print(create_result['message'])

    # Handle Inventory_Keys_Combined table
    if combined.table_exists():
        print("\nInventory_Keys_Combined table exists, clearing all data...")
        clear_result = combined.clear_table()
        print(clear_result['message'])
    else:
        print("\nCreating Inventory_Keys_Combined table...")
        create_result = combined.create_table()
        print(create_result['message'])

    # Insert test data into Inventory table
    print("\nInserting test data into Inventory table...")
    insert_result = inventory.insert_test_data()
    if insert_result['success']:
        print(insert_result['message'])
        
        # Insert compressed data into combined table
        print("\nInserting compressed data into Inventory_Keys_Combined table...")
        combined_result = combined.insert_test_data(insert_result['data'])
        print(combined_result['message'])

        # Query all items from combined table
        print("\nQuerying all items from Inventory_Keys_Combined table...")
        query_result = combined.query_all_items()
        if not query_result['success']:
            print(f"Error: {query_result['message']}")

        # Calculate and show compression ratio
        print("\nCalculating compression ratio...")
        ratio_result = calculate_compression_ratio(inventory, combined)
        if ratio_result['success']:
            print(ratio_result['message'])
        else:
            print(f"Error: {ratio_result['message']}")
    else:
        print(f"Error: {insert_result['message']}")

if __name__ == "__main__":
    main()
