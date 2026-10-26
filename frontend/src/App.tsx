import { askPolicyQuestion } from './services/api'
import type { PolicySource } from './services/api'
import { useEffect, useRef, useState } from 'react'
import LoanCalculator from './components/LoanCalculator'
import './App.css'
import EmployeeLogin from './components/EmployeeLogin'
import { getEmployeeProfile } from './services/api'
import type { EmployeeProfileResponse } from './services/api'
import MyAssessment from './components/MyAssessment'


interface ChatMessage {
  id: number
  question: string
  answer: string
  sources: PolicySource[]
}

function App() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const requestIdRef = useRef(0)
  type Page = 'chat' | 'calculator' | 'login' | 'assessment'
  const [activePage, setActivePage] = useState<Page>('chat')
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [employeeProfile, setEmployeeProfile] =
  useState<EmployeeProfileResponse | null>(null)

  useEffect(() => {
    const container = chatContainerRef.current

    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, [messages, loading, error])

  async function handleSend() {
    if (!question.trim() || loading) return

    const submittedQuestion = question.trim()
    const requestId = ++requestIdRef.current

    setLoading(true)
    setError('')

    try {
      const result = await askPolicyQuestion(submittedQuestion)

      if (requestId !== requestIdRef.current) return

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now(),
          question: submittedQuestion,
          answer: result.answer,
          sources: result.sources,
        },
      ])

      setQuestion('')
    } catch {
      if (requestId === requestIdRef.current) {
        setError('Unable to retrieve an answer. Please try again.')
      }
    } finally {
      if (requestId === requestIdRef.current) {
        setLoading(false)
      }
    }
  }

  async function handleLoginSuccess(token: string) {
    setAccessToken(token)

    try {
      const profile = await getEmployeeProfile(token)
      setEmployeeProfile(profile)
      setActivePage('chat')
    } catch {
      setEmployeeProfile(null)
      setAccessToken(null)
      setActivePage('login')
    }
  }

  function handleNewChat() {
    requestIdRef.current += 1

    setMessages([])
    setQuestion('')
    setError('')
    setLoading(false)
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <h2>Office Loan</h2>
          <p>Policy Assistant</p>
        </div>

        <nav className="navigation">
          <button
            className={`nav-item ${activePage === 'chat' ? 'active' : ''}`}
            onClick={() => setActivePage('chat')}
          >
            AI Assistant
          </button>

          <button
            className={`nav-item ${activePage === 'calculator' ? 'active' : ''}`}
            onClick={() => setActivePage('calculator')}
          >
            Loan Calculator
          </button>
          <button
            type="button"
            className={`nav-item ${activePage === 'assessment' ? 'active' : ''}`}
            onClick={() => {
              setActivePage(accessToken ? 'assessment' : 'login')
            }}
          >
            My Assessment
          </button>
        </nav>

        <div className="sidebar-footer">
          <p>Office Loan Policy Assistant</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <h1>
            {activePage === 'chat'
              ? 'AI Policy Assistant'
              : activePage === 'calculator'
                ? 'Loan Calculator'
                : activePage === 'assessment'
                  ? 'My Assessment'
                  : 'Employee Login'}
          </h1>
        <div className="header-actions">
          {accessToken && employeeProfile && (
            <div className="employee-info">
              <strong>{employeeProfile.full_name}</strong>
              <span>{employeeProfile.staff_id}</span>
            </div>
          )}

          {accessToken ? (
            <button
              type="button"
              className="login-button"
              onClick={() => {
                setAccessToken(null)
                setEmployeeProfile(null)
                setActivePage('chat')
              }}
            >
              Logout
            </button>
          ) : (
            <button
              type="button"
              className="login-button"
              onClick={() => setActivePage('login')}
            >
              Employee Login
            </button>
          )}
        </div>
        </header>

        {activePage === 'login' ? (
          <EmployeeLogin onLoginSuccess={handleLoginSuccess} />
        ) : activePage === 'chat' ? (
          <>
            <section className="welcome-section">
              <h2>How can I help you today?</h2>

              <p>
                Ask questions about company loan policies,
                calculate repayments, or explore your loan eligibility.
              </p>
            </section>

            <section className="chat-container">

            <div className="chat-header">
              <span>Conversation</span>

              <button
                type="button"
                className="new-chat-button"
                onClick={handleNewChat}
              >
                + New Chat
              </button>
            </div>

          <div className="chat-placeholder" ref={chatContainerRef}>
            {messages.length === 0 && !loading && !error ? (
              <>
                <h3>Your AI Loan Assistant</h3>
                <p>Ask me anything about the Office Loan Policy.</p>
              </>
            ) : (
              <div className="chat-messages">
                {messages.map((message) => (
                  <div key={message.id} className="conversation">
                    <div className="user-message">
                      <strong>You</strong>
                      <p>{message.question}</p>
                    </div>

                    <div className="assistant-answer">
                      <h3>AI Assistant</h3>
                      <p>{message.answer}</p>

                      {message.sources.length > 0 && (
                        <div className="answer-sources">
                          <h4>Policy Sources</h4>

                          <ul>
                            {message.sources.map((source) => (
                              <li
                                key={`${source.document}-${source.page_number}`}
                              >
                                {source.document} — Page {source.page_number}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {loading && <p role="status">Thinking...</p>}

                {error && (
                  <p role="alert" className="error-message">
                    {error}
                  </p>
                )}
              </div>
            )}
          </div>

          <form
            className="chat-input"
            onSubmit={(event) => {
              event.preventDefault()
              void handleSend()
            }}
          >
            <input
              type="text"
              aria-label="Ask a policy question"
              placeholder="Ask a question about the loan policy..."
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              maxLength={1000}
            />

            <button
              type="submit"
              disabled={loading || !question.trim()}
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </form>
            </section>
          </>
        ) : activePage === 'calculator' ? (
          <LoanCalculator />
        ) : activePage === 'assessment' && accessToken ? (
          <MyAssessment accessToken={accessToken} />
        ) : (
          <EmployeeLogin onLoginSuccess={handleLoginSuccess} />
        )}
      </main>
    </div>
  )
}

export default App