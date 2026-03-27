# 🚀 Deployment Guide for Seller Intelligence Dashboard

## 📋 Overview
This is a full-stack application with:
- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Python FastAPI with AI components

## 🔧 System Requirements

### **Minimum Requirements:**
- **Node.js**: 16.x or higher
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum
- **Storage**: 1GB free space

### **Recommended:**
- **Node.js**: 18.x LTS
- **Python**: 3.9+
- **RAM**: 4GB+
- **Storage**: 2GB+

## 🏗️ Architecture

### **Frontend Requirements:**
- React 18.2.0
- Vite 4.4.5
- Tailwind CSS 3.3.0
- Lucide React Icons
- Recharts for data visualization
- React Router 6.8.1
- Firebase 10.14.1 (mock)

### **Backend Requirements:**
- FastAPI 0.110.0+
- Uvicorn server
- AI Libraries (LangChain, Groq, OpenAI)
- Web Scraping (BeautifulSoup4, Requests)
- Data Processing (spaCy, scikit-learn)

## 🌐 Deployment Options

### **Option 1: Local Development**
```bash
# Frontend
cd frontend/seller
npm install
npm run dev

# Backend (separate terminal)
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Option 2: Static Hosting (Frontend Only)**
**Platforms:** Netlify, Vercel, GitHub Pages, AWS S3

**Steps:**
1. Build frontend: `npm run build`
2. Deploy `dist/` folder to hosting platform
3. Update API endpoints to point to deployed backend

### **Option 3: Full Stack Hosting**

#### **A. Railway (Easiest)**
```bash
# Frontend (Railway)
- Connect GitHub repo
- Railway auto-detects Vite app
- Auto-deploys on push

# Backend (Railway)
- Add Python service
- Set PYTHON_VERSION=3.9
- Install requirements automatically
```

#### **B. Render**
```bash
# Frontend (Static Site)
- Connect GitHub repo
- Build command: npm run build
- Publish directory: dist

# Backend (Web Service)
- Connect GitHub repo
- Build command: pip install -r requirements.txt
- Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### **C. AWS**
- **Frontend**: S3 + CloudFront
- **Backend**: EC2 + Elastic Beanstalk
- **Database**: RDS (if needed)

#### **D. DigitalOcean**
- **Frontend**: App Platform (static)
- **Backend**: App Platform (Python)
- **Droplet**: Custom setup

## 🔑 Environment Variables

### **Backend (.env):**
```bash
# AI API Keys (required for AI features)
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional
DEBUG=false
PORT=8000
```

### **Frontend:**
```bash
# API endpoint (if backend deployed separately)
VITE_API_URL=https://your-backend-url.com
```

## 📦 Production Build

### **Frontend:**
```bash
cd frontend/seller
npm run build
# Output: dist/ folder (ready for deployment)
```

### **Backend:**
```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🛠️ Docker Deployment (Recommended)

### **Create Dockerfile (Backend):**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Create Dockerfile (Frontend):**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

### **Docker Compose:**
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend/seller
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build: ./Backend
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

## 🚀 Quick Deploy Commands

### **Netlify (Frontend):**
```bash
npm install -g netlify-cli
npm run build
netlify deploy --prod --dir=dist
```

### **Vercel (Frontend):**
```bash
npm install -g vercel
npm run build
vercel --prod
```

### **Heroku (Full Stack):**
```bash
# Backend
heroku create your-app-backend
git subtree push --prefix Backend heroku main

# Frontend
heroku create your-app-frontend
git subtree push --prefix frontend/seller heroku main
```

## 🔍 Pre-Deployment Checklist

### **Frontend:**
- [ ] `npm run build` completes successfully
- [ ] All environment variables set
- [ ] API endpoints configured
- [ ] Login functionality works
- [ ] Responsive design tested

### **Backend:**
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] API endpoints tested
- [ ] AI services accessible
- [ ] CORS settings configured

### **Security:**
- [ ] API keys secured (environment variables)
- [ ] HTTPS enabled
- [ ] Rate limiting considered
- [ ] Input validation in place

## 📊 Monitoring & Maintenance

### **Recommended Tools:**
- **Uptime monitoring**: UptimeRobot, Pingdom
- **Error tracking**: Sentry (frontend), Rollbar (backend)
- **Performance**: Lighthouse, Web Vitals
- **Logs**: Papertrail, Logtail

### **Backup Strategy:**
- **Code**: Git repository
- **Environment**: Secure backup of .env files
- **Data**: If database added, regular backups

## 🎯 Recommended Deployment Path

### **For Beginners:**
1. **Frontend**: Netlify (free, easy)
2. **Backend**: Railway (free tier, Python support)

### **For Production:**
1. **Frontend**: Vercel or AWS S3 + CloudFront
2. **Backend**: AWS EC2, DigitalOcean, or Railway Pro

### **For Enterprise:**
1. **Frontend**: AWS CloudFront + S3
2. **Backend**: AWS ECS/EKS or Kubernetes
3. **Database**: AWS RDS
4. **Monitoring**: CloudWatch + Sentry

## 💡 Pro Tips

1. **Start simple**: Deploy frontend first, then backend
2. **Use environment variables**: Never hardcode API keys
3. **Test locally**: Ensure everything works before deploying
4. **Monitor performance**: Set up uptime monitoring
5. **Backup everything**: Keep backups of code and config

## 🆘 Troubleshooting

### **Common Issues:**
- **Build fails**: Check Node.js version compatibility
- **API errors**: Verify environment variables and CORS
- **Login issues**: Check AuthContext and protected routes
- **AI features not working**: Verify API keys and network access

### **Debug Commands:**
```bash
# Frontend build check
npm run build
npm run preview

# Backend health check
curl http://localhost:8000/health
```

Ready to deploy! 🚀
