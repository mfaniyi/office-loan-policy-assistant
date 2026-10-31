# Office Loan Policy Assistant — Deployment Guide

## 1. Deployment Overview

The Office Loan Policy Assistant is deployed on Microsoft Azure using containerized services.

The frontend and backend run independently as Azure Container Apps. Application images are stored in Azure Container Registry, while PostgreSQL provides persistent database storage.

## 2. Azure Infrastructure

| Resource | Azure Resource Name | Purpose |
|---|---|---|
| Resource Group | rg-secure-candidate | Groups project resources |
| Container Apps Environment | secure-candidate-env | Hosts containerized applications |
| Container Registry | securecandidateacr | Stores application images |
| Backend Container App | office-loan-policy-assistant-api | Hosts the FastAPI backend |
| Frontend Container App | office-loan-frontend | Hosts the React frontend |
| PostgreSQL Server | secure-candidate-pg-wc | Hosts the application database |
| Database | office_loan_policy_db | Stores application records |
| Key Vault | officeloanpolicymf | Stores application secrets |
| Managed Identity | office-loan-policy-identity | Provides secure Azure resource access |
| Application Insights | office-loan-policy-assistant-insights | Collects application telemetry |
| Log Analytics Workspace | workspace-rgsecurecandidateVCDt | Stores monitoring data |

## 3. Containerization

Docker is used to package the application and its dependencies.

The backend Dockerfile defines the FastAPI application image.

The frontend Dockerfile packages the React application for deployment, with Nginx serving the frontend.

Azure Container Registry stores the resulting images.

### Backend Image

`securecandidateacr.azurecr.io/office-loan-policy-assistant-api:v8`

### Frontend Image

`securecandidateacr.azurecr.io/office-loan-policy-assistant-frontend:v1`

## 4. Azure Container Apps

The backend and frontend are deployed as separate Azure Container Apps.

### Backend

- Application: office-loan-policy-assistant-api
- Hosting: Azure Container Apps
- Container port: 8000
- API documentation: /docs

### Frontend

- Application: office-loan-frontend
- Hosting: Azure Container Apps
- Web server: Nginx

The frontend communicates with the backend through the deployed API endpoint.

## 5. Database Deployment

The application uses Azure Database for PostgreSQL Flexible Server.

Database configuration:

- Server: secure-candidate-pg-wc
- Database: office_loan_policy_db
- Port: 5432
- Transport security: TLS required
- Driver: PostgreSQL with Psycopg

SQLAlchemy manages database operations, while Alembic manages database migrations.

The application uses pgvector for vector-based document retrieval.

## 6. Secrets Management

Azure Key Vault is used to store sensitive application configuration.

A user-assigned Managed Identity named office-loan-policy-identity provides access to the required Azure resources.

The identity has the following permissions:

- Key Vault Secrets User on the dedicated Key Vault.
- AcrPull on Azure Container Registry.

The Application Insights connection string is stored in Key Vault and exposed to the backend through a Container Apps secret reference.

Sensitive credentials should never be committed to source control.

## 7. Application Monitoring

Azure Application Insights is connected to the backend through Azure Monitor OpenTelemetry.

The backend uses the APPLICATIONINSIGHTS_CONNECTION_STRING environment variable to initialize monitoring.

A shared workbook named Office Loan Policy Assistant Monitoring Workbook provides six monitoring panels:

1. API Request Volume.
2. Successful vs Failed Requests.
3. Average and P95 API Latency.
4. Dependency Performance.
5. Application Logs by Severity.
6. Application Exceptions.

## 8. Deployment Verification

The following checks were performed during deployment:

- Backend Container App provisioned successfully.
- Backend container revision became healthy.
- Backend API root returned HTTP 200.
- Frontend Container App deployed successfully.
- Frontend login and employee dashboard were accessed.
- PostgreSQL connection and application API operations were tested.
- Key Vault secret integration was configured.
- Managed Identity permissions were assigned.
- Application Insights received application logs and request telemetry.
- Azure Monitor Workbook was created and populated with six monitoring panels.

## 9. Operational Considerations

- Keep application secrets in Azure Key Vault.
- Use Managed Identity instead of embedding Azure credentials.
- Monitor application health and request failures.
- Review dependency latency and application exceptions.
- Maintain secure database connectivity.
- Build and deploy new container image versions when application code changes.
- Preserve the GitHub repository as the source of truth for application code.
