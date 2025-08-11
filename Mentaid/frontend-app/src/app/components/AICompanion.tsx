"use client";

import React, { useState, useEffect } from 'react';
import { 
  ChatBubbleLeftRightIcon, 
  ExclamationTriangleIcon,
  HeartIcon,
  BrainIcon,
  UserIcon
} from '@heroicons/react/24/outline';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  riskLevel?: string;
}

interface Conversation {
  id: string;
  conditionFocus?: string;
  conversationType: string;
  messages: Message[];
  riskAssessment?: string;
}

const AICompanion: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCondition, setSelectedCondition] = useState<string>('');
  const [conversationType, setConversationType] = useState<string>('general_support');

  const mentalHealthConditions = [
    { value: 'depression', label: 'Depression', icon: HeartIcon },
    { value: 'anxiety', label: 'Anxiety', icon: BrainIcon },
    { value: 'schizophrenia', label: 'Schizophrenia', icon: BrainIcon },
    { value: 'suicidal_thoughts', label: 'Suicidal Thoughts', icon: ExclamationTriangleIcon },
    { value: 'bipolar', label: 'Bipolar Disorder', icon: BrainIcon },
    { value: 'ptsd', label: 'PTSD', icon: BrainIcon },
    { value: 'ocd', label: 'OCD', icon: BrainIcon },
    { value: 'eating_disorder', label: 'Eating Disorder', icon: HeartIcon }
  ];

  const conversationTypes = [
    { value: 'general_support', label: 'General Support' },
    { value: 'crisis_intervention', label: 'Crisis Intervention' },
    { value: 'therapy_session', label: 'Therapy Session' },
    { value: 'mood_tracking', label: 'Mood Tracking' },
    { value: 'coping_strategies', label: 'Coping Strategies' }
  ];

  const startNewConversation = async () => {
    if (!selectedCondition) {
      alert('Please select a mental health condition');
      return;
    }

    setIsLoading(true);
    try {
      // Simulate API call - replace with actual API call
      const newConversation: Conversation = {
        id: Date.now().toString(),
        conditionFocus: selectedCondition,
        conversationType,
        messages: [{
          id: '1',
          content: `Hello! I'm your AI mental health companion. I understand you're dealing with ${selectedCondition.replace('_', ' ')}. I'm here to listen and support you. How are you feeling today?`,
          sender: 'ai',
          timestamp: new Date(),
          riskLevel: 'low'
        }]
      };

      setConversations(prev => [...prev, newConversation]);
      setCurrentConversation(newConversation);
      setMessage('');
    } catch (error) {
      console.error('Error starting conversation:', error);
      alert('Failed to start conversation');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || !currentConversation) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      sender: 'user',
      timestamp: new Date()
    };

    // Add user message to conversation
    const updatedConversation = {
      ...currentConversation,
      messages: [...currentConversation.messages, userMessage]
    };

    setCurrentConversation(updatedConversation);
    setConversations(prev => 
      prev.map(conv => 
        conv.id === currentConversation.id ? updatedConversation : conv
      )
    );

    setMessage('');
    setIsLoading(true);

    try {
      // Simulate AI response - replace with actual API call
      setTimeout(() => {
        const aiResponse = generateAIResponse(message, currentConversation.conditionFocus);
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: aiResponse.content,
          sender: 'ai',
          timestamp: new Date(),
          riskLevel: aiResponse.riskLevel
        };

        const finalConversation = {
          ...updatedConversation,
          messages: [...updatedConversation.messages, aiMessage],
          riskAssessment: aiResponse.riskLevel
        };

        setCurrentConversation(finalConversation);
        setConversations(prev => 
          prev.map(conv => 
            conv.id === currentConversation.id ? finalConversation : conv
          )
        );
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);
    }
  };

  const generateAIResponse = (userMessage: string, condition?: string) => {
    const messageLower = userMessage.toLowerCase();
    
    // Crisis detection
    if (messageLower.includes('suicide') || messageLower.includes('kill myself') || messageLower.includes('want to die')) {
      return {
        content: "I'm very concerned about what you're saying. Your life has value and you matter. Please, if you're having thoughts of suicide, call the National Suicide Prevention Lifeline at 988 right now. They're available 24/7 and can help you stay safe. You're not alone, and there are people who want to help you.",
        riskLevel: 'critical'
      };
    }

    if (messageLower.includes('hurt myself') || messageLower.includes('self harm')) {
      return {
        content: "I'm very concerned about what you're experiencing. Your safety is my top priority. Can you tell me more about what's happening? I want to make sure you're safe.",
        riskLevel: 'high'
      };
    }

    // Condition-specific responses
    if (condition === 'depression') {
      if (messageLower.includes('hopeless') || messageLower.includes('worthless') || messageLower.includes('burden')) {
        return {
          content: "I hear how much you're struggling right now. Depression can make everything feel overwhelming. It's okay to have days where getting out of bed is a major accomplishment. You're not a burden. Your feelings are valid and important.",
          riskLevel: 'medium'
        };
      }
    }

    if (condition === 'anxiety') {
      if (messageLower.includes('worry') || messageLower.includes('anxious') || messageLower.includes('panic')) {
        return {
          content: "Anxiety can feel overwhelming, but we can work through this together. Let's practice some breathing exercises to help calm your nervous system. Your anxiety doesn't define you. It's a condition that can be managed.",
          riskLevel: 'medium'
        };
      }
    }

    if (condition === 'schizophrenia') {
      if (messageLower.includes('voices') || messageLower.includes('hearing')) {
        return {
          content: "I understand that you're experiencing some distressing symptoms. Can you tell me more about what you're hearing? It sounds like you're feeling very anxious and paranoid. Let's work on some grounding techniques together.",
          riskLevel: 'medium'
        };
      }
    }

    // General supportive response
    return {
      content: "I hear you, and I understand this is really difficult for you right now. Thank you for sharing that with me. It takes courage to open up about these things. I'm here to listen and support you through this. You don't have to face this alone.",
      riskLevel: 'low'
    };
  };

  const getRiskLevelColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getRiskLevelIcon = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'critical': return <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />;
      case 'high': return <ExclamationTriangleIcon className="w-4 h-4 text-orange-600" />;
      case 'medium': return <ExclamationTriangleIcon className="w-4 h-4 text-yellow-600" />;
      case 'low': return <HeartIcon className="w-4 h-4 text-green-600" />;
      default: return <UserIcon className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">AI Mental Health Companion</h1>
        </div>

        {/* New Conversation Setup */}
        {!currentConversation && (
          <div className="bg-blue-50 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-blue-900 mb-4">Start a New Conversation</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mental Health Condition
                </label>
                <select
                  value={selectedCondition}
                  onChange={(e) => setSelectedCondition(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a condition</option>
                  {mentalHealthConditions.map(condition => (
                    <option key={condition.value} value={condition.value}>
                      {condition.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Conversation Type
                </label>
                <select
                  value={conversationType}
                  onChange={(e) => setConversationType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {conversationTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={startNewConversation}
              disabled={!selectedCondition || isLoading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Starting...' : 'Start Conversation'}
            </button>
          </div>
        )}

        {/* Current Conversation */}
        {currentConversation && (
          <div className="space-y-4">
            {/* Conversation Header */}
            <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
              <div>
                <h3 className="font-semibold text-gray-900">
                  {currentConversation.conditionFocus?.replace('_', ' ')} Support
                </h3>
                <p className="text-sm text-gray-600">
                  {conversationTypes.find(t => t.value === currentConversation.conversationType)?.label}
                </p>
              </div>
              
              {currentConversation.riskAssessment && (
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(currentConversation.riskAssessment)}`}>
                  <div className="flex items-center gap-1">
                    {getRiskLevelIcon(currentConversation.riskAssessment)}
                    {currentConversation.riskAssessment.toUpperCase()}
                  </div>
                </div>
              )}
            </div>

            {/* Messages */}
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {currentConversation.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs opacity-70">
                        {msg.timestamp.toLocaleTimeString()}
                      </span>
                      {msg.riskLevel && (
                        <div className={`px-2 py-1 rounded-full text-xs ${getRiskLevelColor(msg.riskLevel)}`}>
                          {msg.riskLevel.toUpperCase()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      <span className="text-sm">AI is typing...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Message Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!message.trim() || isLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>

            {/* New Conversation Button */}
            <button
              onClick={() => {
                setCurrentConversation(null);
                setSelectedCondition('');
                setConversationType('general_support');
              }}
              className="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
            >
              Start New Conversation
            </button>
          </div>
        )}

        {/* Emergency Information */}
        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
            <h3 className="font-semibold text-red-900">Emergency Resources</h3>
          </div>
          <p className="text-sm text-red-800 mb-2">
            If you're experiencing a mental health crisis or having thoughts of suicide:
          </p>
          <ul className="text-sm text-red-800 space-y-1">
            <li>• <strong>National Suicide Prevention Lifeline:</strong> 988 (24/7)</li>
            <li>• <strong>Crisis Text Line:</strong> Text HOME to 741741</li>
            <li>• <strong>Emergency Services:</strong> 911</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AICompanion;
