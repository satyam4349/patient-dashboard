"""
Test script for AI Companion module.
Tests conversation flow, risk assessment, and crisis intervention.
"""
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.ai_companion_models import (
    MentalHealthCondition,
    ConversationType,
    AIConversationCreate
)
from services.ai_companion_service import AICompanionService
from data.demo_mental_health_data import (
    DEMO_PATIENTS,
    DEMO_CONVERSATION_TEMPLATES,
    DEMO_COPING_STRATEGIES
)


def test_ai_companion():
    """Test the AI companion service with different scenarios."""
    print("🧠 Testing AI Companion Module")
    print("=" * 50)
    
    # Initialize service
    ai_service = AICompanionService()
    
    # Test 1: Start conversation for depression
    print("\n1. Testing Depression Conversation")
    print("-" * 30)
    
    dep_request = AIConversationCreate(
        user_id="test_user_001",
        condition_focus=MentalHealthCondition.DEPRESSION,
        conversation_type=ConversationType.GENERAL_SUPPORT,
        initial_message="I just don't see the point in anything anymore."
    )
    
    try:
        response = ai_service.start_conversation(dep_request)
        print(f"✅ Conversation started: {response.conversation_id}")
        print(f"🤖 AI Response: {response.ai_message}")
        print(f"⚠️  Risk Level: {response.risk_assessment}")
        print(f"💡 Suggested Actions: {response.suggested_actions}")
        if response.emergency_contact:
            print(f"🚨 Emergency Contact: {response.emergency_contact}")
    except Exception as e:
        print(f"❌ Error starting depression conversation: {e}")
    
    # Test 2: Continue conversation with crisis message
    print("\n2. Testing Crisis Response")
    print("-" * 30)
    
    try:
        crisis_response = ai_service.continue_conversation(
            response.conversation_id,
            "I want to kill myself"
        )
        print(f"🤖 Crisis Response: {crisis_response.ai_message}")
        print(f"⚠️  Updated Risk Level: {crisis_response.risk_assessment}")
        print(f"💡 Crisis Actions: {crisis_response.suggested_actions}")
        if crisis_response.emergency_contact:
            print(f"🚨 Emergency Contact: {crisis_response.emergency_contact}")
    except Exception as e:
        print(f"❌ Error in crisis response: {e}")
    
    # Test 3: Start conversation for anxiety
    print("\n3. Testing Anxiety Conversation")
    print("-" * 30)
    
    anx_request = AIConversationCreate(
        user_id="test_user_002",
        condition_focus=MentalHealthCondition.ANXIETY,
        conversation_type=ConversationType.COPING_STRATEGIES,
        initial_message="I can't stop worrying about everything."
    )
    
    try:
        anx_response = ai_service.start_conversation(anx_request)
        print(f"✅ Anxiety conversation started: {anx_response.conversation_id}")
        print(f"🤖 AI Response: {anx_response.ai_message}")
        print(f"⚠️  Risk Level: {anx_response.risk_assessment}")
        print(f"💡 Suggested Actions: {anx_response.suggested_actions}")
    except Exception as e:
        print(f"❌ Error starting anxiety conversation: {e}")
    
    # Test 4: Start conversation for schizophrenia
    print("\n4. Testing Schizophrenia Conversation")
    print("-" * 30)
    
    schiz_request = AIConversationCreate(
        user_id="test_user_003",
        condition_focus=MentalHealthCondition.SCHIZOPHRENIA,
        conversation_type=ConversationType.THERAPY_SESSION,
        initial_message="I've been hearing voices again."
    )
    
    try:
        schiz_response = ai_service.start_conversation(schiz_request)
        print(f"✅ Schizophrenia conversation started: {schiz_response.conversation_id}")
        print(f"🤖 AI Response: {schiz_response.ai_message}")
        print(f"⚠️  Risk Level: {schiz_response.risk_assessment}")
        print(f"💡 Suggested Actions: {schiz_response.suggested_actions}")
    except Exception as e:
        print(f"❌ Error starting schizophrenia conversation: {e}")
    
    # Test 5: Test mental health assessment
    print("\n5. Testing Mental Health Assessment")
    print("-" * 30)
    
    try:
        assessment = ai_service.assess_mental_health("test_user_001")
        print(f"📊 Overall Risk: {assessment.overall_risk}")
        print(f"🔍 Condition Breakdown: {assessment.condition_breakdown}")
        print(f"💡 Recommendations: {assessment.recommendations}")
        print(f"👨‍⚕️  Professional Help Recommended: {assessment.professional_help_recommended}")
    except Exception as e:
        print(f"❌ Error in mental health assessment: {e}")
    
    # Test 6: Test coping strategies
    print("\n6. Testing Coping Strategies")
    print("-" * 30)
    
    try:
        dep_strategies = ai_service.get_coping_strategies(MentalHealthCondition.DEPRESSION)
        print(f"🧘 Depression Coping Strategies:")
        for strategy in dep_strategies:
            print(f"   • {strategy.name} ({strategy.difficulty_level}, {strategy.time_required_minutes}min)")
        
        anx_strategies = ai_service.get_coping_strategies(MentalHealthCondition.ANXIETY)
        print(f"🧘 Anxiety Coping Strategies:")
        for strategy in anx_strategies:
            print(f"   • {strategy.name} ({strategy.difficulty_level}, {strategy.time_required_minutes}min)")
    except Exception as e:
        print(f"❌ Error getting coping strategies: {e}")
    
    # Test 7: Test crisis intervention
    print("\n7. Testing Crisis Intervention")
    print("-" * 30)
    
    try:
        high_risk_intervention = ai_service.get_crisis_intervention(RiskLevel.HIGH)
        print(f"🚨 High Risk Intervention:")
        print(f"   • Immediate Actions: {high_risk_intervention.immediate_actions}")
        print(f"   • Professional Help Required: {high_risk_intervention.professional_help_required}")
        print(f"   • Emergency Contacts: {high_risk_intervention.emergency_contacts}")
        
        critical_intervention = ai_service.get_crisis_intervention(RiskLevel.CRITICAL)
        print(f"🚨 Critical Risk Intervention:")
        print(f"   • Immediate Actions: {critical_intervention.immediate_actions}")
        print(f"   • Professional Help Required: {critical_intervention.professional_help_required}")
        print(f"   • Emergency Contacts: {critical_intervention.emergency_contacts}")
    except Exception as e:
        print(f"❌ Error getting crisis intervention: {e}")
    
    # Test 8: Display demo data
    print("\n8. Demo Data Overview")
    print("-" * 30)
    
    print(f"👥 Demo Patients: {len(DEMO_PATIENTS)}")
    for patient in DEMO_PATIENTS:
        print(f"   • {patient.name} ({patient.age}) - {patient.primary_condition.value}")
    
    print(f"💬 Conversation Templates: {len(DEMO_CONVERSATION_TEMPLATES)}")
    for template in DEMO_CONVERSATION_TEMPLATES:
        print(f"   • {template.condition.value} - {len(template.conversation_starters)} starters")
    
    print(f"🧘 Coping Strategies: {len(DEMO_COPING_STRATEGIES)}")
    for strategy in DEMO_COPING_STRATEGIES:
        print(f"   • {strategy.name} - Targets: {[c.value for c in strategy.condition_target]}")
    
    print("\n✅ AI Companion Module Test Complete!")
    print("=" * 50)


if __name__ == "__main__":
    test_ai_companion()
