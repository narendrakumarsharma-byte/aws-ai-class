#!/usr/bin/env python3
"""
Script to create IAM execution role for AgentCore Runtime.

This script creates an IAM role with comprehensive permissions for running
agents in AgentCore Runtime with Memory, Gateway, and Knowledge Base access.
"""

import json
import boto3
import time

# Configuration
REGION = "us-west-2"
ROLE_NAME = "ReturnsAgentRuntimeExecutionRole"
POLICY_NAME = "ReturnsAgentRuntimePolicy"

print("="*80)
print("IAM RUNTIME EXECUTION ROLE SETUP")
print("="*80)
print(f"Region: {REGION}")
print(f"Role Name: {ROLE_NAME}")
print(f"Policy Name: {POLICY_NAME}")
print("="*80)

# Create IAM client
iam_client = boto3.client('iam', region_name=REGION)
sts_client = boto3.client('sts', region_name=REGION)

try:
    # Get AWS account ID
    print("\n📝 Getting AWS Account ID...")
    account_id = sts_client.get_caller_identity()['Account']
    print(f"✓ Account ID: {account_id}")
    
    # Step 1: Define trust policy for bedrock-agentcore.amazonaws.com
    print(f"\n📝 Step 1: Creating IAM role with trust policy...")
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
            Description="Execution role for Returns Agent Runtime with Memory, Gateway, and KB access"
        )
        role_arn = role_response['Role']['Arn']
        print(f"✓ Role created: {ROLE_NAME}")
        print(f"✓ Role ARN: {role_arn}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"⚠️  Role already exists, retrieving ARN...")
        role_response = iam_client.get_role(RoleName=ROLE_NAME)
        role_arn = role_response['Role']['Arn']
        print(f"✓ Role ARN: {role_arn}")
    
    # Step 2: Create comprehensive permissions policy
    print(f"\n📝 Step 2: Creating permissions policy...")
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockModelAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            },
            {
                "Sid": "AgentCoreMemoryAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetMemory",
                    "bedrock-agentcore:CreateEvent",
                    "bedrock-agentcore:GetLastKTurns",
                    "bedrock-agentcore:RetrieveMemory",
                    "bedrock-agentcore:ListEvents",
                    "bedrock-agentcore:GetMemoryRecord",
                    "bedrock-agentcore:RetrieveMemoryRecords",
                    "bedrock-agentcore:ListMemoryRecords"
                ],
                "Resource": f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:memory/*"
            },
            {
                "Sid": "KnowledgeBaseAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agent:Retrieve"
                ],
                "Resource": f"arn:aws:bedrock:{REGION}:{account_id}:knowledge-base/*"
            },
            {
                "Sid": "CloudWatchLogsAccess",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams",
                    "logs:DescribeLogGroups"
                ],
                "Resource": [
                    f"arn:aws:logs:{REGION}:{account_id}:log-group:/aws/bedrock-agentcore/*",
                    f"arn:aws:logs:{REGION}:{account_id}:log-group:*"
                ]
            },
            {
                "Sid": "XRayAccess",
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                    "xray:GetSamplingRules",
                    "xray:GetSamplingTargets"
                ],
                "Resource": "*"
            },
            {
                "Sid": "GatewayAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:InvokeGateway",
                    "bedrock-agentcore:GetGateway",
                    "bedrock-agentcore:ListGatewayTargets"
                ],
                "Resource": f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:gateway/*"
            },
            {
                "Sid": "ECRAccess",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage"
                ],
                "Resource": "*"
            },
            {
                "Sid": "CloudWatchMetrics",
                "Effect": "Allow",
                "Action": "cloudwatch:PutMetricData",
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "cloudwatch:namespace": "bedrock-agentcore"
                    }
                }
            },
            {
                "Sid": "WorkloadIdentityAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
                ],
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:workload-identity-directory/default/workload-identity/*"
                ]
            }
        ]
    }
    
    try:
        policy_response = iam_client.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(permissions_policy),
            Description="Permissions for Returns Agent Runtime with Memory, Gateway, and KB"
        )
        policy_arn = policy_response['Policy']['Arn']
        print(f"✓ Policy created: {POLICY_NAME}")
        print(f"✓ Policy ARN: {policy_arn}")
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
    
    # Step 4: Wait for role to propagate
    print(f"\n📝 Step 4: Waiting for IAM propagation...")
    time.sleep(10)
    print(f"✓ IAM propagation complete")
    
    # Save configuration
    print(f"\n📝 Step 5: Saving configuration...")
    config = {
        "role_name": ROLE_NAME,
        "role_arn": role_arn,
        "policy_name": POLICY_NAME,
        "policy_arn": policy_arn,
        "region": REGION,
        "account_id": account_id
    }
    
    with open('runtime_execution_role_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to runtime_execution_role_config.json")
    
    # Summary
    print("\n" + "="*80)
    print("✅ RUNTIME EXECUTION ROLE SETUP COMPLETE!")
    print("="*80)
    print(f"Role ARN: {role_arn}")
    print(f"Policy ARN: {policy_arn}")
    print("\n📋 Permissions Granted:")
    print("   ✓ Bedrock - Invoke models (InvokeModel, InvokeModelWithResponseStream)")
    print("   ✓ Memory - Full access (GetMemory, CreateEvent, RetrieveMemory, etc.)")
    print("   ✓ Knowledge Base - Retrieve documents (bedrock-agent:Retrieve)")
    print("   ✓ Gateway - Invoke and list (InvokeGateway, GetGateway, ListGatewayTargets)")
    print("   ✓ CloudWatch Logs - Write and read logs")
    print("   ✓ X-Ray - Distributed tracing")
    print("   ✓ ECR - Pull container images")
    print("   ✓ CloudWatch Metrics - Performance monitoring")
    print("   ✓ Workload Identity - Secure credential management")
    print("\n💡 Next Steps:")
    print("   1. Use this role ARN for AgentCore Runtime deployment")
    print("   2. Configure runtime with memory, gateway, and KB IDs")
    print("   3. Deploy agent to runtime")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
