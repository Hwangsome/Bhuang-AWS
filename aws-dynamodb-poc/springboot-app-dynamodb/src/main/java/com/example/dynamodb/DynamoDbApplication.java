package com.example.dynamodb;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * doc: https://medium.com/@sudacgb/integrate-aws-dynamodb-with-spring-boot-dc62b9ceae96
 */
@SpringBootApplication
public class DynamoDbApplication {
    public static void main(String[] args) {
        SpringApplication.run(DynamoDbApplication.class, args);
    }
}
