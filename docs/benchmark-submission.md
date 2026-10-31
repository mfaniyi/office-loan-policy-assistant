# Office Loan Policy Assistant
## AI/ML Engineering Capstone — Benchmark Submission

**Submitted by:** Michael O. Faniyi  
**Project Type:** AI/ML Engineering Capstone  
**Project Version:** 1.0.0

---

## 1. Executive Summary

The Office Loan Policy Assistant is an AI-powered application developed to help employees understand organizational loan policies, calculate potential loan repayments, and assess their eligibility for available loan facilities.

The application combines conventional backend engineering with Retrieval-Augmented Generation (RAG) to provide policy guidance grounded in organizational documents.

The solution includes a React frontend, FastAPI backend, PostgreSQL database with pgvector, and an LLM integration through Microsoft Foundry.

The application was containerized and deployed to Microsoft Azure, with security controls and application monitoring implemented as part of the deployment.

## 2. Problem Statement

Employees may find organizational loan policies difficult to interpret, particularly when policies contain eligibility requirements, repayment conditions, and other financial provisions.

Manual interpretation can create delays and inconsistencies.

The project addresses this challenge by providing a centralized assistant that supports policy enquiries, loan calculations, and employee loan assessments.

## 3. Project Objectives

The objectives were to:

1. Develop an AI-powered assistant for organizational loan policy guidance.
2. Implement document ingestion and retrieval using RAG.
3. Provide loan repayment calculations.
4. Support employee loan eligibility assessment.
5. Develop secure authentication and API services.
6. Containerize and deploy the application.
7. Implement automated testing.
8. Apply Azure security hardening.
9. Establish application monitoring and observability.
10. Produce technical documentation suitable for handover and evaluation.

## 4. Technology Stack

| Area | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend | React 19, TypeScript |
| Frontend Build Tool | Vite |
| Database | PostgreSQL |
| Vector Database Extension | pgvector |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| AI Integration | Microsoft Foundry |
| LLM Client | OpenAI SDK |
| Embeddings | Sentence Transformers |
| Retrieval | Hybrid Search |
| Reranking | Cross-Encoder |
| API Security | JWT, Argon2, SlowAPI |
| Containerization | Docker |
| Package Management | uv |
| Cloud Platform | Microsoft Azure |
| Container Registry | Azure Container Registry |
| Application Hosting | Azure Container Apps |
| Secret Management | Azure Key Vault |
| Identity | Azure Managed Identity |
| Monitoring | Azure Monitor, Application Insights, OpenTelemetry |
| Testing | pytest |

## 5. Application Features

### 5.1 Employee Authentication
- Secure employee login.
- JWT-based authentication.
- Argon2 password hashing.

### 5.2 Loan Calculation
- Calculate potential loan repayments.
- Calculate loan interest.
- Provide loan-related assessment information.

### 5.3 Policy Assistance
- Accept employee questions about organizational loan policies.
- Retrieve relevant policy document sections.
- Evaluate retrieved evidence.
- Generate responses using the configured LLM service.

### 5.4 Employee Assessment
- Support employee loan assessment.
- Apply configured eligibility and business rules.

## 6. AI and RAG Implementation

The policy assistant implements a modular RAG pipeline.

The workflow consists of:

1. Policy document ingestion.
2. Document chunking.
3. Embedding generation.
4. Vector storage using PostgreSQL and pgvector.
5. Hybrid retrieval.
6. Cross-encoder reranking.
7. Evidence evaluation.
8. Answerability assessment.
9. LLM-based answer generation.

The pipeline separates document retrieval, evidence evaluation, and answer generation to support grounded policy responses.

## 7. System Architecture

The application is organized into six major layers:

- Presentation layer: React and TypeScript.
- API layer: FastAPI routers.
- Business logic layer: Loan, eligibility, and authentication services.
- AI layer: RAG and LLM services.
- Data layer: PostgreSQL and pgvector.
- Infrastructure layer: Docker and Azure services.

Detailed architecture documentation is available in `architecture.md`.

## 8. Testing and Validation

The project includes automated tests covering:

- Authentication.
- Database configuration.
- Eligibility.
- Loan API operations.
- Loan services.
- Application startup.
- Personal loan functionality.
- RAG functionality.
- Security.

### Recorded Test Evidence

A previous full test run completed with:

**87 tests passed, 10 warnings.**

The application was also validated through deployed API operations, including:

- Authentication.
- Employee profile retrieval.
- Loan calculations.
- Interest calculations.
- Loan assessments.
- Policy questions.

The tested API operations returned successful HTTP responses.

## 9. Containerization and Cloud Deployment

The application was containerized and deployed to Microsoft Azure.

The backend and frontend run as separate Azure Container Apps.

Azure Container Registry stores the application images.

PostgreSQL Flexible Server provides persistent database storage.

### Deployed Infrastructure

- Resource Group: `rg-secure-candidate`
- Container Apps Environment: `secure-candidate-env`
- Container Registry: `securecandidateacr`
- Backend App: `office-loan-policy-assistant-api`
- Frontend App: `office-loan-frontend`
- PostgreSQL Server: `secure-candidate-pg-wc`
- Database: `office_loan_policy_db`

The backend API root returned HTTP 200 during deployment validation, and the frontend login and employee dashboard were accessed successfully.

## 10. Security Hardening

Security improvements include:

- JWT-based authentication.
- Argon2 password hashing.
- API rate limiting.
- Restricted CORS configuration.
- Azure Key Vault secret management.
- User-assigned Managed Identity.
- Managed identity-based access to Azure resources.
- Azure Container Registry pull permissions.
- TLS-secured PostgreSQL connectivity.
- Environment-based configuration.
- Separation of secrets from source code.

The backend uses a Key Vault-backed Container Apps secret reference for the Application Insights connection string.

## 11. Monitoring and Observability

Azure Application Insights was integrated using Azure Monitor OpenTelemetry.

A shared Azure Monitor Workbook was created:

**Office Loan Policy Assistant Monitoring Workbook**

The workbook contains six monitoring panels:

1. API Request Volume.
2. Successful vs Failed Requests.
3. Average and P95 API Latency.
4. Dependency Performance.
5. Application Logs by Severity.
6. Application Exceptions.

### Initial Monitoring Evidence

| Metric | Observed Value |
|---|---:|
| Successful requests | 4 |
| Average API latency | 14.25 ms |
| P95 API latency | 29 ms |
| HTTP dependency calls | 21 |
| HTTP dependency failures | 0 |
| Informational-level logs | 7 |
| Recorded exceptions | No results |

These are initial observations from a limited sample, not results from a formal load test.

The exception panel returned no results during the observed period.

## 12. Engineering Decisions and Trade-offs

### Modular application architecture
The application separates API routes, business logic, database models, and AI services to improve maintainability.

### PostgreSQL with pgvector
A single database platform supports relational application records and vector-based document retrieval.

### Hybrid retrieval and reranking
The retrieval pipeline combines complementary search approaches and reranking to improve the relevance of retrieved policy information.

### Containerized deployment
Docker and Azure Container Apps provide a repeatable deployment model for the frontend and backend.

### Managed identity and Key Vault
Azure identity and secret-management services reduce the need to embed sensitive credentials in application configuration.

### Application Insights
Centralized telemetry supports operational visibility without requiring manual inspection of container logs alone.

## 13. Risks and Limitations

The following limitations remain relevant:

1. The initial monitoring sample is too small to establish production performance baselines.
2. Retrieval quality requires further evaluation using a larger and more representative question set.
3. Database dependency telemetry has not yet been independently verified.
4. Exception telemetry has been configured, but actual exception capture has not been demonstrated.
5. Additional load and resilience testing would strengthen deployment confidence.
6. The AI assistant depends on the availability and configuration of its external LLM service.

## 14. Future Improvements

Potential improvements include:

- Expand the RAG evaluation dataset.
- Measure retrieval precision, recall, and ranking quality.
- Evaluate answer faithfulness and groundedness.
- Add representative load and stress tests.
- Validate PostgreSQL dependency telemetry.
- Conduct controlled exception-capture testing.
- Improve operational alerting.
- Introduce CI/CD automation.
- Expand application audit logging.
- Improve user experience and accessibility.

## 15. Conclusion

The Office Loan Policy Assistant demonstrates the integration of backend engineering, frontend development, relational and vector data storage, AI-powered document retrieval, application security, containerization, and cloud deployment.

The project progressed from an application implementation to a deployed and monitored Azure solution.

It demonstrates practical application of AI/ML engineering principles, particularly the integration of RAG into a business-focused application.

The resulting solution provides a foundation for secure, maintainable, and extensible organizational policy assistance.

---

**Project:** Office Loan Policy Assistant  
**Submitted by:** Michael O. Faniyi  
**Project Type:** AI/ML Engineering Capstone
