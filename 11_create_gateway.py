#!/usr/bin/env python3
"""
Script to create AgentCore Gateway.

Prerequisites:
- cognito_config.json (from Cognito setup)
- gateway_role_config.json (from IAM role setup)
"""

import json
import boto3

print("="*80)
print("AGENTCORE GATEWAY SETUP")
print("="*80)

# Load configuration
print("\n📝 Loading configuration files...")
try:
    with open('cognito_config.json') as f:
        cognito_config = json.load(f)
    print(f"✓ Loaded Cognito config")
    print(f"  Client ID: {cognito_config['client_id']}")
    print(f"  Discovery URL: {cognito_config['discovery_url']}")
except FileNotFoundError:
    print("❌ Error: cognito_config.json not found")
    print("   Run 08_create_cognito.py first")
    exit(1)

try:
    with open('gateway_role_config.json') as f:
        role_config = json.load(f)
    print(f"✓ Loaded Gateway role config")
    print(f"  Role ARN: {role_config['role_arn']}")
except FileNotFoundError:
    print("❌ Error: gateway_role_config.json not found")
    print("   Run 09_create_gateway_role.py first")
    exit(1)

# Initialize AgentCore control plane client
print(f"\n📝 Initializing AgentCore client...")
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')
print("✓ Client initialized")

# Build auth configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Create gateway
print(f"\n📝 Creating AgentCore Gateway 'ReturnsRefundsGateway'...")
try:
    create_response = gateway_client.create_gateway(
        name="ReturnsRefundsGateway",
        roleArn=role_config["role_arn"],
        protocolType="MCP",
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration=auth_config,
        description="Gateway for Returns and Refunds Agent with order lookup capabilities"
    )
    
    # Extract gateway details
    gateway_id = create_response["gatewayId"]
    gateway_url = create_response["gatewayUrl"]
    gateway_arn = create_response["gatewayArn"]
    
    print(f"✓ Gateway created successfully!")
    print(f"  Gateway ID: {gateway_id}")
    print(f"  Gateway URL: {gateway_url}")
    print(f"  Gateway ARN: {gateway_arn}")
    
except Exception as e:
    print(f"❌ Error creating gateway: {str(e)}")
    exit(1)

# Save gateway config
print(f"\n📝 Saving configuration to gateway_config.json...")
config = {
    "id": gateway_id,
    "gateway_id": gateway_id,
    "gateway_url": gateway_url,
    "gateway_arn": gateway_arn,
    "name": "ReturnsRefundsGateway",
    "region": "us-west-2",
    "cognito_client_id": cognito_config["client_id"],
    "cognito_client_secret": cognito_config["client_secret"],
    "token_endpoint": cognito_config["token_endpoint"]
}

with open('gateway_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"✓ Configuration saved to gateway_config.json")

# Summary
print("\n" + "="*80)
print("✅ GATEWAY SETUP COMPLETE!")
print("="*80)
print(f"Gateway ID: {gateway_id}")
print(f"Gateway URL: {gateway_url}")
print(f"Authentication: OAuth 2.0 via Cognito")
print("\n💡 Next Steps:")
print("   1. Add Lambda function as a gateway target")
print("   2. Test gateway with OAuth token")
print("   3. Connect agent to gateway")
print("="*80)
