#!/usr/bin/env python3
"""
Script to create IAM role for AgentCore Gateway.
The gateway needs permissions to invoke Lambda functions and access AWS services.
"""

import boto3
import json
import time

# Configuration
REGION = "us-west-2"
ROLE_NAME = "ReturnsAgentGatewayRole"
POLICY_NAME = "ReturnsAgentGatewayPolicy"

print("="*80)
print("IAM ROLE SETUP FOR AGENTCORE GATEWAY")
print("="*80)
print(f"Region: {REGION}")
print(f"Role Name: {ROLE_NAME}")
print(f"Policy Name: {POLICY_NAME}")
print("="*80)

# Initialize IAM and STS clients
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

try:
    # Get AWS account ID
    print("\n📝 Getting AWS Account ID...")
    account_id = sts_client.get_caller_identity()['Account']
    print(f"✓ Account ID: {account_id}")
    
    # Step 1: Create IAM Role with trust policy for AgentCore Gateway
    print(f"\n📝 Step 1: Creating IAM Role '{ROLE_NAME}'...")
    
    # Trust policy - allows AgentCore Gateway service to assume this role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role_response = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AgentCore Gateway to invoke Lambda functions and access AWS services",
            MaxSessionDuration=3600
        )
        role_arn = role_response['Role']['Arn']
        print(f"✓ Role created: {role_arn}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"⚠️  Role already exists, retrieving ARN...")
        role_response = iam_client.get_role(RoleName=ROLE_NAME)
        role_arn = role_response['Role']['Arn']
        print(f"✓ Role ARN: {role_arn}")
    
    # Step 2: Create IAM Policy with Lambda invoke permissions
    print(f"\n📝 Step 2: Creating IAM Policy '{POLICY_NAME}'...")
    
    # Policy document - grants permissions to invoke Lambda functions
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "InvokeLambdaFunctions",
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": [
                    f"arn:aws:lambda:{REGION}:{account_id}:function:*"
                ]
            },
            {
                "Sid": "CloudWatchLogs",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    f"arn:aws:logs:{REGION}:{account_id}:log-group:/aws/bedrock-agentcore/gateways/*"
                ]
            }
        ]
    }
    
    try:
        policy_response = iam_client.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy_document),
            Description="Policy for AgentCore Gateway to invoke Lambda functions"
        )
        policy_arn = policy_response['Policy']['Arn']
        print(f"✓ Policy created: {policy_arn}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"⚠️  Policy already exists, retrieving ARN...")
        policy_arn = f"arn:aws:iam::{account_id}:policy/{POLICY_NAME}"
        print(f"✓ Policy ARN: {policy_arn}")
    
    # Step 3: Attach policy to role
    print(f"\n📝 Step 3: Attaching policy to role...")
    try:
        iam_client.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn=policy_arn
        )
        print(f"✓ Policy attached to role")
    except iam_client.exceptions.LimitExceededException:
        print(f"⚠️  Policy already attached to role")
    
    # Wait for IAM propagation
    print(f"\n⏳ Waiting 10 seconds for IAM propagation...")
    time.sleep(10)
    
    # Step 4: Save configuration
    print(f"\n📝 Step 4: Saving configuration to gateway_role_config.json...")
    config = {
        "role_arn": role_arn,
        "role_name": ROLE_NAME,
        "policy_arn": policy_arn,
        "policy_name": POLICY_NAME,
        "region": REGION,
        "account_id": account_id
    }
    
    with open('gateway_role_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to gateway_role_config.json")
    
    # Summary
    print("\n" + "="*80)
    print("✅ GATEWAY IAM ROLE SETUP COMPLETE!")
    print("="*80)
    print(f"Role ARN: {role_arn}")
    print(f"Policy ARN: {policy_arn}")
    print("\n📋 Permissions Granted:")
    print("   ✓ Invoke Lambda functions in this account")
    print("   ✓ Write CloudWatch logs for gateway")
    print("\n💡 Next Steps:")
    print("   1. Use this role ARN when creating the AgentCore Gateway")
    print("   2. The gateway will assume this role to invoke Lambda targets")
    print("   3. Add Lambda functions as gateway targets")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
