package com.marlabs.assessment.api;

import com.fasterxml.jackson.databind.JsonNode;
import com.marlabs.assessment.service.AnswerGatewayService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping({"/api", ""})
public class AnswerController {
    private final AnswerGatewayService service;

    public AnswerController(AnswerGatewayService service) {
        this.service = service;
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("{\"status\":\"ok\"}");
    }

    @PostMapping("/answer")
    public JsonNode answer(@Valid @RequestBody AnswerRequest request) {
        return service.answer(request);
    }
}
