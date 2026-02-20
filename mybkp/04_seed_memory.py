#!/usr/bin/env python3
"""
Script to seed AgentCore Memory with sample customer conversations.
"""

import json
import time

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

print(f"Using Memory ID: {memory_id}")
print(f"Region: us-west-2")
print(f"Customer ID: user_001")
print("="*80)

# Create memory client
memory_client = MemoryClient(region_name='us-west-2')

# Conversation 1: Customer mentions email preference and previous defective laptop return
print("\n📝 Storing Conversation 1: Email preference and defective laptop history")
messages_1 = [
    ("Hello, I need help with a return. I prefer to receive notifications via email.", "USER"),
    ("I'd be happy to help you with your return! I've noted your preference for email notifications. Could you please tell me more about the item you'd like to return?", "ASSISTANT"),
    ("I previously returned a defective laptop last month and want to make sure the process is the same.", "USER"),
    ("Yes, the return process is the same. For defective items like your laptop, you're eligible for a full refund including shipping costs. The return window for electronics is 30 days from purchase. Is this a new return you'd like to process?", "ASSISTANT")
]

memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_001",
    messages=messages_1
)

print(f"✓ Stored {len(messages_1)} messages from conversation 1")

# Small delay between conversations
time.sleep(2)

# Conversation 2: Customer asks about return windows for electronics
print("\n📝 Storing Conversation 2: Return windows for electronics inquiry")
messages_2 = [
    ("Hi, I have a question about return policies. What's the return window for electronics?", "USER"),
    ("Great question! For most electronics, the return window is 30 days from the date of purchase. This includes items like laptops, tablets, smartphones, and other electronic devices. The item should be in its original condition with all accessories and packaging.", "ASSISTANT"),
    ("And what if the item is defective? Is the window the same?", "USER"),
    ("Yes, the 30-day window applies to defective items as well. However, for defective items, you'll receive a full refund including any shipping costs you paid. We also waive any restocking fees for defective products.", "ASSISTANT"),
    ("That's helpful, thank you!", "USER"),
    ("You're welcome! If you need to process a return, just let me know and I'll guide you through the process.", "ASSISTANT")
]

memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_002",
    messages=messages_2
)

print(f"✓ Stored {len(messages_2)} messages from conversation 2")

# Wait for memory processing
print("\n" + "="*80)
print("⏳ Waiting 30 seconds for memory processing...")
print("   Memory strategies will extract:")
print("   - Preferences: Email notification preference")
print("   - Semantic: Previous defective laptop return, return window knowledge")
print("   - Summary: Conversation context and summaries")
print("="*80)

for i in range(30, 0, -5):
    print(f"   {i} seconds remaining...")
    time.sleep(5)

print("\n✓ Memory seeding complete!")
print(f"✓ Total conversations stored: 2")
print(f"✓ Total messages: {len(messages_1) + len(messages_2)}")
print(f"✓ Customer preferences and history are now available for retrieval")
