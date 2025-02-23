import boto3

# Initialize a session using Boto3 for local DynamoDB
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# Function to check if the Warehouses table exists
def table_exists(table_name):
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    return table_name in existing_tables

# Function to create the Warehouses table
def create_warehouses_table():
    table = dynamodb.create_table(
        TableName='Warehouses',
        KeySchema=[
            {
                'AttributeName': 'Country',  # Partition Key
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'Region#Airport#WarehouseID',  # Sort Key
                'KeyType': 'RANGE'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Country',
                'AttributeType': 'S'  # S for String
            },
            {
                'AttributeName': 'Region#Airport#WarehouseID',
                'AttributeType': 'S'  # S for String
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait for the table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName='Warehouses')
    print("Table created successfully!")

# Function to insert test data into the Warehouses table
def insert_test_data():
    table = dynamodb.Table('Warehouses')
    items = [
        {'Country': 'USA', 'Region#Airport#WarehouseID': 'CA#SFO#WH3', 'Description': 'Warehouse in California near SFO'},
        {'Country': 'USA', 'Region#Airport#WarehouseID': 'CA#LAX#WH4', 'Description': 'Warehouse in California near LAX'},
        {'Country': 'USA', 'Region#Airport#WarehouseID': 'NJ#EWR#WH1', 'Description': 'Warehouse in New Jersey near EWR'},
        {'Country': 'France', 'Region#Airport#WarehouseID': 'Paris#CDG#WH6', 'Description': 'Warehouse in Paris near CDG'},
        {'Country': 'France', 'Region#Airport#WarehouseID': 'Clichy#ORY#WH8', 'Description': 'Warehouse in Clichy near ORY'}
    ]
    
    for item in items:
        table.put_item(Item=item)
        print(f"Inserted item: {item['Region#Airport#WarehouseID']}")

# Main execution
if __name__ == '__main__':
    if not table_exists('Warehouses'):
        create_warehouses_table()
    insert_test_data()