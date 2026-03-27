import React, { useState } from 'react'
import { useAnalysis } from '../contexts/AnalysisContext'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import { Package, MessageSquare, Trophy, Clock, Search, ChevronRight, Building2, Users } from 'lucide-react'

const Dashboard = () => {
  const { data, loading, error, query, jobStatus, search, sellerBrand, selectBrand, comparisonLoading } = useAnalysis()
  const [inputValue, setInputValue] = useState('')
  const navigate = useNavigate()

  const handleSearch = (e) => {
    e.preventDefault()
    if (inputValue.trim()) search(inputValue.trim())
  }

  const handleBrandSelect = async (brand) => {
    await selectBrand(brand)
    navigate('/competitor-analysis')
  }

  const statusMsg = {
    pending: 'Starting analysis...',
    running: 'Scraping products across brands...',
  }

  const brands = data ? Object.keys(data.brands) : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Seller Intelligence Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Search a product category, then select your brand to compare against competitors</p>
      </div>

      {/* Step 1: Search */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center">1</span>
          <h2 className="font-semibold text-gray-900 dark:text-white">Search Product Category</h2>
        </div>
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input type="text" value={inputValue} onChange={e => setInputValue(e.target.value)}
              placeholder="e.g. laptops, wireless headphones, running shoes..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
          </div>
          <button type="submit" disabled={loading || !inputValue.trim()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            {loading ? 'Scraping...' : 'Search'}
          </button>
        </form>
        <div className="flex flex-wrap gap-2 mt-3">
          {['laptops', 'wireless headphones', 'running shoes', 'smartphones', 'coffee maker'].map(s => (
            <button key={s} onClick={() => { setInputValue(s); search(s) }}
              className="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-full text-xs hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 transition-colors">
              {s}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-12 text-center shadow-sm">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-300 font-medium">{statusMsg[jobStatus] || 'Analyzing...'}</p>
          <p className="text-sm text-gray-400 mt-1">Scraping real-time data from multiple e-commerce sites</p>
        </div>
      )}

      {error && !loading && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
          <p className="text-red-800 dark:text-red-300 font-medium">Error: {error}</p>
          <p className="text-red-600 dark:text-red-400 text-sm mt-1">Make sure the backend is running at https://datathon-production-c1f0.up.railway.app</p>
        </div>
      )}

      {/* Step 2: Brand Selection */}
      {data && !loading && (
        <>
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-6 h-6 rounded-full bg-green-600 text-white text-xs font-bold flex items-center justify-center">2</span>
              <h2 className="font-semibold text-gray-900 dark:text-white">Select Your Brand</h2>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 ml-8">
              Found {brands.length} brands for "{data.query}". Select the brand you own to compare against competitors.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {brands.map((brand) => {
                const info = data.brands[brand]
                const isSelected = sellerBrand === brand
                return (
                  <button key={brand} onClick={() => handleBrandSelect(brand)}
                    disabled={comparisonLoading}
                    className={`relative p-4 rounded-xl border-2 text-left transition-all hover:shadow-md disabled:opacity-60 ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-blue-300'
                    }`}>
                    <div className="flex items-center justify-between mb-2">
                      <Building2 className={`h-5 w-5 ${isSelected ? 'text-blue-600' : 'text-gray-400'}`} />
                      {comparisonLoading && isSelected && <LoadingSpinner size="sm" />}
                    </div>
                    <p className="font-semibold text-gray-900 dark:text-white text-sm">{brand}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {info.average_rating > 0 ? `${info.average_rating}★` : 'N/A'} · {info.products.length} product{info.products.length !== 1 ? 's' : ''}
                    </p>
                    <div className="flex items-center gap-1 mt-2 text-xs text-blue-600 dark:text-blue-400 font-medium">
                      <span>Compare</span>
                      <ChevronRight className="h-3 w-3" />
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Quick stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Products Found', value: data.total_products, icon: Package, color: 'bg-blue-500' },
              { name: 'Brands Found', value: brands.length, icon: Users, color: 'bg-green-500' },
              { name: 'Market Leader', value: data.top_brand, icon: Trophy, color: 'bg-yellow-500' },
              { name: 'Analysis Time', value: data.execution_time, icon: Clock, color: 'bg-purple-500' },
            ].map(stat => (
              <div key={stat.name} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4 flex items-center gap-3 shadow-sm">
                <div className={`${stat.color} p-2.5 rounded-xl flex-shrink-0`}>
                  <stat.icon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{stat.name}</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">{stat.value}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Brand overview table */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
              <h2 className="font-semibold text-gray-900 dark:text-white">All Brands Found</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    {['Brand', 'Avg Rating', 'Avg Price', 'Products', 'Action'].map(h => (
                      <th key={h} className="px-5 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {Object.entries(data.brands).map(([brand, info]) => (
                    <tr key={brand} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                      <td className="px-5 py-3 font-medium text-gray-900 dark:text-white">{brand}</td>
                      <td className="px-5 py-3 text-gray-600 dark:text-gray-400">{info.average_rating > 0 ? `${info.average_rating}★` : 'N/A'}</td>
                      <td className="px-5 py-3 text-gray-600 dark:text-gray-400">{info.average_price > 0 ? `$${info.average_price}` : 'N/A'}</td>
                      <td className="px-5 py-3 text-gray-600 dark:text-gray-400">{info.products.length}</td>
                      <td className="px-5 py-3">
                        <button onClick={() => handleBrandSelect(brand)}
                          disabled={comparisonLoading}
                          className="text-xs px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 transition-colors">
                          Select as My Brand
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {!loading && !error && !data && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-16 text-center shadow-sm">
          <Search className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-600 dark:text-gray-300">Start by searching a product category</h2>
          <p className="text-gray-400 dark:text-gray-500 mt-2">We'll scrape real products, then you select your brand to see how you compare</p>
        </div>
      )}
    </div>
  )
}

export default Dashboard
