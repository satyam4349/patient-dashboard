#!/usr/bin/env python3
"""
Test script for AI Companion system with Journal Data integration
This script demonstrates how the AI companion uses real journal data to provide personalized responses.
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_companion_service import AICompanionService
from services.journal_data_service import JournalDataService
from models.ai_companion_models import AIConversationCreate, ConversationType, MentalHealthCondition

def test_journal_data_loading():
    """Test that journal data is loaded correctly"""
    print("📊 Testing Journal Data Loading")
    print("=" * 50)
    
    journal_service = JournalDataService()
    
    print(f"✅ Total journal entries loaded: {len(journal_service.journal_data)}")
    print(f"✅ User profiles created: {len(journal_service.user_profiles)}")
    
    # Show user profiles
    for user_id, profile in journal_service.user_profiles.items():
        print(f"👤 {user_id}: {profile.primary_condition.value}")
        print(f"   Medication: {profile.current_medication}")
        print(f"   Therapist: {profile.therapist or 'None'}")
        print(f"   Risk Trend: {profile.risk_trend}")
        print(f"   Mood Trend: {profile.mood_trend}")
        print(f"   Sleep Trend: {profile.sleep_trend}")
        print()
    
    return journal_service

def test_user_analytics():
    """Test user analytics generation"""
    print("📈 Testing User Analytics")
    print("=" * 50)
    
    journal_service = JournalDataService()
    
    # Test analytics for each user
    for user_id in journal_service.user_profiles.keys():
        analytics = journal_service.get_user_analytics(user_id)
        if analytics:
            print(f"👤 {user_id} Analytics:")
            print(f"   Mood Trend: {analytics.mood_trend}")
            print(f"   Sleep Pattern: {analytics.sleep_pattern}")
            print(f"   Top Stress Triggers: {', '.join(analytics.stress_triggers[:3])}")
            print(f"   Effective Coping: {', '.join(analytics.effective_coping_strategies[:3])}")
            print(f"   Risk Pattern: {analytics.risk_patterns}")
            print(f"   Improvement Areas: {', '.join(analytics.improvement_areas)}")
            print(f"   Positive Progress: {', '.join(analytics.positive_progress)}")
            print()

def test_medication_adherence():
    """Test medication adherence tracking"""
    print("💊 Testing Medication Adherence")
    print("=" * 50)
    
    journal_service = JournalDataService()
    
    for user_id in journal_service.user_profiles.keys():
        adherence = journal_service.get_medication_adherence(user_id)
        print(f"👤 {user_id}:")
        print(f"   Adherence Rate: {adherence['adherence_rate']}%")
        print(f"   Total Entries: {adherence['total_entries']}")
        print(f"   Missed Doses: {adherence['missed_doses']}")
        print(f"   Current Medication: {adherence['current_medication']}")
        print()

def test_ai_companion_conversations():
    """Test AI companion conversations with journal data context"""
    print("🤖 Testing AI Companion Conversations")
    print("=" * 50)
    
    ai_service = AICompanionService()
    
    # Test conversation for each user type
    test_users = [
        ("user_001", MentalHealthCondition.SCHIZOPHRENIA, "I'm hearing voices again today"),
        ("user_002", MentalHealthCondition.DEPRESSION, "I feel so hopeless and tired"),
        ("user_003", MentalHealthCondition.ANXIETY, "I'm really anxious about my presentation tomorrow"),
        ("user_004", MentalHealthCondition.SUICIDAL_THOUGHTS, "I don't see the point in living anymore"),
        ("user_005", MentalHealthCondition.BIPOLAR, "I'm feeling really energetic and creative today"),
        ("user_006", MentalHealthCondition.PTSD, "I had a flashback to the accident"),
        ("user_007", MentalHealthCondition.OCD, "I can't stop washing my hands"),
        ("user_008", MentalHealthCondition.EATING_DISORDER, "I'm struggling with my body image today")
    ]
    
    for user_id, condition, message in test_users:
        print(f"👤 {user_id} ({condition.value})")
        print(f"💬 User: {message}")
        
        # Start conversation
        request = AIConversationCreate(
            user_id=user_id,
            condition_focus=condition,
            conversation_type=ConversationType.GENERAL_SUPPORT,
            initial_message=message
        )
        
        try:
            response = ai_service.start_conversation(request)
            print(f"🤖 AI: {response.ai_message}")
            print(f"⚠️  Risk Level: {response.risk_assessment.value}")
            print(f"📋 Suggested Actions: {', '.join(response.suggested_actions[:3])}")
            print(f"🆘 Emergency Contacts: {', '.join(response.emergency_contacts[:2])}")
            print(f"⏰ Next Check-in: {response.next_check_in}")
            print()
            
            # Test continuing conversation
            follow_up = "Can you help me more with this?"
            follow_response = ai_service.continue_conversation(response.conversation_id, follow_up)
            print(f"💬 User: {follow_up}")
            print(f"🤖 AI: {follow_response.ai_message}")
            print(f"⚠️  Updated Risk: {follow_response.risk_assessment.value}")
            print()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()

def test_crisis_detection():
    """Test crisis detection and intervention"""
    print("🚨 Testing Crisis Detection")
    print("=" * 50)
    
    ai_service = AICompanionService()
    
    crisis_messages = [
        "I want to kill myself",
        "I can't take it anymore",
        "Everyone would be better off without me",
        "I'm going to end my life tonight",
        "I have a plan to hurt myself"
    ]
    
    for message in crisis_messages:
        print(f"💬 Crisis Message: {message}")
        
        # Test with different users
        for user_id in ["user_002", "user_004"]:  # Users with depression/suicidal thoughts
            request = AIConversationCreate(
                user_id=user_id,
                conversation_type=ConversationType.CRISIS_INTERVENTION,
                initial_message=message
            )
            
            try:
                response = ai_service.start_conversation(request)
                print(f"👤 {user_id} - Risk: {response.risk_assessment.value}")
                print(f"🤖 AI Response: {response.ai_message[:100]}...")
                print(f"🆘 Emergency Actions: {', '.join(response.suggested_actions[:2])}")
                print()
            except Exception as e:
                print(f"❌ Error for {user_id}: {str(e)}")
                print()

def test_coping_strategies():
    """Test coping strategies for different conditions"""
    print("🧘 Testing Coping Strategies")
    print("=" * 50)
    
    ai_service = AICompanionService()
    
    conditions = [
        MentalHealthCondition.SCHIZOPHRENIA,
        MentalHealthCondition.DEPRESSION,
        MentalHealthCondition.ANXIETY,
        MentalHealthCondition.SUICIDAL_THOUGHTS
    ]
    
    for condition in conditions:
        strategies = ai_service.get_coping_strategies(condition)
        print(f"🧠 {condition.value.upper()}:")
        for strategy in strategies:
            print(f"   📌 {strategy.strategy_name}")
            print(f"      Description: {strategy.description}")
            print(f"      Effectiveness: {strategy.effectiveness_rating}/5")
            print(f"      When to use: {strategy.when_to_use}")
            print()
        print()

def test_crisis_intervention():
    """Test crisis intervention protocols"""
    print("🚑 Testing Crisis Intervention Protocols")
    print("=" * 50)
    
    ai_service = AICompanionService()
    
    risk_levels = ["low", "medium", "high", "critical"]
    
    for risk_level in risk_levels:
        intervention = ai_service.get_crisis_intervention(risk_level)
        if intervention:
            print(f"⚠️  {risk_level.upper()} RISK:")
            print(f"   Immediate Actions: {', '.join(intervention.immediate_actions)}")
            print(f"   Professional Help Required: {intervention.professional_help_required}")
            print(f"   Emergency Contacts: {', '.join(intervention.emergency_contacts)}")
            print(f"   Follow-up Plan: {intervention.follow_up_plan}")
            print()

def test_high_risk_users():
    """Test identification of high-risk users"""
    print("🔴 Testing High-Risk User Identification")
    print("=" * 50)
    
    journal_service = JournalDataService()
    
    high_risk_users = journal_service.get_high_risk_users()
    print(f"🚨 High-Risk Users: {', '.join(high_risk_users) if high_risk_users else 'None'}")
    
    for user_id in high_risk_users:
        profile = journal_service.get_user_profile(user_id)
        recent_entries = journal_service.get_recent_entries(user_id, days=3)
        
        if profile and recent_entries:
            print(f"👤 {user_id} ({profile.primary_condition.value}):")
            print(f"   Current Risk: {recent_entries[0].risk_flags}")
            print(f"   Recent Mood: {recent_entries[0].mood_score}/5")
            print(f"   Recent Sleep: {recent_entries[0].sleep_hours} hours")
            print(f"   Risk Trend: {profile.risk_trend}")
            print()

def main():
    """Run all tests"""
    print("🧠 AI Companion System Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now()}")
    print()
    
    try:
        # Test journal data loading
        test_journal_data_loading()
        print()
        
        # Test user analytics
        test_user_analytics()
        print()
        
        # Test medication adherence
        test_medication_adherence()
        print()
        
        # Test AI companion conversations
        test_ai_companion_conversations()
        print()
        
        # Test crisis detection
        test_crisis_detection()
        print()
        
        # Test coping strategies
        test_coping_strategies()
        print()
        
        # Test crisis intervention
        test_crisis_intervention()
        print()
        
        # Test high-risk user identification
        test_high_risk_users()
        print()
        
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
