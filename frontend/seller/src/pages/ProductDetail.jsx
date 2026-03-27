import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAnalysis } from '../contexts/AnalysisContext'
import LoadingSpinner from '../components/LoadingSpinner'
import { ArrowLeft, Star, MessageSquare, TrendingUp, Users, AlertTriangle, ExternalLink } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

const COLORS = ['#10b981', '#f59e0b', '#ef4444']

const ProductDetail = () => {
  const { productName } = useParams()
  const { data, loading, error } = useAnalysis()

  if (loading) return <div className="flex justify-center py-24"><LoadingSpinner size="lg" /></div>
  if (error) return <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6"><p className="text-red-800 dark:text-red-300">Error: {error}</p></div>
  if (!data) return (
    <div className="card text-center py-8">
      <p className="text-gray-500 dark:text-gray-400">No data available. Please search for a product first.</p>
      <Link to="/" className="mt-3 inline-block text-blue-600 hover:underline">Go to Dashboard</Link>
    </div>
  )

  const product = data.products.find(p => p.name === decodeURIComponent(productName))
  if (!product) return (
    <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4">
      <p className="text-yellow-800 dark:text-yellow-300">Product not found. <Link to="/" className="underline">Back to Dashboard</Link></p>
    </div>
  )

  const sentimentData = [
    { name: 'Positive', value: Math.round((product.sentiment?.positive || 0) * 100) },
    { name: 'Neutral', value: Math.round((product.sentiment?.neutral || 0) * 100) },
    { name: 'Negative', value: Math.round((product.sentiment?.negative || 0) * 100) },
  ]
  const components = product.components || {}
  const radarData = Object.entries(components).map(([comp, score]) => ({ component: comp.replace(/_/g, ' '), score }))
  const relatedIssues = (data.customer_issues || []).filter(issue =>
    issue.affected_products?.some(p => p.includes(product.name.slice(0, 20)))
  )

  return (
    <div className="space-y-6">
      <Link to="/" className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline text-sm">
        <ArrowLeft className="h-4 w-4" />Back to Dashboard
      </Link>

      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-2xl p-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{product.name}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">{product.brand} · {product.source}</p>
            {product.url && (
              <a href={product.url} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 hover:underline mt-1">
                View on {product.source} <ExternalLink className="h-3.5 w-3.5" />
              </a>
            )}
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{product.price > 0 ? `$${product.price}` : 'N/A'}</p>
            <div className="flex items-center justify-end mt-1 gap-1">
              <Star className="h-5 w-5 text-yellow-400 fill-yellow-400" />
              <span className="text-lg font-semibold text-gray-900 dark:text-white">{product.rating || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Listed Reviews', value: (product.reviews || 0).toLocaleString(), icon: MessageSquare, color: 'text-blue-600 dark:text-blue-400' },
          { label: 'Rating', value: product.rating || 'N/A', icon: Star, color: 'text-yellow-500' },
          { label: 'Sentiment Score', value: product.sentiment?.average_score?.toFixed(2) || '0.00', icon: TrendingUp, color: 'text-purple-600 dark:text-purple-400' },
          { label: 'Components Found', value: Object.keys(components).length, icon: Users, color: 'text-green-600 dark:text-green-400' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card flex items-center gap-3">
            <Icon className={`h-7 w-7 ${color} flex-shrink-0`} />
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Component Scores */}
      {Object.keys(components).length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Component Performance</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {Object.entries(components).map(([comp, score]) => {
              const isWinner = data.component_winners?.[comp] === product.name
              return (
                <div key={comp} className={`text-center p-3 rounded-xl border-2 transition-colors ${isWinner ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800'}`}>
                  <h3 className="text-xs font-semibold text-gray-600 dark:text-gray-400 capitalize">{comp.replace(/_/g, ' ')}</h3>
                  <p className={`text-2xl font-bold mt-1 ${isWinner ? 'text-green-600 dark:text-green-400' : 'text-gray-800 dark:text-gray-200'}`}>{score.toFixed(1)}</p>
                  {isWinner && <p className="text-xs text-green-600 dark:text-green-400 mt-0.5">🏆 Winner</p>}
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Pie */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Sentiment Breakdown</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={sentimentData} cx="50%" cy="50%" outerRadius={85} dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`} labelLine={false}>
                {sentimentData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip formatter={v => `${v}%`} contentStyle={{ borderRadius: '8px' }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Component Radar */}
        {radarData.length > 0 && (
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Component Radar</h2>
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="component" tick={{ fontSize: 11, fontWeight: 'bold', fill: '#374151' }} />
                <PolarRadiusAxis angle={90} domain={[0, 5]} tick={{ fontSize: 9 }} />
                <Radar name={product.brand} dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} />
                <Tooltip formatter={v => [`${v}/5`, '']} contentStyle={{ borderRadius: '8px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Related Issues */}
      {relatedIssues.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Related Customer Issues</h2>
          </div>
          <div className="space-y-2">
            {relatedIssues.map((issue, i) => (
              <div key={i} className="border border-gray-200 dark:border-gray-700 rounded-xl p-3 flex items-center justify-between">
                <span className="font-medium text-gray-900 dark:text-white text-sm">{issue.issue}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500 dark:text-gray-400">{issue.percentage}%</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    issue.severity === 'High' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                    issue.severity === 'Medium' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' :
                    'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                  }`}>{issue.severity}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Market Position */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Market Position</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { icon: Users, color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-900/20', label: 'Brand Rank', value: `#${Object.keys(data.brands).indexOf(product.brand) + 1}`, sub: `of ${Object.keys(data.brands).length} brands` },
            { icon: TrendingUp, color: 'text-green-600 dark:text-green-400', bg: 'bg-green-50 dark:bg-green-900/20', label: 'Price Rank', value: `#${data.products.filter(p => p.price > 0 && p.price < product.price).length + 1}`, sub: 'cheapest position' },
            { icon: Star, color: 'text-purple-600 dark:text-purple-400', bg: 'bg-purple-50 dark:bg-purple-900/20', label: 'Rating Rank', value: `#${data.products.filter(p => p.rating > product.rating).length + 1}`, sub: 'highest rated' },
          ].map(({ icon: Icon, color, bg, label, value, sub }) => (
            <div key={label} className={`text-center p-4 ${bg} rounded-xl`}>
              <Icon className={`h-8 w-8 mx-auto mb-2 ${color}`} />
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm">{label}</h3>
              <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{sub}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ProductDetail
