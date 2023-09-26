import asyncio
import httpx
from typing import Optional, List

import async_timeout
import gradio as gr
from loguru import logger
from pydantic import BaseModel

API_KEY = "OPENAI_API_KEY"


class Message(BaseModel):
    role: str
    content: str


async def make_completion(messages: List[Message], nb_retries: int = 3, delay: int = 30) -> Optional[str]:
    """
    Sends a request to the ChatGPT API to retrieve a response based on a list of previous messages.
    """
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        async with async_timeout.timeout(delay=delay):
            async with httpx.AsyncClient(headers=header) as aio_client:
                counter = 0
                keep_loop = True
                while keep_loop:
                    logger.debug(f"Chat/Completions Nb Retries : {counter}")
                    try:
                        resp = await aio_client.post(
                            url="https://localhost:8089/v1/chat/completions",
                            json={
                                "model": "gpt-3.5-turbo",
                                "messages": messages
                            }
                        )
                        logger.debug(f"Status Code : {resp.status_code}")
                        if resp.status_code == 200:
                            return resp.json()["choices"][0]["message"]["content"]
                        else:
                            logger.warning(resp.content)
                            keep_loop = False
                    except Exception as e:
                        logger.error(e)
                        counter = counter + 1
                        keep_loop = counter < nb_retries
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout {delay} seconds !")
    return None


async def predict(input, history):
    """
    Predict the response of the chatbot and complete a running list of chat history.
    """
    history.append({"role": "user", "content": input})
    response = await make_completion(history)
    history.append({"role": "assistant", "content": response})
    messages = [(history[i]["content"], history[i + 1]["content"]) for i in range(0, len(history) - 1, 2)]
    return messages, history


"""
Gradio Blocks low-level API that allows to create custom web applications (here our chat app)
"""
with gr.Blocks() as chatui:
    logger.info("Starting Demo...")
    chatbot = gr.Chatbot(label="WebGPT")
    state = gr.State([])
    with gr.Row():
        txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(container=False)
    txt.submit(predict, [txt, state], [chatbot, state])

chatui.launch(server_port=8090)
