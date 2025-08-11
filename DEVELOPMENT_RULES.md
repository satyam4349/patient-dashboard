# Development Rules & Guidelines

## 🚀 Project Development Workflow

### General Rules
- **No long chats** - Keep discussions focused and concise
- **Commands run by you** - All terminal commands must be executed by you, not automated
- **Module-wise approach** - Develop and test one module at a time
- **Testing responsibility** - You handle all testing of modules

---

## 📁 Module Development Structure

### 1. Backend Modules
```
Backend/
├── models/          # Database models
├── routes/          # API endpoints
├── services/        # Business logic
├── middleware/      # Authentication & validation
└── utils/           # Helper functions
```

### 2. Frontend Modules
```
Frontend/
├── components/      # Reusable UI components
├── pages/          # Route pages
├── services/       # API calls
└── utils/          # Helper functions
```

---

## 🔧 Development Process

### Phase 1: Backend Foundation
1. **Database Models** - Complete patient and user models
2. **Authentication** - JWT tokens, middleware
3. **Core APIs** - Patient CRUD operations
4. **Testing** - API endpoints validation

### Phase 2: Frontend Foundation
1. **Authentication UI** - Login/signup forms
2. **Dashboard Layout** - Basic structure
3. **Patient Management** - CRUD operations
4. **Testing** - Component functionality

### Phase 3: Advanced Features
1. **Analytics** - Patient data visualization
2. **AI Agent** - Chatbot integration
3. **Real-time Updates** - WebSocket connections
4. **Testing** - End-to-end workflows

---

## 🧪 Testing Guidelines

### Backend Testing
- Test each API endpoint individually
- Validate database operations
- Check authentication middleware
- Verify error handling

### Frontend Testing
- Test component rendering
- Validate form submissions
- Check API integrations
- Test responsive design

### Integration Testing
- End-to-end user workflows
- Cross-module communication
- Database consistency
- Performance benchmarks

---

## 📋 Command Execution Rules

### You Will Execute:
- Database migrations
- Server startup/shutdown
- Package installations
- Testing commands
- Build processes
- Deployment commands

### AI Assistant Will:
- Provide code suggestions
- Explain implementation details
- Help debug issues
- Suggest testing strategies
- Review code structure

---

## 🎯 Module Completion Checklist

### Before Moving to Next Module:
- [ ] All functions implemented
- [ ] Error handling complete
- [ ] Basic testing done
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] No critical bugs

---

## 🚫 What NOT to Do

- Don't implement multiple modules simultaneously
- Don't skip testing phase
- Don't merge incomplete features
- Don't ignore error messages
- Don't proceed without validation

---

## ✅ Success Criteria

- Each module works independently
- Clear separation of concerns
- Comprehensive error handling
- User-friendly interfaces
- Scalable architecture
- Well-documented code

---

## 📞 Communication Rules

- **Keep it brief** - One question per message
- **Be specific** - Mention exact module/function
- **Show errors** - Include error messages
- **Confirm actions** - Verify before proceeding

---

*Remember: Quality over speed. Test thoroughly before moving forward.*
