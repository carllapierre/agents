from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_ENDPOINT = os.getenv('SLACK_ENDPOINT')

app = FastAPI()

class SlackEvent(BaseModel):
    type: str
    event: dict

def get_bot_user_id():
    url = f"{SLACK_ENDPOINT}/auth.test"
    headers = {"Authorization": "Bearer " + SLACK_BOT_TOKEN}
    response = requests.post(url, headers=headers).json()
    return response.get('user_id')

BOT_USER_ID = get_bot_user_id()

@app.post("/")
async def handle_slack_event(request: Request):
    body = await request.json()

    # Handle Slack URL verification challenge
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}

    event = SlackEvent(**body)
    
    if event.type == "event_callback":
        # Filter out messages from the bot itself
        if event.event.get("user") == BOT_USER_ID:
            print("Ignoring bot's own message.")
            return {"status": "ignored"}

        # Filter direct messages
        if event.event.get("channel_type") == "im":
            user = event.event.get("user")
            text = event.event.get("text")
            ts = event.event.get("ts")  # Timestamp of the original message

            print(f"User: {user}, Text: {text}, Timestamp: {ts}")

            # Process message
            response = process_message(text)

            print(f"Response: {response}")
            # Send response back to Slack
            post_message_to_slack(user, response, ts)
            
    return {"status": "ok"}

def process_message(text: str):
    response = requests.post("http://ai-agent:8004/inference", json={"prompt": text})
    return response.json().get("response")

def post_message_to_slack(user: str, text: str, thread_ts: str):
    url = f"{SLACK_ENDPOINT}/chat.postMessage"
    headers = {"Authorization": "Bearer " + SLACK_BOT_TOKEN}
    payload = {
        "channel": user,
        "text": text,
        "thread_ts": thread_ts
    }
    requests.post(url, headers=headers, json=payload)
