"""
Test script for returns_refunds_agent
Tests various customer service scenarios
"""

import os
import sys
import importlib.util

# Set environment variable for Knowledge Base
os.environ["KNOWLEDGE_BASE_ID"] = "XAJMXADZWS"

# Import run_agent from 01_returns_refunds_agent.py using importlib
spec = importlib.util.spec_from_file_location("returns_refunds_agent", "01_returns_refunds_agent.py")
agent_module = importlib.util.module_from_spec(spec)
sys.modules["returns_refunds_agent"] = agent_module
spec.loader.exec_module(agent_module)

run_agent = agent_module.run_agent

def print_test_header(test_num, description):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"TEST {test_num}: {description}")
    print("="*80)

def run_test(test_num, description, query):
    """Run a single test and display results"""
    print_test_header(test_num, description)
    print(f"\nQuery: {query}\n")
    print("-" * 80)
    
    try:
        response = run_agent(query)
        print(f"\nAgent Response:\n{response}\n")
        return True
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        return False

def main():
    """Run all test cases"""
    print("\n" + "🤖 RETURNS & REFUNDS AGENT TEST SUITE".center(80))
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Current time
    if run_test(1, "Current Time Check", "What time is it?"):
        tests_passed += 1
    
    # Test 2: Return eligibility check
    if run_test(2, "Return Eligibility Check", 
                "Can I return a laptop I purchased 25 days ago?"):
        tests_passed += 1
    
    # Test 3: Refund calculation
    if run_test(3, "Refund Calculation", 
                "Calculate my refund for a $500 item returned due to defect in like-new condition"):
        tests_passed += 1
    
    # Test 4: Policy explanation
    if run_test(4, "Policy Explanation", 
                "Explain the return policy for electronics in a simple way"):
        tests_passed += 1
    
    # Test 5: Knowledge base retrieval
    if run_test(5, "Knowledge Base Retrieval", 
                "Use the retrieve tool to search the knowledge base for 'Amazon return policy for electronics'"):
        tests_passed += 1
    
    # Summary
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {tests_passed}/{total_tests} tests passed")
    print("="*80 + "\n")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
