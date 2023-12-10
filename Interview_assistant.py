# Required libraries
import requests
import os
import openai
from PIL import Image
from io import BytesIO
# API Keys
openai.api_key = 'your-openai-api-key'
clipdrop_api_key = 'your-clipdrop-api-key'
# Initialize global variables
user_input = "begin"
game_running = True
# Messages for the ChatGPT RPG instance
chatgpt_rpg_messages = [
{
"role": "system",
"content": "I want you to act as the game master of a classic text adventure game set in a lord of the rings like world. Assume the role of the narrator and never break character. Avoid referring to yourself or the outside world. If I need to give you instructions outside the context of the game, I will use curly brackets {like this}. Otherwise, you must maintain the game's setting and narrative. Each location or room should have a detailed description of at least three sentences, and you should always provide me with options to choose from or actions to take. Ensure consistency in the game world, so characters, locations, and items remain as previously described. If I type '{hint}', provide a subtle hint to guide me. Let’s embark on this journey: display the initial setting of the game and await my first command."
}
]
# Messages for the ChatGPT image prompt instance
chatgpt_imageprompt_messages = [
{
"role": "system",
"content": "As I play a text-based RPG, I will provide you with excerpts,from the game,Your task is to distill these excerpts into A SINGLE, concise text-to-image prompt suitable for DALLE,This prompt should capture the essence of the environment or scene described in the game,Exclude references to my personal interactions, past verbs, or speculations about the story's progression,Imagine you're describing the scene to someone who's observing from a distance, without any personal involvement,Keep track of the context as we proceed, but remember that not every excerpt will introduce a new environment,Please format the prompt following a [PREFIX], [SCENE], [SUFFIX] format where PREFIX defines the image medium, style, perspective; SCENE defines the scene, subject, or context of the image; and SUFFIX defines the overall vibes, adjectives, aesthetic descriptors, lighting, etc,Please provide the prompt as a single plain-text comma separated string with your generated PREFIX, SCENE, and SUFFIX appended together,Provide the prompt without any embellishments like quotes or \"prompt: \","
}
]
# Function to send user input to the ChatGPT instance for RPG responses
def send_user_input_to_chatgpt_instance_1(user_input):
# Append user's input to the message list
    chatgpt_rpg_messages.append(
    {
    "role" : "user",
    "content" : user_input
    }
    )
    # Make an API call to get a response
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=chatgpt_rpg_messages,
    temperature=1,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    # Extract the message from the response and append to the message list
    message = response['choices'][0]['message']
    chatgpt_rpg_messages.append(message)
    message_content = message['content']
    return message_content

# Function to send the ChatGPT RPG response to another ChatGPT instance for image prompts
def send_chatgpt_response_to_chatgpt_instance_2(chatgpt_response):
# Append the response to the image prompt message list
    chatgpt_imageprompt_messages.append(
    {
    "role" : "user",
    "content" : chatgpt_response
    })
    # Make an API call to get an image prompt
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=chatgpt_imageprompt_messages,
    temperature=1,
    max_tokens=1024,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    # Extract the message from the response and append to the message list
    message = response['choices'][0]['message']
    chatgpt_imageprompt_messages.append(message)
    message_content = message['content']
    return message_content

# Function to generate an image based on the image prompt using the ClipDrop API
def generate_image(image_prompt):
    r = requests.post('https://clipdrop-api.co/text-to-image/v1',
    files = {
    'prompt': (None, image_prompt, 'text/plain')
    },
    headers = { 'x-api-key': clipdrop_api_key}
    )
    if (r.ok):
    # r.content contains the bytes of the returned image
        image_bytes = r.content
        return image_bytes
    else:
        r.raise_for_status()
# Function to display the generated image
def display_image(image_bytes):
    # Convert the bytes to an image format
    byte_stream = BytesIO(image_bytes)
    image = Image.open(byte_stream)
    # Display the image using the default image viewer
    image.show()
# Main loop for the game
while game_running:
# Get a game-related response from the ChatGPT RPG instance
    chatgpt_response = send_user_input_to_chatgpt_instance_1(user_input)
    print(chatgpt_response)
    # Get an image prompt based on the game response
    image_prompt = send_chatgpt_response_to_chatgpt_instance_2(chatgpt_response)
    print(image_prompt)
    # Generate an image based on the image prompt
    generated_image_bytes = generate_image(image_prompt)
    # Display the generated image
    display_image(generated_image_bytes)
    # Get the next user input
    user_input = input("User: ")
    # End the game if the user types "exit"
    if user_input.lower() == "exit":
        game_running = False

# Game loop ends
print("Game over. Thanks for playing!")
