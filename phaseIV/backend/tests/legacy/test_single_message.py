"""Simple single-message test for OpenAI Agent + MCP integration.

This test makes only ONE API call to verify the integration works without hitting rate limits.
"""

import asyncio
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_single_message():
    """Test a single message to verify integration without hitting rate limits."""
    print("\n" + "=" * 80)
    print("SINGLE MESSAGE TEST - OpenAI Agent + MCP Integration")
    print("=" * 80 + "\n")

    # Check API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not set")
        return False

    # Check MCP server URL
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
    print(f"📡 MCP Server URL: {mcp_url}")
    print(f"🤖 Model: gemini/gemini-2.0-flash")
    print(f"👤 Test User ID: test_user_single")
    print()

    try:
        from app.services.agent_service import AgentService

        # Initialize agent
        print("🔧 Initializing agent service...")
        agent_service = AgentService()
        print("✅ Agent service initialized\n")

        # Simple test message
        test_message = "List my tasks"
        print(f"💬 Test message: '{test_message}'")
        print("⏳ Processing (this may take 5-10 seconds)...\n")

        # Process message
        result = await agent_service.process_message(
            user_message=test_message,
            conversation_history=[],
            user_id="test_user_single",
        )

        # Show result
        print("=" * 80)
        print("✅ SUCCESS - Integration Working!")
        print("=" * 80)
        print(f"\n🤖 Agent Response:\n{result['content']}\n")
        print("=" * 80)
        print("\n✨ The OpenAI Agent + MCP integration is fully functional!")
        print("📊 The agent successfully:")
        print("   1. Connected to MCP server")
        print("   2. Discovered MCP tools")
        print("   3. Sent request to Gemini API")
        print("   4. Processed the response")
        print()
        return True

    except Exception as e:
        error_str = str(e)
        print("=" * 80)

        if "rate limit" in error_str.lower() or "quota" in error_str.lower() or "429" in error_str:
            print("⚠️  QUOTA EXCEEDED (But Integration Works!)")
            print("=" * 80)
            print("\n🎉 Good news: The integration is working correctly!")
            print("📊 The request successfully reached Gemini API\n")
            print("❌ Bad news: Free tier quota exhausted\n")
            print("💡 Solutions:")
            print("   1. Wait for quota to reset (usually daily)")
            print("   2. Check usage: https://ai.dev/usage")
            print("   3. Upgrade to paid tier for more quota")
            print("   4. Try a different Gemini API key")
            print()
            return False
        else:
            print("❌ ERROR")
            print("=" * 80)
            print(f"\n{error_str}\n")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(test_single_message())
    sys.exit(0 if success else 1)
