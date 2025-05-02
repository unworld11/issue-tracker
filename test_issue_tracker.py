import json
from app.models.issue_tracker import analyze_conversation

def main():
    # Load the sample conversation
    with open('sample_conversation.json', 'r') as f:
        conversation = json.load(f)
    
    # Analyze the conversation
    issue_ticket = analyze_conversation(conversation)
    
    # Print the issue ticket
    print("=== Issue Ticket ===")
    print(f"Title: {issue_ticket.title}")
    print(f"Reporter: {issue_ticket.reporter}")
    print(f"Description: {issue_ticket.description}")
    print(f"Timestamp: {issue_ticket.timestamp}")
    print("\nConversation Snapshot:")
    for msg in issue_ticket.conversation_snapshot:
        print(f"- {msg.role} ({msg.timestamp}): {msg.content}")

if __name__ == "__main__":
    main() 