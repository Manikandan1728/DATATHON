import React from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { AnalysisProvider } from "./contexts/AnalysisContext"
import { AuthProvider } from "./contexts/AuthContext"
import { ThemeProvider } from "./contexts/ThemeContext"
import ProtectedRoute from "./components/ProtectedRoute"
import Sidebar from "./components/Sidebar"
import Navbar from "./components/Navbar"
import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import ComponentAnalysis from "./pages/ComponentAnalysis"
import CompetitorAnalysis from "./pages/CompetitorAnalysis"
import CustomerIssues from "./pages/CustomerIssues"
import ExecutiveSummary from "./pages/ExecutiveSummary"
import ProductDetail from "./pages/ProductDetail"

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AnalysisProvider>
          <Router>
            <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-200">
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/*" element={
                  <ProtectedRoute>
                    <Sidebar />
                    <div className="lg:pl-64">
                      <Navbar />
                      <main className="p-6">
                        <Routes>
                          <Route path="/" element={<Dashboard />} />
                          <Route path="/dashboard" element={<Dashboard />} />
                          <Route path="/component-analysis" element={<ComponentAnalysis />} />
                          <Route path="/competitor-analysis" element={<CompetitorAnalysis />} />
                          <Route path="/customer-issues" element={<CustomerIssues />} />
                          <Route path="/executive-summary" element={<ExecutiveSummary />} />
                          <Route path="/product/:productName" element={<ProductDetail />} />
                        </Routes>
                      </main>
                    </div>
                  </ProtectedRoute>
                } />
              </Routes>
            </div>
          </Router>
        </AnalysisProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App