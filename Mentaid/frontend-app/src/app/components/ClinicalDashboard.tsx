'use client';

import { useState } from 'react';
import { FaBrain, FaUsers, FaRobot, FaChartBar, FaFileAlt, FaExclamationTriangle } from 'react-icons/fa';
import UserProfile from './UserProfile';

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

interface ClinicalDashboardProps {
  user: User;
  tokens: AuthTokens;
  onLogout: () => void;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ClinicalDashboard({ user, tokens, onLogout }: ClinicalDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [patientSearch, setPatientSearch] = useState('');
  const [reportPatientId, setReportPatientId] = useState('');
  const [reportType, setReportType] = useState('Progress Report');

  // const getAuthHeaders = () => ({
  //   'Authorization': `Bearer ${tokens.access_token}`,
  //   'Content-Type': 'application/json'
  // });

  const sendMessage = async () => {
    if (!userInput.trim()) return;

    const newMessage: ChatMessage = {
      role: 'user',
      content: userInput,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, newMessage]);
    setUserInput('');
    setLoading(true);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      let response = '';
      const input = userInput.toLowerCase();

      if (input.includes('patient') && input.includes('overview')) {
        response = `📊 **Patient Overview Summary**:

**Active Patients**: 12
🚨 **High Risk**: 2 patients require immediate attention
📈 **Improving**: 7 patients showing positive trends
📉 **Declining**: 3 patients need intervention

**Recent Activity**:
- 5 new mood entries today
- 8 journal entries this week
- 2 missed appointments requiring follow-up

Would you like me to provide details on any specific patient or risk category?`;
      } else if (input.includes('risk')) {
        response = `🚨 **Risk Assessment Summary**:

**High Risk Patients**:
- Patient #1234: Suicidal ideation indicators detected
- Patient #5678: Severe depression symptoms worsening

**Medium Risk**:
- 4 patients with anxiety escalation
- 2 patients with medication non-adherence

**Recommendations**:
- Schedule immediate consultations for high-risk patients
- Review medication plans for medium-risk patients
- Consider crisis intervention protocols`;
      } else if (input.includes('treatment')) {
        response = `📋 **Treatment Plan Insights**:

**Current Modalities**:
- CBT: 8 patients (78% improvement rate)
- DBT: 3 patients (85% engagement)
- Medication therapy: 10 patients (65% adherence)

**Recommendations**:
- Increase CBT sessions for 3 patients
- Medication adjustments needed for 2 patients
- Group therapy suitable for 4 patients

**Success Metrics**:
- Overall improvement rate: 72%
- Treatment adherence: 68%
- Patient satisfaction: 88%`;
      } else {
        response = `I understand you're asking about: "${userInput}"

As your Clinical AI Assistant, I can help with:
- 👥 Patient risk assessments and overviews
- 📋 Treatment recommendations and plans
- 📊 Data analysis and population trends
- 🩺 Diagnostic support using DSM-V criteria
- 🚨 Crisis intervention protocols
- 📈 Outcome tracking and analytics

Please ask me specific questions about patient care, and I'll provide evidence-based insights.`;
      }

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response,
        timestamp: new Date()
      };

      setChatMessages(prev => [...prev, aiMessage]);
      setLoading(false);
    }, 1500);
  };

  const quickAction = (action: string) => {
    const actions = {
      overview: "Show me a comprehensive patient overview",
      risk: "Perform risk assessment for all patients",
      treatment: "Generate treatment plan recommendations",
      analytics: "Provide analytics summary for all patients"
    };
    setUserInput(actions[action as keyof typeof actions] || '');
  };

  const generateReport = () => {
    if (!reportPatientId.trim()) return;

    const currentDate = new Date().toISOString().split('T')[0];
    
    let reportContent = '';
    
    if (reportType === 'SOAP Note') {
      reportContent = `# SOAP Note - Patient ${reportPatientId}
**Date**: ${currentDate}

## Subjective
Patient reports feeling "better than last week" with improved sleep patterns. Continues to experience mild anxiety in social situations but notes decreased frequency of panic attacks.

## Objective
- Mood: 4/5 (improved from 2/5 last session)
- Affect: Appropriate, mood-congruent
- Speech: Normal rate and volume
- Thought process: Linear and goal-directed
- No suicidal or homicidal ideation

## Assessment
Patient showing significant improvement in depressive symptoms. Anxiety symptoms remain but are manageable. Good medication compliance reported.

## Plan
- Continue current medication regimen
- Weekly CBT sessions
- Homework: Daily mood tracking and journaling
- Follow-up in 1 week`;
    } else if (reportType === 'Progress Report') {
      reportContent = `# Progress Report - Patient ${reportPatientId}
**Date**: ${currentDate}

## Treatment Summary
Patient has been in treatment for 8 weeks with significant improvement in mood and functioning.

## Current Status
- **Mood**: Stable, improved from baseline
- **Anxiety**: Mild, manageable
- **Sleep**: Improved, 7-8 hours nightly
- **Social functioning**: Gradual improvement

## Metrics
- Journal entries: 85% compliance
- Mood tracking: 90% compliance
- Session attendance: 100%

## Recommendations
Continue current treatment plan with gradual reduction in session frequency as improvement stabilizes.`;
    } else {
      reportContent = `# ${reportType} - Patient ${reportPatientId}
**Date**: ${currentDate}

*This is a placeholder for ${reportType.toLowerCase()}. Full report generation will be implemented with patient data integration.*

## Key Points
- Patient assessment completed
- Clinical recommendations provided
- Follow-up scheduled

*Report generation functionality will be enhanced with AI-powered clinical insights.*`;
    }

    // Add report as a chat message
    const reportMessage: ChatMessage = {
      role: 'assistant',
      content: `📋 **Generated ${reportType}**:\n\n${reportContent}`,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, reportMessage]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b backdrop-blur-sm bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <FaBrain className="text-3xl text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">MirrorMind Clinical</h1>
                <p className="text-sm text-gray-600">Clinical Dashboard</p>
              </div>
            </div>
            
            {/* User Profile Section */}
            <UserProfile user={user} onLogout={onLogout} />
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'overview', label: 'Patient Overview', icon: FaUsers },
                { id: 'assistant', label: 'AI Assistant', icon: FaRobot },
                { id: 'analytics', label: 'Analytics Dashboard', icon: FaChartBar },
                { id: 'reports', label: 'Reports & Documentation', icon: FaFileAlt }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Patient Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Patient Management 👥</h2>
                  <p className="text-gray-600 mb-6">View and manage your patients&apos; mental health data.</p>
                </div>

                <div className="flex space-x-4 mb-6">
                  <input
                    type="text"
                    value={patientSearch}
                    onChange={(e) => setPatientSearch(e.target.value)}
                    placeholder="Search Patient (name or ID)"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors">
                    Search
                  </button>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-red-500">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">High Risk Patients</h3>
                      <FaExclamationTriangle className="text-red-500" />
                    </div>
                    <p className="text-3xl font-bold text-red-600 mb-2">3</p>
                    <p className="text-sm text-gray-600">Require immediate attention</p>
                  </div>

                  <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-yellow-500">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">Medium Risk</h3>
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    </div>
                    <p className="text-3xl font-bold text-yellow-600 mb-2">8</p>
                    <p className="text-sm text-gray-600">Need monitoring</p>
                  </div>

                  <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">Stable Patients</h3>
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    </div>
                    <p className="text-3xl font-bold text-green-600 mb-2">34</p>
                    <p className="text-sm text-gray-600">Doing well</p>
                  </div>
                </div>

                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold mb-4">Recent Patient Activity</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-700">Patient #1234 - New mood entry</span>
                      <span className="text-sm text-gray-500">2 hours ago</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-700">Patient #5678 - Journal entry submitted</span>
                      <span className="text-sm text-gray-500">4 hours ago</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-700">Patient #9012 - Missed appointment</span>
                      <span className="text-sm text-red-500">1 day ago</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* AI Assistant Tab */}
            {activeTab === 'assistant' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Clinical AI Assistant 🤖</h2>
                  <p className="text-gray-600 mb-6">Ask questions about patient data, get diagnostic insights, and receive treatment recommendations.</p>
                </div>

                <div className="grid lg:grid-cols-4 gap-6">
                  <div className="lg:col-span-3">
                    <div className="bg-white rounded-lg shadow-sm border h-96 mb-4 overflow-y-auto p-4">
                      {chatMessages.length === 0 ? (
                        <div className="text-center text-gray-500 mt-20">
                          <FaRobot className="text-4xl mx-auto mb-4 text-gray-400" />
                          <p>Start a conversation with your AI assistant</p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {chatMessages.map((message, index) => (
                            <div
                              key={index}
                              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                              <div
                                className={`max-w-3xl p-3 rounded-lg ${
                                  message.role === 'user'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-100 text-gray-900'
                                }`}
                              >
                                <div className="whitespace-pre-wrap">{message.content}</div>
                                <div className={`text-xs mt-2 ${
                                  message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                                }`}>
                                  {message.timestamp.toLocaleTimeString()}
                                </div>
                              </div>
                            </div>
                          ))}
                          {loading && (
                            <div className="flex justify-start">
                              <div className="bg-gray-100 p-3 rounded-lg">
                                <div className="flex space-x-1">
                                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={userInput}
                        onChange={(e) => setUserInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Ask the AI Assistant..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        onClick={sendMessage}
                        disabled={loading || !userInput.trim()}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium transition-colors"
                      >
                        Send
                      </button>
                      <button
                        onClick={() => setChatMessages([])}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Clear
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">Quick Actions</h3>
                    <div className="space-y-2">
                      <button
                        onClick={() => quickAction('overview')}
                        className="w-full px-4 py-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        Patient Overview
                      </button>
                      <button
                        onClick={() => quickAction('risk')}
                        className="w-full px-4 py-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        Risk Assessment
                      </button>
                      <button
                        onClick={() => quickAction('treatment')}
                        className="w-full px-4 py-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        Treatment Plans
                      </button>
                      <button
                        onClick={() => quickAction('analytics')}
                        className="w-full px-4 py-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        Analytics Summary
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Analytics Dashboard Tab */}
            {activeTab === 'analytics' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Population Analytics 📊</h2>
                  <p className="text-gray-600 mb-6">Analyze trends across your patient population.</p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-white p-6 rounded-lg shadow-sm">
                    <h3 className="text-lg font-semibold mb-2">Total Patients</h3>
                    <p className="text-3xl font-bold text-blue-600">45</p>
                    <p className="text-sm text-gray-600">8 new this month</p>
                  </div>

                  <div className="bg-white p-6 rounded-lg shadow-sm">
                    <h3 className="text-lg font-semibold mb-2">Avg Improvement</h3>
                    <p className="text-3xl font-bold text-green-600">72%</p>
                    <p className="text-sm text-gray-600">Across all patients</p>
                  </div>

                  <div className="bg-white p-6 rounded-lg shadow-sm">
                    <h3 className="text-lg font-semibold mb-2">Engagement Rate</h3>
                    <p className="text-3xl font-bold text-purple-600">85%</p>
                    <p className="text-sm text-gray-600">Daily activity</p>
                  </div>

                  <div className="bg-white p-6 rounded-lg shadow-sm">
                    <h3 className="text-lg font-semibold mb-2">Crisis Interventions</h3>
                    <p className="text-3xl font-bold text-red-600">3</p>
                    <p className="text-sm text-gray-600">This month</p>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm">
                  <h3 className="text-lg font-semibold mb-4">Condition Distribution</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>Major Depressive Disorder</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-blue-600 h-2 rounded-full" style={{width: '40%'}}></div>
                        </div>
                        <span className="text-sm text-gray-600">18 (40%)</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Anxiety Disorders</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-green-600 h-2 rounded-full" style={{width: '33%'}}></div>
                        </div>
                        <span className="text-sm text-gray-600">15 (33%)</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Bipolar Disorder</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-purple-600 h-2 rounded-full" style={{width: '16%'}}></div>
                        </div>
                        <span className="text-sm text-gray-600">7 (16%)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Reports & Documentation Tab */}
            {activeTab === 'reports' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Clinical Reports 📋</h2>
                  <p className="text-gray-600 mb-6">Generate clinical reports and documentation.</p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm">
                  <h3 className="text-lg font-semibold mb-4">Generate Report</h3>
                  <div className="grid md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Patient ID
                      </label>
                      <input
                        type="text"
                        value={reportPatientId}
                        onChange={(e) => setReportPatientId(e.target.value)}
                        placeholder="Enter patient ID"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Report Type
                      </label>
                      <select
                        value={reportType}
                        onChange={(e) => setReportType(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="SOAP Note">SOAP Note</option>
                        <option value="Progress Report">Progress Report</option>
                        <option value="Risk Assessment">Risk Assessment</option>
                        <option value="Treatment Plan">Treatment Plan</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <button
                        onClick={generateReport}
                        disabled={!reportPatientId.trim()}
                        className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium transition-colors"
                      >
                        Generate Report
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">
                    Generated reports will appear in the AI Assistant chat above.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}