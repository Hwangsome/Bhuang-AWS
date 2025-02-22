package com.example.dynamodb.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.net.URI;

@Configuration
public class DynamoDbConfig {

    @Value("${aws.dynamodb.endpoint}")
    private String dynamoDbEndpoint;

    @Value("${aws.dynamodb.region}")
    private String awsRegion;

    @Value("${aws.dynamodb.accessKey}")
    private String accessKey;

    @Value("${aws.dynamodb.secretKey}")
    private String secretKey;

    /**
     * DynamoDBClient vs DynamoDBMapper
     * AWS DynamoDB SDK provides two ways to interact with DynamoDB: DynamoDBClient and DynamoDBMapper.
     * If you prefer manual serialization and deserialization of Java objects using libraries like Jackson or Gson and need to handle low-level details,
     * DynamoDBClient is the choice. On the other hand, DynamoDBMapper simplifies the process by automatically mapping Java objects
     * to DynamoDB items and vice versa using annotations. And DynamoDBMapper use annotation-based mapping:
     * you can annotation your Java classes and fields with annotations like ‘@DynamoDBTable’, ‘DynamoDBHashKey’, ‘DynamoDBRangeKey’, etc.,
     * to define the mapping between Java objects and DynamoDB items.
     * @return
     */
    @Bean
    public DynamoDbClient dynamoDbClient() {
        return DynamoDbClient.builder()
                .endpointOverride(URI.create(dynamoDbEndpoint))
                .region(Region.of(awsRegion))
                .credentialsProvider(StaticCredentialsProvider.create(
                        AwsBasicCredentials.create(accessKey, secretKey)))
                .build();
    }

    @Bean
    public DynamoDbEnhancedClient dynamoDbEnhancedClient(DynamoDbClient dynamoDbClient) {
        return DynamoDbEnhancedClient.builder()
                .dynamoDbClient(dynamoDbClient)
                .build();
    }
}
