import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from models.ai_companion_models import (
    AIConversationCreate, AIConversationResponse, MentalHealthCondition,
    RiskLevel, ConversationType, CopingStrategy, CrisisIntervention
)
from services.journal_data_service import JournalDataService

class AICompanionService:
    def __init__(self):
        self.journal_service = JournalDataService()
        self.conversations = {}
        self.coping_strategies = self._initialize_coping_strategies()
        self.crisis_interventions = self._initialize_crisis_interventions()
    
    def _initialize_coping_strategies(self) -> Dict[MentalHealthCondition, List[CopingStrategy]]:
        """Initialize condition-specific coping strategies"""
        strategies = {
            MentalHealthCondition.SCHIZOPHRENIA: [
                CopingStrategy(
                    condition=MentalHealthCondition.SCHIZOPHRENIA,
                    strategy_name="Grounding Techniques",
                    description="Use your 5-4-3-2-1 senses to stay present",
                    effectiveness_rating=4,
                    when_to_use="When experiencing hallucinations or paranoia"
                ),
                CopingStrategy(
                    condition=MentalHealthCondition.SCHIZOPHRENIA,
                    strategy_name="Reality Testing",
                    description="Ask trusted people about your perceptions",
                    effectiveness_rating=4,
                    when_to_use="When unsure if something is real"
                )
            ],
            MentalHealthCondition.DEPRESSION: [
                CopingStrategy(
                    condition=MentalHealthCondition.DEPRESSION,
                    strategy_name="Behavioral Activation",
                    description="Start with small, achievable activities",
                    effectiveness_rating=5,
                    when_to_use="When feeling unmotivated or hopeless"
                ),
                CopingStrategy(
                    condition=MentalHealthCondition.DEPRESSION,
                    strategy_name="Cognitive Restructuring",
                    description="Challenge negative thoughts with evidence",
                    effectiveness_rating=4,
                    when_to_use="When having persistent negative thoughts"
                )
            ],
            MentalHealthCondition.ANXIETY: [
                CopingStrategy(
                    condition=MentalHealthCondition.ANXIETY,
                    strategy_name="Deep Breathing",
                    description="4-7-8 breathing pattern to calm nervous system",
                    effectiveness_rating=5,
                    when_to_use="During panic attacks or high anxiety"
                ),
                CopingStrategy(
                    condition=MentalHealthCondition.ANXIETY,
                    strategy_name="Progressive Muscle Relaxation",
                    description="Tense and relax muscle groups systematically",
                    effectiveness_rating=4,
                    when_to_use="When feeling tense or anxious"
                )
            ],
            MentalHealthCondition.SUICIDAL_THOUGHTS: [
                CopingStrategy(
                    condition=MentalHealthCondition.SUICIDAL_THOUGHTS,
                    strategy_name="Safety Planning",
                    description="Create a plan for crisis moments",
                    effectiveness_rating=5,
                    when_to_use="When having suicidal thoughts"
                ),
                CopingStrategy(
                    condition=MentalHealthCondition.SUICIDAL_THOUGHTS,
                    strategy_name="Crisis Contacts",
                    description="Reach out to crisis line or trusted person",
                    effectiveness_rating=5,
                    when_to_use="Immediately when thoughts become intense"
                )
            ]
        }
        return strategies
    
    def _initialize_crisis_interventions(self) -> Dict[RiskLevel, CrisisIntervention]:
        """Initialize crisis intervention protocols"""
        interventions = {
            RiskLevel.LOW: CrisisIntervention(
                risk_level=RiskLevel.LOW,
                immediate_actions=["Continue current coping strategies", "Monitor symptoms"],
                professional_help_required=False,
                emergency_contacts=["Your therapist"],
                follow_up_plan="Schedule next therapy session"
            ),
            RiskLevel.MEDIUM: CrisisIntervention(
                risk_level=RiskLevel.MEDIUM,
                immediate_actions=["Increase self-care", "Use crisis coping skills", "Contact therapist"],
                professional_help_required=False,
                emergency_contacts=["Your therapist", "Crisis line"],
                follow_up_plan="Therapy session within 48 hours"
            ),
            RiskLevel.HIGH: CrisisIntervention(
                risk_level=RiskLevel.HIGH,
                immediate_actions=["Immediate therapy contact", "Increase support network", "Safety planning"],
                professional_help_required=True,
                emergency_contacts=["Your therapist", "Crisis line", "Trusted friend/family"],
                follow_up_plan="Therapy session within 24 hours"
            ),
            RiskLevel.CRITICAL: CrisisIntervention(
                risk_level=RiskLevel.CRITICAL,
                immediate_actions=["Call 911 or go to ER", "Contact crisis line", "Remove access to harmful items"],
                professional_help_required=True,
                emergency_contacts=["911", "Crisis line", "ER", "Your therapist"],
                follow_up_plan="Immediate professional intervention required"
            )
        }
        return interventions
    
    def start_conversation(self, request: AIConversationCreate) -> AIConversationResponse:
        """Start a new AI conversation with personalized context"""
        conversation_id = str(uuid.uuid4())
        
        # Get user profile and recent data
        user_profile = self.journal_service.get_user_profile(request.user_id)
        recent_entries = self.journal_service.get_recent_entries(request.user_id, days=3)
        analytics = self.journal_service.get_user_analytics(request.user_id)
        
        # Assess current risk level
        current_risk = self._assess_risk_level(request.user_id, recent_entries, request.initial_message)
        
        # Generate personalized AI message
        ai_message = self._generate_personalized_message(
            user_profile, recent_entries, analytics, current_risk, request
        )
        
        # Get suggested actions and emergency contacts
        suggested_actions = self._get_suggested_actions(user_profile, current_risk, analytics)
        emergency_contacts = self._get_emergency_contacts(current_risk, user_profile)
        
        # Create conversation response
        response = AIConversationResponse(
            conversation_id=conversation_id,
            user_id=request.user_id,
            ai_message=ai_message,
            risk_assessment=current_risk,
            suggested_actions=suggested_actions,
            emergency_contacts=emergency_contacts,
            next_check_in=self._calculate_next_checkin(current_risk),
            conversation_summary=f"Started {request.conversation_type.value} conversation for {user_profile.primary_condition.value if user_profile else 'unknown condition'}"
        )
        
        # Store conversation
        self.conversations[conversation_id] = {
            "user_id": request.user_id,
            "start_time": datetime.now(),
            "risk_level": current_risk,
            "condition": user_profile.primary_condition if user_profile else None
        }
        
        return response
    
    def continue_conversation(self, conversation_id: str, user_message: str) -> AIConversationResponse:
        """Continue an existing conversation with updated context"""
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")
        
        conversation = self.conversations[conversation_id]
        user_id = conversation["user_id"]
        
        # Get updated user data
        user_profile = self.journal_service.get_user_profile(user_id)
        recent_entries = self.journal_service.get_recent_entries(user_id, days=1)
        analytics = self.journal_service.get_user_analytics(user_id)
        
        # Reassess risk with new message
        updated_risk = self._assess_risk_level(user_id, recent_entries, user_message)
        
        # Generate contextual response
        ai_message = self._generate_contextual_response(
            user_profile, recent_entries, analytics, updated_risk, user_message
        )
        
        # Update conversation
        conversation["risk_level"] = updated_risk
        conversation["last_message"] = user_message
        
        # Get updated suggestions
        suggested_actions = self._get_suggested_actions(user_profile, updated_risk, analytics)
        emergency_contacts = self._get_emergency_contacts(updated_risk, user_profile)
        
        return AIConversationResponse(
            conversation_id=conversation_id,
            user_id=user_id,
            ai_message=ai_message,
            risk_assessment=updated_risk,
            suggested_actions=suggested_actions,
            emergency_contacts=emergency_contacts,
            next_check_in=self._calculate_next_checkin(updated_risk),
            conversation_summary=f"Continued conversation - Risk: {updated_risk.value}"
        )
    
    def _assess_risk_level(self, user_id: str, recent_entries: List, message: Optional[str] = None) -> RiskLevel:
        """Assess current risk level based on journal data and message content"""
        # Check for crisis keywords in message
        if message and self._is_crisis_message(message):
            return RiskLevel.CRITICAL
        
        # Check recent journal entries for risk patterns
        if recent_entries:
            latest_entry = recent_entries[0]
            if latest_entry.risk_flags == "Critical":
                return RiskLevel.CRITICAL
            elif latest_entry.risk_flags == "High":
                return RiskLevel.HIGH
            elif latest_entry.risk_flags == "Medium":
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
        
        # Default to medium if no data
        return RiskLevel.MEDIUM
    
    def _is_crisis_message(self, message: str) -> bool:
        """Check if message contains crisis indicators"""
        crisis_keywords = [
            "kill myself", "end my life", "suicide", "die", "want to die",
            "hurt myself", "self harm", "can't take it anymore", "everyone would be better off",
            "no reason to live", "give up", "hopeless"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in crisis_keywords)
    
    def _generate_personalized_message(self, user_profile, recent_entries, analytics, risk_level, request) -> str:
        """Generate personalized AI message based on user context"""
        if not user_profile:
            return "Hello! I'm here to support you. How are you feeling today?"
        
        # Get user's name from profile or use ID
        user_name = f"User {user_profile.user_id[-3:]}"
        
        # Base message based on condition and risk
        if risk_level == RiskLevel.CRITICAL:
            return f"I'm very concerned about what you're sharing, {user_name}. This sounds like a crisis situation. Please call 911 or go to the nearest emergency room immediately. You're not alone, and help is available."
        
        elif risk_level == RiskLevel.HIGH:
            return f"Thank you for reaching out, {user_name}. I can see you're going through a difficult time. Let's work together to keep you safe. Have you contacted your therapist or crisis line?"
        
        else:
            # Personalized greeting based on condition
            condition_greetings = {
                MentalHealthCondition.SCHIZOPHRENIA: f"Hello {user_name}! I understand managing symptoms can be challenging. How are your grounding techniques working today?",
                MentalHealthCondition.DEPRESSION: f"Hi {user_name}. Depression can make everything feel heavy. I'm here to listen and support you. What's on your mind?",
                MentalHealthCondition.ANXIETY: f"Hello {user_name}! Anxiety can be overwhelming. Let's work on some calming strategies together. How are you feeling right now?",
                MentalHealthCondition.SUICIDAL_THOUGHTS: f"Hi {user_name}. I'm glad you're reaching out. Let's talk about what's happening and make sure you're safe.",
                MentalHealthCondition.BIPOLAR: f"Hello {user_name}! How's your mood stability today? I'm here to help you track patterns and stay balanced.",
                MentalHealthCondition.PTSD: f"Hi {user_name}. PTSD symptoms can be really challenging. How are you managing today?",
                MentalHealthCondition.OCD: f"Hello {user_name}! OCD thoughts can be persistent. Let's work on some ERP techniques together.",
                MentalHealthCondition.EATING_DISORDER: f"Hi {user_name}. Recovery is possible and you're doing great work. How are you feeling about your relationship with food today?"
            }
            
            greeting = condition_greetings.get(user_profile.primary_condition, f"Hello {user_name}! How can I support you today?")
            
            # Add trend information if available
            if analytics:
                if analytics.mood_trend == "improving":
                    greeting += " I can see you've been making positive progress with your mood!"
                elif analytics.mood_trend == "worsening":
                    greeting += " I notice things have been challenging lately. Let's work on some strategies together."
            
            return greeting
    
    def _generate_contextual_response(self, user_profile, recent_entries, analytics, risk_level, user_message) -> str:
        """Generate contextual response based on user's message and current state"""
        if risk_level == RiskLevel.CRITICAL:
            return "This is a crisis situation. Please call 911 or go to the emergency room immediately. You're not alone, and professional help is available right now."
        
        # Analyze message content and provide appropriate response
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["sad", "depressed", "hopeless", "down"]):
            return "I hear how difficult this is for you. Depression can make everything feel overwhelming. Let's work on some strategies together. What specific coping techniques have helped you in the past?"
        
        elif any(word in message_lower for word in ["anxious", "worried", "panic", "nervous"]):
            return "Anxiety can be really challenging. Let's try some breathing exercises together. Take a deep breath in for 4 counts, hold for 7, and exhale for 8. How does that feel?"
        
        elif any(word in message_lower for word in ["voices", "paranoid", "hallucination"]):
            return "I understand you're experiencing some challenging symptoms. Remember to use your grounding techniques. Can you tell me 5 things you can see right now?"
        
        elif any(word in message_lower for word in ["sleep", "tired", "exhausted"]):
            if analytics and analytics.sleep_pattern == "worsening":
                return "I notice your sleep has been challenging lately. Let's work on some sleep hygiene strategies. What time do you usually go to bed?"
            else:
                return "Sleep is so important for mental health. How have you been sleeping lately? Are there any patterns you've noticed?"
        
        elif any(word in message_lower for word in ["medication", "pill", "medicine"]):
            adherence = self.journal_service.get_medication_adherence(user_profile.user_id)
            if adherence["adherence_rate"] < 80:
                return "I notice you might be having some challenges with medication adherence. This is common and nothing to be ashamed of. What barriers are you experiencing?"
            else:
                return "Great job staying on top of your medication! Consistency is key. How are you feeling about your current medication routine?"
        
        else:
            # General supportive response
            return "Thank you for sharing that with me. I'm here to listen and support you. What would be most helpful right now - talking through what's happening, learning some coping strategies, or something else?"
    
    def _get_suggested_actions(self, user_profile, risk_level, analytics) -> List[str]:
        """Get personalized suggested actions based on user context"""
        actions = []
        
        if risk_level == RiskLevel.CRITICAL:
            actions.extend([
                "Call 911 or go to emergency room immediately",
                "Contact crisis hotline",
                "Remove access to harmful items",
                "Stay with a trusted person"
            ])
        elif risk_level == RiskLevel.HIGH:
            actions.extend([
                "Contact your therapist immediately",
                "Use your crisis coping skills",
                "Reach out to a trusted friend or family member",
                "Review your safety plan"
            ])
        else:
            # Regular support actions
            if user_profile and user_profile.primary_condition:
                condition_strategies = self.coping_strategies.get(user_profile.primary_condition, [])
                actions.extend([strategy.strategy_name for strategy in condition_strategies[:2]])
            
            if analytics:
                if analytics.mood_trend == "worsening":
                    actions.append("Practice mood-boosting activities")
                if analytics.sleep_pattern == "worsening":
                    actions.append("Work on sleep hygiene routine")
            
            actions.extend([
                "Practice self-care activities",
                "Use your grounding techniques",
                "Check in with your support network"
            ])
        
        return actions[:5]  # Limit to 5 actions
    
    def _get_emergency_contacts(self, risk_level, user_profile) -> List[str]:
        """Get appropriate emergency contacts based on risk level"""
        contacts = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            contacts.append("911 (Emergency)")
            contacts.append("National Suicide Prevention Lifeline: 988")
            contacts.append("Crisis Text Line: Text HOME to 741741")
        
        if user_profile and user_profile.therapist:
            contacts.append(f"Your Therapist: {user_profile.therapist}")
        
        contacts.extend([
            "Your primary care physician",
            "Local mental health crisis center"
        ])
        
        return contacts
    
    def _calculate_next_checkin(self, risk_level: RiskLevel) -> Optional[datetime]:
        """Calculate when the next check-in should occur based on risk level"""
        now = datetime.now()
        
        if risk_level == RiskLevel.CRITICAL:
            return now + timedelta(hours=1)
        elif risk_level == RiskLevel.HIGH:
            return now + timedelta(hours=4)
        elif risk_level == RiskLevel.MEDIUM:
            return now + timedelta(hours=12)
        else:
            return now + timedelta(days=1)
    
    def get_coping_strategies(self, condition: MentalHealthCondition) -> List[CopingStrategy]:
        """Get coping strategies for a specific condition"""
        return self.coping_strategies.get(condition, [])
    
    def get_crisis_intervention(self, risk_level: RiskLevel) -> Optional[CrisisIntervention]:
        """Get crisis intervention protocol for a risk level"""
        return self.crisis_interventions.get(risk_level)
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive insights for a user"""
        profile = self.journal_service.get_user_profile(user_id)
        analytics = self.journal_service.get_user_analytics(user_id)
        adherence = self.journal_service.get_medication_adherence(user_id)
        
        return {
            "profile": profile.dict() if profile else None,
            "analytics": analytics.dict() if analytics else None,
            "medication_adherence": adherence,
            "recent_entries": len(self.journal_service.get_recent_entries(user_id, days=7))
        }
