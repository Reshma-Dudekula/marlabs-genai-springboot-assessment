# Marlabs GenAI Assessment

This repository contains the requested two-service implementation. Spring Boot owns the public API, caller context, request validation, and public response. Python 3.11 handles document extraction, policy retrieval, and answer generation behind the gateway.

## Architecture

- `gateway/`: Spring Boot public API on port `8080`
- `app/main.py`: internal FastAPI service on port `8001`
- `app/data_loader.py`: loads policy/caller JSON data
- `app/policy_engine.py`: eligibility and conflict evaluation
- `app/extraction.py`: sanitizes text and extracts values from TXT/PDF inputs
- `app/answer_service.py`: resolves `ANSWERED`, `INSUFFICIENT_EVIDENCE`, and `CONFLICT`
- `app/batch_service.py`: processes batch items while preserving order
- `app/duplicate_detector.py`: SHA256 duplicate detection
- `app/validators.py`: manifest validation and metadata checks
- `data/policies.json`: policy corpus
- `data/callers.json`: caller registry
- `tests/test_assessment.py`: automated validation suite
- `gateway/src/test/`: Spring Boot validation tests

## Prerequisites

- Python 3.11
- Java 17
- Maven 3.9+
- pip
- Docker (optional, for container validation)

## Setup

From the project root:

```powershell
Set-Location "D:\project task\marlabs-genai-springboot-assessment"

& "C:\Python311\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The verified machine paths are:

```powershell
$env:JAVA_HOME = "C:\Tools\jdk-17.0.20.1+1"
$env:MAVEN_HOME = "C:\Tools\apache-maven-3.9.9"
$env:Path = "$env:JAVA_HOME\bin;$env:MAVEN_HOME\bin;$env:Path"
```

## Execution Steps

### 1) Start the Python service

Open **Terminal 1** and run:

```powershell
Set-Location "D:\project task\marlabs-genai-springboot-assessment"
& "C:\Python311\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

The service will be available at:

```text
http://127.0.0.1:8001
```

Keep this terminal running. Spring Boot uses this service for document processing and answer generation.

### 2) Start the Spring Boot public API

Open **Terminal 2** and run:

```powershell
Set-Location "D:\project task\marlabs-genai-springboot-assessment\gateway"
$env:JAVA_HOME = "C:\Tools\jdk-17.0.20.1+1"
$env:MAVEN_HOME = "C:\Tools\apache-maven-3.9.9"
$env:Path = "$env:JAVA_HOME\bin;$env:MAVEN_HOME\bin;$env:Path"
& "C:\Tools\apache-maven-3.9.9\bin\mvn.cmd" spring-boot:run
```

Successful startup includes these messages:

```text
Tomcat started on port 8080
Started AssessmentGatewayApplication
```

These messages mean the Spring Boot public API is running. Keep this terminal open.

The public API will be available at:

```text
http://127.0.0.1:8080/api
```

### 3) Run the Python test suite

From the project root:

```powershell
Set-Location "D:\project task\marlabs-genai-springboot-assessment"
& "C:\Python311\python.exe" -m pytest -q
```

### 4) Run the Spring Boot test suite

```powershell
Set-Location "D:\project task\marlabs-genai-springboot-assessment\gateway"
$env:JAVA_HOME = "C:\Tools\jdk-17.0.20.1+1"
$env:MAVEN_HOME = "C:\Tools\apache-maven-3.9.9"
$env:Path = "$env:JAVA_HOME\bin;$env:MAVEN_HOME\bin;$env:Path"
& "C:\Tools\apache-maven-3.9.9\bin\mvn.cmd" test
```

### 5) Validate the public health endpoint

Open **Terminal 3** while both services are running:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/health
```

Expected response:

```json
{"status":"ok"}
```

### 6) Exercise the public answer endpoint

```powershell
$payload = @{
  tenant = "acme"
  role = "manager"
  as_of = "2025-12-30"
  document_text = "Benefit: Travel`nAmount: 22000`nCurrency: USD`nReference: REF-1"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8080/api/answer" `
  -Method Post `
  -ContentType "application/json" `
  -Body $payload
```

The request must be sent to Spring Boot on port `8080`. Spring Boot validates the request and caller context, then calls Python on port `8001`. A successful request returns a JSON result such as `ANSWERED`, `CONFLICT`, or `INSUFFICIENT_EVIDENCE`.

To stop either running service, press `Ctrl+C` in its terminal.

The Spring Boot gateway validates the caller context and forwards the request to Python's internal `/internal/answer` endpoint. The Python service should not be treated as the public API.

### 7) Exercise the legacy Python batch endpoint

```powershell
$batch = @{
  documents = @(
    @{ document_id = "d1"; filename = "request-01.txt"; content = "Benefit: Travel`nAmount: 22000`nCurrency: USD`nReference: REF-1" },
    @{ document_id = "d2"; filename = "request-06.txt"; content = "Benefit: Travel`nAmount: 22000`nCurrency: USD`nReference: REF-1" }
  )
} | ConvertTo-Json -Depth 4

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8001/batches" `
  -Method Post `
  -ContentType "application/json" `
  -Body $batch
```

## Docker Commands

Build and run:

```powershell
docker compose up --build
```

Stop containers:

```powershell
docker compose down
```

## Pytest Troubleshooting

Use the Python 3.11 interpreter explicitly. On this machine, plain `pytest` resolves to Python 3.14 and can fail during test collection.

```powershell
Set-Location "D:\project task\marlabs-genai-springboot-assessment"
& "C:\Python311\python.exe" -m pytest -q
```

Verified result: `31 passed`.

## Sample Output

```json
{"result": "ANSWERED", "benefit": "Travel", "amount": 22000, "currency": "USD", "review_required": true}
```

```json
{"result": "INSUFFICIENT_EVIDENCE", "review_issues": ["Insufficient evidence for policy evaluation"]}
```

```json
{"result": "CONFLICT", "review_issues": ["Conflicting eligible policies detected"]}
```

## Assumptions

- This repository implements the simplified Python-based assessment workflow used in this session.
- Policy and caller data are stored in JSON under the `data/` directory.
- Content is treated as untrusted; fields are sanitized before evaluation.
- The solution uses local sample files and deterministic logic rather than external paid AI services.
- Duplicate detection is based on SHA256 content hashes.

## Important note about the assessment brief

The public contract is implemented by Spring Boot. Python remains an internal service for extraction, policy evaluation, and answer generation.

## Audit Status

This repository now includes the Spring Boot public gateway and the Python internal service. Remaining limitations are:

- policy evaluation in batch processing; batch items currently do not carry tenant/role/date context
- full multipart/file-upload handling for PDF batch submissions
- a real external provider integration

Verified test status:

- Python: `31 passed`
- Spring Boot: `3 tests passed; BUILD SUCCESS`
- Docker: not verified because Docker is not installed in the current environment

See [requirements-coverage.md](requirements-coverage.md) for the detailed coverage and known gaps.
