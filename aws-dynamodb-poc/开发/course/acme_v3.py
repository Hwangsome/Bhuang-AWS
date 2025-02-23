import boto3
from boto3.dynamodb.conditions import Key

# Initialize a session using Boto3 for local DynamoDB
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# Function to check if the table exists
def table_exists(table_name):
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    return table_name in existing_tables

# Function to create the acme-bank-v3 table
# def create_acme_bank_table():
    table = dynamodb.create_table(
        TableName='acme-bank-v3',
        KeySchema=[
            {
                'AttributeName': 'PK',  # Partition Key
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'SK',  # Sort Key
                'KeyType': 'RANGE'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'PK',
                'AttributeType': 'S'  # S for String
            },
            {
                'AttributeName': 'SK',
                'AttributeType': 'S'  # S for String
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait for the table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName='acme-bank-v3')
    print("Table 'acme-bank-v3' created successfully!")

# Function to insert data into the acme-bank-v3 table
def insert_acme_bank_data():
    table = dynamodb.Table('acme-bank-v3')
    data = [
        {'PK': 'CUST#101', 'SK': 'CUST#101', 'fname': 'john', 'lname': 'doe', 'phone': '555-555-5555'},
        {'PK': 'CUST#102', 'SK': 'CUST#102', 'fname': 'jane', 'lname': 'doe', 'phone': '555-555-5566'},
        {'PK': 'CUST#101', 'SK': 'ACCT#501', 'acct_type': 'checking', 'acct_balance': 534},
        {'PK': 'CUST#101', 'SK': 'ACCT#672', 'acct_type': 'saving', 'acct_balance': 100},
        {'PK': 'CUST#102', 'SK': 'ACCT#510', 'acct_type': 'checking', 'acct_balance': 1000}
    ]
    for item in data:
        table.put_item(Item=item)
        print(f"Inserted item: {item['PK']} - {item['SK']}")

# Function to get all accounts for a customer
def get_all_accounts_for_customer(customer_id):
    table = dynamodb.Table('acme-bank-v3')
    response = table.query(
        KeyConditionExpression=Key('PK').eq(customer_id) & Key('SK').begins_with('ACCT#')
    )
    return response.get('Items', [])

# Function to get all accounts for a customer of specific account type
def get_accounts_by_type(customer_id, account_type):
    accounts = get_all_accounts_for_customer(customer_id)
    return [account for account in accounts if account.get('acct_type') == account_type]

# Function to get customer for an account
def get_customer_for_account(customer_id, account_id):
    table = dynamodb.Table('acme-bank-v3')
    response = table.query(
        KeyConditionExpression=Key('PK').eq(customer_id) & Key('SK').eq(account_id)
    )
    return response.get('Items', [])

def get_customer_for_account_v4(account_id):
    table = dynamodb.Table('acme-bank-v4')
    response = table.query(
        IndexName="GSI_Inverted",
        KeyConditionExpression=Key('SK').eq(account_id)
    )
    for item in response['Items']:
        print(item)
        if item['SK'] == account_id:
            return item.get('PK', None)
    return None




# Function to get account balance for an account
def get_account_balance(account_id):
    table = dynamodb.Table('acme-bank-v3') 
    response = table.query(
        IndexName="AccountIndex",
        KeyConditionExpression=Key('SK').eq(account_id)
    )
    
    # 查找账户余额
    for item in response['Items']:
        print(item)
        if item['SK'] == account_id:  # 确保获取的是对应账户的项
            return item.get('acct_balance', 0)  # 直接返回 Decimal 值

    return None  # 如果没有找到账户或余额

# Main execution
if __name__ == '__main__':
    # if not table_exists('acme-bank-v3'):
    #     create_acme_bank_table()
    # insert_acme_bank_data()

    # Example usages
    # print("All accounts for customer CUST#101:", get_all_accounts_for_customer('CUST#101'))
    # print("Checking accounts for customer CUST#101:", get_accounts_by_type('CUST#101', 'checking'))
    # print("Customer for account ACCT#501:", get_customer_for_account('CUST#101','ACCT#501'))
    # print("Balance for account ACCT#501:", get_account_balance('ACCT#510'))
    print("Customer for account ACCT#510:", get_customer_for_account_v4('ACCT#510'))
