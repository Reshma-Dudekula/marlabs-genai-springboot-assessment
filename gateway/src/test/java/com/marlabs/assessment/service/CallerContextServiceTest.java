package com.marlabs.assessment.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class CallerContextServiceTest {
    @Test
    void loadsKnownCallerContext() throws Exception {
        CallerContextService service = new CallerContextService(new ObjectMapper());
        service.loadCallers();

        assertTrue(service.isKnown("acme", "manager"));
    }
}
