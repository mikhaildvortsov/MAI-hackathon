import { useState } from 'react'
import EmailForm from './EmailForm'
import ParametersForm from './ParametersForm'
import Result from './Result'
import Loading from './Loading'
import OperatorSidebar from './OperatorSidebar'
import { analyzeEmail, analyzeEmailDetailed, generateEmail } from '../services/api'
import './Generator.css'

function Generator({ onBack, apiStatus }) {
  const [currentRequestData, setCurrentRequestData] = useState(null)
  const [parameters, setParameters] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('Анализируем письмо...')
  const [showResult, setShowResult] = useState(false)
  const [detailedAnalysis, setDetailedAnalysis] = useState(null)
  const [showSourceEmail, setShowSourceEmail] = useState(false)

  const handleAnalyzeAndGenerate = async (formData) => {
    setLoading(true)
    setLoadingText('AI анализирует входящее письмо...')
    setShowResult(false)

    try {
      // ШАГ 1: Расширенный анализ
      const analysis = await analyzeEmailDetailed(
        formData.source_subject,
        formData.source_body,
        formData.company_context
      )

      setDetailedAnalysis(analysis)
      setParameters(analysis.parameters)
      setCurrentRequestData(formData)

      // ШАГ 2: Генерация
      setLoadingText('Генерируем ответное письмо...')
      const emailResult = await generateEmail({
        ...formData,
        parameters: analysis.parameters,
      })

      setResult(emailResult)
      setShowResult(true)
    } catch (error) {
      alert('❌ Ошибка: ' + error.message)
      setResult({
        subject: 'Ошибка',
        body: error.message,
      })
      setShowResult(true)
    } finally {
      setLoading(false)
    }
  }

  const handleRegenerate = async (newParameters) => {
    if (!currentRequestData) return

    setLoading(true)
    setLoadingText('Генерируем ответное письмо...')

    try {
      const emailResult = await generateEmail({
        ...currentRequestData,
        parameters: newParameters,
      })

      setResult(emailResult)
      setParameters(newParameters)
    } catch (error) {
      alert('❌ Ошибка: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setCurrentRequestData(null)
    setParameters(null)
    setResult(null)
    setShowResult(false)
    setDetailedAnalysis(null)
  }

  return (
    <div className="generator-page">
      <div className="generator-header">
        <div className="generator-header-wrapper">
          <div className="generator-header-container">
            <div className="generator-header-content">
              <button className="btn-back" onClick={onBack}>
                ← Назад
              </button>
              <h1>Генератор писем</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="generator-main">
        <p className="api-status-small">{apiStatus}</p>
        {!showResult && (
          <>
            <EmailForm onSubmit={handleAnalyzeAndGenerate} />
          </>
        )}

        {showResult && parameters && result && (
          <>
            <div className="operator-section">
              <OperatorSidebar 
                emailData={currentRequestData}
                parameters={parameters}
                detailedAnalysis={detailedAnalysis}
                isVisible={true}
                showSourceEmail={showSourceEmail}
                onToggleSourceEmail={() => setShowSourceEmail(!showSourceEmail)}
              />

              {showSourceEmail && currentRequestData && (
                <div className="source-email-panel">
                  <div className="source-email-header">
                    <h3>Входящее письмо</h3>
                    <button 
                      className="btn-close-source" 
                      onClick={() => setShowSourceEmail(false)}
                      aria-label="Закрыть"
                    >
                      ×
                    </button>
                  </div>
                  <div className="source-email-content">
                    <div className="source-email-field">
                      <div className="source-email-label">Тема:</div>
                      <div className="source-email-value">{currentRequestData.source_subject}</div>
                    </div>
                    <div className="source-email-field">
                      <div className="source-email-label">Текст письма:</div>
                      <div className="source-email-value">{currentRequestData.source_body}</div>
                    </div>
                    {currentRequestData.company_context && (
                      <div className="source-email-field">
                        <div className="source-email-label">Контекст компании:</div>
                        <div className="source-email-value">{currentRequestData.company_context}</div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="result-layout">
              <div className="result-wrapper">
                <Result result={result} />
              </div>

              <div className="parameters-sidebar">
                <ParametersForm
                  initialParameters={parameters}
                  onRegenerate={handleRegenerate}
                  onClear={handleClear}
                  hasSenderName={!!(currentRequestData?.sender_first_name && currentRequestData?.sender_last_name)}
                  isLoading={loading}
                />
              </div>
            </div>
          </>
        )}

        <Loading active={loading} text={loadingText} />
      </div>
    </div>
  )
}

export default Generator;
