"""
Test script to demonstrate the feedback loop between Idea Agent and Critic Agent
"""
import asyncio
import sys
sys.path.append('.')

from agents import run_all_agents


async def test_feedback_loop():
    """
    Test the feedback loop with a prompt that will likely require revision
    """
    print("=" * 70)
    print("🧪 TESTING AGENT FEEDBACK LOOP")
    print("=" * 70)
    
    # Use a prompt that will likely get rejected initially due to security concerns
    test_prompt = """
    Build a simple web application for storing user passwords and personal data.
    It should be fast and easy to deploy.
    """
    
    print(f"\n📝 Test Prompt:")
    print(f"   {test_prompt.strip()}")
    print(f"\nℹ️  This prompt intentionally lacks security considerations")
    print(f"   to trigger the feedback loop.\n")
    
    # Run with max 2 revisions to keep the test reasonable
    result = await run_all_agents(
        user_prompt=test_prompt,
        session_id="test_feedback_loop",
        max_revisions=1
    )
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    
    print(f"\n🔄 Revision Count: {result['revision_count']}")
    print(f"✅ Critic Approved: {result['critic_approved']}")
    
    print(f"\n💡 FINAL IDEA (after revisions):")
    print("-" * 70)
    print(result['idea_response'][:500] + "..." if len(result['idea_response']) > 500 else result['idea_response'])
    
    print(f"\n⚖️ CRITIC RESPONSE:")
    print("-" * 70)
    print(result['critic_response'][:500] + "..." if len(result['critic_response']) > 500 else result['critic_response'])
    
    print(f"\n🔨 BUILDER OUTPUT:")
    print("-" * 70)
    print(result['builder_response'][:500] + "..." if len(result['builder_response']) > 500 else result['builder_response'])
    
    print("\n" + "=" * 70)
    print("✅ Test completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_feedback_loop())
