# Requirements Coverage Matrix

This matrix describes the current repository, not a claim of full compliance with the attached Spring Boot/Java assessment brief.

| Requirement | Implemented File | Status |
| --- | --- | --- |
| Python 3.11 app | [requirements.txt](requirements.txt) | Implemented |
| FastAPI app with `/answer` and `/batches` | [app/main.py](app/main.py) | Implemented |
| JSON policy corpus and caller data | [data/policies.json](data/policies.json), [data/callers.json](data/callers.json) | Implemented |
| Dynamic loading of policies | [app/data_loader.py](app/data_loader.py) | Implemented |
| Policy order independence | [app/policy_engine.py](app/policy_engine.py) | Partially tested |
| Eligibility filtering | [app/policy_engine.py](app/policy_engine.py) | Implemented |
| Answer outcomes | [app/answer_service.py](app/answer_service.py) | Implemented, simplified |
| Conflict detection | [app/policy_engine.py](app/policy_engine.py), [app/answer_service.py](app/answer_service.py) | Implemented, simplified |
| Citations with `chunk_id` and verbatim quote | [app/answer_service.py](app/answer_service.py) | Implemented |
| Prompt injection sanitization | [app/extraction.py](app/extraction.py) | Implemented, limited |
| Batch manifest validation | [app/validators.py](app/validators.py) | Implemented |
| Duplicate detection via SHA256 | [app/duplicate_detector.py](app/duplicate_detector.py), [app/validators.py](app/validators.py) | Implemented |
| PDF extraction using PyPDF2 | [app/extraction.py](app/extraction.py), [app/batch_service.py](app/batch_service.py) | Implemented for direct helper use and PDF batch content |
| Review issues and required review flag | [app/answer_service.py](app/answer_service.py), [app/extraction.py](app/extraction.py) | Implemented, simplified |
| Failure handling for unreadable PDF | [app/extraction.py](app/extraction.py) | Implemented for direct helper use |
| Python test suite | [tests/test_assessment.py](tests/test_assessment.py) | 31 tests pass; important gaps remain |
| Spring Boot test suite | [gateway/src/test/java](gateway/src/test/java) | 3 tests pass; BUILD SUCCESS |
| Docker packaging | [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml) | Defined; Docker unavailable in this environment |
| Documentation | [README.md](README.md) | Implemented with scope disclaimer |
| Spring Boot/Java public application | [gateway/pom.xml](gateway/pom.xml), [gateway/src/main/java](gateway/src/main/java) | Implemented |
| Strict HTTP request validation | [app/main.py](app/main.py), [app/models.py](app/models.py) | Implemented |
| Policy amount-limit enforcement | [app/answer_service.py](app/answer_service.py) | Implemented for a single eligible policy |
| Caller registry validation | [gateway/src/main/java/com/marlabs/assessment/service/CallerContextService.java](gateway/src/main/java/com/marlabs/assessment/service/CallerContextService.java) | Implemented by Spring gateway |
| Provider integration | [app/answer_service.py](app/answer_service.py) | Stub only |
| Batch policy evaluation with tenant/role/date context | [app/batch_service.py](app/batch_service.py) | Missing from batch contract |
