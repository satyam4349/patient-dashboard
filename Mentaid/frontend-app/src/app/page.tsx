'use client';

import { useState, useEffect } from 'react';
import { FaBrain, FaHeart, FaChartLine, FaUserMd, FaRobot } from 'react-icons/fa';
import AuthModal from './components/AuthModal';
import PatientDashboard from './components/PatientDashboard';
import ClinicalDashboard from './components/ClinicalDashboard';

interface User {
  id: string;
  email: string;
  role: 'regular_user' | 'clinician';
  full_name?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  role: string;
  user_id: string;
}

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  useEffect(() => {
    // Check for stored auth data
    const storedUser = localStorage.getItem('user');
    const storedTokens = localStorage.getItem('tokens');
    
    if (storedUser && storedTokens) {
      try {
        setUser(JSON.parse(storedUser));
        setTokens(JSON.parse(storedTokens));
      } catch (error) {
        console.error('Error parsing stored auth data:', error);
        localStorage.removeItem('user');
        localStorage.removeItem('tokens');
      }
    }
  }, []);

  const handleLogin = (userData: User, tokenData: AuthTokens) => {
    console.log('handleLogin called with:', { userData, tokenData });
    setUser(userData);
    setTokens(tokenData);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('tokens', JSON.stringify(tokenData));
    setShowAuthModal(false);
    console.log('Auth modal closed, user state updated');
  };

  const handleLogout = () => {
    setUser(null);
    setTokens(null);
    localStorage.removeItem('user');
    localStorage.removeItem('tokens');
  };

  const openAuthModal = (mode: 'login' | 'signup') => {
    setAuthMode(mode);
    setShowAuthModal(true);
  };

  if (user && tokens) {
    console.log('Rendering dashboard for user:', user);
    console.log('User role:', user.role);
    // Show appropriate dashboard based on user role
    if (user.role === 'clinician') {
      console.log('Rendering ClinicalDashboard');
      return <ClinicalDashboard user={user} tokens={tokens} onLogout={handleLogout} />;
    } else {
      console.log('Rendering PatientDashboard');
      return <PatientDashboard user={user} tokens={tokens} onLogout={handleLogout} />;
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <FaBrain className="text-2xl text-blue-600" />
              <span className="text-xl font-bold text-gray-900">MirrorMind</span>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => openAuthModal('login')}
                className="px-4 py-2 text-gray-700 hover:text-blue-600 font-medium transition-colors"
              >
                Login
              </button>
              <button
                onClick={() => openAuthModal('signup')}
                className="btn-primary"
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-20">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            AI-Powered Mental Health Platform
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            Experience the future of mental health care with our dual-agent AI system. 
            Natural conversations for patients, intelligent insights for clinicians.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button
              onClick={() => openAuthModal('signup')}
              className="btn-primary text-lg px-8 py-4"
            >
              Get Started Free
            </button>
            <button
              onClick={() => openAuthModal('login')}
              className="btn-secondary text-lg px-8 py-4"
            >
              Sign In
            </button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
          <div className="card p-8">
            <FaRobot className="text-4xl text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Patient Companion Agent</h3>
            <p className="text-gray-600 leading-relaxed">
              Natural conversation partner that extracts clinical insights through empathetic dialogue. 
              No more forms - just talk naturally about your day.
            </p>
          </div>

          <div className="card p-8">
            <FaUserMd className="text-4xl text-green-600 mb-4" />
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Clinical AI Assistant</h3>
            <p className="text-gray-600 leading-relaxed">
              Autonomous diagnostic support using DSM-V criteria. Get evidence-based treatment 
              recommendations and comprehensive patient insights.
            </p>
          </div>

          <div className="card p-8">
            <FaHeart className="text-4xl text-red-600 mb-4" />
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Mood & Journal Tracking</h3>
            <p className="text-gray-600 leading-relaxed">
              Daily mood tracking with 5-emoji system and conversational journaling. 
              Track your wellness journey with beautiful visualizations.
            </p>
          </div>

          <div className="card p-8">
            <FaChartLine className="text-4xl text-purple-600 mb-4" />
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Wellness Analytics</h3>
            <p className="text-gray-600 leading-relaxed">
              Advanced language analysis, LIWC processing, and trend visualization. 
              Understand patterns in your mental health journey.
            </p>
          </div>

          <div className="card p-8">
            <FaBrain className="text-4xl text-indigo-600 mb-4" />
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Crisis Detection</h3>
            <p className="text-gray-600 leading-relaxed">
              Real-time risk assessment and early intervention. AI monitors for warning signs 
              and provides immediate support when needed.
            </p>
          </div>

          <div className="card p-8">
            <div className="text-4xl text-orange-600 mb-4">🔒</div>
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Privacy & Security</h3>
            <p className="text-gray-600 leading-relaxed">
              End-to-end encryption, HIPAA compliance, and granular privacy controls. 
              Your mental health data is completely secure.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h3 className="text-3xl font-bold mb-4">Ready to Transform Your Mental Health Journey?</h3>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of patients and clinicians using AI-powered mental health care.
          </p>
          <button
            onClick={() => openAuthModal('signup')}
            className="px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-gray-100 font-semibold text-lg transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            Start Your Journey Today
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <FaBrain className="text-2xl text-blue-400" />
                <span className="text-xl font-bold">MirrorMind</span>
              </div>
              <p className="text-gray-400">
                AI-powered mental health platform revolutionizing patient care and clinical practice.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">For Patients</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Mood Tracking</li>
                <li>Journal Writing</li>
                <li>AI Companion</li>
                <li>Wellness Trends</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">For Clinicians</h4>
              <ul className="space-y-2 text-gray-400">
                <li>AI Assistant</li>
                <li>Patient Analytics</li>
                <li>Risk Assessment</li>
                <li>Treatment Plans</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Security</h4>
              <ul className="space-y-2 text-gray-400">
                <li>HIPAA Compliant</li>
                <li>End-to-End Encryption</li>
                <li>Privacy Controls</li>
                <li>Secure Infrastructure</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 MirrorMind. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          mode={authMode}
          onClose={() => setShowAuthModal(false)}
          onLogin={handleLogin}
          onSwitchMode={(mode) => setAuthMode(mode)}
        />
      )}
    </div>
  );
}