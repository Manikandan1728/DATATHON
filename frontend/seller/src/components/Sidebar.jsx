import React from "react"
import { NavLink } from "react-router-dom"
import { LayoutDashboard, Component, Users, AlertTriangle, FileText, BarChart3 } from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Component Analysis", href: "/component-analysis", icon: Component },
  { name: "Competitor Analysis", href: "/competitor-analysis", icon: Users },
  { name: "Customer Issues", href: "/customer-issues", icon: AlertTriangle },
  { name: "Executive Summary", href: "/executive-summary", icon: FileText },
]

const Sidebar = () => (
  <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
    <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white dark:bg-gray-900 px-6 pb-4 shadow-sm border-r border-gray-200 dark:border-gray-700 transition-colors duration-200">
      <div className="flex h-16 shrink-0 items-center gap-2">
        <BarChart3 className="h-7 w-7 text-blue-600" />
        <span className="text-lg font-bold text-gray-900 dark:text-white">Seller Intelligence</span>
      </div>
      <nav className="flex flex-1 flex-col">
        <ul className="flex flex-1 flex-col gap-y-1 -mx-2">
          {navigation.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  "group flex gap-x-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-150 " +
                  (isActive
                    ? "bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800")
                }
              >
                <item.icon className="h-5 w-5 shrink-0" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  </div>
)

export default Sidebar