#!/usr/bin/env python3
"""
Script to list AgentCore Gateway targets.

Prerequisites:
- gateway_config.json (from gateway creation)
"""

import json
import boto3

print("="*80)
print("LIST GATEWAY TARGETS")
print("="*80)

# Load configuration
print("\n📝 Loading gateway configuration...")
try:
    with open('gateway_config.json') as f:
        gateway_config = json.load(f)
    print(f"✓ Loaded gateway config")
    print(f"  Gateway ID: {gateway_config['gateway_id']}")
    print(f"  Gateway URL: {gateway_config['gateway_url']}")
except FileNotFoundError:
    print("❌ Error: gateway_config.json not found")
    print("   Run 11_create_gateway.py first")
    exit(1)

# Initialize AgentCore control plane client
print(f"\n📝 Initializing AgentCore client...")
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')
print("✓ Client initialized")

# List targets
print(f"\n📝 Listing targets for gateway '{gateway_config.get('name', 'Unknown')}'...")
try:
    response = gateway_client.list_gateway_targets(
        gatewayIdentifier=gateway_config["gateway_id"]
    )
    
    targets = response.get("items", [])
    
    print(f"\n✓ Found {len(targets)} target(s)")
    
    if targets:
        print("\n" + "="*80)
        print("GATEWAY TARGETS")
        print("="*80)
        
        for i, target in enumerate(targets, 1):
            print(f"\n{i}. {target.get('name', 'N/A')}")
            print(f"   {'─'*76}")
            print(f"   Target ID:    {target.get('targetId', 'N/A')}")
            print(f"   Status:       {target.get('status', 'unknown')}")
            print(f"   Description:  {target.get('description', 'N/A')}")
            print(f"   Created:      {target.get('createdAt', 'N/A')}")
            print(f"   Updated:      {target.get('updatedAt', 'N/A')}")
            
            # Show target type if available
            if 'targetConfiguration' in target:
                config = target['targetConfiguration']
                if 'mcp' in config:
                    mcp_config = config['mcp']
                    if 'lambda' in mcp_config:
                        lambda_info = mcp_config['lambda']
                        print(f"   Type:         Lambda")
                        print(f"   Lambda ARN:   {lambda_info.get('lambdaArn', 'N/A')}")
                        
                        # Show tools if available
                        if 'toolSchema' in lambda_info:
                            tool_schema = lambda_info['toolSchema']
                            if 'inlinePayload' in tool_schema:
                                tools = tool_schema['inlinePayload']
                                print(f"   Tools:        {len(tools)} tool(s)")
                                for tool in tools:
                                    print(f"                 - {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')[:60]}...")
    else:
        print("\n⚠️  No targets found for this gateway")
        print("   Run 12_add_lambda_to_gateway.py to add a Lambda target")
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"❌ Error listing targets: {str(e)}")
    exit(1)

# Summary
print("\n💡 Gateway Status:")
print(f"   Gateway ID: {gateway_config['gateway_id']}")
print(f"   Total Targets: {len(targets)}")
print(f"   Active Tools: {sum(len(t.get('targetConfiguration', {}).get('mcp', {}).get('lambda', {}).get('toolSchema', {}).get('inlinePayload', [])) for t in targets)}")
print("="*80)
