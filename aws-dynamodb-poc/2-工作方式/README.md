# 工作方式

---





# notes

# 核心组件


## 分区键 & 排序键
![img.png](..%2Fimg%2Fimg.png)
- 分区键：决定数据存储在哪个分区
- 排序键：决定数据在分区内的排序


---
在 AWS DynamoDB 中，表的主键可以有两种类型：简单主键和复合主键。

1. **简单主键**：这种主键只由一个分区键组成。在这种情况下，分区键的值必须是唯一的，以确保表中每个项（Item）的唯一性。每个项都可以通过其分区键进行快速、直接的访问。

2. **复合主键**：复合主键由两个部分组成：分区键和排序键（Sort Key）。在这种情况下，分区键负责数据的分布和分区，而排序键则允许在同一个分区内根据一定的顺序存储多个项。具体来说，具有相同分区键的项目可以根据其排序键进行排序和查询。

### 总结

- **一个分区键**：对于简单主键的表，只能有一个分区键。
- **一个分区键和一个排序键**：对于复合主键的表，可以有一个分区键和一个排序键，允许更灵活的数据组织。

因此，可以说，你可以根据需要选择使用一个分区键或者一个分区键加排序键的组合来构建 DynamoDB 表。这样的灵活性使得用户可以根据应用程序的需求进行优化。


## 二级索引
![img_1.png](..%2Fimg%2Fimg_1.png)

---
在 AWS DynamoDB 中，二级索引（Secondary Index）是用于为表的其他属性创建索引的机制。通过二级索引，您可以对数据进行不同的查询而无需扫描整个表，从而提高检索效率。

### 二级索引的种类

1. **全局二级索引（Global Secondary Index, GSI）**：
    - **定义**：GSI 允许您在表的任何属性上创建索引，并且不需要与表的主键（分区键和排序键）相同。在 GSI 中，您可以指定一个分区键（和可选的排序键）。
    - **查询能力**：您可以通过 GSI 查询与主表不同的属性，并以 GSI 的分区键进行快速查询。
    - **一致性**：GSI 提供最终一致性读取，默认情况下，您可以在数据写入后立即查询 GSI，但结果可能与表中的数据存在延迟。

2. **本地二级索引（Local Secondary Index, LSI）**：
    - **定义**：LSI 允许您在同一分区键下使用不同的排序键。换句话说，它们与表的分区键相同，但可以选择不同的排序键。
    - **查询能力**：LSI 适用于需要在同一分区下对数据进行不同排序或过滤的场景。例如，您可能希望按发布日期或其他属性对同一组项进行查询。
    - **一致性**：LSI 支持强一致性读取，即在数据项被写入后，您可以立即通过 LSI 查询到最新的数据。

### 二级索引的使用场景

- **查询优化**：当您需要在表的多个属性上执行查询时，二级索引提供了一种高效的检索方式。
- **多样化查询**：通过 GSI 和 LSI，您可以使用不同的属性进行查询，改进数据访问模式。
- **数据分析**：如果您需要分析特定属性的数据，例如按用户或时间范围进行过滤，二级索引可以帮助高效实现。

### 创建和管理二级索引

1. **创建索引**：在创建 DynamoDB 表时，您可以同时定义一个或多个二级索引。您需要为每个索引指定名称、分区键和可选的排序键。

2. **读取和写入**：对于 GSI 和 LSI，所有的写操作（插入、更新、删除）会自动影响相关的索引。因此，无论对主表进行何种修改，索引都会自动更新。

3. **成本**：使用二级索引会增加存储和读取费用。因为每个二级索引在后台维护着自己的数据副本。

### 注意事项

- **性能**：尽管二级索引提高了查询性能，但也可能增加数据写入延迟，因为每次写操作都需要更新索引。
- **属性限制**：每个索引的键属性数量和类型必须符合 DynamoDB 的限制。
- **最大数量**：一个表最多可以有 20 个全局二级索引和 5 个本地二级索引。

## usecase
### 用例 1：电子商务平台产品查询

**场景**：在电子商务平台中，您需要存储产品信息，用户可以根据类别和价格范围来搜索产品。

#### 表结构（JSON）

```json
{
  "TableName": "Products",
  "KeySchema": [
    {
      "AttributeName": "ProductID",
      "KeyType": "HASH"  // Partition Key
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "ProductID",
      "AttributeType": "S"  // String
    },
    {
      "AttributeName": "Category",
      "AttributeType": "S"  // String
    },
    {
      "AttributeName": "Price",
      "AttributeType": "N"  // Number
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "CategoryIndex",
      "KeySchema": [
        {
          "AttributeName": "Category",
          "KeyType": "HASH"  // Partition Key
        },
        {
          "AttributeName": "Price",
          "KeyType": "RANGE" // Sort Key
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    }
  ],
  "ProvisionedThroughput": {
    "ReadCapacityUnits": 5,
    "WriteCapacityUnits": 5
  }
}
```

### 用例 2：社交网络帖子查询

**场景**：在一个社交网络应用中，用户可以发布帖子。您需要能够根据用户 ID 查询该用户的所有帖子，并且按发布时间排序。

#### 表结构（JSON）

```json
{
  "TableName": "Posts",
  "KeySchema": [
    {
      "AttributeName": "PostID",
      "KeyType": "HASH"  // Partition Key
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "PostID",
      "AttributeType": "S"  // String
    },
    {
      "AttributeName": "UserID",
      "AttributeType": "S"  // String
    },
    {
      "AttributeName": "CreatedAt",
      "AttributeType": "S"  // String, e.g., ISO 8601 format
    }
  ],
  "LocalSecondaryIndexes": [
    {
      "IndexName": "UserPostsIndex",
      "KeySchema": [
        {
          "AttributeName": "UserID",
          "KeyType": "HASH"  // Partition Key
        },
        {
          "AttributeName": "CreatedAt",
          "KeyType": "RANGE" // Sort Key
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    }
  ],
  "ProvisionedThroughput": {
    "ReadCapacityUnits": 5,
    "WriteCapacityUnits": 5
  }
}
```

### 总结

AWS DynamoDB 的二级索引（GSI 和 LSI）为开发者提供了灵活的查询机制，以满足各种数据检索需求。合理使用二级索引可以显著提高数据访问效率，但也需要谨慎管理，以应对潜在的成本和性能问题。利用好二级索引，将有助于构建高效的可扩展应用程序。



# doc
[Amazon DynamoDB 的核心组件](https://docs.aws.amazon.com/zh_cn/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html)