package com.example.dynamodb.repository;

import com.example.dynamodb.model.Customer;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.Key;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.enhanced.dynamodb.model.PageIterable;
import software.amazon.awssdk.enhanced.dynamodb.model.QueryConditional;
import software.amazon.awssdk.enhanced.dynamodb.model.QueryEnhancedRequest;

import javax.annotation.PostConstruct;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
@RequiredArgsConstructor
public class CustomerRepository {

    private final DynamoDbEnhancedClient dynamoDbEnhancedClient;
    private DynamoDbTable<Customer> customerTable;

    @PostConstruct
    public void init() {
        customerTable = dynamoDbEnhancedClient.table("Customer", TableSchema.fromBean(Customer.class));
        // Create table if it doesn't exist
        if (!tableExists()) {
            customerTable.createTable();
        }
    }

    private boolean tableExists() {
        try {
            customerTable.describeTable();
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public Customer save(Customer customer) {
        customerTable.putItem(customer);
        return customer;
    }

    public Optional<Customer> findById(String id, String email) {
        Key key = Key.builder()
                .partitionValue(id)
                .sortValue(email)
                .build();
        return Optional.ofNullable(customerTable.getItem(key));
    }

    public List<Customer> findAll() {
        PageIterable<Customer> results = customerTable.scan();
        return results.items().stream().collect(Collectors.toList());
    }

    public void deleteById(String id, String email) {
        Key key = Key.builder()
                .partitionValue(id)
                .sortValue(email)
                .build();
        customerTable.deleteItem(key);
    }

    public long count() {
        return customerTable.scan().items().spliterator().getExactSizeIfKnown();
    }

    public List<Customer> queryByCustomerId(String customerId) {
        QueryConditional queryConditional = QueryConditional.keyEqualTo(Key.builder().partitionValue(customerId).build());
        return customerTable.query(QueryEnhancedRequest.builder()
                .queryConditional(queryConditional)
                .build())
                .items().stream().collect(Collectors.toList());
    }
}
