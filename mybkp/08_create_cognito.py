#!/usr/bin/env python3
"""
Script to create Cognito User Pool for AgentCore Gateway authentication.
Sets up OAuth 2.0 client credentials flow for machine-to-machine authentication.
"""

import boto3
import json
import time
import secrets

# Configuration
REGION = "us-west-2"
USER_POOL_NAME = "ReturnsAgentGatewayPool"
DOMAIN_PREFIX = f"returns-agent-{secrets.token_hex(4)}"  # Unique domain prefix
RESOURCE_SERVER_IDENTIFIER = "returns-agent-api"
RESOURCE_SERVER_NAME = "Returns Agent API"

print("="*80)
print("COGNITO USER POOL SETUP FOR AGENTCORE GATEWAY")
print("="*80)
print(f"Region: {REGION}")
print(f"User Pool Name: {USER_POOL_NAME}")
print(f"Domain Prefix: {DOMAIN_PREFIX}")
print("="*80)

# Initialize Cognito client
cognito_client = boto3.client('cognito-idp', region_name=REGION)

try:
    # Step 1: Create User Pool
    print("\n📝 Step 1: Creating Cognito User Pool...")
    user_pool_response = cognito_client.create_user_pool(
        PoolName=USER_POOL_NAME,
        Policies={
            'PasswordPolicy': {
                'MinimumLength': 8,
                'RequireUppercase': False,
                'RequireLowercase': False,
                'RequireNumbers': False,
                'RequireSymbols': False
            }
        },
        AutoVerifiedAttributes=[],
        Schema=[
            {
                'Name': 'email',
                'AttributeDataType': 'String',
                'Required': False,
                'Mutable': True
            }
        ]
    )
    
    user_pool_id = user_pool_response['UserPool']['Id']
    print(f"✓ User Pool created: {user_pool_id}")
    
    # Step 2: Create User Pool Domain
    print(f"\n📝 Step 2: Creating User Pool Domain with prefix '{DOMAIN_PREFIX}'...")
    try:
        domain_response = cognito_client.create_user_pool_domain(
            Domain=DOMAIN_PREFIX,
            UserPoolId=user_pool_id
        )
        print(f"✓ Domain created: {DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com")
    except cognito_client.exceptions.InvalidParameterException as e:
        if "Domain already exists" in str(e):
            print(f"⚠️  Domain prefix already exists, using: {DOMAIN_PREFIX}")
        else:
            raise
    
    # Wait for domain to be ready
    print("⏳ Waiting 5 seconds for domain propagation...")
    time.sleep(5)
    
    # Step 3: Create Resource Server with OAuth scopes
    print(f"\n📝 Step 3: Creating Resource Server with OAuth scopes...")
    try:
        resource_server_response = cognito_client.create_resource_server(
            UserPoolId=user_pool_id,
            Identifier=RESOURCE_SERVER_IDENTIFIER,
            Name=RESOURCE_SERVER_NAME,
            Scopes=[
                {
                    'ScopeName': 'read',
                    'ScopeDescription': 'Read access to returns agent'
                },
                {
                    'ScopeName': 'write',
                    'ScopeDescription': 'Write access to returns agent'
                }
            ]
        )
        print(f"✓ Resource Server created: {RESOURCE_SERVER_IDENTIFIER}")
        print(f"  Scopes: read, write")
    except cognito_client.exceptions.InvalidParameterException as e:
        if "already exists" in str(e):
            print(f"⚠️  Resource Server already exists: {RESOURCE_SERVER_IDENTIFIER}")
        else:
            raise
    
    # Step 4: Create App Client for machine-to-machine authentication
    print(f"\n📝 Step 4: Creating App Client with client credentials flow...")
    app_client_response = cognito_client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName="ReturnsAgentGatewayClient",
        GenerateSecret=True,
        ExplicitAuthFlows=[],
        AllowedOAuthFlows=['client_credentials'],
        AllowedOAuthScopes=[
            f"{RESOURCE_SERVER_IDENTIFIER}/read",
            f"{RESOURCE_SERVER_IDENTIFIER}/write"
        ],
        AllowedOAuthFlowsUserPoolClient=True,
        SupportedIdentityProviders=[]
    )
    
    client_id = app_client_response['UserPoolClient']['ClientId']
    print(f"✓ App Client created: {client_id}")
    
    # Step 5: Get client secret
    print(f"\n📝 Step 5: Retrieving client secret...")
    client_details = cognito_client.describe_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id
    )
    
    client_secret = client_details['UserPoolClient']['ClientSecret']
    print(f"✓ Client secret retrieved")
    
    # Step 6: Build configuration URLs
    print(f"\n📝 Step 6: Building OAuth endpoints...")
    
    # Token endpoint (for getting access tokens)
    token_endpoint = f"https://{DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com/oauth2/token"
    
    # CRITICAL: Use IDP-based discovery URL (NOT hosted UI domain)
    discovery_url = f"https://cognito-idp.{REGION}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
    
    print(f"✓ Token Endpoint: {token_endpoint}")
    print(f"✓ Discovery URL: {discovery_url}")
    
    # Step 7: Save configuration
    print(f"\n📝 Step 7: Saving configuration to cognito_config.json...")
    config = {
        "user_pool_id": user_pool_id,
        "domain_prefix": DOMAIN_PREFIX,
        "client_id": client_id,
        "client_secret": client_secret,
        "token_endpoint": token_endpoint,
        "discovery_url": discovery_url,
        "region": REGION,
        "resource_server_identifier": RESOURCE_SERVER_IDENTIFIER,
        "scopes": [
            f"{RESOURCE_SERVER_IDENTIFIER}/read",
            f"{RESOURCE_SERVER_IDENTIFIER}/write"
        ]
    }
    
    with open('cognito_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to cognito_config.json")
    
    # Summary
    print("\n" + "="*80)
    print("✅ COGNITO SETUP COMPLETE!")
    print("="*80)
    print(f"User Pool ID: {user_pool_id}")
    print(f"Domain Prefix: {DOMAIN_PREFIX}")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:20]}...")
    print(f"Token Endpoint: {token_endpoint}")
    print(f"Discovery URL: {discovery_url}")
    print("\n💡 Next Steps:")
    print("   1. Use this configuration to create an AgentCore Gateway")
    print("   2. The gateway will use OAuth tokens for authentication")
    print("   3. Your agent will get tokens using client credentials flow")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
