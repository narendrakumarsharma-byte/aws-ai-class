#!/usr/bin/env python3
"""
Script to test memory retrieval for user_001.
Retrieves memories from all namespaces to show what the agent remembers.
"""

import json

try:
    from bedrock_agentcore.memory import MemoryClient
except ImportError:
    print("✗ Error: bedrock_agentcore package not found")
    print("  Install with: pip install bedrock-agentcore")
    exit(1)

# Load memory_id from config
with open('memory_config.json') as f:
    config = json.load(f)
    memory_id = config['memory_id']

print("="*80)
print("AGENTCORE MEMORY RETRIEVAL TEST")
print("="*80)
print(f"Memory ID: {memory_id}")
print(f"Region: us-west-2")
print(f"Customer: user_001")
print("="*80)

# Create memory client
memory_client = MemoryClient(region_name='us-west-2')

def retrieve_and_display(namespace, query, description):
    """Retrieve and display memories from a specific namespace"""
    print(f"\n📋 {description}")
    print(f"   Namespace: {namespace}")
    print(f"   Query: '{query}'")
    print("-"*80)
    
    try:
        memories = memory_client.retrieve_memories(
            memory_id=memory_id,
            namespace=namespace,
            query=query,
            top_k=3
        )
        
        if memories:
            print(f"✓ Found {len(memories)} memory/memories\n")
            
            for i, memory in enumerate(memories, 1):
                print(f"Memory {i}:")
                content = memory.get('content', {})
                if isinstance(content, dict):
                    text = content.get('text', 'N/A')
                else:
                    text = str(content)
                print(f"  Content: {text}")
                
                relevance = memory.get('relevanceScore', 'N/A')
                if isinstance(relevance, (int, float)):
                    print(f"  Relevance Score: {relevance:.3f}")
                else:
                    print(f"  Relevance Score: {relevance}")
                print()
        else:
            print("⚠️  No memories found in this namespace")
            print("   (Memory extraction may still be processing)\n")
            
    except Exception as e:
        print(f"❌ Error: {e}\n")

# Test 1: Retrieve from preferences namespace
retrieve_and_display(
    namespace="app/user_001/preferences",
    query="customer preferences and communication",
    description="PREFERENCES - What does the customer prefer?"
)

# Test 2: Retrieve from semantic namespace
retrieve_and_display(
    namespace="app/user_001/semantic",
    query="previous returns and laptop",
    description="SEMANTIC - What facts do we know about this customer?"
)

# Test 3: Retrieve from summary namespace (session 001)
retrieve_and_display(
    namespace="app/user_001/session_001/summary",
    query="conversation summary",
    description="SUMMARY (Session 1) - What was discussed?"
)

# Test 4: Retrieve from summary namespace (session 002)
retrieve_and_display(
    namespace="app/user_001/session_002/summary",
    query="conversation summary",
    description="SUMMARY (Session 2) - What was discussed?"
)

print("="*80)
print("MEMORY TEST COMPLETE")
print("="*80)
print("\n💡 What the agent remembers about user_001:")
print("   - Communication preferences (email notifications)")
print("   - Return history (defective laptop)")
print("   - Knowledge about return policies")
print("   - Previous conversation context")
print()
