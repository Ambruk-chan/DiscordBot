# This is the function that supports the Observer
import discord
import re
import util


# For xtts2 TTS (now imported conditionally at the bottom of the script)
# import torch
# import torchaudio
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts


async def get_reply(message:discord.Message, client:discord.Client):
    reply = ""

    # If the message reference is not none, meaning someone is replying to a message
    if message.reference is not None:
        # Grab the message that's being replied to
        referenced_message = await message.channel.fetch_message(message.reference.message_id)

        # Verify that the author of the message is bot and that it has a reply
        if referenced_message.reference is not None and referenced_message.author == client.user:
            # Grab that other reply as well
            try:
                referenced_user_message = await message.channel.fetch_message(referenced_message.reference.message_id)
                # Process the fetched message as needed
            except discord.NotFound:
                # Handle the case where the message cannot be found
                print("Message not found or access denied.")
                return reply

            # If the author of the reply is not the same person as the initial user, we need this data
            if referenced_user_message.author != message.author:
                reply = referenced_user_message.author.display_name + \
                    ": " + referenced_user_message.clean_content + "\n"
                reply = reply + referenced_message.author.display_name + \
                    ": " + referenced_message.clean_content + "\n"
                reply = util.clean_user_message(reply)

                return reply

        # If the referenced message isn't from the bot, use it in the reply
        if referenced_message.author != client.user:
            reply = referenced_message.author.display_name + \
                ": " + referenced_message.clean_content + "\n"

            return reply

    return reply


def get_user_list(history):
    # Define the regex pattern
    pattern = r'(?<=\n)[\w-]+(?=:)'
    
    # Find all matches using the regex pattern
    matches = re.findall(pattern, history, flags=re.MULTILINE)
    
    # Convert the list of matches to a set to remove duplicates
    unique_usernames = [username for username in set(matches)]
    
    # Convert the set back to a sorted list (if sorting is needed)
    return sorted(list(unique_usernames))

def get_replied_user(reply):
    pattern = r'[\w-]+(?=:)'
    matches = re.findall(pattern, reply, flags=re.MULTILINE)
    
    # Convert the list of matches to a set to remove duplicates
    unique_usernames = [username for username in set(matches)]
    # Convert the set back to a sorted list (if sorting is needed)
    return sorted(list(unique_usernames))

