import json
from chat_bots.chatbot_interface import ChatbotInterface
from performane_tracker import PerformanceTracker
from logger import performance_logger
import aiohttp


class OllamaBot(ChatbotInterface):
    def __init__(self, client, message_history_handler, api_url, name, api_model):
        self.client = client
        self.message_history_handler = message_history_handler
        self.api_url = api_url
        self.api_model = api_model
        self.name = name

    async def generate_response(self, message, prompt):
        # initialize result
        name_of_bot_for_message = self.name + ":\n"
        result = str()
        new_message = await message.channel.send("🧠") # Initial message
        context = self.message_history_handler.give_context_to_chatbot(message)

        tracker = PerformanceTracker() #initalize performance tracker
        tracker.update_delta_time() # used only once in ollama so we can get the average speed, it does not work inside the stream
        tracker.update_delta_time() # used only once in ollama so we can get the average speed, it does not work inside the stream
        tracker.get_delta_and_from_initial_time()   



        headers = {
            'Content-Type': 'application/json',
        }

        data = json.dumps({
          "model": f"{self.api_model}",
          "prompt": f"{prompt}",
          "context": context
        })

        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.api_url}/api/generate', headers=headers, data=data) as response:
                if response.status == 200:
                    result = ""
                    async for line in response.content:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line:
                            message_data = json.loads(decoded_line)
                            result += message_data.get("response", "")
                            if len(result) > 2000:
                                break

                else:
                    print(f"Failed to receive streaming response for {self.api_model}")





        tracker.get_delta_and_from_initial_time() # get the delta time
        # calculate average tokenspeed
        tracker.get_rough_average_from_whole_time(result)
        # final edit (discord max is 2000 characters for a message) 
        if len(result) >= 1998:
            await self.client.edit_message(message, name_of_bot_for_message + result[:1998-len(name_of_bot_for_message)-16] + f"\n{tracker.average_speed:.2g} avg tokens/s", new_message.id, new_message.channel.id) # no dots to signalize stop
        else:
            await self.client.edit_message(message, name_of_bot_for_message + result + f"\n{tracker.average_speed:.2g} avg tokens/s", new_message.id, new_message.channel.id) # no dots to signalize stop
        
        performance_logger.info("%s, tokens/s %s, initial time %ss", self.name, tracker.average_speed, tracker.pathfinding_time)

        channel = self.client.get_channel(message.channel.id)
        updated_human_message = await channel.fetch_message(message.id)
        updated_robot_message = await channel.fetch_message(new_message.id)
        self.message_history_handler.add_message_to_handler(updated_robot_message, updated_human_message, message_data)
        return new_message
        # await response_message.edit(content=response)

