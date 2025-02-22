package com.example.dynamodb.service;

import com.example.dynamodb.model.Customer;
import com.example.dynamodb.repository.CustomerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class CustomerService {

    private final CustomerRepository customerRepository;

    public Customer createCustomer(Customer customer) {
        customer.setId(UUID.randomUUID().toString());
        customer.setCreatedAt(LocalDateTime.now().toString());
        return customerRepository.save(customer);
    }

    public Customer getCustomer(String id, String email) {
        return customerRepository.findById(id, email)
                .orElseThrow(() -> new RuntimeException("Customer not found"));
    }

    public List<Customer> getAllCustomers() {
        return customerRepository.findAll();
    }

    public Customer updateCustomer(String id, String email, Customer customer) {
        Customer existingCustomer = getCustomer(id, email);
        customer.setId(existingCustomer.getId());
        customer.setEmail(existingCustomer.getEmail());
        customer.setCreatedAt(existingCustomer.getCreatedAt());
        return customerRepository.save(customer);
    }

    public void deleteCustomer(String id, String email) {
        customerRepository.deleteById(id, email);
    }

    public long countCustomers() {
        return customerRepository.count();
    }
}
