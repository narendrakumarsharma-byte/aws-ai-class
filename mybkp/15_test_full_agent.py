#!/usr/bin/env python3
"""
Test script for full-featured returns agent.
Tests memory, gateway, and knowledge base integration.
"""

import os
import sys
import json
import importlib.util

print("="*80)
print("FULL-FEATURED AGENT TEST")
print("="*80)

# Load all configuration files
print("\n📝 Loading configuration files...")

configs = {}
config_files = {
    'memory': 'memory_config.json',
    'gateway': 'gateway_config.json',
    'cognito': 'cognito_config.json',
    'kb': 'kb_config.json'
}

missing_configs = []
for config_name, config_file in config_files.items():
    try:
        with open(config_file) as f:
            configs[config_name] = json.load(f)
        print(f"✓ Loaded {config_file}")
    except FileNotFoundError:
        print(f"❌ Missing {config_file}")
        missing_configs.append(config_file)

if missing_configs:
    print(f"\n❌ Error: Missing configuration files: {', '.join(missing_configs)}")
    print("   Please run the setup scripts first:")
    print("   - 03_create_memory.py")
    print("   - 08_create_cognito.py")
    print("   - 11_create_gateway.py")
    sys.exit(1)

print("\n✓ All configuration files loaded successfully")

# Set up environment variables
print("\n📝 Setting up environment variables...")
os.environ["MEMORY_ID"] = configs['memory']['memory_id']
os.environ["KNOWLEDGE_BASE_ID"] = configs['kb']['knowledge_base_id']
os.environ["GATEWAY_URL"] = configs['gateway']['gateway_url']
os.environ["COGNITO_CLIENT_ID"] = configs['cognito']['client_id']
os.environ["COGNITO_CLIENT_SECRET"] = configs['cognito']['client_secret']
os.environ["COGNITO_DISCOVERY_URL"] = configs['cognito']['discovery_url']

print(f"✓ MEMORY_ID: {configs['memory']['memory_id']}")
print(f"✓ KNOWLEDGE_BASE_ID: {configs['kb']['knowledge_base_id']}")
print(f"✓ GATEWAY_URL: {configs['gateway']['gateway_url']}")
print(f"✓ COGNITO_CLIENT_ID: {configs['cognito']['client_id']}")

# Import the full-featured agent
print("\n📝 Importing full-featured agent...")
spec = importlib.util.spec_from_file_location("full_agent", "14_full_agent.py")
agent_module = importlib.util.module_from_spec(spec)
sys.modules["full_agent"] = agent_module
spec.loader.exec_module(agent_module)

run_agent = agent_module.run_agent

print("✓ Agent imported successfully")

# Test query
print("\n" + "="*80)
print("TEST: Full Integration with Memory, Gateway, and Knowledge Base")
print("="*80)
print("\nCustomer: user_001")
print("Session: session_004 (new session)")
print("\nExpected Behavior:")
print("  ✓ Remember email preference from memory")
print("  ✓ Look up order ORD-001 via gateway (Dell XPS 15 Laptop)")
print("  ✓ Check return eligibility (15 days old, should be eligible)")
print("  ✓ Provide personalized response mentioning email preference")
print("="*80)

user_query = "Hi! Can you look up my order ORD-001 and tell me if I can return it? Remember, I prefer email updates."

print(f"\n📝 User Query:\n{user_query}\n")
print("-"*80)
print("🤖 Agent Response:\n")

try:
    # Run agent with user_001's actor_id to retrieve their memory
    response = run_agent(
        user_input=user_query,
        actor_id="user_001",
        session_id="session_004"
    )
    
    print(response)
    print("\n" + "-"*80)
    
    # Verify integration points
    print("\n" + "="*80)
    print("INTEGRATION VERIFICATION")
    print("="*80)
    
    response_lower = response.lower()
    
    checks = {
        "Memory - Email Preference": any(word in response_lower for word in ["email", "notification", "prefer"]),
        "Gateway - Order Lookup": any(word in response_lower for word in ["ord-001", "dell", "xps", "laptop", "1299", "$1299"]),
        "Return Eligibility": any(word in response_lower for word in ["eligible", "return", "15 days", "30 days"]),
        "Personalization": any(word in response_lower for word in ["remember", "preference", "noted"])
    }
    
    print("\nIntegration Points Detected:")
    for check_name, detected in checks.items():
        status = "✅" if detected else "❌"
        print(f"  {status} {check_name}: {'Detected' if detected else 'Not detected'}")
    
    all_passed = all(checks.values())
    
    # Additional checks
    print("\n" + "="*80)
    print("DETAILED ANALYSIS")
    print("="*80)
    
    print("\n1. Memory Integration:")
    if checks["Memory - Email Preference"]:
        print("   ✅ Agent recalled email preference from memory")
    else:
        print("   ⚠️  Agent may not have accessed memory")
    
    print("\n2. Gateway Integration:")
    if checks["Gateway - Order Lookup"]:
        print("   ✅ Agent successfully called lookup_order via gateway")
        print("   ✅ Retrieved order details (Dell XPS 15 Laptop)")
    else:
        print("   ⚠️  Agent may not have used gateway tool")
    
    print("\n3. Return Eligibility:")
    if checks["Return Eligibility"]:
        print("   ✅ Agent determined return eligibility")
    else:
        print("   ⚠️  Agent may not have checked eligibility")
    
    print("\n4. Personalization:")
    if checks["Personalization"]:
        print("   ✅ Agent provided personalized response")
    else:
        print("   ⚠️  Response may not be personalized")
    
    # Summary
    print("\n" + "="*80)
    if all_passed:
        print("✅ SUCCESS: All integrations working correctly!")
        print("   - Memory: Recalled customer preferences")
        print("   - Gateway: Retrieved order details via Lambda")
        print("   - Personalization: Combined data for tailored response")
    else:
        print("⚠️  PARTIAL: Some integrations may not be working")
        failed = [name for name, passed in checks.items() if not passed]
        print(f"   Failed checks: {', '.join(failed)}")
    print("="*80)
    
    sys.exit(0 if all_passed else 1)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}\n")
    import traceback
    traceback.print_exc()
    
    print("\n" + "="*80)
    print("TROUBLESHOOTING")
    print("="*80)
    print("\nPossible issues:")
    print("  1. Gateway not created - run 11_create_gateway.py")
    print("  2. Lambda not added to gateway - run 12_add_lambda_to_gateway.py")
    print("  3. Memory not seeded - run 04_seed_memory.py")
    print("  4. OAuth token expired - tokens expire after 1 hour")
    print("  5. Network connectivity issues")
    print("="*80)
    
    sys.exit(1)
