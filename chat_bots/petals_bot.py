from chat_bots.chatbot_interface import ChatbotInterface
from performane_tracker import PerformanceTracker
from logger import performance_logger



class PetalsBot(ChatbotInterface):
    def __init__(self, client, tokenizer, model, message_history_handler):
        self.client = client
        self.message_history_handler = message_history_handler
        self.model = model
        self.tokenizer = tokenizer
        self.fake_token = tokenizer("^")["input_ids"][0]

        self.name = "Petals"

    async def generate_response(self, message, prompt):
        # initialize result
        name_of_bot_for_message = self.name + ":\n"
        result = str()

        new_message = await message.channel.send("🧠") # Initial message

        #context if there is any
        context = self.message_history_handler.give_context_to_chatbot(message)

        with self.model.inference_session(max_length=512) as sess:
            prefix = f"{context}Human: {prompt}\nFriendly AI:"
            prefix = self.tokenizer(prefix, return_tensors="pt")["input_ids"]

            tracker = PerformanceTracker() #initalize performance tracker
            while self.client.generation:

                tracker.update_delta_time() # the one changing
                outputs = self.model.generate(prefix, max_new_tokens=1, session=sess,
                                do_sample=True, temperature=0.9, top_p=0.6)
                
                result += self.tokenizer.decode([self.fake_token, outputs[0, -1].item()])[1:]  

                tracker.get_delta_and_from_initial_time() # get the delta time
                # stop check
                if "\n" in result or "</s>" in result or "^" in result:
                    result = result[:-1]
                    break
                
                prefix = None  # Prefix is passed only for the 1st token of the bot's response

            # calculate average tokenspeed
            tracker.get_average_token_speed()
            # final edit
            await self.client.edit_message(message, name_of_bot_for_message + result + f"\n{tracker.average_speed:.2g} avg tokens/s", new_message.id, new_message.channel.id) # no dots to signalize stop
            
            performance_logger.info("petals, tokens/s %s, initial time %ss", tracker.average_speed, tracker.pathfinding_time)

            channel = self.client.get_channel(message.channel.id)
            updated_human_message = await channel.fetch_message(message.id)
            updated_robot_message = await channel.fetch_message(new_message.id)
            self.message_history_handler.add_message_to_handler(updated_robot_message, updated_human_message)
            return new_message

