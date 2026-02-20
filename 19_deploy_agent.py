#!/usr/bin/env python3
"""
Deploy agent to AgentCore Runtime with all configurations
"""
import json
from bedrock_agentcore_starter_toolkit import Runtime

# Load all configuration files
with open('memory_config.json', 'r') as f:
    memory_config = json.load(f)

with open('gateway_config.json', 'r') as f:
    gateway_config = json.load(f)

with open('cognito_config.json', 'r') as f:
    cognito_config = json.load(f)

with open('runtime_execution_role_config.json', 'r') as f:
    runtime_role_config = json.load(f)

with open('kb_config.json', 'r') as f:
    kb_config = json.load(f)

# Initialize Runtime
runtime = Runtime()

print("Configuring runtime deployment...")

# Configure authorizer with Cognito (tagged union structure)
authorizer_config = {
    'customJWTAuthorizer': {
        'allowedClients': [cognito_config['client_id']],
        'discoveryUrl': cognito_config['discovery_url']
    }
}

runtime.configure(
    entrypoint='17_runtime_agent.py',
    agent_name='returns_refunds_agent',
    execution_role=runtime_role_config['role_arn'],
    authorizer_configuration=authorizer_config,
    auto_create_ecr=True,
    memory_mode='NO_MEMORY',  # Memory is handled via environment variables
    requirements_file='requirements.txt',
    region='us-west-2'
)

print("Launching agent to AgentCore Runtime...")
print("This will take 5-10 minutes to build and deploy...")

# Set environment variables for all integrations
env_vars = {
    'MEMORY_ID': memory_config['memory_id'],
    'GATEWAY_URL': gateway_config['gateway_url'],
    'COGNITO_CLIENT_ID': cognito_config['client_id'],
    'COGNITO_CLIENT_SECRET': cognito_config['client_secret'],
    'COGNITO_DISCOVERY_URL': cognito_config['discovery_url'],
    'KNOWLEDGE_BASE_ID': kb_config['knowledge_base_id']
}

result = runtime.launch(
    env_vars=env_vars,
    auto_update_on_conflict=True
)

print(f"\nDeployment initiated!")
print(f"Agent ARN: {result.agent_arn}")
print(f"Status: {result.status}")

# Save agent ARN to runtime_config.json
runtime_config = {
    'agent_arn': result.agent_arn,
    'agent_name': 'returns_refunds_agent',
    'status': result.status,
    'region': 'us-west-2'
}

with open('runtime_config.json', 'w') as f:
    json.dump(runtime_config, f, indent=2)

print(f"\nConfiguration saved to runtime_config.json")
print("\nUse 20_check_runtime_status.py to monitor deployment progress")
