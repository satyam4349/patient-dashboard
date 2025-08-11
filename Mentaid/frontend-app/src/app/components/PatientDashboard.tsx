'use client';

import { useState, useEffect } from 'react';
import { FaBrain, FaHeart, FaBook, FaHistory, FaChartLine, FaRobot } from 'react-icons/fa';
import axios from 'axios';
import UserProfile from './UserProfile';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

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

interface PatientDashboardProps {
  user: User;
  tokens: AuthTokens;
  onLogout: () => void;
}

interface MoodStats {
  total_entries: number;
  average_mood: number;
  trend: string;
  most_common_mood: number;
}

interface JournalStats {
  total_entries: number;
  total_words: number;
  average_words: number;
  current_streak: number;
  longest_streak: number;
  consistency_rate: number;
}

interface LanguageStats {
  avg_coherence: number;
  coherence_trend: string;
  dominant_themes: Array<{ theme: string; score: number }>;
}

interface MoodAnalytics {
  mood_data: Array<{ date: string; emoji: number; note: string }>;
  mood_counts: Record<number, number>;
  stats: MoodStats;
}

interface JournalAnalytics {
  journal_data: Array<{ date: string; word_count: number; char_count: number; has_entry: boolean }>;
  stats: JournalStats;
}

interface LanguageAnalytics {
  coherence_data: Array<{ date: string; coherence: number }>;
  liwc_data: Record<string, number>;
  stats: LanguageStats;
}

interface AnalyticsSummary {
  total_mood_entries: number;
  total_journal_entries: number;
  average_mood: number;
  current_streak: number;
  avg_coherence: number;
}

interface AnalyticsData {
  mood_analytics: MoodAnalytics;
  journal_analytics: JournalAnalytics;
  language_analytics: LanguageAnalytics;
  summary: AnalyticsSummary;
}

// interface AnalyticsResponse {
//   status: string;
//   data: AnalyticsData;
// }

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function PatientDashboard({ user, tokens, onLogout }: PatientDashboardProps) {
  const [activeTab, setActiveTab] = useState('mood');
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [moodNote, setMoodNote] = useState('');
  const [sleepHours, setSleepHours] = useState<number | null>(null);
  const [journalText, setJournalText] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [todayEntryLoaded, setTodayEntryLoaded] = useState(false);
  const [hasExistingMood, setHasExistingMood] = useState(false);
  const [hasExistingJournal, setHasExistingJournal] = useState(false);
  const [historyEntry, setHistoryEntry] = useState<{
    mood?: { emoji: number; note: string; sleep_hours?: number; created_at: string };
    journal?: { text: string; created_at: string };
  } | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [todayEntriesLoading, setTodayEntriesLoading] = useState(false);

  const moodEmojis = [
    { value: 1, emoji: '😢', label: 'Very Sad' },
    { value: 2, emoji: '😔', label: 'Sad' },
    { value: 3, emoji: '😐', label: 'Neutral' },
    { value: 4, emoji: '😊', label: 'Happy' },
    { value: 5, emoji: '😄', label: 'Very Happy' }
  ];

  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${tokens.access_token}`,
    'Content-Type': 'application/json'
  });

  // Load today's entries on component mount
  useEffect(() => {
    loadTodayEntries();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load today's entries when switching to mood or journal tab if not already loaded
  useEffect(() => {
    if ((activeTab === 'journal' || activeTab === 'mood') && !todayEntryLoaded && !todayEntriesLoading) {
      loadTodayEntries();
    }
  }, [activeTab, todayEntryLoaded, todayEntriesLoading]); // eslint-disable-line react-hooks/exhaustive-deps

  // Load history entry when selected date changes or when switching to history tab
  useEffect(() => {
    if (activeTab === 'history') {
      loadHistoryEntry(selectedDate);
    }
  }, [selectedDate, activeTab]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadTodayEntries = async () => {
    // Prevent multiple simultaneous loads
    if (todayEntriesLoading) return;
    
    setTodayEntriesLoading(true);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/patient/today-entry`,
        { headers: getAuthHeaders() }
      );

      console.log('Today entries response:', response.data); // Debug log

      if (response.data.status === 'success') {
        const data = response.data.data;
        
        // Load mood data
        if (data.mood) {
          setSelectedMood(data.mood.emoji);
          setMoodNote(data.mood.note || '');
          setSleepHours(data.mood.sleep_hours || null);
          setHasExistingMood(true);
          console.log('Loaded existing mood:', data.mood); // Debug log
        } else {
          // Only reset mood state if no existing selection
          if (!selectedMood) {
            setSelectedMood(null);
            setMoodNote('');
            setSleepHours(null);
          }
          setHasExistingMood(false);
        }
        
        // Load journal data - handle different possible data structures
        if (data.journal) {
          // Handle if journal is an object with text property
          const journalTextFromServer = typeof data.journal === 'string' ? data.journal : data.journal.text || data.journal;
          setJournalText(journalTextFromServer || '');
          setHasExistingJournal(true);
          console.log('Loaded existing journal:', journalTextFromServer); // Debug log
        } else {
          // Only reset journal if no current text (preserve user's typing)
          if (!journalText.trim()) {
            setJournalText('');
          }
          setHasExistingJournal(false);
        }
        
        setTodayEntryLoaded(true);
      } else {
        console.log('No today entries found or API error:', response.data);
        // Only reset states when no data is found and no current user input
        if (!selectedMood) {
          setSelectedMood(null);
          setMoodNote('');
          setSleepHours(null);
        }
        setHasExistingMood(false);
        
        if (!journalText.trim()) {
          setJournalText('');
        }
        setHasExistingJournal(false);
        setTodayEntryLoaded(true);
      }
    } catch (error) {
      console.error('Error loading today\'s entries:', error);
      // On error, preserve any user input but mark as not having existing entries
      setHasExistingMood(false);
      setHasExistingJournal(false);
      setTodayEntryLoaded(true); // Still mark as loaded to show the interface
    } finally {
      setTodayEntriesLoading(false);
    }
  };

  const loadHistoryEntry = async (date: string) => {
    setHistoryLoading(true);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/patient/entry-by-date?date=${date}`,
        { headers: getAuthHeaders() }
      );

      if (response.data.status === 'success') {
        const data = response.data.data;
        setHistoryEntry({
          mood: data.mood ? {
            emoji: data.mood.emoji,
            note: data.mood.note || '',
            sleep_hours: data.mood.sleep_hours,
            created_at: data.mood.created_at
          } : undefined,
          journal: data.journal ? {
            text: data.journal,
            created_at: data.journal_created_at
          } : undefined
        });
      } else {
        setHistoryEntry(null);
      }
    } catch (error) {
      console.error('Error loading history entry:', error);
      setHistoryEntry(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  const saveMood = async () => {
    if (!selectedMood) {
      setMessage('Please select a mood first.');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    setLoading(true);
    try {
      const moodData: any = {
        emoji: selectedMood,
        note: moodNote.trim() || undefined
      };
      
      if (sleepHours !== null && sleepHours > 0) {
        moodData.sleep_hours = sleepHours;
      }

      const response = await axios.post(
        `${API_BASE_URL}/patient/today-mood`,
        moodData,
        { headers: getAuthHeaders() }
      );

      if (response.data.status === 'success') {
        const action = hasExistingMood ? 'updated' : 'saved';
        setMessage(`✅ Mood ${action} successfully!`);
        setHasExistingMood(true);
        setTimeout(() => setMessage(''), 5000);
      } else {
        setMessage(response.data.message || 'Failed to save mood');
        setTimeout(() => setMessage(''), 5000);
      }
    } catch (error: unknown) {
      console.error('Save mood error:', error);
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setMessage(axiosError.response?.data?.detail || 'Failed to save mood');
      setTimeout(() => setMessage(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  const saveJournal = async () => {
    if (!journalText.trim()) {
      setMessage('Please write something before saving.');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/patient/today-journal`,
        { text: journalText.trim() },
        { headers: getAuthHeaders() }
      );

      console.log('Save journal response:', response.data); // Debug log

      if (response.data.status === 'success') {
        const action = hasExistingJournal ? 'updated' : 'saved';
        setMessage(`✅ Journal entry ${action} successfully!`);
        setHasExistingJournal(true);
        
        // Ensure the journal text is preserved in state
        // The text should remain exactly as the user typed it
        console.log('Journal saved, preserving text:', journalText); // Debug log
        
        setTimeout(() => setMessage(''), 5000);
      } else {
        setMessage(response.data.message || 'Failed to save journal');
        setTimeout(() => setMessage(''), 5000);
      }
    } catch (error: unknown) {
      console.error('Save journal error:', error);
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setMessage(axiosError.response?.data?.detail || 'Failed to save journal');
      setTimeout(() => setMessage(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async (range: string = 'Last 30 days') => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/patient/analytics?range=${encodeURIComponent(range)}`,
        { headers: getAuthHeaders() }
      );

      if (response.data.status === 'success') {
        setAnalytics(response.data.data);
      } else {
        setMessage('Failed to load analytics');
      }
    } catch (error: unknown) {
      console.error('Load analytics error:', error);
      setMessage('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const wordCount = journalText.split(/\s+/).filter(word => word.length > 0).length;
  const charCount = journalText.length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <FaBrain className="text-2xl text-blue-600" />
              <div>
                <span className="text-xl font-bold text-gray-900">MirrorMind</span>
                <span className="text-sm text-gray-500 ml-2">Patient Dashboard</span>
              </div>
            </div>
            
            {/* User Profile Section */}
            <UserProfile user={user} onLogout={onLogout} />
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="card mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'mood', label: 'Daily Mood & Sleep', icon: FaHeart },
                { id: 'journal', label: 'Daily Journal', icon: FaBook },
                { id: 'history', label: 'Journal History', icon: FaHistory },
                { id: 'trends', label: 'Wellness Trends', icon: FaChartLine },
                { id: 'companion', label: 'AI Companion', icon: FaRobot }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`tab-button flex items-center space-x-2 ${
                    activeTab === tab.id ? 'active' : ''
                  }`}
                >
                  <tab.icon />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Quick Actions Panel */}
          <div className="bg-gradient-to-r from-blue-100 to-purple-100 px-6 py-6 border-b-2 border-blue-300 shadow-sm">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-800 uppercase tracking-wide flex items-center">
                <span className="text-blue-600 mr-2">⚡</span>
                Quick Actions
              </h3>
              <p className="text-sm text-gray-600 mt-1">Jump to any section quickly</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setActiveTab('mood')}
                className="quick-action-btn bg-red-100 hover:bg-red-200 text-red-700 border-red-300"
              >
                <FaHeart className="mr-2" />
                Record Mood
              </button>
              <button
                onClick={() => setActiveTab('journal')}
                className="quick-action-btn bg-blue-100 hover:bg-blue-200 text-blue-700 border-blue-300"
              >
                <FaBook className="mr-2" />
                Write Journal
              </button>
              <button
                onClick={() => setActiveTab('trends')}
                className="quick-action-btn bg-green-100 hover:bg-green-200 text-green-700 border-green-300"
              >
                <FaChartLine className="mr-2" />
                View Trends
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className="quick-action-btn bg-purple-100 hover:bg-purple-200 text-purple-700 border-purple-300"
              >
                <FaHistory className="mr-2" />
                Browse History
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {message && (
              <div className={`alert ${
                message.includes('✅') ? 'alert-success' : 'alert-error'
              }`}>
                {message.includes('✅') ? '✅' : '⚠️'}
                {message}
              </div>
            )}

            {/* Daily Mood Tab */}
            {activeTab === 'mood' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">How are you feeling today? 🌟</h2>
                  <p className="text-gray-600 mb-6">
                    {todayEntriesLoading || !todayEntryLoaded ? (
                      <span className="flex items-center">
                        <div className="spinner mr-2"></div>
                        Loading your mood...
                      </span>
                    ) : hasExistingMood ? 
                      'You can update your mood selection anytime today:' : 
                      'Select one emoji that best represents your mood:'}
                  </p>
                </div>

                <div className="grid grid-cols-5 gap-4 mb-6">
                  {moodEmojis.map(mood => (
                    <button
                      key={mood.value}
                      onClick={() => setSelectedMood(mood.value)}
                      className={`mood-button ${
                        selectedMood === mood.value ? 'selected' : ''
                      }`}
                    >
                      <div className="text-4xl mb-2">{mood.emoji}</div>
                      <div className="text-sm font-medium text-gray-700">{mood.label}</div>
                    </button>
                  ))}
                </div>

                {selectedMood && todayEntryLoaded && (
                  <div className="bg-blue-50 p-4 rounded-lg mb-4">
                    <p className="text-blue-800 font-medium">
                      {hasExistingMood ? 'Current mood: ' : 'Selected mood: '}
                      {moodEmojis.find(m => m.value === selectedMood)?.emoji} {moodEmojis.find(m => m.value === selectedMood)?.label}
                      {hasExistingMood && <span className="text-sm ml-2">(recorded today)</span>}
                    </p>
                    {sleepHours !== null && (
                      <p className="text-purple-700 text-sm mt-2 font-semibold bg-purple-100 px-3 py-1 rounded-full inline-block">
                        😴 Sleep: {sleepHours} hours last night
                      </p>
                    )}
                  </div>
                )}

                <div className="space-y-4">
                  <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                    <label className="block text-sm font-semibold text-purple-800 mb-3 flex items-center">
                      <span className="text-lg mr-2">😴</span>
                      Sleep Hours (Optional)
                    </label>
                    <div className="flex items-center space-x-3">
                      <input
                        type="number"
                        value={sleepHours || ''}
                        onChange={(e) => setSleepHours(e.target.value ? parseFloat(e.target.value) : null)}
                        placeholder="8.5"
                        min="0"
                        max="24"
                        step="0.5"
                        className="w-28 px-4 py-3 border-2 border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-semibold text-center text-lg"
                      />
                      <span className="text-sm text-purple-700 font-medium">hours of sleep last night</span>
                    </div>
                    {sleepHours !== null && (
                      <p className="text-sm font-medium mt-2 px-3 py-1 rounded-full inline-block" style={{
                        backgroundColor: sleepHours < 6 ? '#fef2f2' : sleepHours >= 6 && sleepHours <= 9 ? '#f0fdf4' : '#fef2f2',
                        color: sleepHours < 6 ? '#dc2626' : sleepHours >= 6 && sleepHours <= 9 ? '#16a34a' : '#dc2626'
                      }}>
                        {sleepHours < 6 ? '⚠️ Less than recommended (6-9h)' : 
                         sleepHours >= 6 && sleepHours <= 9 ? '✅ Good amount of sleep' : 
                         '⚠️ More than usual (6-9h recommended)'}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Optional note
                    </label>
                    <textarea
                      value={moodNote}
                      onChange={(e) => setMoodNote(e.target.value)}
                      placeholder="How was your day?"
                      rows={3}
                      className="form-textarea"
                    />
                  </div>

                  <button
                    onClick={saveMood}
                    disabled={loading || !selectedMood}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <div className="flex items-center">
                        <div className="spinner mr-2"></div>
                        Saving...
                      </div>
                    ) : (
                      hasExistingMood ? "Update Today's Data" : "Save Today's Data"
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Daily Journal Tab */}
            {activeTab === 'journal' && (
              <div className="space-y-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Today&apos;s Journal Entry 📝</h2>
                    <p className="text-gray-600 mb-6">
                      {todayEntriesLoading || !todayEntryLoaded ? (
                        <span className="flex items-center">
                          <div className="spinner mr-2"></div>
                          Loading your journal...
                        </span>
                      ) : hasExistingJournal ? 
                        'You can edit your journal entry anytime today:' : 
                        'Write about your day, thoughts, and feelings. One entry per day.'}
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      setTodayEntryLoaded(false);
                      await loadTodayEntries();
                    }}
                    disabled={todayEntriesLoading}
                    className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center space-x-2 disabled:opacity-50"
                    title="Refresh today's entries"
                  >
                    <span>{todayEntriesLoading ? '⏳' : '🔄'}</span>
                    <span>{todayEntriesLoading ? 'Loading...' : 'Refresh'}</span>
                  </button>
                </div>

                {hasExistingJournal && todayEntryLoaded && (
                  <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <p className="text-green-800 font-medium flex items-center">
                      <span className="mr-2">✅</span>
                      Journal entry found for today - you can continue editing below
                    </p>
                  </div>
                )}

                {/* Debug info - can be removed later */}
                {process.env.NODE_ENV === 'development' && (
                  <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200 text-xs">
                    <p className="text-yellow-800">
                      <strong>Debug:</strong> todayEntryLoaded: {todayEntryLoaded.toString()}, 
                      hasExistingJournal: {hasExistingJournal.toString()}, 
                      journalText length: {journalText.length}
                    </p>
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Journal Entry
                    </label>
                    <textarea
                      value={journalText}
                      onChange={(e) => setJournalText(e.target.value)}
                      placeholder={todayEntriesLoading || !todayEntryLoaded ? "Loading your journal..." : "Dear journal, today I..."}
                      rows={12}
                      className="form-textarea"
                      disabled={todayEntriesLoading || !todayEntryLoaded}
                    />
                  </div>

                  <div className="flex justify-between text-sm text-gray-500">
                    <span>Words: {wordCount}</span>
                    <span>Characters: {charCount}</span>
                  </div>

                  <div className="flex space-x-4">
                    <button
                      onClick={saveJournal}
                      disabled={loading || !journalText.trim()}
                      className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? (
                        <div className="flex items-center">
                          <div className="spinner mr-2"></div>
                          Saving...
                        </div>
                      ) : (
                        hasExistingJournal ? "Update Today's Entry" : "Save Today's Entry"
                      )}
                    </button>
                    <button
                      onClick={() => {
                        if (confirm('Are you sure you want to clear your journal text? This will not delete your saved entry, only clear the current text.')) {
                          setJournalText('');
                        }
                      }}
                      className="btn-secondary"
                    >
                      Clear
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Journal History Tab */}
            {activeTab === 'history' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Journal Timeline 📅</h2>
                  <p className="text-gray-600 mb-6">Browse your journal entries and mood records by date.</p>
                </div>

                <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Date
                    </label>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      max={new Date().toISOString().split('T')[0]}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="flex items-end space-x-2">
                    <button
                      onClick={() => {
                        const date = new Date(selectedDate);
                        date.setDate(date.getDate() - 1);
                        setSelectedDate(date.toISOString().split('T')[0]);
                      }}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      ← Previous Day
                    </button>
                    <button
                      onClick={() => {
                        const today = new Date().toISOString().split('T')[0];
                        if (selectedDate < today) {
                          const date = new Date(selectedDate);
                          date.setDate(date.getDate() + 1);
                          setSelectedDate(date.toISOString().split('T')[0]);
                        }
                      }}
                      disabled={selectedDate >= new Date().toISOString().split('T')[0]}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next Day →
                    </button>
                    <button
                      onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Today
                    </button>
                  </div>
                </div>

                {historyLoading ? (
                  <div className="bg-gray-50 p-8 rounded-lg text-center">
                    <div className="spinner mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading entries for {selectedDate}...</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Date Header */}
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {new Date(selectedDate).toLocaleDateString('en-US', { 
                          weekday: 'long', 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {selectedDate === new Date().toISOString().split('T')[0] ? 'Today' : 
                         selectedDate === new Date(Date.now() - 86400000).toISOString().split('T')[0] ? 'Yesterday' :
                         `${Math.abs(Math.floor((new Date().getTime() - new Date(selectedDate).getTime()) / (1000 * 60 * 60 * 24)))} days ago`}
                      </p>
                    </div>

                    {/* Mood Entry */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center space-x-2 mb-4">
                        <FaHeart className="text-red-500" />
                        <h4 className="text-lg font-semibold text-gray-900">Mood</h4>
                      </div>
                      
                      {historyEntry?.mood ? (
                        <div className="space-y-3">
                          <div className="flex items-center space-x-3">
                            <div className="text-3xl">
                              {moodEmojis.find(m => m.value === historyEntry.mood!.emoji)?.emoji || '😐'}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                {moodEmojis.find(m => m.value === historyEntry.mood!.emoji)?.label || 'Neutral'}
                              </p>
                              <p className="text-sm text-gray-500">
                                Recorded at {new Date(historyEntry.mood.created_at).toLocaleTimeString('en-US', { 
                                  hour: '2-digit', 
                                  minute: '2-digit' 
                                })}
                              </p>
                            </div>
                          </div>
                          {historyEntry.mood.sleep_hours && (
                            <div className="bg-blue-50 p-3 rounded-lg mb-2">
                              <p className="text-sm font-medium text-blue-700 mb-1">Sleep:</p>
                              <p className="text-blue-600">😴 {historyEntry.mood.sleep_hours} hours</p>
                            </div>
                          )}
                          {historyEntry.mood.note && (
                            <div className="bg-gray-50 p-3 rounded-lg">
                              <p className="text-sm font-medium text-gray-700 mb-1">Note:</p>
                              <p className="text-gray-600">{historyEntry.mood.note}</p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <div className="text-4xl text-gray-300 mb-2">😐</div>
                          <p className="text-gray-500">No mood recorded for this day</p>
                        </div>
                      )}
                    </div>

                    {/* Journal Entry */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center space-x-2 mb-4">
                        <FaBook className="text-blue-500" />
                        <h4 className="text-lg font-semibold text-gray-900">Journal Entry</h4>
                      </div>
                      
                      {historyEntry?.journal ? (
                        <div className="space-y-3">
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <div className="prose max-w-none">
                              <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                                {historyEntry.journal.text}
                              </p>
                            </div>
                          </div>
                          <div className="flex justify-between text-sm text-gray-500">
                            <span>
                              Words: {historyEntry.journal.text.split(/\s+/).filter(word => word.length > 0).length}
                            </span>
                            <span>
                              Characters: {historyEntry.journal.text.length}
                            </span>
                            <span>
                              Written at {new Date(historyEntry.journal.created_at).toLocaleTimeString('en-US', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <div className="text-4xl text-gray-300 mb-2">📝</div>
                          <p className="text-gray-500">No journal entry for this day</p>
                        </div>
                      )}
                    </div>

                    {/* No entries message */}
                    {!historyEntry?.mood && !historyEntry?.journal && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                        <div className="text-4xl text-yellow-400 mb-2">📅</div>
                        <h4 className="text-lg font-semibold text-yellow-800 mb-2">No entries for this day</h4>
                        <p className="text-yellow-700">
                          You didn&apos;t record any mood or journal entries on {new Date(selectedDate).toLocaleDateString('en-US', { 
                            month: 'long', 
                            day: 'numeric', 
                            year: 'numeric' 
                          })}.
                        </p>
                        {selectedDate === new Date().toISOString().split('T')[0] && (
                          <div className="mt-4 space-x-3">
                            <button
                              onClick={() => setActiveTab('mood')}
                              className="btn-primary"
                            >
                              Record Today&apos;s Mood
                            </button>
                            <button
                              onClick={() => setActiveTab('journal')}
                              className="btn-secondary"
                            >
                              Write Journal Entry
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Wellness Trends Tab */}
            {activeTab === 'trends' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Wellness Journey 📊</h2>
                  <p className="text-gray-600 mb-6">Visualize your mental health trends and insights.</p>
                </div>

                <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 mb-6">
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium text-gray-700">Time Range:</label>
                    <select
                      onChange={(e) => loadAnalytics(e.target.value)}
                      className="px-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 font-medium"
                      defaultValue="Last 30 days"
                    >
                      <option value="Last 7 days">Last 7 days</option>
                      <option value="Last 30 days">Last 30 days</option>
                      <option value="Last 90 days">Last 90 days</option>
                      <option value="All time">All time</option>
                    </select>
                  </div>
                  <button
                    onClick={() => loadAnalytics()}
                    disabled={loading}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all duration-200 flex items-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <div className="spinner"></div>
                        <span>Loading...</span>
                      </>
                    ) : (
                      <>
                        <FaChartLine />
                        <span>Refresh Analytics</span>
                      </>
                    )}
                  </button>
                </div>

                {analytics ? (
                  <div className="space-y-8">
                    {/* Mood Pattern Graph */}
                    <div className="wellness-card bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                      <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center">
                        <FaHeart className="text-red-500 mr-2" />
                        Mood Pattern - Last 7 Days
                      </h3>
                      {analytics.mood_analytics?.mood_data && analytics.mood_analytics.mood_data.length > 0 ? (
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={analytics.mood_analytics.mood_data.slice(-7)}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                              <XAxis 
                                dataKey="date" 
                                stroke="#6b7280"
                                fontSize={12}
                                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                              />
                              <YAxis 
                                domain={[1, 5]} 
                                stroke="#6b7280"
                                fontSize={12}
                                tickFormatter={(value) => {
                                  const moodLabels = ['', '😢', '😔', '😐', '😊', '😄'];
                                  return moodLabels[value] || value;
                                }}
                              />
                              <Tooltip 
                                formatter={(value: number) => {
                                  const moodLabels = ['', 'Very Sad 😢', 'Sad 😔', 'Neutral 😐', 'Happy 😊', 'Very Happy 😄'];
                                  return [moodLabels[value] || value, 'Mood'];
                                }}
                                labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                                contentStyle={{ 
                                  backgroundColor: '#f9fafb', 
                                  border: '1px solid #e5e7eb',
                                  borderRadius: '8px',
                                  color: '#374151'
                                }}
                              />
                              <Line 
                                type="monotone" 
                                dataKey="emoji" 
                                stroke="#ef4444" 
                                strokeWidth={3}
                                dot={{ fill: '#ef4444', strokeWidth: 2, r: 6 }}
                                activeDot={{ r: 8, fill: '#dc2626' }}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      ) : (
                        <div className="h-64 flex items-center justify-center text-gray-500">
                          <div className="text-center">
                            <FaHeart className="text-4xl text-gray-300 mx-auto mb-2" />
                            <p>No mood data available for the last 7 days</p>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Statistics Cards Row */}
                    <div className="grid md:grid-cols-2 gap-6">
                      {/* Sleep Pattern Chart */}
                      <div className="wellness-card bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center">
                          <span className="text-purple-500 mr-2">😴</span>
                          Sleep Pattern - Last 7 Days
                        </h3>
                        {analytics.mood_analytics?.mood_data && analytics.mood_analytics.mood_data.length > 0 ? (
                          (() => {
                            // Filter and prepare sleep data
                            const sleepData = analytics.mood_analytics.mood_data
                              .slice(-7)
                              .map(item => ({
                                date: item.date,
                                sleep_hours: (item as any).sleep_hours || 0
                              }))
                              .filter(item => item.sleep_hours > 0);
                            
                            return sleepData.length > 0 ? (
                              <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                  <LineChart data={sleepData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis 
                                      dataKey="date" 
                                      stroke="#374151"
                                      fontSize={13}
                                      fontWeight={500}
                                      tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                    />
                                    <YAxis 
                                      domain={[0, 12]} 
                                      stroke="#374151"
                                      fontSize={13}
                                      fontWeight={500}
                                      tickFormatter={(value) => `${value}h`}
                                    />
                                    <Tooltip 
                                      formatter={(value: number) => [`${value} hours`, 'Sleep Duration']}
                                      labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                                      contentStyle={{ 
                                        backgroundColor: '#ffffff', 
                                        border: '2px solid #8b5cf6',
                                        borderRadius: '12px',
                                        color: '#1f2937',
                                        fontWeight: '600',
                                        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)'
                                      }}
                                      labelStyle={{
                                        color: '#8b5cf6',
                                        fontWeight: '700'
                                      }}
                                    />
                                    <Line 
                                      type="monotone" 
                                      dataKey="sleep_hours" 
                                      stroke="#8b5cf6" 
                                      strokeWidth={3}
                                      dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 6 }}
                                      activeDot={{ r: 8, fill: '#7c3aed' }}
                                    />
                                  </LineChart>
                                </ResponsiveContainer>
                              </div>
                            ) : (
                              <div className="h-64 flex items-center justify-center text-gray-500">
                                <div className="text-center">
                                  <span className="text-4xl text-gray-300 mb-2">😴</span>
                                  <p>No sleep data available for the last 7 days</p>
                                  <p className="text-sm mt-1">Start recording your sleep hours with your mood entries</p>
                                </div>
                              </div>
                            );
                          })()
                        ) : (
                          <div className="h-64 flex items-center justify-center text-gray-500">
                            <div className="text-center">
                              <span className="text-4xl text-gray-300 mb-2">😴</span>
                              <p>No sleep data available for the last 7 days</p>
                              <p className="text-sm mt-1">Start recording your sleep hours with your mood entries</p>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Journal Activity Card */}
                      <div className="wellness-card bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center">
                          <FaBook className="text-blue-500 mr-2" />
                          Journal Activity
                        </h3>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="text-gray-700 font-medium">Total Entries:</span>
                            <span className="text-gray-900 font-semibold">{analytics.journal_analytics?.stats?.total_entries || 0}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-700 font-medium">Total Words:</span>
                            <span className="text-gray-900 font-semibold">{analytics.journal_analytics?.stats?.total_words?.toLocaleString() || 0}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-700 font-medium">Current Streak:</span>
                            <span className="text-green-600 font-semibold">{analytics.journal_analytics?.stats?.current_streak || 0} days</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-700 font-medium">Longest Streak:</span>
                            <span className="text-blue-600 font-semibold">{analytics.journal_analytics?.stats?.longest_streak || 0} days</span>
                          </div>
                        </div>
                      </div>
                    </div>



                    {/* Summary Statistics Card */}
                    <div className="analytics-summary bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-lg shadow-sm border border-blue-200">
                      <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center">
                        <FaChartLine className="text-indigo-500 mr-2" />
                        Overall Summary
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">{analytics.summary?.total_mood_entries || 0}</div>
                          <div className="text-sm text-gray-700 font-medium">Mood Entries</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">{analytics.summary?.total_journal_entries || 0}</div>
                          <div className="text-sm text-gray-700 font-medium">Journal Entries</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">{analytics.summary?.average_mood?.toFixed(1) || 0}/5</div>
                          <div className="text-sm text-gray-700 font-medium">Avg Mood</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-600">{analytics.summary?.current_streak || 0}</div>
                          <div className="text-sm text-gray-700 font-medium">Day Streak</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="wellness-card bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center">
                    <FaChartLine className="text-4xl text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No Analytics Data</h3>
                    <p className="text-gray-600 mb-4">Click &apos;Refresh&apos; to load your wellness trends and insights.</p>
                    <button
                      onClick={() => loadAnalytics()}
                      className="btn-primary"
                    >
                      Load Analytics
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* AI Companion Tab */}
            {activeTab === 'companion' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Companion 🤖</h2>
                  <p className="text-gray-600 mb-6">Chat with your personal AI companion for emotional support and insights.</p>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg text-center">
                  <FaRobot className="text-6xl text-blue-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-4">AI Companion Coming Soon</h3>
                  <p className="text-gray-600 mb-6">
                    Your personal AI companion will provide empathetic conversations, 
                    emotional support, and help you process your thoughts and feelings naturally.
                  </p>
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <p className="text-sm text-gray-500">
                      Features in development:
                    </p>
                    <ul className="text-sm text-gray-600 mt-2 space-y-1">
                      <li>• Natural conversation interface</li>
                      <li>• Emotional support and validation</li>
                      <li>• Personalized insights and recommendations</li>
                      <li>• Crisis detection and intervention</li>
                      <li>• Integration with your mood and journal data</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}