import { useState } from 'react'
import {
  calculateLoan,
  type LoanType,
  type LoanCalculationRequest,
  type LoanCalculationResponse,
} from '../services/api'

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

function LoanCalculator() {
  const [form, setForm] = useState<LoanCalculationRequest>({
    loan_type: 'personal',
    gross_monthly_salary: 0,
    net_monthly_salary: 0,
    requested_amount: 0,
    repayment_months: 12,
    annual_interest_rate: null,
  })

  const [result, setResult] = useState<LoanCalculationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

    function updateField<K extends keyof LoanCalculationRequest>(
    field: K,
    value: LoanCalculationRequest[K]
    ) {
    setForm((previous) => ({
        ...previous,
        [field]: value,
    }))

    setResult(null)
    setError('')
    }

  async function handleCalculate(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    if (
      form.gross_monthly_salary <= 0 ||
      form.net_monthly_salary <= 0 ||
      form.requested_amount <= 0
    ) {
      setError('Please enter valid salary and loan amounts.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await calculateLoan(form)
      setResult(response)
    } catch {
      setError('Unable to calculate the loan. Please check your inputs.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="calculator-container">
      <h2>Loan Calculator</h2>

      <p>
        Calculate estimated loan limits and repayments based on
        the Office Loan Policy.
      </p>

      <form onSubmit={handleCalculate} className="calculator-form">
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
          Gross Monthly Salary (₦)
          <input
            type="number"
            min="0.01"
            step="0.01"
            required
            value={form.gross_monthly_salary || ''}
            onChange={(event) =>
              updateField(
                'gross_monthly_salary',
                Number(event.target.value)
              )
            }
          />
        </label>

        <label>
          Net Monthly Salary (₦)
          <input
            type="number"
            min="0.01"
            step="0.01"
            required
            value={form.net_monthly_salary || ''}
            onChange={(event) =>
              updateField(
                'net_monthly_salary',
                Number(event.target.value)
              )
            }
          />
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
              updateField(
                'requested_amount',
                Number(event.target.value)
              )
            }
          />
        </label>

        <label>
          Repayment Period
          <select
            value={form.repayment_months}
            onChange={(event) =>
              updateField(
                'repayment_months',
                Number(event.target.value)
              )
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
            placeholder="Leave blank if not applicable"
            value={form.annual_interest_rate ?? ''}
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

        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Loan'}
        </button>
      </form>

      {error && <p role="alert" className="error-message">{error}</p>}

      {result && (
        <div className="calculator-result">
          <h3>Calculation Results</h3>

            <p>
            Maximum Loan: {formatCurrency(result.maximum_loan_amount)}
            </p>

            <p>
            Requested Amount: {formatCurrency(result.requested_amount)}
            </p>

            <p>
            Monthly Repayment Limit: {formatCurrency(result.monthly_repayment_limit)}
            </p>

            <p>
            Estimated Monthly Repayment: {formatCurrency(result.estimated_monthly_repayment)}
            </p>

          <p>
            Within Loan Limit:
            {result.is_within_loan_limit ? ' Yes' : ' No'}
          </p>

          <p>
            Principal Affordable:
            {result.is_principal_affordable ? ' Yes' : ' No'}
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

                {result.is_interest_affordable !== null && (
                <p>
                    Interest-Inclusive Repayment Affordable:{' '}
                    {result.is_interest_affordable ? 'Yes' : 'No'}
                </p>
                )}
            </>
            )}

            <div className="assessment-details">
            <div>
                <h4>Assessment Summary</h4>
                <p>{result.message}</p>
            </div>

            <div className="repayment-details">
            <h4>Repayment Information</h4>

            {result.interest_included ? (
                <p>
                The repayment estimate includes illustrative interest
                calculated using the selected annual interest rate.
                The final repayment amount may differ depending on
                the applicable interest calculation method, fees,
                and approved repayment schedule.
                </p>
            ) : (
                <p>{result.repayment_calculation_note}</p>
            )}
            </div>
            </div>

            <div className="calculator-disclaimer">
            <strong>Important:</strong> This is a hypothetical calculation,
            not a loan approval.
            </div>
        </div>
      )}
    </section>
  )
}

export default LoanCalculator