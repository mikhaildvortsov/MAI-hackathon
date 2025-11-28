import { useState } from 'react'
import EmailForm from './EmailForm'
import ParametersForm from './ParametersForm'
import Result from './Result'
import Loading from './Loading'
import { analyzeEmail, generateEmail } from '../services/api'
import './Generator.css'

function Generator({ onBack, apiStatus }) {
  const [currentRequestData, setCurrentRequestData] = useState(null)
  const [parameters, setParameters] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('Анализируем письмо...')
  const [showResult, setShowResult] = useState(false)

  const handleAnalyzeAndGenerate = async (formData) => {
    setLoading(true)
    setLoadingText('AI анализирует входящее письмо...')
    setShowResult(false)

    try {
      // ШАГ 1: Анализ параметров
      const analyzed = await analyzeEmail(
        formData.source_subject,
        formData.source_body,
        formData.company_context
      )

      const params = analyzed.parameters
      setParameters(params)
      setCurrentRequestData(formData)

      // ШАГ 2: Генерация
      setLoadingText('Генерируем ответное письмо...')
      const emailResult = await generateEmail({
        ...formData,
        parameters: params,
      })

      setResult(emailResult)
      setShowResult(true)
      console.log('Result set:', emailResult) // Debug
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
  }

  return (
    <div className="generator-page">
      <div className="generator-header">
        <div className="container">
          <button className="btn-back" onClick={onBack}>
            ← Назад
          </button>
          <h1>Генератор писем</h1>
          <p className="api-status-small">{apiStatus}</p>
        </div>
      </div>

      <div className="generator-content">
        <div className="container">
          {!showResult && (
            <>
              <EmailForm onSubmit={handleAnalyzeAndGenerate} />
            </>
          )}

          {showResult && parameters && result && (
            <>
              <div className="parameters-container">
                <ParametersForm
                  initialParameters={parameters}
                  onRegenerate={handleRegenerate}
                  onClear={handleClear}
                />
              </div>

              <div className="result-wrapper">
                <Result result={result} />
              </div>
            </>
          )}

          <Loading active={loading} text={loadingText} />
        </div>
      </div>
    </div>
  )
}

export default Generator;
