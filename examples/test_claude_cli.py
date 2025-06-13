#!/usr/bin/env python3
"""
Test script for Claude CLI integration with mlx-use.

This script tests the basic functionality of the Claude CLI wrapper
without running a full Agent workflow.
"""

import os
import sys
import asyncio
import logging

# Add the parent directory to the path so we can import mlx_use
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mlx_use import ClaudeCLI
from langchain_core.messages import HumanMessage, SystemMessage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_claude_cli():
    """Test basic Claude CLI functionality."""
    print("🧪 Testing basic Claude CLI functionality...")
    
    try:
        # Initialize Claude CLI
        claude = ClaudeCLI()
        
        # Test basic message
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello! Please respond with a simple greeting.")
        ]
        
        # Test basic generation
        result = await claude._agenerate(messages)
        response = result.generations[0].message.content
        
        print(f"✅ Basic test passed!")
        print(f"📝 Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


async def test_structured_output():
    """Test structured output functionality."""
    print("\n🧪 Testing structured output functionality...")
    
    try:
        # Initialize Claude CLI with structured output
        claude = ClaudeCLI()
        
        # Create a simple schema for testing
        from pydantic import BaseModel
        
        class TestOutput(BaseModel):
            message: str
            status: str
        
        structured_claude = claude.with_structured_output(TestOutput, include_raw=True)
        
        # Test structured output
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Please respond with a JSON object containing 'message' and 'status' fields.")
        ]
        
        result = await structured_claude.ainvoke(messages)
        
        print(f"✅ Structured output test passed!")
        print(f"📝 Parsed result: {result.get('parsed', 'No parsed result')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Structured output test failed: {e}")
        return False


async def test_agent_compatibility():
    """Test compatibility with Agent system."""
    print("\n🧪 Testing Agent system compatibility...")
    
    try:
        from mlx_use import Agent, Controller
        
        # Initialize Claude CLI
        claude = ClaudeCLI()
        
        # Create a simple agent
        controller = Controller()
        agent = Agent(
            task='Say hello and then call done',
            llm=claude,
            controller=controller,
            use_vision=False,
            max_actions_per_step=1,
            max_failures=2
        )
        
        print(f"✅ Agent initialization test passed!")
        print(f"📝 Agent created successfully with Claude CLI")
        
        # Note: We don't run the agent here to avoid actual system interaction
        # This test just verifies that the Agent can be created with Claude CLI
        
        return True
        
    except Exception as e:
        print(f"❌ Agent compatibility test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Claude CLI integration tests...\n")
    
    # Check if claude command is available
    try:
        import subprocess
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("⚠️  Warning: 'claude' command not found or not working.")
            print("   Make sure Claude Code CLI is installed and accessible.")
            print("   You can install it from: https://claude.ai/cli")
            return
    except Exception as e:
        print(f"⚠️  Warning: Could not check claude command: {e}")
        print("   Make sure Claude Code CLI is installed and accessible.")
        return
    
    print("✅ Claude CLI command is available\n")
    
    # Run tests
    tests = [
        test_basic_claude_cli,
        test_structured_output,
        test_agent_compatibility,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Claude CLI integration is working correctly.")
        print("\n💡 To use Claude CLI in your scripts:")
        print("   1. Set LLM_PROVIDER=claude-cli in your .env file")
        print("   2. Run any example script: python examples/try.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())
