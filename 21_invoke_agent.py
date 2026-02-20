#!/usr/bin/env python3
"""
Invoke the deployed AgentCore Runtime agent with authentication
"""
import json
import requests
import base64
from bedrock_agentcore_starter_toolkit import Runtime

# Load configuration files
with open('cognito_config.json', 'r') as f:
    cognito_config = json.load(f)

with open('runtime_execution_role_config.json', 'r') as f:
    runtime_role_config = json.load(f)

# Step 1: Get OAuth token from Cognito
print("Getting OAuth token from Cognito...")

# Prepare client credentials for Basic Auth
client_id = cognito_config['client_id']
client_secret = cognito_config['client_secret']
credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Request token using client credentials flow
token_endpoint = cognito_config['token_endpoint']
headers = {
    'Authorization': f'Basic {encoded_credentials}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Request all scopes
scopes = ' '.join(cognito_config['scopes'])
data = {
    'grant_type': 'client_credentials',
    'scope': scopes
}

response = requests.post(token_endpoint, headers=headers, data=data)

if response.status_code != 200:
    print(f"❌ Failed to get OAuth token: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

token_data = response.json()
bearer_token = token_data['access_token']
print(f"✅ OAuth token obtained successfully")

# Step 2: Initialize Runtime and configure
print("\nConfiguring runtime...")
runtime = Runtime()

# Build authorizer configuration
auth_config = {
    'customJWTAuthorizer': {
        'allowedClients': [cognito_config['client_id']],
        'discoveryUrl': cognito_config['discovery_url']
    }
}

runtime.configure(
    entrypoint='17_runtime_agent.py',
    agent_name='returns_refunds_agent',
    execution_role=runtime_role_config['role_arn'],
    authorizer_configuration=auth_config,
    auto_create_ecr=True,
    memory_mode='NO_MEMORY',
    requirements_file='requirements.txt',
    region='us-west-2'
)

# Step 3: Invoke the agent
print("\nInvoking agent...")
print("User: user_001")
print("Prompt: 'Can you look up my order ORD-001 and help me with a return?'")
print("\n" + "=" * 80)

payload = {
    'prompt': 'Can you look up my order ORD-001 and help me with a return?',
    'actor_id': 'user_001'
}

try:
    result = runtime.invoke(
        payload=payload,
        bearer_token=bearer_token
    )
    
    print("\n🤖 Agent Response:")
    print("=" * 80)
    
    # Handle different response structures
    if isinstance(result, dict):
        # Extract response text from dict
        if 'response' in result:
            print(result['response'])
        elif 'output' in result:
            print(result['output'])
        else:
            print(json.dumps(result, indent=2, default=str))
    elif hasattr(result, 'response'):
        print(result.response)
    else:
        print(str(result))
    
    print("=" * 80)
    
    # Display full result for debugging
    print(f"\nFull Response Structure:")
    print(json.dumps(result, indent=2, default=str) if isinstance(result, dict) else str(result))
    
    print(f"\n✅ Invocation completed successfully")
    
except Exception as e:
    print(f"\n❌ Error invoking agent: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
