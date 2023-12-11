import gradio as gr
from transformers import pipeline
import numpy as np

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def transcribe(audio):
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))
    text = transcriber({"sampling_rate": sr, "raw": y})["text"]
    return text


demo = gr.Interface(
    transcribe,
    gr.Audio(sources=["microphone"]),
    outputs = "text",
)

demo.launch()