#!/usr/bin/env python3
"""
Script to add Lambda target to AgentCore Gateway.

Prerequisites:
- gateway_config.json (from gateway creation)
- lambda_config.json (from Lambda creation)
"""

import json
import boto3

print("="*80)
print("ADD LAMBDA TARGET TO GATEWAY")
print("="*80)

# Load gateway configuration
print("\n📝 Loading configuration files...")
try:
    with open('gateway_config.json') as f:
        gateway_config = json.load(f)
    print(f"✓ Loaded gateway config")
    print(f"  Gateway ID: {gateway_config['gateway_id']}")
except FileNotFoundError:
    print("❌ Error: gateway_config.json not found")
    print("   Run 11_create_gateway.py first")
    exit(1)

try:
    with open('lambda_config.json') as f:
        lambda_config = json.load(f)
    print(f"✓ Loaded Lambda config")
    print(f"  Function ARN: {lambda_config['function_arn']}")
    print(f"  Tool Schema: {len(lambda_config['tool_schema'])} tool(s)")
except FileNotFoundError:
    print("❌ Error: lambda_config.json not found")
    print("   Run 10_create_lambda.py first")
    exit(1)

# Initialize AgentCore control plane client
print(f"\n📝 Initializing AgentCore client...")
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')
print("✓ Client initialized")

# Extract Lambda details
lambda_arn = lambda_config["function_arn"]
tool_schema = lambda_config["tool_schema"]

# Build Lambda target configuration with MCP protocol
lambda_target_config = {
    "mcp": {
        "lambda": {
            "lambdaArn": lambda_arn,
            "toolSchema": {
                "inlinePayload": tool_schema
            }
        }
    }
}

# Use gateway's IAM role for Lambda invocation
credential_config = [{"credentialProviderType": "GATEWAY_IAM_ROLE"}]

# Create target
print(f"\n📝 Adding Lambda target 'OrderLookup' to gateway...")
print(f"  Gateway ID: {gateway_config['gateway_id']}")
print(f"  Target Name: OrderLookup")
print(f"  Lambda ARN: {lambda_arn}")
print(f"  Tool: {tool_schema[0]['name']}")

try:
    create_response = gateway_client.create_gateway_target(
        gatewayIdentifier=gateway_config["gateway_id"],
        name="OrderLookup",
        description="Lambda target for looking up order details and return eligibility",
        targetConfiguration=lambda_target_config,
        credentialProviderConfigurations=credential_config
    )
    
    target_id = create_response["targetId"]
    
    print(f"✓ Lambda target added successfully!")
    print(f"  Target ID: {target_id}")
    
except Exception as e:
    print(f"❌ Error adding target: {str(e)}")
    exit(1)

# Update gateway config with target info
print(f"\n📝 Updating gateway_config.json with target info...")
gateway_config["target_id"] = target_id
gateway_config["target_name"] = "OrderLookup"
gateway_config["lambda_arn"] = lambda_arn

with open('gateway_config.json', 'w') as f:
    json.dump(gateway_config, f, indent=2)

print(f"✓ Configuration updated")

# Summary
print("\n" + "="*80)
print("✅ LAMBDA TARGET ADDED TO GATEWAY!")
print("="*80)
print(f"Gateway ID: {gateway_config['gateway_id']}")
print(f"Target ID: {target_id}")
print(f"Target Name: OrderLookup")
print(f"Tool Available: lookup_order")
print("\n📋 Sample Orders:")
for order_id in lambda_config.get('sample_orders', []):
    print(f"   - {order_id}")
print("\n💡 Next Steps:")
print("   1. Test the gateway with an OAuth token")
print("   2. Connect your agent to the gateway")
print("   3. Agent can now use lookup_order tool")
print("="*80)
