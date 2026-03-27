import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth'
import { auth } from '../firebase/config'
import { useAuth } from '../contexts/AuthContext'
import { Mail, Lock, Eye, EyeOff, AlertCircle, CheckCircle, BarChart2, TrendingUp, Shield } from 'lucide-react'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const navigate = useNavigate()
  const { login, isAuthenticated, loading } = useAuth()
  const location = useLocation()

  // Clear any stored auth data on component mount to ensure fresh login
  useEffect(() => {
    if (!isAuthenticated) {
      setEmail('')
      setPassword('')
      setError('')
      setSuccess('')
    }
  }, [])

  // Additional reset to prevent browser auto-fill
  useEffect(() => {
    const timer = setTimeout(() => {
      setEmail('')
      setPassword('')
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (isAuthenticated && !loading) {
      navigate(location.state?.from?.pathname || '/dashboard', { replace: true })
    }
  }, [isAuthenticated, loading, navigate, location.state])

  const handleGoogleSignIn = async () => {
    setIsLoading(true)
    setError('')
    try {
      const provider = new GoogleAuthProvider()
      provider.setCustomParameters({ prompt: 'select_account' })
      const result = await signInWithPopup(auth, provider)
      const user = result.user
      login({ uid: user.uid, email: user.email, displayName: user.displayName, photoURL: user.photoURL })
      setSuccess('Signed in successfully!')
      setTimeout(() => navigate(location.state?.from?.pathname || '/dashboard', { replace: true }), 1000)
    } catch (err) {
      if (err.code === 'auth/popup-closed-by-user') setError('Sign-in popup was closed.')
      else if (err.code === 'auth/popup-blocked') setError('Pop-up blocked. Please allow pop-ups and try again.')
      else setError('Failed to sign in with Google. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Basic validation
    if (!email || !password) { 
      setError('Please fill in all fields.'); 
      return 
    }
    if (password.length < 6) { 
      setError('Password must be at least 6 characters.'); 
      return 
    }
    
    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address.')
      return
    }
    
    setIsLoading(true)
    setError('')
    
    try {
      // Simulate authentication with hardcoded credentials
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Hardcoded valid credentials for demo
      const validCredentials = [
        { email: 'admin@example.com', password: 'admin123', name: 'Admin User' },
        { email: 'user@example.com', password: 'user123', name: 'Demo User' },
        { email: 'test@example.com', password: 'test123', name: 'Test User' }
      ]
      
      const isValidUser = validCredentials.find(cred => 
        cred.email === email && cred.password === password
      )
      
      if (isValidUser) {
        // Successful login - use AuthContext login function
        const result = await login({
          email: isValidUser.email,
          displayName: isValidUser.name
        })
        
        if (result.success) {
          setSuccess('Signed in successfully!')
          // Navigate to dashboard after successful login
          setTimeout(() => {
            navigate(location.state?.from?.pathname || '/dashboard', { replace: true })
          }, 1000)
        } else {
          setError(result.error || 'Login failed')
        }
      } else {
        // Failed login
        setError('Invalid email or password. Please try again.')
      }
      
    } catch (err) {
      setError('Login failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 flex-col justify-between p-12 text-white">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 p-2 rounded-xl">
            <BarChart2 className="h-7 w-7 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">Seller Intelligence</span>
        </div>
        <div>
          <h1 className="text-4xl font-bold leading-tight mb-4">
            Real-time product<br />intelligence for sellers
          </h1>
          <p className="text-blue-200 text-lg mb-10">
            Scrape, analyze, and compare products across the web. Understand your competition and customers instantly.
          </p>
          <div className="space-y-4">
            {[
              { icon: TrendingUp, text: 'Live competitor analysis across Amazon, eBay & more' },
              { icon: BarChart2, text: 'Component-level product scoring & comparison' },
              { icon: Shield, text: 'AI-powered customer issue detection' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3">
                <div className="bg-white/15 p-2 rounded-lg flex-shrink-0">
                  <Icon className="h-4 w-4 text-white" />
                </div>
                <span className="text-blue-100 text-sm">{text}</span>
              </div>
            ))}
          </div>
        </div>
        <p className="text-blue-300 text-xs">© 2026 Seller Intelligence. All rights reserved.</p>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-6 bg-gray-50">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="bg-blue-600 p-2 rounded-xl">
              <BarChart2 className="h-6 w-6 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-900">Seller Intelligence</span>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">
              Welcome back
            </h2>
            <p className="text-gray-500 text-sm mb-6">
              Sign in to your dashboard
            </p>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-3 flex items-center gap-2 mb-4">
                <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
            {success && (
              <div className="bg-green-50 border border-green-200 rounded-xl p-3 flex items-center gap-2 mb-4">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                <p className="text-green-700 text-sm">{success}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input 
                    type="text" 
                    value={email} 
                    onChange={e => setEmail(e.target.value)}
                    autoComplete="new-password"
                    autoCorrect="off"
                    autoCapitalize="off"
                    spellCheck="false"
                    name="email-field"
                    id="email-field"
                    required
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all" 
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input 
                    type="password" 
                    value={password} 
                    onChange={e => setPassword(e.target.value)}
                    autoComplete="new-password"
                    autoCorrect="off"
                    autoCapitalize="off"
                    spellCheck="false"
                    name="password-field"
                    id="password-field"
                    required
                    className="w-full pl-10 pr-10 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all" 
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex justify-end">
                <a href="#" className="text-xs text-blue-600 hover:text-blue-800">Forgot password?</a>
              </div>

              <button type="submit" disabled={isLoading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                {isLoading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : null}
                {isLoading ? 'Please wait...' : 'Sign In'}
              </button>
            </form>

            <div className="relative my-5">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-200" /></div>
              <div className="relative flex justify-center"><span className="px-3 bg-white text-xs text-gray-400">or continue with</span></div>
            </div>

            <button onClick={handleGoogleSignIn} disabled={isLoading}
              className="w-full flex items-center justify-center gap-3 py-3 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50">
              <svg className="h-4 w-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Sign in with Google
            </button>
          </div>

          <p className="text-center text-xs text-gray-400 mt-6">
            By continuing, you agree to our{' '}
            <a href="#" className="text-blue-600 hover:underline">Terms</a> and{' '}
            <a href="#" className="text-blue-600 hover:underline">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
