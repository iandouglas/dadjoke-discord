import asyncio
import json
from pprint import PrettyPrinter
import time

from config import airtable_api_key, discord_token

from airtable.airtable import Airtable, AirtableError
import discord
from discord.ext import commands
from fastapi import FastAPI
import redis
import requests

from pydantic import BaseModel
from discord_webhook import AsyncDiscordWebhook


class Message(BaseModel):
    joke: str


# anonymous questions webhook
# https://discord.com/api/webhooks/1032162027931709500/h_ULfkY7QdMjZ9aUHsolWYHaGxz7IEObwBkxgMKF0p31DKIZDAQNMTXJ2aVSErWQIRPv

# dad jokes webhook
# https://discord.com/api/webhooks/1094254813522440272/S-oFIJF95ShDT8ixXoOXQar7TTPSxFTtFFJKXgAMD1_DTeJwi1VRe5QnW7dnOUsDIC4n

discord_webhook_url = "https://discord.com/api/webhooks/1094254813522440272/S-oFIJF95ShDT8ixXoOXQar7TTPSxFTtFFJKXgAMD1_DTeJwi1VRe5QnW7dnOUsDIC4n"
discord_channel_id = 934896606845763584
discord_guild_id = 934890732005777430 # server id

# connect to redis
rds = redis.Redis(host='localhost', port=6379, db=0)


def pprint(obj):
    pp = PrettyPrinter(indent=2, sort_dicts=True)
    pp.pprint(obj)

def ppprint(context, obj):
    print('-'*50)
    print(context)
    pprint(obj)
    print('-'*50)

def log(*args, **kw):
    print(f'{round(time.time(),2)} ', *args, **kw)

app = FastAPI()
dbot = commands.Bot(command_prefix='~', intents=None)
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

# connect to airtable, fetch jokes to put in redis
jokes = []


@dbot.event
async def on_ready():
    print(f'{dbot.user} has connected to Discord!')

@app.get('/jokes')
async def get_jokes(limit=1):
    return {'Hello': 'World'}

@app.post('/jokes')
async def create_joke(joke_payload: Message):
    global jokes
    # check if joke is already in redis/array

    ppprint('message', joke_payload)

    # if not, add to airtable and redis

    # create a new discord thread, post the joke
    guild = dbot.get_guild(discord_guild_id)
    channel = guild.get_channel(discord_channel_id)

    webhook = AsyncDiscordWebhook(url=discord_webhook_url, content=joke_payload.joke)
    response = await webhook.execute()
    resp = response.json()
    ppprint('resp', resp)

    return {"data":{"success": True, "joke": joke_payload.joke}}

async def run():
    try:
        await dbot.start(discord_token)
    except KeyboardInterrupt:
        await dbot.logout()

asyncio.create_task(run())
