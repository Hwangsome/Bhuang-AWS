package com.example.dynamodb.controller;

import com.example.dynamodb.model.Customer;
import com.example.dynamodb.service.CustomerService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/customers")
@RequiredArgsConstructor
public class CustomerController {

    private final CustomerService customerService;

    @PostMapping
    public ResponseEntity<Customer> createCustomer(@RequestBody Customer customer) {
        return ResponseEntity.ok(customerService.createCustomer(customer));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Customer> getCustomer(@PathVariable String id, @RequestParam String email) {
        return ResponseEntity.ok(customerService.getCustomer(id, email));
    }

    @GetMapping
    public ResponseEntity<List<Customer>> getAllCustomers() {
        return ResponseEntity.ok(customerService.getAllCustomers());
    }

    @PutMapping("/{id}")
    public ResponseEntity<Customer> updateCustomer(
            @PathVariable String id,
            @RequestParam String email,
            @RequestBody Customer customer) {
        return ResponseEntity.ok(customerService.updateCustomer(id, email, customer));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCustomer(@PathVariable String id, @RequestParam String email) {
        customerService.deleteCustomer(id, email);
        return ResponseEntity.ok().build();
    }
}
