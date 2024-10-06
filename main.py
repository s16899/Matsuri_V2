import requests
import json
import discord
from dotenv import load_dotenv
import os
import webserver

load_dotenv()

API_KEY = os.getenv('API_KEY')
FILENAME = "GF_Conversation.txt"

intents = discord.Intents.default()
intents.message_content = True  # Required to read the content of messages in DMs
bot = discord.Client(intents=intents)

# Load the context from the file
with open("contexts/cute_ai.txt", "r") as f:
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

@bot.event
async def on_ready():
    print("Bot is ready.")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if the message is a DM (not from a guild)
    if isinstance(message.channel, discord.DMChannel):
        user_input = message.content.strip()

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

        # Send the request to the AI API
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

            # Save the conversation (both user input and AI response) to the file
            save_conversation_to_file(f"User: {user_input}")
            save_conversation_to_file(f"AI: {assistant_message}")

            # Reply to the user in the DM
            await message.channel.send(assistant_message)
        else:
            await message.channel.send(f"Error: {response.status_code}, {response.text}")

webserver.keep_alive()
# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))