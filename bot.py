import asyncio
import os
import discord
from discord import app_commands
from discord import Intents
from discord import Client
import logging
import argparse
import config
from process import charutil

import util

from discord import app_commands
from dotenv import load_dotenv
from observer import observer
from model import apiconfig
from interface import main
from process import history

from transformers import AutoProcessor, AutoModelForCausalLM 

load_dotenv()
discord_token: str | None = os.getenv("DISCORD_TOKEN")
if discord_token is None:
    raise RuntimeError("$DISCORD_TOKEN env variable is not set!")

client = config.client

# try:
#     config.florence = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-base-ft", trust_remote_code=True)
#     config.florence_processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base-ft", trust_remote_code=True)
# except:
#     print("Florence Not Downloaded... Don't worry about it~")
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    # Let owner known in the console that the bot is now running!
    print(f'Discord Bot is Loading...')

    # Oh right, I have logging...
    logging.basicConfig(level=logging.DEBUG)

    # Setup the Connection with API
    config.text_api = await apiconfig.set_api("text-default.json")
    await apiconfig.api_status_check(config.text_api["address"] + config.text_api["model"], headers=config.text_api["headers"])

    # Setup the 'tasks' that will be queued
    asyncio.create_task(apiconfig.send_to_model_queue())
    asyncio.create_task(apiconfig.send_to_stable_diffusion_queue())
    asyncio.create_task(apiconfig.send_to_discord_queue())

    # Command to Edit Message (You Right Click On It)
    edit_message = discord.app_commands.ContextMenu(
    name='Edit Message',
    callback=main.edit_message_context,
    type=discord.AppCommandType.message
    )

    # Command to Delete Message (You Right Click On It)
    delete_message = discord.app_commands.ContextMenu(
        name='Delete Message',
        callback=main.delete_message_context,
        type=discord.AppCommandType.message
    )
    
    # Initialize the Commands
    tree.add_command(edit_message)
    tree.add_command(delete_message)

    # I don't know how this work

    # async def character_info(interaction: discord.Interaction):
    #     characters = main.character_info()
    #     await interaction.response.send_message(characters)

    # character_info_command = app_commands.Command(
    #     name="character_info",
    #     description="Show a list of available characters",
    #     callback=character_info
    # )

    # tree.add_command(character_info_command)

    

    await tree.sync(guild=None)  
    print(f'Discord Bot is up and running.')



@client.event
async def on_message(message):

    if message is None:
        return
    
    # Trigger the Observer Behavior (The command that listens to Keyword)
    print("Message Get")
    await observer.bot_behavior(message, client)

# Run the Bot
client.run(discord_token)
