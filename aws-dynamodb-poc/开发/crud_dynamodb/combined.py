import boto3
from typing import Dict, List
from decimal import Decimal
import random
from datetime import datetime, timedelta
from tqdm import tqdm

class CombinedTableStats:
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

    def calculate_table_size(self, table_name: str) -> Dict:
        """
        Calculate the size of all data in the specified table
        """
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
        """
        Calculate the size of a single item (in bytes)
        """
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
        """
        Count the distribution of restriction combinations in the AvailabilityRestrictionsCombined table
        """
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

def main():
    # Initialize
    stats = CombinedTableStats()
    
    # Store table size information
    table_sizes = {}
    
    # 1. Calculate size of AvailabilityRestrictions table
    print("\n1. Calculating size of AvailabilityRestrictions table:")
    size_result = stats.calculate_table_size(stats.availability_table_name)
    if size_result['success']:
        data = size_result['data']
        table_sizes['availability'] = data
        print(f"\nAvailabilityRestrictions Table:")
        print(f"Total Records: {data['total_items']:,}")
        print(f"Total Size: {data['total_size_bytes']:,} bytes")
        print(f"        = {data['total_size_kb']:.2f} KB")
        print(f"        = {data['total_size_mb']:.2f} MB")
        print(f"Average Record Size: {data['avg_item_size_bytes']:.2f} bytes")
        print("\nSize Distribution:")
        for size_range, count in data['size_distribution'].items():
            print(f"{size_range}: {count:,} records")
    else:
        print(size_result['message'])

    # 2. Calculate size of RestrictionDetail table
    print("\n2. Calculating size of RestrictionDetail table:")
    size_result = stats.calculate_table_size(stats.detail_table_name)
    if size_result['success']:
        data = size_result['data']
        table_sizes['detail'] = data
        print(f"\nRestrictionDetail Table:")
        print(f"Total Records: {data['total_items']:,}")
        print(f"Total Size: {data['total_size_bytes']:,} bytes")
        print(f"        = {data['total_size_kb']:.2f} KB")
        print(f"        = {data['total_size_mb']:.2f} MB")
        print(f"Average Record Size: {data['avg_item_size_bytes']:.2f} bytes")
        print("\nSize Distribution:")
        for size_range, count in data['size_distribution'].items():
            print(f"{size_range}: {count:,} records")
    else:
        print(size_result['message'])

    # 3. Calculate size of AvailabilityRestrictionsCombined table
    print("\n3. Calculating size of AvailabilityRestrictionsCombined table:")
    size_result = stats.calculate_table_size(stats.combined_table_name)
    if size_result['success']:
        data = size_result['data']
        table_sizes['combined'] = data
        print(f"\nAvailabilityRestrictionsCombined Table:")
        print(f"Total Records: {data['total_items']:,}")
        print(f"Total Size: {data['total_size_bytes']:,} bytes")
        print(f"        = {data['total_size_kb']:.2f} KB")
        print(f"        = {data['total_size_mb']:.2f} MB")
        print(f"Average Record Size: {data['avg_item_size_bytes']:.2f} bytes")
        print("\nSize Distribution:")
        for size_range, count in data['size_distribution'].items():
            print(f"{size_range}: {count:,} records")
    else:
        print(size_result['message'])

    # Calculate compression ratio
    if all(k in table_sizes for k in ['availability', 'detail', 'combined']):
        original_size = table_sizes['availability']['total_size_bytes']
        new_size = table_sizes['detail']['total_size_bytes'] + table_sizes['combined']['total_size_bytes']
        compression_ratio = (new_size / original_size) * 100 if original_size > 0 else 0
        
        print("\nData Compression Statistics:")
        print(f"Original Size (AvailabilityRestrictions): {original_size:,} bytes")
        print(f"New Size (RestrictionDetail + AvailabilityRestrictionsCombined): {new_size:,} bytes")
        print(f"Compression Ratio: {compression_ratio:.2f}%")
        print(f"Space Saved: {(100 - compression_ratio):.2f}%")
        
        # Display detailed size comparison
        print("\nDetailed Size Comparison:")
        print(f"AvailabilityRestrictions: {table_sizes['availability']['total_size_mb']:.2f} MB")
        print(f"RestrictionDetail: {table_sizes['detail']['total_size_mb']:.2f} MB")
        print(f"AvailabilityRestrictionsCombined: {table_sizes['combined']['total_size_mb']:.2f} MB")
        print(f"Total New Size: {(table_sizes['detail']['total_size_mb'] + table_sizes['combined']['total_size_mb']):.2f} MB")

    # 4. Count distribution of restriction combinations in AvailabilityRestrictionsCombined
    print("\n4. Analyzing restriction combination distribution in AvailabilityRestrictionsCombined:")
    distribution_result = stats.count_by_restriction_detail()
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
    else:
        print(distribution_result['message'])

if __name__ == "__main__":
    main()
