import React, { useState } from 'react'
import { useAnalysis } from '../contexts/AnalysisContext'
import { Link } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell
} from 'recharts'
import { Trophy, Search, Star, ChevronDown, ChevronUp } from 'lucide-react'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16']

const ScoreBar = ({ score, max = 5, color }) => {
  const pct = Math.round((score / max) * 100)
  const bg = score >= 4 ? '#10b981' : score >= 3 ? '#f59e0b' : '#ef4444'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-100 rounded-full h-2">
        <div className="h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color || bg }} />
      </div>
      <span className="text-xs font-semibold w-7 text-right" style={{ color: color || bg }}>{score.toFixed(1)}</span>
    </div>
  )
}

const ComponentAnalysis = () => {
  const { data, loading, error } = useAnalysis()
  const [expandedProduct, setExpandedProduct] = useState(null)
  const [activeTab, setActiveTab] = useState('overview') // 'overview' | 'radar' | 'table'

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-24">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-500 text-sm">Analyzing components...</p>
    </div>
  )
  if (error) return <div className="bg-red-50 border border-red-200 rounded-xl p-6"><p className="text-red-800">Error: {error}</p></div>
  if (!data) return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="bg-blue-50 rounded-full p-6 mb-4"><Search className="h-12 w-12 text-blue-400" /></div>
      <h3 className="text-lg font-semibold text-gray-700">No data yet</h3>
      <p className="text-gray-400 mt-1">Search for a product to see component analysis</p>
    </div>
  )

  const allComponents = [...new Set(data.products.flatMap(p => Object.keys(p.components || {})))]

  // Radar data per product (up to 6 products, 8 components)
  const radarComponents = allComponents.slice(0, 8)
  const radarData = radarComponents.map(comp => {
    const entry = { component: comp.replace(/_/g, ' ') }
    data.products.slice(0, 6).forEach(p => {
      entry[p.name.slice(0, 18)] = p.components?.[comp] || 0
    })
    return entry
  })

  // Bar chart: average score per component across all products
  const avgCompData = allComponents.map(comp => {
    const vals = data.products.map(p => p.components?.[comp] || 0).filter(v => v > 0)
    return {
      component: comp.replace(/_/g, ' '),
      avg: vals.length ? Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 10) / 10 : 0,
      max: vals.length ? Math.max(...vals) : 0,
      min: vals.length ? Math.min(...vals) : 0,
    }
  }).sort((a, b) => b.avg - a.avg)

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Component Analysis</h1>
          <p className="text-gray-500 mt-1">Per-product breakdown for <span className="font-medium text-gray-700">"{data.query}"</span></p>
        </div>
        <span className="bg-blue-100 text-blue-700 text-xs font-semibold px-3 py-1 rounded-full">{data.category}</span>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Products', value: data.products.length, color: 'bg-blue-500' },
          { label: 'Components', value: allComponents.length, color: 'bg-purple-500' },
          { label: 'Winners', value: Object.keys(data.component_winners || {}).length, color: 'bg-yellow-500' },
          { label: 'Top Brand', value: data.top_brand, color: 'bg-green-500' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
            <div className={`${s.color} w-2 h-10 rounded-full flex-shrink-0`} />
            <div>
              <p className="text-xs text-gray-500">{s.label}</p>
              <p className="text-xl font-bold text-gray-900">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Tab nav */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {[['overview', 'Overview'], ['radar', 'Radar Chart'], ['table', 'Full Table']].map(([key, label]) => (
          <button key={key} onClick={() => setActiveTab(key)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeTab === key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
            {label}
          </button>
        ))}
      </div>

      {/* Overview tab */}
      {activeTab === 'overview' && (
        <>
          {/* Average component scores bar */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Average Component Scores</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={avgCompData} margin={{ top: 5, right: 20, left: 0, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="component" angle={-30} textAnchor="end" tick={{ fontSize: 11 }} interval={0} />
                <YAxis domain={[0, 5]} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => [`${v}/5`, '']} contentStyle={{ borderRadius: '8px' }} />
                <Bar dataKey="avg" radius={[6, 6, 0, 0]} maxBarSize={50}>
                  {avgCompData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Per-product expandable cards */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900">Per-Product Component Scores</h2>
            </div>
            <div className="divide-y divide-gray-100">
              {data.products.map((product, i) => {
                const isExpanded = expandedProduct === i
                const comps = Object.entries(product.components || {}).sort((a, b) => b[1] - a[1])
                const topComp = comps[0]
                const weakComp = comps[comps.length - 1]
                const color = COLORS[i % COLORS.length]
                return (
                  <div key={i}>
                    <button onClick={() => setExpandedProduct(isExpanded ? null : i)}
                      className="w-full px-6 py-4 flex items-center gap-4 hover:bg-gray-50 transition-colors text-left">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                        style={{ backgroundColor: color }}>{i + 1}</div>
                      <div className="flex-1 min-w-0">
                        <Link to={`/product/${encodeURIComponent(product.name)}`}
                          onClick={e => e.stopPropagation()}
                          className="font-medium text-gray-900 hover:text-blue-600 text-sm line-clamp-1">{product.name}</Link>
                        <div className="flex items-center gap-3 mt-0.5">
                          <span className="text-xs text-gray-500">{product.brand}</span>
                          <span className="text-xs text-gray-400">·</span>
                          <span className="text-xs text-gray-500 flex items-center gap-0.5">
                            <Star className="h-3 w-3 text-yellow-400 fill-yellow-400" />{product.rating}
                          </span>
                          {topComp && <span className="text-xs text-green-600">↑ {topComp[0].replace(/_/g, ' ')} {topComp[1].toFixed(1)}</span>}
                          {weakComp && weakComp[0] !== topComp?.[0] && <span className="text-xs text-red-500">↓ {weakComp[0].replace(/_/g, ' ')} {weakComp[1].toFixed(1)}</span>}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-400">{comps.length} components</span>
                        {isExpanded ? <ChevronUp className="h-4 w-4 text-gray-400" /> : <ChevronDown className="h-4 w-4 text-gray-400" />}
                      </div>
                    </button>
                    {isExpanded && (
                      <div className="px-6 pb-5 bg-gray-50 grid grid-cols-1 md:grid-cols-2 gap-3">
                        {comps.map(([comp, score]) => {
                          const isWinner = data.component_winners?.[comp] === product.name
                          return (
                            <div key={comp} className={`flex items-center gap-3 p-2 rounded-lg ${isWinner ? 'bg-yellow-50 border border-yellow-200' : ''}`}>
                              <div className="w-28 flex-shrink-0">
                                <span className="text-xs text-gray-600 capitalize">{comp.replace(/_/g, ' ')}</span>
                                {isWinner && <span className="ml-1 text-xs text-yellow-600">🏆</span>}
                              </div>
                              <div className="flex-1">
                                <ScoreBar score={score} color={color} />
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </>
      )}

      {/* Radar tab */}
      {activeTab === 'radar' && radarData.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Component Radar — All Products</h2>
          <ResponsiveContainer width="100%" height={480}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="component" tick={{ fontSize: 12, fontWeight: 'bold', fill: '#374151' }} />
              <PolarRadiusAxis angle={90} domain={[0, 5]} tick={{ fontSize: 9 }} />
              {data.products.slice(0, 6).map((p, i) => (
                <Radar key={i} name={p.name.slice(0, 18)} dataKey={p.name.slice(0, 18)}
                  stroke={COLORS[i % COLORS.length]} fill={COLORS[i % COLORS.length]}
                  fillOpacity={0.12} strokeWidth={2} />
              ))}
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Tooltip formatter={(v) => [`${v}/5`, '']} contentStyle={{ borderRadius: '8px' }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Table tab */}
      {activeTab === 'table' && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">Full Component Score Table</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase sticky left-0 bg-gray-50">Product</th>
                  {allComponents.map(c => (
                    <th key={c} className="px-3 py-3 text-center text-sm font-bold text-gray-700 uppercase whitespace-nowrap">
                      {c.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.products.map((product, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-3 sticky left-0 bg-white">
                      <Link to={`/product/${encodeURIComponent(product.name)}`}
                        className="text-blue-600 hover:underline text-sm font-bold block">
                        {product.name}
                      </Link>
                      <span className="text-xs text-gray-400">{product.brand}</span>
                    </td>
                    {allComponents.map(c => {
                      const score = product.components?.[c] || 0
                      const isWinner = data.component_winners?.[c] === product.name
                      const bg = score >= 4 ? 'text-green-700 bg-green-50' : score >= 3 ? 'text-yellow-700 bg-yellow-50' : score > 0 ? 'text-red-700 bg-red-50' : 'text-gray-400'
                      return (
                        <td key={c} className="px-3 py-3 text-center">
                          {score > 0 ? (
                            <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${bg} ${isWinner ? 'ring-1 ring-yellow-400' : ''}`}>
                              {score.toFixed(1)}{isWinner ? ' 🏆' : ''}
                            </span>
                          ) : <span className="text-gray-300 text-xs">—</span>}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Component Winners */}
      {Object.keys(data.component_winners || {}).length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Trophy className="h-5 w-5 text-yellow-500" />
            <h2 className="text-lg font-semibold text-gray-900">Component Winners</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(data.component_winners).map(([component, winner]) => {
              const score = data.products.find(p => p.name === winner)?.components?.[component] || 0
              const brand = data.products.find(p => p.name === winner)?.brand || ''
              const idx = data.products.findIndex(p => p.name === winner)
              return (
                <div key={component} className="bg-gradient-to-br from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-yellow-700 uppercase tracking-wide">{component.replace(/_/g, ' ')}</span>
                    <span className="text-sm font-bold text-yellow-600">{score.toFixed(1)}/5</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-800">{winner}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                    <span className="text-xs font-medium text-gray-600">{brand}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default ComponentAnalysis
