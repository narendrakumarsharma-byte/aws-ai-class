#!/usr/bin/env python3
"""
Script to create Lambda function for order lookup.
This Lambda will be used as a Gateway target for the returns agent.
"""

import boto3
import json
import zipfile
import io
import time

# Configuration
REGION = "us-west-2"
FUNCTION_NAME = "OrderLookupFunction"
LAMBDA_ROLE_NAME = "OrderLookupLambdaRole"

print("="*80)
print("LAMBDA FUNCTION SETUP FOR ORDER LOOKUP")
print("="*80)
print(f"Region: {REGION}")
print(f"Function Name: {FUNCTION_NAME}")
print("="*80)

# Initialize clients
lambda_client = boto3.client('lambda', region_name=REGION)
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

try:
    # Get account ID
    account_id = sts_client.get_caller_identity()['Account']
    
    # Step 1: Create Lambda execution role
    print("\n📝 Step 1: Creating Lambda execution role...")
    
    lambda_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role_response = iam_client.create_role(
            RoleName=LAMBDA_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(lambda_trust_policy),
            Description="Execution role for OrderLookupFunction Lambda"
        )
        lambda_role_arn = role_response['Role']['Arn']
        print(f"✓ Role created: {lambda_role_arn}")
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print("✓ Basic execution policy attached")
        
        # Wait for role propagation
        print("⏳ Waiting 10 seconds for IAM propagation...")
        time.sleep(10)
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"⚠️  Role already exists, retrieving ARN...")
        role_response = iam_client.get_role(RoleName=LAMBDA_ROLE_NAME)
        lambda_role_arn = role_response['Role']['Arn']
        print(f"✓ Role ARN: {lambda_role_arn}")
    
    # Step 2: Create Lambda function code
    print(f"\n📝 Step 2: Creating Lambda function code...")
    
    lambda_code = '''
import json
from datetime import datetime, timedelta

# Mock order database
ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "product_name": "Dell XPS 15 Laptop",
        "purchase_date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        "amount": 1299.99,
        "category": "electronics",
        "condition": "unopened",
        "status": "delivered"
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "product_name": "iPhone 13 Pro",
        "purchase_date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
        "amount": 999.99,
        "category": "electronics",
        "condition": "opened",
        "status": "delivered"
    },
    "ORD-003": {
        "order_id": "ORD-003",
        "product_name": "Samsung Galaxy Tab S8",
        "purchase_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "amount": 649.99,
        "category": "electronics",
        "condition": "defective",
        "status": "delivered"
    }
}

def calculate_return_eligibility(order):
    """Calculate if order is eligible for return"""
    purchase_date = datetime.strptime(order["purchase_date"], "%Y-%m-%d")
    days_since_purchase = (datetime.now() - purchase_date).days
    
    # 30-day return window for electronics
    if days_since_purchase > 30:
        return {
            "eligible": False,
            "reason": f"Return window expired ({days_since_purchase} days since purchase)",
            "days_remaining": 0
        }
    
    # Defective items always eligible within window
    if order["condition"] == "defective":
        return {
            "eligible": True,
            "reason": "Defective item - full refund available",
            "days_remaining": 30 - days_since_purchase
        }
    
    return {
        "eligible": True,
        "reason": "Within return window",
        "days_remaining": 30 - days_since_purchase
    }

def lambda_handler(event, context):
    """
    Lambda handler for order lookup.
    Expected input: {"order_id": "ORD-001"}
    """
    try:
        # Extract order_id from event
        order_id = event.get("order_id", "").upper()
        
        if not order_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing order_id parameter"
                })
            }
        
        # Look up order
        order = ORDERS.get(order_id)
        
        if not order:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "error": f"Order {order_id} not found",
                    "available_orders": list(ORDERS.keys())
                })
            }
        
        # Calculate return eligibility
        eligibility = calculate_return_eligibility(order)
        
        # Build response
        response_data = {
            "order_id": order["order_id"],
            "product_name": order["product_name"],
            "purchase_date": order["purchase_date"],
            "amount": order["amount"],
            "category": order["category"],
            "condition": order["condition"],
            "status": order["status"],
            "return_eligibility": eligibility
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Internal error: {str(e)}"
            })
        }
'''
    
    # Create deployment package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    zip_buffer.seek(0)
    
    print("✓ Lambda code packaged")
    
    # Step 3: Create Lambda function
    print(f"\n📝 Step 3: Creating Lambda function '{FUNCTION_NAME}'...")
    
    try:
        function_response = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.12',
            Role=lambda_role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_buffer.read()},
            Description='Order lookup function for returns agent',
            Timeout=30,
            MemorySize=128
        )
        function_arn = function_response['FunctionArn']
        print(f"✓ Lambda function created: {function_arn}")
        
    except lambda_client.exceptions.ResourceConflictException:
        print(f"⚠️  Function already exists, updating code...")
        zip_buffer.seek(0)
        lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_buffer.read()
        )
        function_response = lambda_client.get_function(FunctionName=FUNCTION_NAME)
        function_arn = function_response['Configuration']['FunctionArn']
        print(f"✓ Lambda function updated: {function_arn}")
    
    # Step 4: Load gateway role ARN for permissions
    print(f"\n📝 Step 4: Adding gateway invoke permissions...")
    
    try:
        with open('gateway_role_config.json', 'r') as f:
            gateway_config = json.load(f)
            gateway_role_arn = gateway_config['role_arn']
            
        # Add permission for gateway to invoke Lambda
        try:
            lambda_client.add_permission(
                FunctionName=FUNCTION_NAME,
                StatementId='AllowGatewayInvoke',
                Action='lambda:InvokeFunction',
                Principal='bedrock-agentcore.amazonaws.com',
                SourceArn=f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:gateway/*"
            )
            print(f"✓ Gateway invoke permission added")
        except lambda_client.exceptions.ResourceConflictException:
            print(f"⚠️  Permission already exists")
            
    except FileNotFoundError:
        print(f"⚠️  gateway_role_config.json not found - skipping permission setup")
    
    # Step 5: Create tool schema for Gateway
    print(f"\n📝 Step 5: Creating tool schema...")
    
    tool_schema = [
        {
            "name": "lookup_order",
            "description": "Look up order details by order ID. Returns order information including product name, purchase date, amount, and return eligibility status.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to look up (e.g., ORD-001, ORD-002, ORD-003)"
                    }
                },
                "required": ["order_id"]
            }
        }
    ]
    
    print("✓ Tool schema created")
    
    # Step 6: Save configuration
    print(f"\n📝 Step 6: Saving configuration to lambda_config.json...")
    
    config = {
        "function_name": FUNCTION_NAME,
        "function_arn": function_arn,
        "lambda_role_arn": lambda_role_arn,
        "region": REGION,
        "tool_schema": tool_schema,
        "sample_orders": ["ORD-001", "ORD-002", "ORD-003"]
    }
    
    with open('lambda_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration saved to lambda_config.json")
    
    # Summary
    print("\n" + "="*80)
    print("✅ LAMBDA FUNCTION SETUP COMPLETE!")
    print("="*80)
    print(f"Function ARN: {function_arn}")
    print(f"Tool Name: lookup_order")
    print("\n📦 Sample Orders Available:")
    print("   - ORD-001: Dell XPS 15 Laptop (15 days old, unopened)")
    print("   - ORD-002: iPhone 13 Pro (45 days old, opened)")
    print("   - ORD-003: Samsung Galaxy Tab S8 (5 days old, defective)")
    print("\n💡 Next Steps:")
    print("   1. Create an AgentCore Gateway")
    print("   2. Add this Lambda as a gateway target")
    print("   3. Agent can use lookup_order tool to get order details")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
