# Spring Boot DynamoDB Application

This is a sample Spring Boot application that demonstrates how to use AWS DynamoDB with Spring Boot.

## Features

- CRUD operations for Customer entity
- DynamoDB Enhanced Client usage
- Local DynamoDB support
- RESTful API endpoints

## Prerequisites

- Java 11
- Maven
- Docker (for local DynamoDB)
- AWS DynamoDB Local

## Setup

1. Start local DynamoDB:
```bash
docker run -p 8000:8000 amazon/dynamodb-local
```

2. Build the application:
```bash
mvn clean install
```

3. Run the application:
```bash
mvn spring-boot:run
```

## API Endpoints

### Customer API

- Create a customer:
```bash
POST /api/customers
Content-Type: application/json

{
    "email": "john@example.com",
    "name": "John Doe",
    "age": 30
}
```

- Get a customer:
```bash
GET /api/customers/{id}?email={email}
```

- Get all customers:
```bash
GET /api/customers
```

- Update a customer:
```bash
PUT /api/customers/{id}?email={email}
Content-Type: application/json

{
    "name": "John Doe Updated",
    "age": 31
}
```

- Delete a customer:
```bash
DELETE /api/customers/{id}?email={email}
```

## Table Structure

The Customer table uses a composite key:
- Partition Key: id (String)
- Sort Key: email (String)

Other attributes:
- name (String)
- age (Integer)
- createdAt (String)

## Configuration

The application is configured to use local DynamoDB by default. Configuration can be found in `application.yml`:

```yaml
aws:
  dynamodb:
    endpoint: http://localhost:8000
    region: us-west-2
    accessKey: dummy
    secretKey: dummy
```

For production, update these values with your AWS credentials and region.
