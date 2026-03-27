import React from 'react'
import { useAnalysis } from '../contexts/AnalysisContext'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import {
  FileText, TrendingUp, TrendingDown, Package, Users, Award,
  Target, AlertTriangle, CheckCircle, Search, DollarSign, Star, Zap
} from 'lucide-react'

const prio = {
  High: { cls: 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20', icon: <AlertTriangle className="h-4 w-4 text-red-500" />, text: 'text-red-700 dark:text-red-300', badge: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300' },
  Medium: { cls: 'border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20', icon: <AlertTriangle className="h-4 w-4 text-yellow-500" />, text: 'text-yellow-700 dark:text-yellow-300', badge: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300' },
  Low: { cls: 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20', icon: <CheckCircle className="h-4 w-4 text-green-500" />, text: 'text-green-700 dark:text-green-300', badge: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300' },
}

const ExecutiveSummary = () => {
  const { data, loading, error } = useAnalysis()

  if (loading) return <div className="flex justify-center py-24"><LoadingSpinner size="lg" /></div>
  if (error) return <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6"><p className="text-red-800 dark:text-red-300">Error: {error}</p></div>
  if (!data) return (
    <div className="card text-center py-16">
      <Search className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
      <p className="text-gray-500 dark:text-gray-400">Search for a product to see the executive summary</p>
    </div>
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Executive Summary</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Competitive intelligence for "{data.query}" — {data.category}</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Products Analyzed', value: data.total_products, icon: Package, bg: 'bg-blue-100 dark:bg-blue-900/40', ic: 'text-blue-600 dark:text-blue-400' },
          { label: 'Reviews Analyzed', value: (data.total_reviews || 0).toLocaleString(), icon: Users, bg: 'bg-green-100 dark:bg-green-900/40', ic: 'text-green-600 dark:text-green-400' },
          { label: 'Top Brand', value: data.top_brand, icon: Award, bg: 'bg-yellow-100 dark:bg-yellow-900/40', ic: 'text-yellow-600 dark:text-yellow-400' },
          { label: 'Analysis Time', value: data.execution_time, icon: TrendingUp, bg: 'bg-purple-100 dark:bg-purple-900/40', ic: 'text-purple-600 dark:text-purple-400' },
        ].map(({ label, value, icon: Icon, bg, ic }) => (
          <div key={label} className="card flex items-center gap-4">
            <div className={`p-3 ${bg} rounded-xl flex-shrink-0`}>
              <Icon className={`h-6 w-6 ${ic}`} />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Component Winners */}
      {Object.keys(data.component_winners || {}).length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Components</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(data.component_winners).map(([comp, winner]) => {
              const score = data.products.find(p => p.name === winner)?.components?.[comp] || 0
              return (
                <div key={comp} className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-4 rounded-xl border border-blue-200 dark:border-blue-800">
                  <h3 className="font-semibold text-gray-900 dark:text-white capitalize text-sm">{comp.replace(/_/g, ' ')}</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 truncate">{winner}</p>
                  <p className="text-sm font-bold text-blue-600 dark:text-blue-400 mt-1">{score.toFixed(1)} / 5</p>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {(data.recommendations || []).length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Target className="h-5 w-5 text-gray-500 dark:text-gray-400" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Strategic Recommendations</h2>
          </div>
          <div className="space-y-4">
            {data.recommendations.map((rec, i) => {
              const { cls, icon, text } = prio[rec.priority] || prio.Low
              return (
                <div key={i} className={`border rounded-xl p-4 ${cls}`}>
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900 dark:text-white">{rec.title}</h3>
                    <div className={`flex items-center gap-1 ml-2 shrink-0 text-xs font-medium ${text}`}>
                      {icon}<span>{rec.priority}</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{rec.description}</p>
                  <ul className="space-y-1">
                    {rec.action_items.map((item, j) => (
                      <li key={j} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                        <span className="text-gray-400 mt-0.5">•</span>{item}
                      </li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Insights */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="h-5 w-5 text-gray-500 dark:text-gray-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Summary Insights</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[
            { label: 'Component Analysis', icon: Package, color: 'text-blue-600 dark:text-blue-400', key: 'component_analysis' },
            { label: 'Competitor Comparison', icon: Users, color: 'text-green-600 dark:text-green-400', key: 'competitor_comparison' },
            { label: 'Customer Issues', icon: AlertTriangle, color: 'text-red-600 dark:text-red-400', key: 'customer_issues' },
          ].map(({ label, icon: Icon, color, key }) => (
            <div key={key}>
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-2">
                <Icon className={`h-4 w-4 ${color}`} />{label}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">{data.insights?.[key]}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Brand table */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Brand Performance Summary</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                {['Brand', 'Products', 'Avg Rating', 'Avg Price', 'Position'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {Object.entries(data.brands).map(([brand, info]) => (
                <tr key={brand} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{brand}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{info.products.length}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{info.average_rating}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{info.average_price > 0 ? `$${info.average_price}` : 'N/A'}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${brand === data.top_brand ? 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'}`}>
                      {brand === data.top_brand ? 'Market Leader' : 'Competitor'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default ExecutiveSummary
