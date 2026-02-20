#!/usr/bin/env python3
"""
Script to check AgentCore Runtime deployment status.
"""

import json
import os
from bedrock_agentcore_starter_toolkit import Runtime

# Check if runtime config exists
if not os.path.exists('runtime_config.json'):
    print("❌ Error: Agent not deployed yet")
    print("Please run launch script first")
    exit(1)

# Load configuration files
with open('runtime_execution_role_config.json') as f:
    role_config = json.load(f)
with open('cognito_config.json') as f:
    cognito_config = json.load(f)

# Load .bedrock_agentcore.yaml to get agent name and entrypoint
if not os.path.exists('.bedrock_agentcore.yaml'):
    print("❌ Error: .bedrock_agentcore.yaml not found")
    print("Please run configure_runtime.py first")
    exit(1)

import yaml
with open('.bedrock_agentcore.yaml') as f:
    runtime_config = yaml.safe_load(f)

default_agent = runtime_config.get('default_agent')
agent_config = runtime_config.get('agents', {}).get(default_agent, {})
agent_name = agent_config.get('name')
entrypoint = agent_config.get('entrypoint')

# Initialize Runtime
runtime = Runtime()

# Build authorizer configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Configure runtime (to load existing configuration)
print("Loading runtime configuration...")
runtime.configure(
    entrypoint=entrypoint,
    agent_name=agent_name,
    execution_role=role_config["role_arn"],
    auto_create_ecr=True,
    memory_mode="NO_MEMORY",
    requirements_file="requirements.txt",
    region="us-west-2",
    authorizer_configuration=auth_config
)

# Check status
print("Checking runtime deployment status...")
status_response = runtime.status()

status = status_response.endpoint["status"]

print(f"\nAgent Status: {status}")
print(f"Endpoint Details: {json.dumps(status_response.endpoint, indent=2, default=str)}")

if status == "READY":
    print("\n" + "=" * 80)
    print("✓ Agent is READY to receive requests!")
    print("=" * 80)
    print("\nYou can now invoke your agent with:")
    print("  python invoke_agent.py")
elif status in ["CREATING", "UPDATING"]:
    print("\n" + "=" * 80)
    print("⏳ Agent deployment in progress...")
    print("=" * 80)
    print("\nThe deployment is still running. This is normal.")
    print("Run this script again in 1-2 minutes to check status.")
elif status in ["CREATE_FAILED", "UPDATE_FAILED"]:
    print("\n" + "=" * 80)
    print("✗ Agent deployment failed!")
    print("=" * 80)
    print("\nCheck CloudWatch logs for details:")
    print(f"  Log group: /aws/bedrock-agentcore/runtime/{agent_name}")
else:
    print(f"\n⚠ Unknown status: {status}")
