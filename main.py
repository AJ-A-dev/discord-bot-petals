import discord
import asyncio
# import requests
# import json

from rater import Rater
from message_history_handler import MessageHistoryHandler, MessageHistoryHandlerOllama
# from performane_tracker import PerformanceTracker
# import ollama
# from transformers import AutoTokenizer
# from petals import AutoDistributedModelForCausalLM
# from logger import performance_logger
# from chat_bots.petals_bot import PetalsBot
from chat_bots.ollama_bot import OllamaBot

"""
petals initialization
"""
# Choose any model available at https://health.petals.dev
model_name = "petals-team/StableBeluga2"  # This one is fine-tuned Llama 2 (70B)

# # Connect to a distributed network hosting model layers
# tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False, add_bos_token=False)
# model = AutoDistributedModelForCausalLM.from_pretrained(model_name)
# fake_token = tokenizer("^")["input_ids"][0]  # Workaround to make tokenizer.decode() keep leading spaces


"""
other functions
"""

# Returns line for line info in info.txt used for sensitive info
def getInfo():
    temp_list = []
    with open("info.txt", "r") as f:
        for linje in f:
            temp_list.append(linje.strip())
    return temp_list



"""
The discord client class
"""
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generation = True # can turn this off to stop all generating
        # Pass `self` to give the bot classes a reference to the client
        # self.petals_bot = PetalsBot(self, tokenizer, model, message_history_handler)
        self.ollama_7B_bot = OllamaBot(self, message_history_handler_ollama, domain, "Ollama 7B", "llama7B_with_context")
        self.ollama_70B_bot = OllamaBot(self, message_history_handler_ollama, domain, "Ollama 70B", "llama70B_with_context")
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == "👍":
            qa = answer_rater.find_question_answer_by_id(reaction.message.id)
            if qa:
                if reaction.message.id == qa.ollama_id:
                    qa.ollama_likes += 1
                else:
                    qa.petals_likes += 1
                answer_rater.store(qa)

    async def start_generation(self, message):
        global generation
        await asyncio.sleep(7)  # Wait for x seconds
        generation = True
        await message.channel.send("Generation can start again")

    async def run_chatbots(self, message, inputs_discord):
        # Schedule both tasks to run concurrently
        task1 = self.ollama_7B_bot.generate_response(message, inputs_discord)
        task2 = self.ollama_70B_bot.generate_response(message, inputs_discord)

        # Wait for both tasks to complete and retrieve their results
        ollama_7B_result, ollama_70B_result = await asyncio.gather(task1, task2)

        # Now ollama_result and petals_result contain the return values of run_ollama and run_petals respectively
        return ollama_7B_result, ollama_70B_result      

    async def run_ollama_7B(self, message, inputs_discord, name):
        return await self.ollama_7B_bot.generate_response(message, inputs_discord)

    async def run_ollama_70B(self, message, inputs_discord, name):
        return await self.ollama_70B_bot.generate_response(message, inputs_discord)
  
    async def edit_message(self, message, new_message, message_id, channel_id):
        # get the channel for the message
        channel = client.get_channel(channel_id)
        if channel:
            try:
                # Fetch the message with the specified ID
                target_message = await channel.fetch_message(message_id)
                await target_message.edit(content=new_message)
            except discord.NotFound as e:
                print(e)
            except discord.Forbidden as e:
                print(e)
            except discord.HTTPException as e:
                print(e)

    async def on_message(self, message):
        global generation
        # don't respond to ourselves 
        if message.author == self.user:
            return

        # users message
        inputs_discord = message.content

        if inputs_discord[0] == "!" or message.reference: # Main question part

            # Removes the !
            if inputs_discord[0] == "!":
                inputs_discord = inputs_discord[1:] 

            # running the actual functions
            ollama_response, petals_response = await self.run_chatbots(message, inputs_discord)
            
            await answer_rater.add_new_question_answer(message, ollama_response, petals_response, client)

        elif inputs_discord == "/breakall": # command to stop all generating
            generation = False
            await message.channel.send("All generation is stopped")
            while not generation:  # Wait until generation is allowed to start again
                await self.start_generation(message)

        else:
            await message.channel.send(
                "Im an Ollama-Discord bot! \nUse ! before your question to get me to answer.\nSee pinned message for more info."
            )

if __name__ == "__main__":
    """
    Meesage history handler and time object and rater
    """
    key_token, domain = getInfo()
    message_history_handler = MessageHistoryHandler()
    message_history_handler_ollama = MessageHistoryHandlerOllama()
    answer_rater = Rater()

    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(key_token)
