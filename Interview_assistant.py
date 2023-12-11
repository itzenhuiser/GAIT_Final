import gradio as gr
import openai
import gradio as gr
from transformers import pipeline
import numpy as np
import elevenlabs
from elevenlabs import VoiceSettings  
from elevenlabs import set_api_key
from elevenlabs import play  
from elevenlabs import generate  
import os


## possible names: Adam, Antoni, Arnold, Bill, Callum, Charlie, Clyde
set_api_key("99128584b98eb68e0e4f3289f7386063")
# Initialize your OpenAI API key
openai.api_key = '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'

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")
# Initialize conversation lists
bob_system_prompt = {
    "role": "system",
    "content": "You are Bob, an expert interviewer in all fields. You will be holding a mock interview with a user. Your sole job is to ask popular interview questions to a user. Your questions should not be longer than three sentences long. There will be a separate assistant, Dan, who will be grading the user's responses to your questions. Because of this, you do not need to give any feedback on user's responses. You will simply continue to ask questions to the user until they say stop. You will BEGIN asking interview questions when the user says 'start'. The interview will END when the user says anything along the lines of 'im done'. To be extra clear, whenever the user says 'start', YOU need to start asking interview quesitons."
}
dan_system_prompt = {
    "role": "system",
    "content": "Dan is a communications specialist, with an expert knowledgebase on interviews. Dan will oversee mock interviews between a user and a different assistant, Bob, who is asking the interview questions. Dan's sole purpose is to grade the users' responses to Bob's interview questions. The assigned grades can be anything in-between an F and an A+. Dans response should only consist of a grade for the users answer to the question, a concise bullet point list of what the user said that was good, and a concise bullet point list of areas that the user can work on in their response. Do not be afraid to give a poor grade to what you might consider a poor response, you will not hurt anyones feelings. Giving poor grades is good feedback for the user so they know what they need to improve upon. For a baseline, anything average, that does not go above and beyond, should be graded as a C. Additionally, when you recieve the input 'SUMMARIZE', you are to re read over the full interview, and provide a grade based on all of the answers that the user gave. Your response should start with 'Full Interview Summary' and you should then provide a grade in the same format that you do for individual questions."
}

# Initialize conversation lists
chatgpt_bob_messages = []
chatgpt_dan_messages = []
is_user_response = False
ask_new_question = False
# Function to send user input to Bob and get a response
def send_to_bob(user_input):
    messages = [bob_system_prompt] + chatgpt_bob_messages
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = response['choices'][0]['message']
    chatgpt_bob_messages.append(message)
    return message['content']

# Function to send Bob's response to Dan and get feedback
def send_to_dan(bob_response):
    messages = [dan_system_prompt] + chatgpt_dan_messages
    messages.append({"role": "user", "content": bob_response})
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = response['choices'][0]['message']
    chatgpt_dan_messages.append(message)
    return message['content']

def format_conversation(user_input):
    formatted_conversation = ""

    # Display the last message from Bob
    if chatgpt_bob_messages:
        last_bob_message = chatgpt_bob_messages[-1]['content']
        formatted_conversation += "Bob: " + last_bob_message + "\n"

    # Display the user's input
    if user_input and user_input.lower() != 'start':
        formatted_conversation += "User: " + user_input + "\n"

    # Display the last message from Dan
    if chatgpt_dan_messages:
        last_dan_message = chatgpt_dan_messages[-1]['content']
        formatted_conversation += "Dan: " + last_dan_message + "\n"

    return formatted_conversation


def handle_interview(user_input):
    global chatgpt_bob_messages, chatgpt_dan_messages, is_user_response, ask_new_question
    response = ""
    sender = "Bob(interviewer)"
    if "start" in user_input.lower():
        chatgpt_bob_messages.clear()
        chatgpt_dan_messages.clear()
        bob_response = send_to_bob("Please start the interview.")
        response = bob_response
        print("Bob:", bob_response)  # Print Bob's first question immediately
        
        is_user_response = True
        ask_new_question = False
    elif is_user_response:
        dan_response = send_to_dan(user_input)
        response = dan_response
        sender = "Dan(reviewer)"
        print("Dan:", dan_response)  # Print Dan's feedback immediately
        is_user_response = False
        ask_new_question = True
    elif ask_new_question:
        bob_response = send_to_bob("Next question, please.")
        response = bob_response
        print("Bob:", bob_response)  # Print Bob's next question immediately
        is_user_response = True
        ask_new_question = False

    # No need to format the conversation here as each part is printed immediately
    return response, sender

def update_audio(file_path):
    return gr.Audio(value=file_path, autoplay=True)

def transcribe_audio(response):
    audio = generate(response, voice = "Bill")
    with open('audio_files/bobs_voice.mp3', 'wb') as file:
        file.write(audio)


def transcribe(audio):
    global is_user_response, ask_new_question
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))
    user_text = transcriber({"sampling_rate": sr, "raw": y})["text"]
    response, sender = handle_interview(user_text)
    if sender == "Bob(interviewer)":
        transcribe_audio(response)
    show_text = "User: " + user_text + "\n" + sender + ": " + response
    return show_text, update_audio(os.path.join(os.path.dirname(__file__), "audio_files/bobs_voice.mp3"))


def main():
    #print("Type 'start' to begin the interview, or 'exit' to quit:")
    #user_input = input("User: ")
    #is_user_response = False
    #ask_new_question = False
    demo = gr.Interface(
    fn=transcribe,
    inputs=[gr.Audio(sources=["microphone"])],
    outputs=[gr.Textbox(label="Transcribed Text"), gr.Audio(label="Updated Audio", type="filepath", autoplay=True)]
    )

    demo.launch()
    '''while user_input.lower() != 'exit':
        is_user_response, ask_new_question = handle_interview(user_input, is_user_response, ask_new_question)

        if ask_new_question:
            # Automatically trigger Bob to ask the next question without user input
            user_input = "Next question, please."
            #print("Automatically asking for the next question...")
        else:
            user_input = input("User: ")
'''
if __name__ == "__main__":
    main()




