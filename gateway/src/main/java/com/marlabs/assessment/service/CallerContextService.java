package com.marlabs.assessment.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Service
public class CallerContextService {
    private final ObjectMapper objectMapper;
    private final Set<String> callerKeys = new HashSet<>();

    public CallerContextService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    void loadCallers() throws IOException {
        List<Map<String, String>> callers = objectMapper.readValue(
                new ClassPathResource("callers.json").getInputStream(),
                new TypeReference<>() { }
        );
        callers.forEach(caller -> callerKeys.add(key(caller.get("tenant"), caller.get("role"))));
    }

    public boolean isKnown(String tenant, String role) {
        return callerKeys.contains(key(tenant, role));
    }

    private String key(String tenant, String role) {
        return tenant.trim().toLowerCase() + ":" + role.trim().toLowerCase();
    }
}
