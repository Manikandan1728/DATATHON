# Seller Intelligence Dashboard

A modern SaaS-style competitive intelligence dashboard that analyzes Amazon product reviews and provides actionable insights for sellers.

## Features

- **Dashboard Overview**: High-level metrics and brand performance analysis
- **Component Analysis**: Detailed comparison of product components with visual charts
- **Competitor Analysis**: Head-to-head comparisons and sentiment analysis
- **Customer Issues**: Visualization of customer complaints and issues
- **Executive Summary**: Comprehensive insights and strategic recommendations

## Tech Stack

- **Frontend**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Routing**: React Router
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd seller-intelligence-dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

### Authentication

The application includes a complete authentication system:

**Demo Mode (Current)**:
- Visit `http://localhost:5173/login`
- Click "Sign in with Google" for demo authentication
- Use any email/password for mock sign-in
- Full dashboard access after authentication

**Production Mode**:
- Set up Firebase project (see `FIREBASE_SETUP.md`)
- Update Firebase configuration in `src/firebase/config.js`
- Real Google OAuth integration
- Secure session management

### Protected Routes
All dashboard pages are protected and require authentication:
- `/dashboard`
- `/component-analysis`
- `/competitor-analysis`
- `/customer-issues`
- `/executive-summary`
- `/product/:productName`

## Project Structure

```
src/
├── components/
│   ├── Sidebar.jsx          # Navigation sidebar
│   └── Navbar.jsx           # Top navigation bar
├── contexts/
│   └── AnalysisContext.jsx  # Data management context
├── pages/
│   ├── Dashboard.jsx        # Main dashboard with metrics
│   ├── ComponentAnalysis.jsx # Component comparison with charts
│   ├── CompetitorAnalysis.jsx # Head-to-head analysis
│   ├── CustomerIssues.jsx   # Customer issues visualization
│   └── ExecutiveSummary.jsx # Strategic insights
├── App.jsx                  # Main app with routing
├── main.jsx                 # App entry point
└── index.css                # Global styles
```

## Data Source

The dashboard loads data from `/public/comprehensive_analysis_results.json`, which contains:

- Product information and ratings
- Component scores (battery, sound, noise cancellation, etc.)
- Sentiment analysis results
- Customer issues and complaints
- Strategic recommendations

## Key Features

### Interactive Charts
- **Bar Charts**: Component comparisons
- **Pie Charts**: Sentiment analysis
- **Radar Charts**: Head-to-head product comparisons
- **Horizontal Bar Charts**: Customer issues visualization

### Responsive Design
- Mobile-friendly layout
- Adaptive grid system
- Touch-friendly navigation

### Modern UI
- Card-based layout
- Soft shadows and rounded corners
- Color-coded severity indicators
- Smooth transitions and hover effects

## Usage

1. **Dashboard**: View overall metrics and brand performance
2. **Component Analysis**: Compare product components side-by-side
3. **Competitor Analysis**: Analyze market positioning and sentiment
4. **Customer Issues**: Identify common complaints and improvement areas
5. **Executive Summary**: Get strategic recommendations and insights

## Customization

### Adding New Charts
```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

const MyChart = ({ data }) => (
  <ResponsiveContainer width="100%" height={400}>
    <BarChart data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="value" fill="#3b82f6" />
    </BarChart>
  </ResponsiveContainer>
)
```

### Styling
The project uses Tailwind CSS with custom color schemes:
- `primary`: Blue color palette
- `success`: Green color palette  
- `warning`: Yellow color palette
- `danger`: Red color palette

## Build and Deploy

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
