# MirrorMind Demo Script 🎬

## 🎯 **Demo Overview**
This script demonstrates all key features of the MirrorMind platform in a logical flow.

---

## 🚀 **DEMO SETUP (5 minutes)**

### **1. Start Backend Server**
```powershell
Set-Location "d:\Projects\Portfolio projects\IEEE\EMBS INTERNSHIP\Backend"
python main.py
```
*Wait for: "MirrorMind API started successfully"*

### **2. Choose Frontend Option**

#### **Option A: Gradio Interface (Recommended for Demo)**
```powershell
Set-Location "d:\Projects\Portfolio projects\IEEE\EMBS INTERNSHIP\FRONTEND"
python app.py
```
*Open: http://localhost:7860*

#### **Option B: Next.js Interface**
```powershell
Set-Location "d:\Projects\Portfolio projects\IEEE\EMBS INTERNSHIP\frontend-app"
npm run dev
```
*Open: http://localhost:3000*

---

## 📋 **DEMO SCRIPT (15 minutes)**

### **Part 1: Authentication & Role-Based Access (3 minutes)**

#### **Step 1.1: Show Landing Page**
- Point out the clean, professional interface
- Highlight the dual-agent AI system messaging
- Show the authentication options

#### **Step 1.2: Create Patient Account**
```
Email: patient@demo.com
Password: DemoPass123
Role: Patient
```
- Demonstrate signup process
- Show immediate login after signup
- **Key Point**: Dashboard only appears after authentication

#### **Step 1.3: Create Clinician Account**
```
Email: clinician@demo.com  
Password: DemoPass123
Role: Clinician
```
- Show different dashboard for clinicians
- **Key Point**: Role-based access control in action

---

### **Part 2: Patient Experience (5 minutes)**

#### **Step 2.1: 5-Emoji Mood Tracking**
- Login as patient@demo.com
- Navigate to "Daily Mood" tab
- **Demonstrate**: Click different emoji moods
- Show visual feedback and mood selection
- Add note: "Had a productive morning meeting"
- Save mood entry
- **Key Point**: Only one mood entry per day allowed

#### **Step 2.2: Conversational Journaling**
- Navigate to "Daily Journal" tab
- Write sample entry:
```
Dear journal, today started with some anxiety about the presentation, 
but it went really well. I felt confident and the team responded 
positively. I'm learning to trust myself more. The afternoon was 
peaceful - took a walk and felt grateful for the sunny weather.
```
- Show word/character count updating in real-time
- Save journal entry
- **Key Point**: Natural, conversational writing vs forms

#### **Step 2.3: Wellness Trends Analytics**
- Navigate to "Wellness Trends" tab
- Click "Refresh" to load analytics
- Show mood statistics, journaling activity, and language insights
- **Key Point**: Comprehensive analytics from simple daily inputs

---

### **Part 3: Clinical Experience (4 minutes)**

#### **Step 3.1: Clinical Dashboard Overview**
- Login as clinician@demo.com
- Show patient overview with risk levels
- Point out high/medium/low risk categorization
- **Key Point**: Population-level insights at a glance

#### **Step 3.2: AI Clinical Assistant**
- Navigate to "AI Assistant" tab
- Try these sample queries:
  - "Show me a comprehensive patient overview"
  - "Perform risk assessment for all patients"
  - "Generate treatment plan recommendations"
- Show AI responses with clinical insights
- **Key Point**: Evidence-based clinical decision support

#### **Step 3.3: Report Generation**
- Navigate to "Reports & Documentation" tab
- Generate a SOAP note for patient ID: "demo_patient_001"
- Show the structured clinical report
- **Key Point**: Automated clinical documentation

---

### **Part 4: AI Agent System (3 minutes)**

#### **Step 4.1: Patient Companion Agent**
- Login as patient
- Navigate to "AI Companion" tab (if available) or use API directly
- Show crisis detection with sample message:
  - "I'm feeling really hopeless and don't want to be here anymore"
- Demonstrate empathetic response and crisis intervention
- **Key Point**: Real-time mental health monitoring

#### **Step 4.2: Clinical Assistant Agent**
- Show diagnostic analysis capabilities
- Demonstrate DSM-V criteria matching
- Show treatment recommendations
- **Key Point**: AI-powered clinical insights

---

## 🎯 **KEY DEMO TALKING POINTS**

### **1. Innovation Highlights**
- **Dual-Agent AI System**: Patient companion + Clinical assistant
- **Natural Interaction**: Conversation-based vs traditional forms
- **Real-time Analytics**: Immediate insights from daily inputs
- **Crisis Detection**: Automatic risk assessment and intervention

### **2. Technical Excellence**
- **Security First**: End-to-end encryption, JWT auth, role-based access
- **Scalable Architecture**: FastAPI backend, modern React frontend
- **Comprehensive Analytics**: Mood trends, language analysis, LIWC integration
- **Clinical Grade**: SOAP notes, DSM-V criteria, treatment planning

### **3. User Experience**
- **Patients**: Simple, empathetic, encouraging daily engagement
- **Clinicians**: Powerful insights, automated documentation, decision support
- **Responsive Design**: Works on desktop, tablet, and mobile

### **4. Real-world Impact**
- **Early Intervention**: Detect mental health issues before crisis
- **Improved Outcomes**: Data-driven treatment decisions
- **Reduced Burden**: Automated documentation and analysis
- **Accessible Care**: 24/7 AI companion support

---

## 🔧 **DEMO TROUBLESHOOTING**

### **Common Issues & Solutions**

#### **Backend Won't Start**
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID_NUMBER> /F

# Restart backend
python main.py
```

#### **Frontend Connection Issues**
- Verify backend is running on http://localhost:8000
- Check .env.local file has correct API URL
- Clear browser cache and cookies

#### **Authentication Issues**
- Use fresh email addresses for demo accounts
- Check network connectivity
- Verify Supabase credentials in .env file

#### **Database Issues**
- Ensure Supabase project is active
- Check service role key permissions
- Verify RLS policies are enabled

---

## 📊 **DEMO SUCCESS METRICS**

### **What to Highlight**
- ✅ **Authentication**: Seamless signup/login with role-based access
- ✅ **Daily Limits**: One mood/journal entry per day enforcement
- ✅ **5-Emoji System**: Intuitive mood tracking interface
- ✅ **Analytics**: Comprehensive wellness insights
- ✅ **AI Agents**: Both patient companion and clinical assistant
- ✅ **Security**: Encrypted data, secure authentication
- ✅ **Clinical Tools**: Professional-grade documentation and analysis

### **Expected Audience Reactions**
- **"This is much more intuitive than traditional forms"**
- **"The AI responses are surprisingly empathetic"**
- **"The clinical insights would save hours of documentation time"**
- **"The crisis detection could literally save lives"**

---

## 🎉 **DEMO CONCLUSION**

### **Wrap-up Points**
1. **Complete Solution**: From patient engagement to clinical insights
2. **AI-Powered**: Dual agents for comprehensive mental health support
3. **Production Ready**: Security, scalability, and clinical-grade features
4. **Immediate Value**: Reduces clinician workload while improving patient care

### **Next Steps Discussion**
- Production deployment timeline
- Integration with existing healthcare systems
- Compliance and certification requirements
- Scaling and customization options

**Demo Duration: ~15 minutes**
**Setup Time: ~5 minutes**
**Total Time: ~20 minutes**