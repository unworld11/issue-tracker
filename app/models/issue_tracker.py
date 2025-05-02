from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
import re
import torch

class MessageSnapshot(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class IssueTicket(BaseModel):
    title: str = Field(..., description="The title of the issue")
    reporter: str = Field(..., description="The person who raised the issue")
    description: str = Field(..., description="Brief description of the issue")
    timestamp: str = Field(..., description="When the issue was identified")
    conversation_snapshot: List[MessageSnapshot] = Field(..., description="Relevant part of the conversation")

class QwenIssueTracker:
    def __init__(self, model_name="Qwen/Qwen3-4B"):
        # Allow custom Qwen code from the model repository
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
    
    def extract_issue(self, conversation: List[Dict[str, Any]]) -> IssueTicket:
        """
        Extract issues from a conversation using Qwen model
        
        Args:
            conversation: List of message dictionaries
            
        Returns:
            IssueTicket object with the extracted issue information
        """
        # Format conversation for the model input
        formatted_convo = self._format_conversation(conversation)
        
        # Create prompt for issue extraction
        prompt = self._create_issue_extraction_prompt(formatted_convo)
        
        # Generate response using the model
        messages = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(
            messages, 
            return_tensors="pt"
        )
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=1024,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the model's response after the prompt
        # The response format may vary, so extract the part after the prompt
        if "Issue information (JSON format):" in response:
            response = response.split("Issue information (JSON format):")[1].strip()
        
        # Parse the response to extract issue details
        issue_data = self._parse_response(response, conversation)
        
        return issue_data
    
    def _format_conversation(self, conversation: List[Dict[str, Any]]) -> str:
        """Format the conversation into a readable string"""
        formatted = ""
        for msg in conversation:
            speaker = msg.get("sender", "Unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            time_info = f" at {timestamp}" if timestamp else ""
            formatted += f"{speaker}{time_info}: {content}\n\n"
        return formatted
    
    def _create_issue_extraction_prompt(self, formatted_convo: str) -> str:
        """Create a prompt for the model to extract issues"""
        return f"""Analyze the following conversation and identify if there's an issue or problem mentioned. 
If there is an issue, extract the following information:
1. Title: A clear, concise title for the issue
2. Reporter: The person who reported or raised the issue
3. Description: A brief description of the issue
4. Timestamp: When the issue was mentioned (if available)
5. Relevant messages: The parts of the conversation related to this issue

Please format your response as JSON with keys: title, reporter, description, timestamp, and relevant_messages.

Conversation:
{formatted_convo}

Issue information (JSON format):"""
    
    def _parse_response(self, response: str, conversation: List[Dict[str, Any]]) -> IssueTicket:
        """Parse model response and create an IssueTicket"""
        # Try to parse the JSON response from the model
        try:
            # First, try to find a JSON block in the response using regex
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # Extract available fields from the parsed JSON
                title = data.get('title', "Issue detected in conversation")
                reporter = data.get('reporter', "Unknown")
                description = data.get('description', "An issue was identified in the conversation")
                timestamp = data.get('timestamp', '')
                
                # If no timestamp provided, try to find one from the conversation
                if not timestamp:
                    for msg in conversation:
                        if "timestamp" in msg:
                            timestamp = msg["timestamp"]
                            break
                
                # If still no timestamp, use current time
                if not timestamp:
                    timestamp = datetime.now().isoformat()
                
                # Create conversation snapshot
                snapshot = []
                relevant_messages = data.get('relevant_messages', [])
                
                # If model provided relevant messages, use those
                if relevant_messages:
                    for msg_info in relevant_messages:
                        if isinstance(msg_info, dict):
                            snapshot.append(MessageSnapshot(
                                role=msg_info.get('sender', "Unknown"),
                                content=msg_info.get('content', ""),
                                timestamp=msg_info.get('timestamp', "")
                            ))
                # Otherwise use all messages
                else:
                    for msg in conversation:
                        snapshot.append(MessageSnapshot(
                            role=msg.get('sender', "Unknown"),
                            content=msg.get('content', ""),
                            timestamp=msg.get('timestamp', "")
                        ))
                
                return IssueTicket(
                    title=title,
                    reporter=reporter,
                    description=description,
                    timestamp=timestamp,
                    conversation_snapshot=snapshot
                )
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed to parse model response as JSON: {e}")
            # Fall back to default ticket creation
        
        # Default fallback if JSON parsing fails
        # Find a likely reporter from the conversation
        reporter = "Unknown"
        for msg in conversation:
            if "issue" in msg.get("content", "").lower() or "problem" in msg.get("content", "").lower():
                reporter = msg.get("sender", "Unknown")
                break
        
        # Extract timestamp from the conversation
        timestamp = datetime.now().isoformat()
        for msg in conversation:
            if "timestamp" in msg:
                timestamp = msg["timestamp"]
                break
        
        # Create a snapshot of the conversation
        snapshot = []
        for msg in conversation:
            snapshot.append(MessageSnapshot(
                role=msg.get("sender", "Unknown"),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp", "")
            ))
        
        return IssueTicket(
            title="Issue detected in conversation",
            reporter=reporter,
            description="An issue was identified in the conversation",
            timestamp=timestamp,
            conversation_snapshot=snapshot
        )

# Initialize the tracker
issue_tracker = QwenIssueTracker()

# Function to use in API
def analyze_conversation(conversation: List[Dict[str, Any]]) -> IssueTicket:
    """Analyze a conversation and extract issues"""
    return issue_tracker.extract_issue(conversation) 