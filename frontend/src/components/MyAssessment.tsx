import { useState, type FormEvent } from 'react'
import {
  assessMyLoan,
  type LoanType,
  type PersonalLoanAssessmentRequest,
  type PersonalLoanAssessmentResponse,
} from '../services/api'

interface MyAssessmentProps {
  accessToken: string
}

const loanTypes: { value: LoanType; label: string }[] = [
  { value: 'emergency', label: 'Emergency Loan' },
  { value: 'personal', label: 'Personal Loan' },
  { value: 'salary_advance', label: 'Salary Advance' },
  { value: 'development', label: 'Development Loan' },
]

const repaymentPeriods: Record<LoanType, number[]> = {
  emergency: [1, 2, 3],
  personal: [6, 7, 8, 9, 10, 11, 12],
  salary_advance: [3],
  development: [3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
}

function formatCurrency(amount: number | null): string {
  if (amount === null) return 'N/A'

  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

function MyAssessment({ accessToken }: MyAssessmentProps) {
  const [form, setForm] = useState<PersonalLoanAssessmentRequest>({
    loan_type: 'personal',
    requested_amount: 0,
    repayment_months: 12,
    annual_interest_rate: null,
    is_topup: false,
  })

  const [result, setResult] =
    useState<PersonalLoanAssessmentResponse | null>(null)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function updateField<K extends keyof PersonalLoanAssessmentRequest>(
    field: K,
    value: PersonalLoanAssessmentRequest[K]
  ) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }))

    setResult(null)
    setError('')
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!Number.isFinite(form.requested_amount) || form.requested_amount <= 0) {
      setError('Please enter a valid loan amount.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await assessMyLoan(form, accessToken)
      setResult(response)
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Unable to complete your assessment.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="calculator-container">
      <h2>My Loan Assessment</h2>

      <p>
        Assess your loan request using your employee records
        and the Office Loan Policy.
      </p>

      <form className="calculator-form" onSubmit={handleSubmit}>
        <fieldset className="assessment-fields" disabled={loading}>
        <label>
          Loan Type
          <select
            value={form.loan_type}
            onChange={(event) => {
              const loanType = event.target.value as LoanType

              setForm((previous) => ({
                ...previous,
                loan_type: loanType,
                repayment_months: repaymentPeriods[loanType][0],
              }))

              setResult(null)
              setError('')
            }}
          >
            {loanTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Requested Loan Amount (₦)
          <input
            type="number"
            min="0.01"
            step="0.01"
            required
            value={form.requested_amount || ''}
            onChange={(event) =>
              updateField('requested_amount', Number(event.target.value))
            }
          />
        </label>

        <label>
          Repayment Period
          <select
            value={form.repayment_months}
            onChange={(event) =>
              updateField('repayment_months', Number(event.target.value))
            }
          >
            {repaymentPeriods[form.loan_type].map((months) => (
              <option key={months} value={months}>
                {months} month{months > 1 ? 's' : ''}
              </option>
            ))}
          </select>
        </label>

        <label>
          Annual Interest Rate (%) - Optional
          <input
            type="number"
            min="0"
            max="100"
            step="0.01"
            value={form.annual_interest_rate ?? ''}
            placeholder="Leave blank if not applicable"
            onChange={(event) =>
              updateField(
                'annual_interest_rate',
                event.target.value === ''
                  ? null
                  : Number(event.target.value)
              )
            }
          />
        </label>

        <label className="topup-option">
          <input
            type="checkbox"
            checked={form.is_topup}
            onChange={(event) =>
              updateField('is_topup', event.target.checked)
            }
          />
          This is a loan top-up request
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Assessing...' : 'Assess My Loan'}
        </button>
        </fieldset>
      </form>

      {error && (
        <p role="alert" className="error-message">
          {error}
        </p>
      )}

      {result && (
        <div className="calculator-result">
          <h3>Personalized Assessment Results</h3>

          <p>
            Maximum Loan: {formatCurrency(result.maximum_loan_amount)}
          </p>

          <p>
            Requested Amount: {formatCurrency(result.requested_amount)}
          </p>

          <p>
            Estimated Monthly Repayment:{' '}
            {formatCurrency(result.estimated_monthly_repayment)}
          </p>

          <p>
            Monthly Repayment Limit:{' '}
            {formatCurrency(result.monthly_repayment_limit)}
          </p>

          <p>
            Within Loan Limit: {result.is_within_loan_limit ? 'Yes' : 'No'}
          </p>

          <p>
            Principal Affordable: {result.is_principal_affordable ? 'Yes' : 'No'}
          </p>

          <p>
            Meets Basic Eligibility:{' '}
            {result.meets_basic_criteria ? 'Yes' : 'No'}
          </p>

          {result.interest_included && (
            <>
              <p>
                Total Interest: {formatCurrency(result.total_interest)}
              </p>

              <p>
                Monthly Repayment Including Interest:{' '}
                {formatCurrency(result.monthly_repayment_with_interest)}
              </p>

              <p>
                Interest-Inclusive Repayment Affordable:{' '}
                {result.is_interest_affordable === null
                  ? 'Not assessed'
                  : result.is_interest_affordable
                    ? 'Yes'
                    : 'No'}
              </p>
            </>
          )}

          <div className="assessment-details">
            <div>
              <h4>Assessment Summary</h4>
              <p>{result.message}</p>
            </div>

            <div className="repayment-details">
              <h4>Repayment Information</h4>
              <p>
                {result.interest_included
                  ? 'The repayment estimate includes illustrative interest. Final repayment terms and applicable fees require confirmation.'
                  : result.repayment_calculation_note}
              </p>
            </div>

            <div className="repayment-details">
              <h4>Eligibility Information</h4>

              <p>{result.eligibility_note}</p>

              {result.eligibility_reasons.length > 0 && (
                <ul>
                  {result.eligibility_reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              )}
            </div>

            <div className="repayment-details">
              <h4>Existing Loan Information</h4>
              <p>{result.active_loan_reason}</p>
              <p>{result.repayment_history_reason}</p>

              {result.existing_outstanding_balance !== null && (
                <p>
                  Outstanding Balance:{' '}
                  {formatCurrency(result.existing_outstanding_balance)}
                </p>
              )}

              {result.combined_loan_amount !== null && (
                <p>
                  Combined Loan Amount:{' '}
                  {formatCurrency(result.combined_loan_amount)}
                </p>
              )}

              {result.repayment_percentage !== null && (
                <p>
                  Repayment Progress:{' '}
                  {Number(result.repayment_percentage).toFixed(1)}%
                </p>
              )}

              {form.is_topup && result && (
                <p>
                    Top-Up Repayment Requirement:{' '}
                    {result.meets_topup_repayment_rule === null
                    ? 'Not assessed'
                    : result.meets_topup_repayment_rule
                        ? 'Satisfied'
                        : 'Not satisfied'}
                </p>
              )}

              {result.requires_management_approval !== null && (
                <p>
                  Management Approval Required:{' '}
                  {result.requires_management_approval ? 'Yes' : 'No'}
                </p>
              )}
            </div>
          </div>

          <div className="calculator-disclaimer">
            <strong>Important:</strong> This is a preliminary assessment,
            not a loan approval.
          </div>
        </div>
      )}
    </section>
  )
}

export default MyAssessment