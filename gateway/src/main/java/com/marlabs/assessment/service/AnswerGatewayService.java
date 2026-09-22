package com.marlabs.assessment.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.marlabs.assessment.api.AnswerRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class AnswerGatewayService {
    private final CallerContextService callerContextService;
    private final PythonAnswerClient pythonAnswerClient;

    public AnswerGatewayService(CallerContextService callerContextService, PythonAnswerClient pythonAnswerClient) {
        this.callerContextService = callerContextService;
        this.pythonAnswerClient = pythonAnswerClient;
    }

    public JsonNode answer(AnswerRequest request) {
        if (!callerContextService.isKnown(request.tenant(), request.role())) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown caller context");
        }
        return pythonAnswerClient.answer(request);
    }
}
