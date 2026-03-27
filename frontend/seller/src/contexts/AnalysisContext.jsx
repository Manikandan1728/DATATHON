import React, { createContext, useContext, useState, useCallback } from 'react'

const AnalysisContext = createContext()

export const useAnalysis = () => {
  const context = useContext(AnalysisContext)
  if (!context) throw new Error('useAnalysis must be used within an AnalysisProvider')
  return context
}

const API_BASE = "https://datathon-production-c1f0.up.railway.app"

export const AnalysisProvider = ({ children }) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [jobId, setJobId] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)

  // Brand selection state
  const [sellerBrand, setSellerBrand] = useState(null)
  const [comparisonData, setComparisonData] = useState(null)
  const [comparisonLoading, setComparisonLoading] = useState(false)
  const [comparisonError, setComparisonError] = useState(null)

  const search = useCallback(async (searchQuery) => {
    if (!searchQuery.trim()) return
    setLoading(true)
    setError(null)
    setData(null)
    setQuery(searchQuery.trim())
    setJobStatus('pending')
    setSellerBrand(null)
    setComparisonData(null)
    setComparisonError(null)

    try {
      const controller = new AbortController();
      setTimeout(() => controller.abort(), 60000);
      
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery
        }),
        signal: controller.signal
      });
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to start analysis')
      }
      const job = await response.json()
      setJobId(job.job_id)
      setJobStatus(job.status)

      const poll = async () => {
        const res = await fetch(`${API_BASE}/jobs/${job.job_id}`)
        const status = await res.json()
        setJobStatus(status.status)

        if (status.status === 'done') {
          if (status.result?.error) {
            setError(status.result.error)
          } else {
            setData(status.result)
          }
          setLoading(false)
        } else if (status.status === 'error') {
          setError(status.error || 'Analysis failed')
          setLoading(false)
        } else {
          setTimeout(poll, 3000)
        }
      }
      setTimeout(poll, 2000)
    } catch (err) {
      setError(err.message)
      setLoading(false)
      setJobStatus('error')
    }
  }, [])

  const selectBrand = useCallback(async (brand) => {
    if (!jobId || !brand) return
    setSellerBrand(brand)
    setComparisonLoading(true)
    setComparisonError(null)
    setComparisonData(null)

    try {
      const res = await fetch(`${API_BASE}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId, seller_brand: brand }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Comparison failed')
      }
      const result = await res.json()
      setComparisonData(result)
    } catch (err) {
      setComparisonError(err.message)
    } finally {
      setComparisonLoading(false)
    }
  }, [jobId])

  return (
    <AnalysisContext.Provider value={{
      data, loading, error, query, jobStatus, search,
      sellerBrand, setSellerBrand,
      comparisonData, comparisonLoading, comparisonError, selectBrand,
    }}>
      {children}
    </AnalysisContext.Provider>
  )
}
