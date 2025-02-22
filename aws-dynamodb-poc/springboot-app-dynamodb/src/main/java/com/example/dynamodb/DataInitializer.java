package com.example.dynamodb;

import com.example.dynamodb.model.Customer;
import com.example.dynamodb.service.CustomerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private CustomerService customerService;

    @Override
    public void run(String... args) throws Exception {
        if (customerService.countCustomers() == 0) {
            for (int i = 1; i <= 10; i++) {
                Customer customer = new Customer();
                customer.setName("Test Customer " + i);
                customer.setEmail("testcustomer" + i + "@example.com");
                customerService.createCustomer(customer);
            }
            System.out.println("Inserted 10 test customers.");
        } else {
            System.out.println("Customers already exist.");
        }
    }
}
