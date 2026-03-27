import React from 'react'
import { Link } from 'react-router-dom'
import { ExternalLink, Star } from 'lucide-react'

const sourceColors = {
  amazon: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400',
  ebay: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
  walmart: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
  bestbuy: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400',
  google_shopping: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
}

const ProductCard = ({ product }) => {
  const sentiment = product.sentiment?.positive || 0
  const sentimentColor = sentiment > 0.6 ? 'text-green-600 dark:text-green-400' : sentiment > 0.4 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'

  return (
    <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-xl hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md dark:hover:shadow-blue-900/20 transition-all duration-200 overflow-hidden">
      <Link to={`/product/${encodeURIComponent(product.name)}`} className="block p-4">
        <div className="flex items-start justify-between mb-2">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sourceColors[product.source] || 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'}`}>
            {product.source}
          </span>
          {product.url && (
            <a href={product.url} target="_blank" rel="noopener noreferrer"
              onClick={e => e.stopPropagation()}
              className="text-gray-400 hover:text-blue-500 dark:hover:text-blue-400">
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>
        <h3 className="font-semibold text-gray-900 dark:text-white text-sm leading-tight mb-1 line-clamp-2">{product.name}</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{product.brand}</p>
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
            {product.price > 0 ? `$${product.price}` : 'N/A'}
          </span>
          <div className="flex items-center gap-1">
            <Star className="h-3.5 w-3.5 text-yellow-400 fill-yellow-400" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{product.rating || 'N/A'}</span>
          </div>
        </div>
        <div className="mt-2 flex items-center justify-between">
          <p className="text-xs text-gray-400 dark:text-gray-500">{(product.reviews || 0).toLocaleString()} reviews</p>
          <span className={`text-xs font-medium ${sentimentColor}`}>{Math.round(sentiment * 100)}% positive</span>
        </div>
      </Link>
    </div>
  )
}

export default ProductCard
