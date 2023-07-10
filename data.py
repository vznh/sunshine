# Gathering data from different APIs
import aiohttp
import asyncio
from dotenv import load_dotenv
import os
from datetime import datetime
from math import floor

# Environment variables for development
load_dotenv()

# Starting with weather
'''
Notes:
calls should be made asynchronously, averages around 4.2 seconds per call for all APIs
'''
async def get_current_weather(city: str):
    api=os.getenv("owm")
    base_url="http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=imperial".format(city, api)
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as resp:
            data=await resp.json()
    return data


# News headline
async def get_current_news():
    api=os.getenv("wwn")
    base_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api}"
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as resp:
            data=await resp.json()
            articles=data
    return articles

# Canvas API
async def fetch_course_assignments(session, course_id, headers, base_url):
    async with session.get(f'{base_url}/courses/{course_id}/assignments', headers=headers) as resp:
        course_assignments = await resp.json()
    return course_assignments

async def get_assignments_due():
    msg:str=""
    api=os.getenv("canvas")
    headers = {'Authorization': f'Bearer {api}'}
    base_url = 'https://canvas.ucsc.edu/api/v1'

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{base_url}/courses?enrollment_state=active', headers=headers) as resp:
            courses = await resp.json()
   # print(f"Fetched {len(courses)} active courses.")

    # For each course, get the list of assignments
    assignments = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_course_assignments(session, course['id'], headers, base_url) for course in courses]
        all_assignments = await asyncio.gather(*tasks)

    for course_assignments in all_assignments:
    #    print(f"Fetched {len(course_assignments)} assignments from one of the courses.")
        assignments.extend(course_assignments)

   # print(f"Total assignments fetched: {len(assignments)}")

    # Filter out assignments that are already due or don't have a due date
    now = datetime.now()
    assignments = [a for a in assignments if a['due_at'] and datetime.strptime(a['due_at'], '%Y-%m-%dT%H:%M:%SZ') > now]
  #  print(f"Assignments due in the future: {len(assignments)}")

    # If there are no assignments, return a message
    if not assignments:
        msg+="No assignments due in the future."

    # Sort assignments by due date
    assignments.sort(key=lambda a: a['due_at'])

    # Format and return the assignments
    number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']  # Add more if needed
    for i, a in enumerate(assignments):
        due_date = datetime.strptime(a['due_at'], '%Y-%m-%dT%H:%M:%SZ')
        hours_until_due = (due_date - now).total_seconds() / 3600
        msg += f"{number_emojis[i]} {a['name']}: ⌛ {floor(hours_until_due)} hrs\n"

    return msg

# Parsing data and displaying
def parse_weather(data)->str:
    weather = data['weather'][0]['main'].lower()
    temp = data['main']['temp'] 
    feels_like = data['main']['feels_like']  
    wind_speed = data['wind']['speed'] 
    
    # Hashmap for emojis because if-blocks are satanic
    weather_emojis = {
        'clear': '☀️',
        'cloud': '☁️',
        'rain': '🌧️',
        'snow': '❄️',
    }
        
    weather_emoji = weather_emojis.get(weather, '🌫️')
    
    if wind_speed > 10:
        windy = 'yes'
    else:
        windy = 'no'

    message:str=""
    message+=f"⭐ today's forecast\n"
    message+=f"{weather_emoji} - {weather}\n"
    message+=f"🌡️ - {temp:.1f}°F\n"
    message+=f"😅 - {feels_like:.1f}°F\n"
    if windy == "yes": message+=f"🌬️ today\n"
    return message

def parse_news(data):
    articles = data['articles'][:3]  
    number_emojis = ['1️⃣', '2️⃣', '3️⃣']
    message = "🇺🇸 top news\n"
    for i, article in enumerate(articles):
        title = article['title']
        message += f"{number_emojis[i]} {title}\n\n"
    return message
