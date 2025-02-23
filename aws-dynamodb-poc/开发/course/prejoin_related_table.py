import boto3

# Initialize a session using Boto3 for local DynamoDB
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# Function to check if the Products table exists
def table_exists(table_name):
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    return table_name in existing_tables

# Function to create the Products table
def create_products_table():
    table = dynamodb.create_table(
        TableName='Products',
        KeySchema=[
            {
                'AttributeName': 'ProductID',  # Partition Key
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'Characteristic',  # Sort Key
                'KeyType': 'RANGE'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ProductID',
                'AttributeType': 'S'  # S for String
            },
            {
                'AttributeName': 'Characteristic',
                'AttributeType': 'S'  # S for String
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait for the table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName='Products')
    print("Table created successfully!")

# Function to insert test data into the Products table
def insert_test_data():
    table = dynamodb.Table('Products')
    
    # Define the test data
    test_data = [
        {
            'ProductID': f'PROD#{i}',
            'Characteristic': 'prod_details',
            'COLOR': ['red', 'white', 'blue'],
            'COUNT': i,
            'DESCRIPTION': f'Product {i} description',
            'NAME': f'Product {i}'
        } for i in range(1, 11)
    ]
    
    # Insert each item
    for item in test_data:
        table.put_item(Item=item)
        print(f"Inserted item: {item['ProductID']}")

# Main execution
if __name__ == '__main__':
    if not table_exists('Products'):
        create_products_table()
    insert_test_data()