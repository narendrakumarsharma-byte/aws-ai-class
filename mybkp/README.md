# Returns & Refunds Agent

A Strands-based AI agent for handling customer returns and refunds inquiries with Amazon Bedrock AgentCore integration.

## Features

- **Returns Eligibility Checking**: Validates if items can be returned based on purchase date, category, and condition
- **Refund Calculations**: Calculates refund amounts including restocking fees and shipping costs
- **Policy Information**: Retrieves and formats return policy information from Knowledge Base
- **Memory Integration**: Stores customer interactions, preferences, and return history
- **Built-in Tools**: Current time and knowledge base retrieval

## Project Structure

```
.
├── 01_returns_refunds_agent.py    # Main Strands agent implementation
├── 02_test_agent.py               # Test suite for the agent
├── 03_create_memory.py            # Script to create AgentCore Memory
├── kb_config.json                 # Knowledge Base configuration
├── memory_config.json             # Memory configuration
└── README.md                      # This file
```

## Setup

### Prerequisites

- Python 3.8+
- AWS credentials configured
- Strands Agents SDK
- AgentCore Starter Toolkit

### Installation

```bash
pip install strands-agents bedrock-agentcore-starter-toolkit strands-tools
```

### Configuration

1. Set up Knowledge Base ID:
```bash
export KNOWLEDGE_BASE_ID=<your-kb-id>
```

2. Create memory resource:
```bash
python3 03_create_memory.py
```

## Usage

### Running the Agent

```bash
export KNOWLEDGE_BASE_ID=<your-kb-id>
python3 01_returns_refunds_agent.py
```

### Running Tests

```bash
python3 02_test_agent.py
```

## Custom Tools

### check_return_eligibility
Checks if an item can be returned based on:
- Purchase date
- Product category
- Item condition

### calculate_refund_amount
Calculates refund amount considering:
- Original price
- Item condition
- Return reason
- Shipping costs

### format_policy_response
Formats policy information in a customer-friendly way.

## Memory Strategies

The agent uses three memory strategies:

- **Summary**: Maintains conversation context and summaries
- **Preferences**: Captures customer preferences
- **Semantic**: Stores factual details about returns and interactions

## License

MIT
