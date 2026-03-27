# Firebase Authentication Setup Guide

## 🚀 Quick Setup for Google Authentication

### Step 1: Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" and create a new project
3. Name your project (e.g., "seller-intelligence")

### Step 2: Enable Authentication
1. In your Firebase project, go to "Authentication" → "Sign-in method"
2. Enable "Google" provider
3. Configure Google provider with your project details
4. Add authorized domains (localhost:5173 for development)

### Step 3: Get Firebase Config
1. Go to Project Settings → General
2. Scroll down to "Firebase SDK snippet"
3. Copy the configuration object
4. Replace the demo config in `src/firebase/config.js`

### Step 4: Update Configuration
Replace the content in `src/firebase/config.js` with your actual Firebase config:

```javascript
import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider } from 'firebase/auth'

const firebaseConfig = {
  apiKey: "your-api-key-here",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const provider = new GoogleAuthProvider()

export { auth, provider }
export default app
```

## 🔐 Authentication Features

### Google Sign-In Flow
- User clicks "Sign in with Google"
- Google authentication popup appears
- User selects Google account
- Permission request shown
- Upon approval, user is signed in

### Session Management
- User session stored in localStorage
- Persistent across browser sessions
- Automatic logout on session expiry

### Security Features
- Email verification status tracking
- Secure token management
- Protected routes implementation

## 🛠 Development vs Production

### Development (Current Setup)
- Mock authentication for email/password
- Google sign-in with demo credentials
- Local storage for session management

### Production (After Firebase Setup)
- Real Google OAuth integration
- Firebase backend authentication
- Secure session management
- Email verification workflows

## 📱 User Experience

### Sign-In Process
1. User visits `/login`
2. Can sign in with email/password (mock) or Google
3. Google shows account selection and permissions
4. Successful sign-in redirects to dashboard
5. User profile shown in navbar

### Session Persistence
- User stays logged in across page refreshes
- Profile information displayed in navbar
- One-click logout functionality

### Error Handling
- Popup blocked detection
- Network error handling
- User cancellation handling
- Clear error messages

## 🔧 Troubleshooting

### Common Issues
1. **Popup Blocked**: Enable popups for localhost
2. **Invalid Domain**: Add localhost to authorized domains
3. **API Key Error**: Update Firebase config
4. **CORS Issues**: Check Firebase security rules

### Debug Mode
Enable Firebase debug mode:
```javascript
import { getAuth, connectAuthEmulator } from 'firebase/auth'

const auth = getAuth()
if (window.location.hostname === 'localhost') {
  connectAuthEmulator(auth, 'http://localhost:9099')
}
```

## 🚀 Next Steps

1. Set up Firebase project
2. Update configuration
3. Test Google authentication
4. Deploy to production
5. Configure production domains

The login system is ready for Firebase integration once you complete the setup above!
