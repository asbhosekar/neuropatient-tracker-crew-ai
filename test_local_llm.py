"""
Quick test script for local LLM connection.

Run this to verify your local Llama 3.2 setup is working.
"""
import asyncio
import sys
from src.config import settings
from src.orchestrator import get_model_client, SingleAgentChat


def print_config():
    """Print current LLM configuration."""
    print("=" * 60)
    print("🔧 Current Configuration")
    print("=" * 60)
    print(f"Provider: {settings.LLM_PROVIDER}")

    if settings.LLM_PROVIDER == "local":
        print(f"🖥️  Local LLM Model: {settings.LOCAL_LLM_MODEL}")
        print(f"📡 Base URL: {settings.LOCAL_LLM_BASE_URL}")
        print(f"🔑 API Key: {settings.LOCAL_LLM_API_KEY}")
    else:
        print(f"☁️  OpenAI Model: {settings.OPENAI_MODEL}")
        print(f"🔑 API Key: {'*' * 20}{settings.OPENAI_API_KEY[-4:] if settings.OPENAI_API_KEY else 'Not Set'}")
    print("=" * 60 + "\n")


def test_connection():
    """Test if we can create a model client."""
    print("🔌 Testing Model Client Connection...")
    try:
        client = get_model_client()
        print("✅ Model client created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create model client: {e}")
        return False


async def test_simple_query():
    """Test a simple query to the LLM."""
    print("\n💬 Testing Simple Query...")
    print("Query: 'What is a neurological assessment?'\n")

    try:
        chat = SingleAgentChat()

        # Simple question
        question = "In 2-3 sentences, what is a neurological assessment?"

        # Create a simple agent consultation
        await chat.consult_neurologist(question)

        print("\n✅ Query test successful!")
        return True

    except Exception as e:
        print(f"\n❌ Query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n🧠 Neuro Patient Tracker - Local LLM Test\n")

    # Print configuration
    print_config()

    # Test 1: Connection
    if not test_connection():
        print("\n⚠️  Connection test failed!")
        print("\nTroubleshooting:")
        if settings.LLM_PROVIDER == "local":
            print("1. Is your local LLM server running?")
            print(f"   - Check if {settings.LOCAL_LLM_BASE_URL} is accessible")
            print("2. For LM Studio: Start the local server")
            print("3. For Ollama: Run 'ollama serve'")
            print("4. Check your .env file for correct BASE_URL")
        else:
            print("1. Check your OPENAI_API_KEY in .env")
            print("2. Verify you have internet connection")
        sys.exit(1)

    # Test 2: Simple Query
    print("\n" + "-" * 60)
    success = await test_simple_query()

    if success:
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        print("\nYour local LLM is ready to use with:")
        print("  - Command line: python -m src.main")
        print("  - Streamlit UI: streamlit run app.py")
    else:
        print("\n" + "=" * 60)
        print("⚠️  Some tests failed")
        print("=" * 60)
        print("\nCheck the errors above and:")
        print("1. Verify your LLM server is running")
        print("2. Check the model is loaded")
        print("3. Review LOCAL_LLM_SETUP.md for troubleshooting")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
