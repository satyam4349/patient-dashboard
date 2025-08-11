# 🧠 AI Companion System with Journal Data Integration

## 📋 Overview

The AI Companion System is an intelligent mental health support tool that provides personalized assistance based on real user journal data. It analyzes patterns, assesses risk levels, and offers condition-specific coping strategies and crisis intervention protocols.

## 🎯 Key Features

### **Data-Driven Personalization**
- **Journal Data Integration**: Uses real CSV journal data to understand user patterns
- **Condition-Specific Responses**: Tailored support for 8 different mental health conditions
- **Trend Analysis**: Tracks mood, sleep, and risk patterns over time
- **Medication Adherence**: Monitors medication compliance and provides reminders

### **Intelligent Risk Assessment**
- **Real-time Analysis**: Assesses risk based on journal entries and conversation content
- **Crisis Detection**: Identifies crisis keywords and escalates appropriately
- **Progressive Monitoring**: Adjusts check-in frequency based on risk level
- **Emergency Protocols**: Provides immediate crisis intervention when needed

### **Personalized Support**
- **Contextual Responses**: AI remembers conversation history and user patterns
- **Coping Strategies**: Condition-specific techniques and exercises
- **Progress Tracking**: Identifies improvement areas and celebrates progress
- **Therapy Integration**: Connects with existing treatment plans

## 🏗️ Architecture

### **Core Components**

```
AI Companion System
├── Journal Data Service     # CSV data loading and analysis
├── AI Companion Service     # Conversation logic and risk assessment
├── API Routes              # REST endpoints for frontend
└── Data Models             # Pydantic schemas for type safety
```

### **Data Flow**

1. **CSV Loading**: `JournalDataService` loads mock user journal data
2. **Profile Creation**: Automatically creates mental health profiles for each user
3. **Pattern Analysis**: Analyzes trends in mood, sleep, and risk levels
4. **AI Response**: Generates personalized responses based on user context
5. **Risk Assessment**: Continuously monitors and updates risk levels
6. **Intervention**: Provides appropriate crisis intervention when needed

## 📊 Journal Data Structure

### **CSV Columns**
- `user_id`: Unique identifier for each patient
- `entry_date`: Date of journal entry
- `mood_score`: 1-5 scale (1=very low, 5=very high)
- `energy_level`: 1-6 scale (1=very low, 6=very high)
- `sleep_hours`: Hours of sleep the previous night
- `stress_level`: 1-5 scale (1=low, 5=very high)
- `anxiety_level`: 1-5 scale (1=low, 5=very high)
- `depression_level`: 1-5 scale (1=low, 5=very high)
- `content`: Detailed journal entry text
- `triggers`: What triggered the current mental state
- `coping_strategies`: Strategies used to manage symptoms
- `medication_taken`: Whether medication was taken and dosage
- `therapy_session`: Whether therapy session occurred
- `risk_flags`: Risk level (Low, Medium, High, Critical)

### **Supported Conditions**
1. **Schizophrenia** (Abilify medication)
2. **Depression** (Prozac medication)
3. **Anxiety** (Lexapro medication)
4. **Suicidal Thoughts** (Zoloft medication)
5. **Bipolar Disorder** (Lithium medication)
6. **PTSD** (Prazosin medication)
7. **OCD** (Luvox medication)
8. **Eating Disorder** (Fluoxetine medication)

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- FastAPI
- Pydantic
- pandas (for CSV processing)

### **Installation**
```bash
cd Mentaid/Backend
pip install -r requirements.txt
```

### **Running the System**
```bash
# Start the FastAPI server
python main.py

# Run comprehensive tests
python test_ai_companion_with_journal.py
```

## 🧪 Testing

### **Comprehensive Test Suite**
The test script `test_ai_companion_with_journal.py` covers:

- **Journal Data Loading**: Verifies CSV data is loaded correctly
- **User Analytics**: Tests pattern analysis and trend detection
- **Medication Adherence**: Checks compliance tracking
- **AI Conversations**: Tests personalized responses for each condition
- **Crisis Detection**: Validates crisis keyword identification
- **Coping Strategies**: Tests condition-specific techniques
- **Crisis Intervention**: Validates emergency protocols
- **High-Risk Identification**: Tests user risk assessment

### **Sample Test Output**
```
🧠 AI Companion System Test Suite
============================================================
⏰ Test started at: 2024-01-18 10:30:00

📊 Testing Journal Data Loading
==================================================
✅ Total journal entries loaded: 30
✅ User profiles created: 8
👤 user_001: schizophrenia
   Medication: Yes - Abilify 10mg
   Therapist: None
   Risk Trend: improving
   Mood Trend: improving
   Sleep Trend: stable

🤖 Testing AI Companion Conversations
==================================================
👤 user_001 (schizophrenia)
💬 User: I'm hearing voices again today
🤖 AI: Hello User 001! I understand managing symptoms can be challenging...
⚠️  Risk Level: medium
📋 Suggested Actions: Grounding Techniques, Reality Testing
🆘 Emergency Contacts: Your therapist, Local mental health crisis center
```

## 🔌 API Endpoints

### **Core Endpoints**

#### **Conversation Management**
- `POST /ai-companion/conversations` - Start new conversation
- `POST /ai-companion/conversations/{id}/messages` - Send message
- `GET /ai-companion/conversations/{id}` - Get conversation status

#### **User Analytics**
- `GET /ai-companion/user/{id}/profile` - Get mental health profile
- `GET /ai-companion/user/{id}/analytics` - Get journal analytics
- `GET /ai-companion/user/{id}/assessment` - Get comprehensive assessment

#### **Support Resources**
- `GET /ai-companion/coping-strategies/{condition}` - Get coping strategies
- `GET /ai-companion/crisis-intervention/{risk_level}` - Get crisis protocols

#### **Data Access**
- `GET /ai-companion/journal-data/summary` - Get system overview
- `GET /ai-companion/journal-data/user/{id}/recent` - Get recent entries
- `GET /ai-companion/medication-adherence/{id}` - Get adherence stats

### **Example API Usage**

#### **Start Conversation**
```bash
curl -X POST "http://localhost:8000/ai-companion/conversations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": "user_002",
    "condition_focus": "depression",
    "conversation_type": "general_support",
    "initial_message": "I feel so hopeless today"
  }'
```

#### **Get User Analytics**
```bash
curl -X GET "http://localhost:8000/ai-companion/user/user_002/analytics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧠 AI Response Examples

### **Condition-Specific Greetings**

#### **Schizophrenia**
```
"Hello User 001! I understand managing symptoms can be challenging. 
How are your grounding techniques working today?"
```

#### **Depression**
```
"Hi User 002. Depression can make everything feel heavy. 
I'm here to listen and support you. What's on your mind?"
```

#### **Anxiety**
```
"Hello User 003! Anxiety can be overwhelming. 
Let's work on some calming strategies together. How are you feeling right now?"
```

### **Crisis Response**
```
"I'm very concerned about what you're sharing, User 004. 
This sounds like a crisis situation. Please call 911 or go to the nearest 
emergency room immediately. You're not alone, and help is available."
```

### **Contextual Responses**
```
"I notice your sleep has been challenging lately. Let's work on some 
sleep hygiene strategies. What time do you usually go to bed?"
```

## 🚨 Crisis Intervention

### **Risk Levels**

#### **LOW RISK**
- Continue current coping strategies
- Monitor symptoms
- Schedule next therapy session

#### **MEDIUM RISK**
- Increase self-care
- Use crisis coping skills
- Contact therapist within 48 hours

#### **HIGH RISK**
- Immediate therapy contact
- Increase support network
- Safety planning
- Therapy session within 24 hours

#### **CRITICAL RISK**
- Call 911 or go to ER
- Contact crisis line
- Remove access to harmful items
- Immediate professional intervention

### **Emergency Contacts**
- **911** (Emergency)
- **National Suicide Prevention Lifeline: 988**
- **Crisis Text Line: Text HOME to 741741**
- **Your Therapist** (if available)
- **Local Mental Health Crisis Center**

## 📈 Analytics Features

### **Pattern Analysis**
- **Mood Trends**: Improving, worsening, or stable
- **Sleep Patterns**: Sleep quality and consistency
- **Stress Triggers**: Most common stressors
- **Effective Coping**: Strategies that work best
- **Risk Patterns**: Risk level distribution

### **Progress Tracking**
- **Improvement Areas**: Areas needing attention
- **Positive Progress**: Celebrating successes
- **Medication Adherence**: Compliance rates
- **Therapy Engagement**: Session attendance

## 🔒 Safety Features

### **Crisis Detection**
- **Keyword Monitoring**: Identifies crisis language
- **Risk Escalation**: Automatically increases monitoring
- **Immediate Response**: Provides crisis protocols
- **Professional Referral**: Directs to appropriate help

### **Data Privacy**
- **User Isolation**: Data separated by user ID
- **Secure Storage**: No sensitive data logging
- **Access Control**: Authentication required for all endpoints
- **Audit Trail**: Conversation tracking for safety

## 🚀 Future Enhancements

### **Planned Features**
- **Machine Learning**: Predictive risk assessment
- **Natural Language Processing**: Better conversation understanding
- **Integration APIs**: Connect with EHR systems
- **Mobile App**: Native mobile experience
- **Clinician Dashboard**: Professional monitoring tools

### **Advanced Analytics**
- **Predictive Modeling**: Forecast mood and risk trends
- **Pattern Recognition**: Identify early warning signs
- **Treatment Effectiveness**: Measure intervention success
- **Population Health**: Aggregate insights for research

## 📚 Documentation

### **API Documentation**
- **Swagger UI**: Available at `/docs` when server is running
- **ReDoc**: Alternative documentation at `/redoc`
- **OpenAPI Schema**: Machine-readable API specification

### **Code Documentation**
- **Inline Comments**: Comprehensive code documentation
- **Type Hints**: Full type annotations for clarity
- **Error Handling**: Detailed error messages and logging

## 🤝 Contributing

### **Development Guidelines**
1. **Follow PEP 8**: Python style guide compliance
2. **Type Hints**: Use Pydantic models and type annotations
3. **Error Handling**: Comprehensive exception handling
4. **Testing**: Maintain test coverage for new features
5. **Documentation**: Update README and docstrings

### **Testing Strategy**
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows
- **Performance Tests**: Ensure scalability

## 📞 Support

### **Getting Help**
- **Documentation**: Check this README first
- **API Docs**: Use Swagger UI for endpoint details
- **Test Scripts**: Run tests to verify functionality
- **Health Check**: Use `/ai-companion/health` endpoint

### **Troubleshooting**
- **Data Loading**: Check CSV file path and format
- **API Errors**: Verify authentication and request format
- **Performance**: Monitor response times and resource usage
- **Logs**: Check application logs for error details

---

**🎉 The AI Companion System is now ready to provide intelligent, personalized mental health support using your journal data!**

**Remember**: This system is designed to support, not replace, professional mental health care. Always encourage users to seek professional help when needed.
