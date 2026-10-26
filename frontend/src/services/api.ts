const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export interface PolicySource {
  document: string
  page_number: number
}

export interface PolicyAnswerResponse {
  question: string
  answer: string
  sources: PolicySource[]
  sources_are_retrieved_context: boolean
  is_answer_supported: boolean | null
}

export async function askPolicyQuestion(
  question: string
): Promise<PolicyAnswerResponse> {
  const response = await fetch(`${API_BASE_URL}/policy/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  })

  if (!response.ok) {
    throw new Error(
      `Unable to retrieve policy answer. Status: ${response.status}`
    )
  }

  return response.json()
}


export type LoanType =
  | 'emergency'
  | 'personal'
  | 'salary_advance'
  | 'development'

export interface LoanCalculationRequest {
  loan_type: LoanType
  gross_monthly_salary: number
  net_monthly_salary: number
  requested_amount: number
  repayment_months: number
  annual_interest_rate: number | null
}

export interface LoanCalculationResponse {
  loan_type: LoanType
  requested_amount: number
  maximum_loan_amount: number
  repayment_months: number
  monthly_repayment_limit: number
  is_within_loan_limit: boolean
  assessment_type: string
  message: string
  estimated_monthly_repayment: number
  is_principal_affordable: boolean
  repayment_calculation_note: string
  interest_included: boolean
  total_interest: number | null
  monthly_repayment_with_interest: number | null
  is_interest_affordable: boolean | null
}


export async function calculateLoan(
  request: LoanCalculationRequest
): Promise<LoanCalculationResponse> {
  const response = await fetch(`${API_BASE_URL}/loans/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(
      `Loan calculation failed. Status: ${response.status}`
    )
  }

  return response.json()
}

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface EmployeeProfileResponse {
  staff_id: string
  full_name: string
  email: string
  staff_level: string
}

export async function loginEmployee(
  credentials: LoginRequest
): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  })

  if (response.status === 401) {
    throw new Error('Invalid email or password.')
  }

  if (!response.ok) {
    throw new Error('Unable to sign in. Please try again.')
  }

  return response.json()
}

export async function getEmployeeProfile(
  accessToken: string
): Promise<EmployeeProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/employees/me`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })

  if (response.status === 401) {
    throw new Error('Your session has expired. Please sign in again.')
  }

  if (!response.ok) {
    throw new Error('Unable to retrieve your employee profile.')
  }

  return response.json()
}

export interface PersonalLoanAssessmentRequest {
  loan_type: LoanType
  requested_amount: number
  repayment_months: number
  annual_interest_rate: number | null
  is_topup: boolean
}

export interface PersonalLoanAssessmentResponse
  extends LoanCalculationResponse {
  meets_basic_criteria: boolean
  eligibility_reasons: string[]
  eligibility_note: string
  meets_repayment_history_rule: boolean | null
  repayment_history_reason: string
  has_active_loan: boolean | null
  active_loan_reason: string
  existing_outstanding_balance: number | null
  combined_loan_amount: number | null
  is_within_total_outstanding_limit: boolean | null
  repaid_amount: number | null
  repayment_percentage: number | null
  meets_topup_repayment_rule: boolean | null
  requires_management_approval: boolean | null
  is_topup: boolean
}

export async function assessMyLoan(
  request: PersonalLoanAssessmentRequest,
  accessToken: string,
  signal?: AbortSignal
): Promise<PersonalLoanAssessmentResponse> {
  const response = await fetch(`${API_BASE_URL}/loans/my-assessment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(request),
    signal,
  })

  if (response.status === 401) {
    throw new Error('Your session has expired. Please sign in again.')
  }

  if (!response.ok) {
    throw new Error(
      `Unable to complete your assessment. Status: ${response.status}`
    )
  }

  return response.json()
}