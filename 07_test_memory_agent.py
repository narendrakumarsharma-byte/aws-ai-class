#!/usr/bin/env python3
"""
Test script for memory-enabled returns agent.
Tests if the agent recalls customer preferences and history.
"""

import os
import sys
import json
import importlib.util

# Load configuration files
print("="*80)
print("MEMORY-ENABLED AGENT TEST")
print("="*80)

# Load Memory ID from config
try:
    with open('memory_config.json') as f:
        memory_config = json.load(f)
        memory_id = memory_config.get('memory_id')
        print(f"✓ Loaded Memory ID: {memory_id}")
except FileNotFoundError:
    print("❌ Error: memory_config.json not found")
    sys.exit(1)

# Load Knowledge Base ID from config
try:
    with open('kb_config.json') as f:
        kb_config = json.load(f)
        kb_id = kb_config.get('knowledge_base_id')
        print(f"✓ Loaded Knowledge Base ID: {kb_id}")
except FileNotFoundError:
    print("❌ Error: kb_config.json not found")
    sys.exit(1)

# Set environment variables (backup in case config loading fails in agent)
os.environ["MEMORY_ID"] = memory_id
os.environ["KNOWLEDGE_BASE_ID"] = kb_id

print("="*80)

# Import run_agent from 06_memory_enabled_agent.py using importlib
spec = importlib.util.spec_from_file_location("memory_enabled_agent", "06_memory_enabled_agent.py")
agent_module = importlib.util.module_from_spec(spec)
sys.modules["memory_enabled_agent"] = agent_module
spec.loader.exec_module(agent_module)

run_agent = agent_module.run_agent

print("\n" + "="*80)
print("TEST: Memory Recall for user_001")
print("="*80)
print("\nCustomer: user_001")
print("Session: session_003 (new session)")
print("\nExpected Memory Recall:")
print("  - Email notification preference")
print("  - Previous defective laptop return")
print("  - Knowledge about return policies")
print("="*80)

# Test query
user_query = "Hi! I'm thinking about returning something. What do you remember about my preferences?"

print(f"\n📝 User Query:\n{user_query}\n")
print("-"*80)
print("🤖 Agent Response:\n")

try:
    # Run agent with user_001's actor_id to retrieve their memory
    response = run_agent(
        user_input=user_query,
        actor_id="user_001",
        session_id="session_003"
    )
    
    print(response)
    print("\n" + "-"*80)
    
    # Check if agent mentioned key memory elements
    print("\n" + "="*80)
    print("MEMORY RECALL VERIFICATION")
    print("="*80)
    
    response_lower = response.lower()
    
    checks = {
        "Email Preference": any(word in response_lower for word in ["email", "notification"]),
        "Previous Return": any(word in response_lower for word in ["laptop", "defective", "previous", "returned"]),
        "Personalization": any(word in response_lower for word in ["remember", "recall", "preference", "history"])
    }
    
    print("\nMemory Elements Detected:")
    for check_name, detected in checks.items():
        status = "✅" if detected else "❌"
        print(f"  {status} {check_name}: {'Mentioned' if detected else 'Not mentioned'}")
    
    all_passed = all(checks.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ SUCCESS: Agent successfully recalled customer memory!")
    else:
        print("⚠️  PARTIAL: Agent may not have recalled all memory elements")
    print("="*80)
    
    sys.exit(0 if all_passed else 1)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
