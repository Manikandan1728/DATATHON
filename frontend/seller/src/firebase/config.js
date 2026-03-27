// Mock Firebase configuration for demo purposes
// Replace with real Firebase config after setup
const mockAuth = {
  currentUser: null,
  signInWithPopup: async (provider) => {
    // Simulate Google sign-in delay
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Return mock user data
    return {
      user: {
        uid: 'demo-user-123',
        email: 'demo@example.com',
        displayName: 'Demo User',
        photoURL: 'https://picsum.photos/seed/demo/40/40.jpg',
        emailVerified: true
      }
    }
  },
  signOut: async () => {
    await new Promise(resolve => setTimeout(resolve, 500))
    return null
  }
}

const mockGoogleProvider = {
  setCustomParameters: () => {}
}

// Mock GoogleAuthProvider for demo
class MockGoogleAuthProvider {
  constructor() {
    this.customParameters = {}
  }
  
  setCustomParameters(params) {
    this.customParameters = { ...this.customParameters, ...params }
  }
}

export const auth = mockAuth
export const provider = mockGoogleProvider
export const GoogleAuthProvider = MockGoogleAuthProvider
export default { auth: mockAuth }
