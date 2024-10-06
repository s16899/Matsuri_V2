import requests
import json

API_KEY = "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"
FILENAME = "scamcallcenter.txt"

# Load the context from the file
with open("contexts/scammer.txt", "r") as f:
    context = f.read()

# Function to save conversation history to a file
def save_conversation_to_file(conversation):
    with open(FILENAME, "a") as file:
        file.write(conversation + "\n")

# Function to read the previous conversation from the file
def read_conversation_from_file():
    try:
        with open(FILENAME, "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""

# Main loop
while True:
    user_input = input("User: ")

    # Read previous conversation from the file
    previous_conversation = read_conversation_from_file()

    # Prepare the message history for the API
    messages = [
        {
            "role": "system",
            "content": context
        },
        {
            "role": "user",
            "content": previous_conversation.strip() + f"\nUser: {user_input}\n"
        }
    ]
    
    # Send the request to the API
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "meta-llama/llama-3.2-3b-instruct:free",
            "messages": messages
        })
    )
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Get the assistant's message
        assistant_message = data['choices'][0]['message']['content']
        
        # Display the assistant's message
        print("AI: " + assistant_message)

        # Save the conversation to the file (both user input and AI response)
        save_conversation_to_file(f"User: {user_input}")
        save_conversation_to_file(f"AI: {assistant_message}")
        
    else:
        print(f"Error: {response.status_code}, {response.text}")