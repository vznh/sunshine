from twilio.rest import Client
from dotenv import load_dotenv
import os
from data import *
import asyncio

# Load environment variables for development
load_dotenv()

# Load API data
loop = asyncio.get_event_loop()
weather_data = loop.run_until_complete(get_current_weather("Milpitas"))
news_data=loop.run_until_complete(get_current_news())
canvas_data=loop.run_until_complete(get_assignments_due())

msg='''👋 hello! here's your daily update:\n\n'''
msg+=parse_weather(weather_data)
msg+="\n"
msg+=parse_news(news_data)
msg+="\n📖"
msg+=canvas_data

# General message func
client = Client(os.getenv("sid"), os.getenv("auth"))
message = client.messages.create(
    to=os.getenv('mine'),
    from_=os.getenv("num"),
    body=msg
)
print("Sent message with SID: " + message.sid)