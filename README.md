<<<<<<< HEAD
# issue-tracker
toy deployment
=======
# Issue Tracker

An application that uses the Qwen language model to analyze conversations and generate issue tickets automatically.

## Features

- Parse conversation JSON files
- Identify issues and problems mentioned in conversations using Qwen3-4B model
- Generate issue tickets with relevant information:
  - Title
  - Reporter
  - Description
  - Timestamp
  - Conversation snapshot

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Technical Implementation

The application uses the Qwen3-4B model loaded directly with Hugging Face's transformers library:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B")
```

The model analyzes conversation data and extracts structured issue information.

## Usage

### As a standalone script

Run the test script with a sample conversation:

```
python test_issue_tracker.py
```

### As an API

Start the FastAPI server:

```
python -m uvicorn app.main:app --reload
```

Then you can send a POST request to `http://localhost:8000/analyze` with a JSON file containing the conversation.

## Input Format

The application expects a JSON file with an array of message objects. Each message should have:

- `sender`: Name of the person
- `content`: Message content
- `timestamp` (optional): When the message was sent

Example:
```json
[
  {
    "sender": "Alice",
    "content": "I've found an issue with the login page.",
    "timestamp": "2023-06-15T10:30:00Z"
  }
]
```

## Output

The application returns an issue ticket with:
- Title: A clear title for the issue
- Reporter: Who raised the issue
- Description: Brief description
- Timestamp: When the issue was identified
- Conversation snapshot: Relevant messages 
>>>>>>> d79ccfa (toy deployment)
