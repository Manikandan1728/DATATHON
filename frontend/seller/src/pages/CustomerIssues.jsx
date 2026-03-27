import React, { useState } from 'react'
import { useAnalysis } from '../contexts/AnalysisContext'
import LoadingSpinner from '../components/LoadingSpinner'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, Legend
} from 'recharts'
import { AlertTriangle, AlertCircle, Info, Search, ChevronDown, ChevronUp, TrendingDown } from 'lucide-react'

const SEV = {
  High: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', badge: 'bg-red-100 text-red-700', bar: '#ef4444', icon: AlertTriangle },
  Medium: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700', badge: 'bg-yellow-100 text-yellow-700', bar: '#f59e0b', icon: AlertCircle },
  Low: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', badge: 'bg-green-100 text-green-700', bar: '#10b981', icon: Info },
}

const CustomerIssues = () => {
  const { data, loading, error } = useAnalysis()
  const [expanded, setExpanded] = useState(null)
  const [view, setView] = useState('cards') // 'cards' | 'chart'

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-24">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-500 text-sm">Detecting customer issues...</p>
    </div>
  )
  if (error) return <div className="bg-red-50 border border-red-200 rounded-xl p-6"><p className="text-red-800">Error: {error}</p></div>
  if (!data) return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="bg-orange-50 rounded-full p-6 mb-4"><Search className="h-12 w-12 text-orange-400" /></div>
      <h3 className="text-lg font-semibold text-gray-700">No data yet</h3>
      <p className="text-gray-400 mt-1">Search for a product to see customer issues</p>
    </div>
  )

  const issues = data.customer_issues || []
  const highCount = issues.filter(i => i.severity === 'High').length
  const medCount = issues.filter(i => i.severity === 'Medium').length
  const lowCount = issues.filter(i => i.severity === 'Low').length

  const pieData = [
    { name: 'High', value: highCount, fill: '#ef4444' },
    { name: 'Medium', value: medCount, fill: '#f59e0b' },
    { name: 'Low', value: lowCount, fill: '#10b981' },
  ].filter(d => d.value > 0)

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customer Issues</h1>
          <p className="text-gray-500 mt-1">Issues detected for <span className="font-medium text-gray-700">"{data.query}"</span></p>
        </div>
        <span className="bg-orange-100 text-orange-700 text-xs font-semibold px-3 py-1 rounded-full">{issues.length} issues found</span>
      </div>

      {/* Severity summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'High Severity', count: highCount, color: 'border-red-300 bg-red-50', text: 'text-red-700', icon: AlertTriangle, iconColor: 'text-red-500' },
          { label: 'Medium Severity', count: medCount, color: 'border-yellow-300 bg-yellow-50', text: 'text-yellow-700', icon: AlertCircle, iconColor: 'text-yellow-500' },
          { label: 'Low Severity', count: lowCount, color: 'border-green-300 bg-green-50', text: 'text-green-700', icon: Info, iconColor: 'text-green-500' },
        ].map(({ label, count, color, text, icon: Icon, iconColor }) => (
          <div key={label} className={`rounded-xl border-2 p-4 ${color}`}>
            <div className="flex items-center gap-2 mb-1">
              <Icon className={`h-4 w-4 ${iconColor}`} />
              <span className="text-xs font-medium text-gray-600">{label}</span>
            </div>
            <p className={`text-3xl font-bold ${text}`}>{count}</p>
          </div>
        ))}
      </div>

      {issues.length === 0 ? (
        <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
          <div className="bg-green-50 rounded-full p-4 w-fit mx-auto mb-3">
            <Info className="h-8 w-8 text-green-500" />
          </div>
          <p className="text-gray-600 font-medium">No significant customer issues detected</p>
          <p className="text-gray-400 text-sm mt-1">Products in this search appear to have good customer satisfaction</p>
        </div>
      ) : (
        <>
          {/* View toggle */}
          <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
            {[['cards', 'Issue Cards'], ['chart', 'Charts']].map(([key, label]) => (
              <button key={key} onClick={() => setView(key)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${view === key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
                {label}
              </button>
            ))}
          </div>

          {view === 'cards' && (
            <div className="space-y-3">
              {issues.map((issue, i) => {
                const s = SEV[issue.severity] || SEV.Low
                const Icon = s.icon
                const isOpen = expanded === i
                return (
                  <div key={i} className={`rounded-xl border ${s.border} ${s.bg} overflow-hidden`}>
                    <button onClick={() => setExpanded(isOpen ? null : i)}
                      className="w-full px-5 py-4 flex items-center gap-4 text-left">
                      <div className={`p-2 rounded-lg bg-white/60`}>
                        <Icon className={`h-5 w-5 ${s.text}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="font-semibold text-gray-900">{issue.issue}</h3>
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${s.badge}`}>{issue.severity}</span>
                        </div>
                        <div className="flex items-center gap-3 mt-1">
                          <div className="flex-1 max-w-xs bg-white/60 rounded-full h-1.5">
                            <div className="h-1.5 rounded-full" style={{ width: `${Math.min(issue.percentage * 3, 100)}%`, backgroundColor: s.bar }} />
                          </div>
                          <span className={`text-sm font-bold ${s.text}`}>{issue.percentage}%</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {issue.affected_products?.length > 0 && (
                          <span className="text-xs text-gray-500 hidden sm:block">{issue.affected_products.length} product{issue.affected_products.length > 1 ? 's' : ''}</span>
                        )}
                        {isOpen ? <ChevronUp className="h-4 w-4 text-gray-400" /> : <ChevronDown className="h-4 w-4 text-gray-400" />}
                      </div>
                    </button>
                    {isOpen && issue.affected_products?.length > 0 && (
                      <div className="px-5 pb-4 border-t border-white/40">
                        <p className="text-xs font-medium text-gray-600 mb-2 mt-3">Affected products:</p>
                        <div className="flex flex-wrap gap-2">
                          {issue.affected_products.map((p, j) => (
                            <span key={j} className="text-xs bg-white/70 border border-white/80 text-gray-700 px-2.5 py-1 rounded-lg">
                              {p.slice(0, 30)}{p.length > 30 ? '…' : ''}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}

          {view === 'chart' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
                <h2 className="text-base font-semibold text-gray-900 mb-4">Issue Frequency (%)</h2>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={issues} layout="vertical" margin={{ left: 10, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis type="number" domain={[0, 'dataMax + 5']} tick={{ fontSize: 11 }} />
                    <YAxis dataKey="issue" type="category" width={150} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v) => [`${v}%`, 'Affected']} contentStyle={{ borderRadius: '8px' }} />
                    <Bar dataKey="percentage" radius={[0, 6, 6, 0]} maxBarSize={28}>
                      {issues.map((entry, i) => <Cell key={i} fill={SEV[entry.severity]?.bar || '#6b7280'} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
                <h2 className="text-base font-semibold text-gray-900 mb-4">Severity Distribution</h2>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" outerRadius={90} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                      {pieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                    </Pie>
                    <Legend />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Priority actions for high severity */}
          {highCount > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <TrendingDown className="h-5 w-5 text-red-500" />
                <h2 className="text-lg font-semibold text-gray-900">Priority Actions</h2>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {issues.filter(i => i.severity === 'High').map((issue, i) => (
                  <div key={i} className="bg-red-50 border border-red-200 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="h-4 w-4 text-red-600" />
                      <h3 className="font-semibold text-red-900 text-sm">Immediate Action Required</h3>
                    </div>
                    <p className="text-red-800 text-sm">{issue.issue} affects {issue.percentage}% of customers</p>
                    {issue.affected_products?.length > 0 && (
                      <p className="text-xs text-red-600 mt-1.5">Focus: {issue.affected_products.slice(0, 2).map(p => p.slice(0, 25)).join(', ')}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default CustomerIssues
