import React, { useState } from 'react'
import { useAnalysis } from '../contexts/AnalysisContext'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, ReferenceLine
} from 'recharts'
import {
  TrendingUp, TrendingDown, Minus, Trophy, AlertTriangle,
  Target, DollarSign, Star, ArrowRight, Zap, Search, Building2
} from 'lucide-react'

const SELLER_COLOR = '#3b82f6'
const COMP_COLOR = '#94a3b8'

const insightColors = {
  STRENGTH: { bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-200 dark:border-green-800', icon: TrendingUp, iconColor: 'text-green-600 dark:text-green-400', badge: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300' },
  WEAKNESS: { bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-200 dark:border-red-800', icon: TrendingDown, iconColor: 'text-red-600 dark:text-red-400', badge: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300' },
  OPPORTUNITY: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', border: 'border-yellow-200 dark:border-yellow-800', icon: Zap, iconColor: 'text-yellow-600 dark:text-yellow-400', badge: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300' },
  PRICING: { bg: 'bg-purple-50 dark:bg-purple-900/20', border: 'border-purple-200 dark:border-purple-800', icon: DollarSign, iconColor: 'text-purple-600 dark:text-purple-400', badge: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300' },
  RATING: { bg: 'bg-blue-50 dark:bg-blue-900/20', border: 'border-blue-200 dark:border-blue-800', icon: Star, iconColor: 'text-blue-600 dark:text-blue-400', badge: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300' },
}

const prioColors = {
  High: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
  Medium: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300',
  Low: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
}

const GapBar = ({ component, sellerScore, competitorScore, gap }) => {
  const isStrength = gap > 0.2
  const isWeakness = gap < -0.2
  const color = isStrength ? '#10b981' : isWeakness ? '#ef4444' : '#94a3b8'
  const label = component.replace(/_/g, ' ')

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-gray-700 dark:text-gray-300 capitalize w-28 truncate">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-blue-600 dark:text-blue-400 font-semibold">{sellerScore.toFixed(1)}</span>
          <span className="text-gray-400">vs</span>
          <span className="text-gray-500 dark:text-gray-400">{competitorScore.toFixed(1)}</span>
          <span className={`font-bold w-12 text-right`} style={{ color }}>
            {gap > 0 ? '+' : ''}{gap.toFixed(2)}
          </span>
        </div>
      </div>
      <div className="relative h-3 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
        {/* Competitor bar */}
        <div className="absolute inset-y-0 left-0 rounded-full bg-gray-300 dark:bg-gray-600 transition-all"
          style={{ width: `${(competitorScore / 5) * 100}%` }} />
        {/* Seller bar */}
        <div className="absolute inset-y-0 left-0 rounded-full transition-all opacity-90"
          style={{ width: `${(sellerScore / 5) * 100}%`, backgroundColor: color }} />
      </div>
    </div>
  )
}

const SummaryCard = ({ label, sellerVal, compVal, unit = '', icon: Icon, isGoodHigh = true }) => {
  const diff = sellerVal - compVal
  const isPositive = isGoodHigh ? diff > 0 : diff < 0
  const isNeutral = Math.abs(diff) < 0.1
  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="h-4 w-4 text-gray-400" />
        <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">{label}</span>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{unit}{sellerVal.toFixed(1)}</p>
          <p className="text-xs text-gray-400 mt-0.5">Your brand</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-semibold text-gray-500 dark:text-gray-400">{unit}{compVal.toFixed(1)}</p>
          <p className="text-xs text-gray-400 mt-0.5">Competitors</p>
        </div>
      </div>
      <div className={`mt-3 flex items-center gap-1 text-xs font-medium ${isNeutral ? 'text-gray-500' : isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
        {isNeutral ? <Minus className="h-3 w-3" /> : isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
        <span>{isNeutral ? 'On par' : isPositive ? `+${Math.abs(diff).toFixed(1)} ahead` : `${Math.abs(diff).toFixed(1)} behind`}</span>
      </div>
    </div>
  )
}

const CompetitorAnalysis = () => {
  const { data, loading, comparisonData, comparisonLoading, comparisonError, sellerBrand, selectBrand } = useAnalysis()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('gap')

  if (loading || comparisonLoading) return (
    <div className="flex flex-col items-center justify-center py-24">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-500 text-sm">{loading ? 'Scraping products...' : 'Running comparison analysis...'}</p>
    </div>
  )

  if (!data) return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <Search className="h-12 w-12 text-gray-300 dark:text-gray-600 mb-4" />
      <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">No data yet</h3>
      <p className="text-gray-400 mt-1">Go to Dashboard and search for a product category first</p>
      <button onClick={() => navigate('/')} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
        Go to Dashboard
      </button>
    </div>
  )

  if (!sellerBrand || !comparisonData) return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Competitor Analysis</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Select your brand to see the comparison</p>
      </div>
      {comparisonError && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
          <p className="text-red-800 dark:text-red-300">{comparisonError}</p>
        </div>
      )}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <Building2 className="h-5 w-5 text-gray-400" />
          <h2 className="font-semibold text-gray-900 dark:text-white">Select Your Brand</h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {Object.keys(data.brands).map(brand => (
            <button key={brand} onClick={() => selectBrand(brand)}
              className="p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-blue-400 text-left transition-all hover:shadow-md">
              <p className="font-semibold text-gray-900 dark:text-white text-sm">{brand}</p>
              <p className="text-xs text-gray-500 mt-1">{data.brands[brand].average_rating}★ · {data.brands[brand].products.length} products</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  )

  const c = comparisonData
  const { summary, gap_analysis, strengths, weaknesses, business_insights, recommendations } = c

  // Radar data
  const radarData = gap_analysis.map(g => ({
    component: g.component.replace(/_/g, ' '),
    [sellerBrand]: g.seller_score,
    Competitors: g.competitor_score,
  }))

  // Gap bar chart data
  const gapChartData = [...gap_analysis].sort((a, b) => a.gap - b.gap).map(g => ({
    name: g.component.replace(/_/g, ' '),
    gap: g.gap,
    fill: g.gap > 0.2 ? '#10b981' : g.gap < -0.2 ? '#ef4444' : '#94a3b8',
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {sellerBrand} vs Market
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Competing against: {c.competitor_brands.join(', ')} · "{data.query}"
          </p>
        </div>
        <div className="flex gap-2">
          <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-semibold px-3 py-1 rounded-full">{data.category}</span>
          <button onClick={() => navigate('/')} className="text-xs px-3 py-1 border border-gray-200 dark:border-gray-700 rounded-full text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
            Change Brand
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <SummaryCard label="Avg Rating" sellerVal={summary.seller.avg_rating} compVal={summary.competitors.avg_rating} icon={Star} />
        <SummaryCard label="Avg Price" sellerVal={summary.seller.avg_price} compVal={summary.competitors.avg_price} unit="$" icon={DollarSign} isGoodHigh={false} />
        <SummaryCard label="Sentiment Score" sellerVal={summary.seller.avg_sentiment} compVal={summary.competitors.avg_sentiment} icon={TrendingUp} />
      </div>

      {/* Business Insights */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Business Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {business_insights.map((insight, i) => {
            const style = insightColors[insight.type] || insightColors.RATING
            const Icon = style.icon
            return (
              <div key={i} className={`rounded-xl border p-4 ${style.bg} ${style.border}`}>
                <div className="flex items-start gap-3">
                  <Icon className={`h-5 w-5 mt-0.5 flex-shrink-0 ${style.iconColor}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${style.badge}`}>{insight.type}</span>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${prioColors[insight.impact] || prioColors.Low}`}>{insight.impact} Impact</span>
                    </div>
                    <p className="font-semibold text-gray-900 dark:text-white text-sm">{insight.title}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{insight.detail}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Tab nav */}
      <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-xl w-fit">
        {[['gap', 'Gap Analysis'], ['radar', 'Radar Chart'], ['chart', 'Score Chart']].map(([key, label]) => (
          <button key={key} onClick={() => setActiveTab(key)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeTab === key ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}>
            {label}
          </button>
        ))}
      </div>

      {/* Gap Analysis Tab */}
      {activeTab === 'gap' && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <Target className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Component Gap Analysis</h2>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-5">
            <span className="inline-flex items-center gap-1 mr-3"><span className="w-3 h-3 rounded-full bg-green-500 inline-block" />Strength (you lead)</span>
            <span className="inline-flex items-center gap-1 mr-3"><span className="w-3 h-3 rounded-full bg-red-500 inline-block" />Weakness (competitor leads)</span>
            <span className="inline-flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-gray-400 inline-block" />Neutral</span>
          </p>
          <div className="space-y-4">
            {gap_analysis.map((g, i) => (
              <GapBar key={i} component={g.component} sellerScore={g.seller_score} competitorScore={g.competitor_score} gap={g.gap} />
            ))}
          </div>
          <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 text-xs text-gray-500">
            <span className="flex items-center gap-1"><span className="w-3 h-2 rounded bg-blue-500 inline-block opacity-90" />{sellerBrand} (your brand)</span>
            <span className="flex items-center gap-1"><span className="w-3 h-2 rounded bg-gray-300 dark:bg-gray-600 inline-block" />Competitors (avg)</span>
          </div>
        </div>
      )}

      {/* Radar Tab */}
      {activeTab === 'radar' && radarData.length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{sellerBrand} vs Competitors — Radar</h2>
          <ResponsiveContainer width="100%" height={420}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="component" tick={{ fontSize: 12, fontWeight: 'bold', fill: '#374151' }} />
              <PolarRadiusAxis angle={90} domain={[0, 5]} tick={{ fontSize: 9 }} />
              <Radar name={sellerBrand} dataKey={sellerBrand} stroke={SELLER_COLOR} fill={SELLER_COLOR} fillOpacity={0.25} strokeWidth={2.5} />
              <Radar name="Competitors" dataKey="Competitors" stroke={COMP_COLOR} fill={COMP_COLOR} fillOpacity={0.1} strokeWidth={1.5} strokeDasharray="4 2" />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Tooltip formatter={(v) => [`${v}/5`, '']} contentStyle={{ borderRadius: '8px' }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Gap Bar Chart Tab */}
      {activeTab === 'chart' && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Gap Score by Component</h2>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">Positive = you lead, Negative = competitor leads</p>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={gapChartData} margin={{ top: 5, right: 20, left: 0, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" angle={-30} textAnchor="end" tick={{ fontSize: 11 }} interval={0} />
              <YAxis domain={[-2, 2]} tick={{ fontSize: 11 }} />
              <ReferenceLine y={0} stroke="#374151" strokeWidth={1.5} />
              <Tooltip formatter={(v) => [`${v > 0 ? '+' : ''}${v.toFixed(2)}`, 'Gap']} contentStyle={{ borderRadius: '8px' }} />
              <Bar dataKey="gap" radius={[4, 4, 0, 0]} maxBarSize={50}>
                {gapChartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-green-50 dark:bg-green-900/10 rounded-2xl border border-green-200 dark:border-green-800 p-5">
          <div className="flex items-center gap-2 mb-3">
            <Trophy className="h-5 w-5 text-green-600 dark:text-green-400" />
            <h2 className="font-semibold text-gray-900 dark:text-white">Strengths ({strengths.length})</h2>
          </div>
          {strengths.length === 0 ? (
            <p className="text-sm text-gray-500">No clear strengths detected yet</p>
          ) : (
            <div className="space-y-2">
              {strengths.map((s, i) => (
                <div key={i} className="flex items-center justify-between bg-white dark:bg-gray-900 rounded-lg px-3 py-2">
                  <span className="text-sm font-bold text-gray-800 dark:text-gray-200 capitalize">{s.component.replace(/_/g, ' ')}</span>
                  <span className="text-xs font-bold text-green-600 dark:text-green-400">+{s.gap.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-red-50 dark:bg-red-900/10 rounded-2xl border border-red-200 dark:border-red-800 p-5">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
            <h2 className="font-semibold text-gray-900 dark:text-white">Weaknesses ({weaknesses.length})</h2>
          </div>
          {weaknesses.length === 0 ? (
            <p className="text-sm text-gray-500">No significant weaknesses detected</p>
          ) : (
            <div className="space-y-2">
              {weaknesses.map((w, i) => (
                <div key={i} className="flex items-center justify-between bg-white dark:bg-gray-900 rounded-lg px-3 py-2">
                  <span className="text-sm font-bold text-gray-800 dark:text-gray-200 capitalize">{w.component.replace(/_/g, ' ')}</span>
                  <span className="text-xs font-bold text-red-600 dark:text-red-400">{w.gap.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Sales Recommendations */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <ArrowRight className="h-5 w-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Sales Improvement Recommendations</h2>
        </div>
        <div className="space-y-3">
          {recommendations.map((rec, i) => (
            <div key={i} className="flex items-start gap-4 p-4 rounded-xl border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <span className={`text-xs font-bold px-2 py-1 rounded-full flex-shrink-0 mt-0.5 ${prioColors[rec.priority] || prioColors.Low}`}>{rec.priority}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-gray-400 font-medium">{rec.category}</span>
                </div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{rec.action}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{rec.expected_impact}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default CompetitorAnalysis
