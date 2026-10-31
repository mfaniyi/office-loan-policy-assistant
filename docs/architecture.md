# Office Loan Policy Assistant — System Architecture

## 1. Overview

The Office Loan Policy Assistant is an AI-powered application that helps employees understand organizational loan policies, calculate potential loan repayments, and assess their eligibility for available loan facilities.

The system combines a React frontend, FastAPI backend, PostgreSQL database, and a Retrieval-Augmented Generation (RAG) pipeline integrated with Microsoft Foundry.

## 2. High-Level Architecture

The application consists of the following layers:

1. **Presentation Layer:** React 19 and TypeScript frontend.
2. **API Layer:** FastAPI application exposing authentication, employee, loan, and policy endpoints.
3. **Business Logic Layer:** Services responsible for authentication, loan calculations, eligibility assessment, and policy assistance.
4. **AI/RAG Layer:** Document ingestion, chunking, embeddings, hybrid retrieval, reranking, evidence evaluation, answerability checks, and LLM generation.
5. **Data Layer:** PostgreSQL with pgvector for relational data and vector-based document retrieval.
6. **Infrastructure and Monitoring Layer:** Docker, Azure Container Registry, Azure Container Apps, Azure Database for PostgreSQL, Key Vault, Managed Identity, and Application Insights.

## 3. Backend Architecture

The backend follows a modular structure:

| Module | Responsibility |
|---|---|
| api | HTTP endpoints for authentication, employees, loans, and policies |
| core | Application configuration, dependencies, security, and rate limiting |
| db | Database connectivity |
| models | Database entities |
| schemas | Request and response validation |
| services | Business logic and RAG orchestration |
| scripts | Policy ingestion, employee seeding, and retrieval evaluation |

### Main API Routers

- Authentication
- Employees
- Loans
- Policy

## 4. RAG Architecture

The policy assistant uses a Retrieval-Augmented Generation workflow.

The principal stages are:

1. **Document ingestion:** Load organizational loan policy documents.
2. **Chunking:** Divide documents into smaller retrievable sections.
3. **Embedding:** Generate vector representations of document chunks.
4. **Storage:** Store document chunks and embeddings in PostgreSQL with pgvector.
5. **Retrieval:** Retrieve relevant information using hybrid search.
6. **Reranking:** Reorder retrieved results by relevance.
7. **Evidence evaluation:** Assess the supporting evidence.
8. **Answerability assessment:** Determine whether sufficient evidence exists to answer the question.
9. **Generation:** Use the configured LLM service to produce a policy response grounded in retrieved evidence.

## 5. Frontend Architecture

The frontend is implemented using React 19, TypeScript, and Vite.

Principal components include:

- EmployeeLogin
- LoanCalculator
- MyAssessment

The frontend communicates with the FastAPI backend through the API service module.

## 6. Database Architecture

PostgreSQL provides persistent application storage.

The database supports:

- User and employee records.
- Loan-related records.
- Document chunks.
- Vector embeddings for semantic retrieval.

SQLAlchemy manages database interactions, Alembic manages schema migrations, and pgvector supports vector similarity search.

## 7. Security Architecture

The application incorporates:

- JWT-based authentication.
- Argon2 password hashing.
- API rate limiting.
- CORS restrictions.
- Environment-based configuration.
- Azure Key Vault for secret management.
- Azure Managed Identity for application access to Azure resources.
- Encrypted PostgreSQL connections in Azure.

## 8. Monitoring Architecture

Azure Application Insights and Azure Monitor OpenTelemetry provide application telemetry.

The monitoring implementation captures:

- API request volume.
- Request success and failure.
- Request latency.
- Dependency performance.
- Application logs.
- Application exceptions.

A shared Azure Monitor Workbook presents these metrics through six monitoring panels.

## 9. Deployment Architecture

The application is deployed using:

- Azure Container Registry for container images.
- Azure Container Apps for application hosting.
- Azure Database for PostgreSQL for persistent storage.
- Azure Key Vault for secrets.
- User-assigned Managed Identity for Azure resource access.
- Application Insights for monitoring and diagnostics.

The frontend and backend are deployed as separate Container Apps.

## 10. Architectural Considerations

The modular architecture separates presentation, API handling, business logic, AI orchestration, and persistence.

This separation improves maintainability, supports independent component development, and makes it easier to test and extend the application.

The RAG pipeline also separates retrieval and evidence evaluation from answer generation, helping the assistant produce policy responses supported by retrieved documents.
