# Office Loan Policy Assistant — Monitoring and Observability

## 1. Overview

The application uses Azure Application Insights and Azure Monitor OpenTelemetry to collect and analyze application telemetry.

Monitoring helps evaluate API availability, request performance, dependency behavior, application logs, and exceptions.

## 2. Monitoring Infrastructure

| Component | Configuration |
|---|---|
| Application Insights | office-loan-policy-assistant-insights |
| Log Analytics Workspace | workspace-rgsecurecandidateVCDt |
| Container App | office-loan-policy-assistant-api |
| Container Apps Environment | secure-candidate-env |
| Key Vault | officeloanpolicymf |
| Monitoring Workbook | Office Loan Policy Assistant Monitoring Workbook |
| Data Retention | 90 days |

## 3. Instrumentation

The backend uses the Azure Monitor OpenTelemetry package.

Monitoring is initialized when the APPLICATIONINSIGHTS_CONNECTION_STRING environment variable is available.

Application logging is configured for the uvicorn.error logger.

The application also records API request information, including:

- Unique request ID.
- HTTP method.
- Request path.
- HTTP status code.
- Request latency in milliseconds.

## 4. Monitoring Dashboard

The Azure Monitor Workbook contains six panels.

### 4.1 API Request Volume

Displays the number of API requests over time.

Purpose:
- Observe API traffic.
- Identify changes in request volume.
- Understand application usage patterns.

### 4.2 Successful vs Failed Requests

Displays successful and unsuccessful API requests.

Purpose:
- Monitor request outcomes.
- Identify unsuccessful API operations.
- Track application reliability.

### 4.3 Average and P95 API Latency

Displays average request duration and the 95th percentile request duration.

Purpose:
- Understand typical API response time.
- Identify slower requests.
- Monitor performance changes.

### 4.4 Dependency Performance

Displays dependency calls, average latency, and failures.

Purpose:
- Monitor external service interactions.
- Observe internal application dependency calls.
- Identify dependency performance issues.

### 4.5 Application Logs by Severity

Groups application trace records by severity level.

Purpose:
- Understand application logging activity.
- Identify the distribution of log severity.
- Support operational troubleshooting.

### 4.6 Application Exceptions

Displays recorded application exceptions over time.

Purpose:
- Identify application exceptions.
- Observe exception frequency.
- Support investigation of unexpected application behavior.

An empty result does not necessarily indicate a monitoring failure. It may mean that no exceptions were recorded during the selected time range.

## 5. Initial Monitoring Observations

During the initial dashboard validation, the following observations were recorded:

| Metric | Observed Value |
|---|---:|
| Successful requests | 4 |
| Average API latency | 14.25 ms |
| P95 API latency | 29 ms |
| HTTP dependency calls | 21 |
| HTTP dependency failures | 0 |
| Informational-level logs | 7 |
| Recorded exceptions | No results |

These values represent an initial observation, not a comprehensive performance benchmark.

The exception panel returned no results during the observation period.

## 6. Monitoring Limitations

- The initial request sample is small and should not be treated as a production performance benchmark.
- An empty exception query does not prove that the application can never generate exceptions.
- Database dependency telemetry has not yet been independently verified.
- Monitoring effectiveness depends on continued telemetry collection and correct instrumentation.
- Additional load testing is required to establish meaningful performance baselines.

## 7. Operational Recommendations

1. Review API failures regularly.
2. Investigate unexpected latency increases.
3. Monitor dependency failures and response times.
4. Review application exceptions when they occur.
5. Verify that database dependencies are represented in telemetry.
6. Establish performance baselines using representative workloads.
7. Review monitoring retention and access permissions periodically.
