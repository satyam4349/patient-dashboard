"""
Database initialization script for Supabase setup.
Run this script once to set up the database schema and RLS policies.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import AuthService

# Load environment variables
load_dotenv()

async def init_database():
    """
    Check database setup and provide guidance for initialization.
    """
    print("🚀 Checking MirrorMind database setup...")
    
    try:
        # Check if user table exists
        result = await AuthService.create_user_table()
        
        if result["status"] == "success":
            print("✅ Database is already set up correctly!")
            print("\nDatabase components verified:")
            print("- ✅ users table with proper schema")
            print("- ✅ Row Level Security (RLS) policies")
            print("- ✅ Database indexes for performance")
            print("\nYour database is ready for use!")
            return True
        else:
            print(f"❌ Database setup required: {result['message']}")
            
            if "instructions" in result:
                print("\n📋 Setup Instructions:")
                instructions = result["instructions"]
                for key, instruction in instructions.items():
                    print(f"   {key.replace('step', 'Step ')}: {instruction}")
                
                print(f"\n📄 SQL Migration File Location:")
                print(f"   database/migrations/001_create_users_table.sql")
                print(f"\n🔧 Alternative Setup Methods:")
                print(f"   1. Copy the SQL from the migration file to Supabase SQL Editor")
                print(f"   2. Use Supabase CLI: supabase db push (if you have supabase CLI set up)")
                print(f"   3. Run the SQL manually in your Supabase dashboard")
            
            return False
            
    except Exception as e:
        print(f"❌ Error during database check: {str(e)}")
        return False

async def create_sample_users():
    """
    Create sample users for testing (optional).
    """
    print("\n🔧 Creating sample users for testing...")
    
    try:
        from models.user_models import UserCreate
        
        # Sample regular user
        regular_user = UserCreate(
            email="user@example.com",
            password="TestPassword123",
            role="regular_user",
            full_name="Test User"
        )
        
        # Sample clinician
        clinician_user = UserCreate(
            email="clinician@example.com",
            password="TestPassword123",
            role="clinician",
            full_name="Dr. Test Clinician"
        )
        
        # Create users
        user_result = await AuthService.signup(regular_user)
        clinician_result = await AuthService.signup(clinician_user)
        
        if user_result["status"] == "success":
            print("✅ Sample regular user created: user@example.com")
        else:
            print(f"⚠️  Regular user creation: {user_result['message']}")
        
        if clinician_result["status"] == "success":
            print("✅ Sample clinician created: clinician@example.com")
        else:
            print(f"⚠️  Clinician creation: {clinician_result['message']}")
            
    except Exception as e:
        print(f"⚠️  Error creating sample users: {str(e)}")

def check_environment():
    """
    Check if all required environment variables are set.
    """
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "JWT_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file before running this script.")
        return False
    
    print("✅ All required environment variables are set!")
    return True

async def main():
    """
    Main initialization function.
    """
    print("=" * 50)
    print("MirrorMind Database Initialization")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Initialize database
    if not await init_database():
        sys.exit(1)
    
    # Ask if user wants to create sample users
    create_samples = input("\n❓ Do you want to create sample users for testing? (y/N): ").lower().strip()
    if create_samples in ['y', 'yes']:
        await create_sample_users()
    
    print("\n" + "=" * 50)
    print("🎉 Database setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Start your FastAPI server: python main.py")
    print("2. Visit http://localhost:8000/docs to see the API documentation")
    print("3. Test authentication endpoints")
    
    if create_samples in ['y', 'yes']:
        print("\nSample users created:")
        print("- Regular user: user@example.com (password: TestPassword123)")
        print("- Clinician: clinician@example.com (password: TestPassword123)")

if __name__ == "__main__":
    asyncio.run(main())