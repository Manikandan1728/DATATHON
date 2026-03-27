import React from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useAnalysis } from "../contexts/AnalysisContext"
import { useTheme } from "../contexts/ThemeContext"
import { LogOut, User, Sun, Moon } from "lucide-react"

const Navbar = () => {
  const { user, logout } = useAuth()
  const { loading } = useAnalysis()
  const { dark, toggle } = useTheme()
  const navigate = useNavigate()

  return (
    <div className="sticky top-0 z-40 bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
      <div className="flex h-16 items-center justify-end gap-3 px-4 sm:px-6 lg:px-8">
        {loading && (
          <span className="text-xs text-blue-500 dark:text-blue-400 font-medium animate-pulse mr-auto">
            Analyzing...
          </span>
        )}
        <button
          onClick={toggle}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          title={dark ? "Switch to light mode" : "Switch to dark mode"}
        >
          {dark
            ? <Sun className="h-5 w-5 text-yellow-400" />
            : <Moon className="h-5 w-5 text-gray-500" />
          }
        </button>
        {user && (
          <>
            {user.photoURL
              ? <img className="h-8 w-8 rounded-full ring-2 ring-gray-200 dark:ring-gray-700" src={user.photoURL} alt="Profile" />
              : (
                <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                  <User className="h-4 w-4 text-white" />
                </div>
              )
            }
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100 hidden sm:block">
              {user.displayName || user.email}
            </span>
            <button
              onClick={() => { logout(); navigate("/login") }}
              className="p-2 rounded-lg text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              title="Sign out"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default Navbar