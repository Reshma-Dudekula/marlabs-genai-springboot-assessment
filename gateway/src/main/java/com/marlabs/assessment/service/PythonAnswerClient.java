package com.marlabs.assessment.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.marlabs.assessment.api.AnswerRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

@Component
public class PythonAnswerClient {
    private final RestClient restClient;

    public PythonAnswerClient(@Value("${python.service.base-url:http://localhost:8001}") String baseUrl,
                              RestClient.Builder builder) {
        this.restClient = builder.baseUrl(baseUrl).build();
    }

    public JsonNode answer(AnswerRequest request) {
        try {
            return restClient.post()
                    .uri("/internal/answer")
                    .body(request)
                    .retrieve()
                    .body(JsonNode.class);
        } catch (Exception exception) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Python answer service unavailable", exception);
        }
    }
}
