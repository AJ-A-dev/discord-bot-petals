"""
Meant to keep track of message histories so the bot have context of previous messages in a conversation
"""

# handler of message histories for petals
class MessageHistoryHandler:
    def __init__(self):
        self.message_histories = []


    # This is what the bot sees so it knows the context of the conversation
    def give_context_to_chatbot(self, message) -> str:
        obj = self.return_conversation_object(message)
        if obj: #if it found an object
            tmp_str = "context:\n"
            for conversation in obj.conversations:
                tmp_str += "Friendly AI" if conversation["is_robot"] else "Human"
                tmp_str += f": {conversation['content']}\n"
            return tmp_str
        return "" # returns an empty string if there is no context

    # returns the object if it is a reply to the otherwise none
    def return_conversation_object(self, message):
        if message.reference is not None: # is it a reply?
            for object in self.message_histories: # go through every object in message hist list
                for hist_message in object.conversations: # for every message in the objects
                    if hist_message["discord_id"] == message.reference.message_id:
                        return object
        return None
                    
    #looks for id in message_histories return object its in
    def add_message_to_handler(self, robot_message, human_message): 
        #TODO putt return_conversation_ovjet her istedet
        if human_message.reference is not None: # is it a reply?
            for object in self.message_histories: # go through every object in message hist list
                for hist_message in object.conversations: # for every message in the objects
                    if hist_message["discord_id"] == human_message.reference.message_id:
                        object.add_message(human_message, is_robot=False) # human message
                        object.add_message(robot_message, is_robot=True) # robot message
                        break
        else: # its not a reply
            tmp_message_history = MessageHistoryOllama()
            tmp_message_history.add_message(human_message, is_robot=False)
            tmp_message_history.add_message(robot_message, is_robot=True)
            self.message_histories.append(tmp_message_history)

#one specific message history 
class MessageHistory:
    def __init__(self, id=None):
        self.id = id
        self.conversations = []

    #will add a message to conversations as a dictionary
    def add_message(self, message, is_robot=False):
        tmp_dict = {
            "discord_id" : message.id,
            "is_robot" : is_robot,
            "content" : message.content[1:] if message.content[0] == "!" else message.content
        }

        self.conversations.append(tmp_dict)

"""
This is special cases for ollama api
"""

class MessageHistoryHandlerOllama(MessageHistoryHandler):
    def __init__(self):
        super().__init__()

    # message data is where it gets the context ids from
    def add_message_to_handler(self, robot_message, human_message, message_data): 
        if human_message.reference is not None: # is it a reply?
            for object in self.message_histories: # go through every object in message hist list
                for hist_message in object.conversations: # for every message in the objects
                    if hist_message["discord_id"] == human_message.reference.message_id:
                        object.add_message(human_message, message_data) # human message
                        object.add_message(robot_message, message_data) # robot message
                        break
        else: # its not a reply
            tmp_message_history = MessageHistoryOllama()
            tmp_message_history.add_message(human_message, message_data)
            tmp_message_history.add_message(robot_message, message_data, True)
            self.message_histories.append(tmp_message_history)

    # This is what the bot sees so it knows the context of the conversation
    def give_context_to_chatbot(self, message) -> str:
        obj = self.return_conversation_object(message)
        if obj: #if it found an object
            tmp_list = []
            for conversation in obj.conversations:
                tmp_list += conversation["content"]
            return tmp_list
        return  [] # returns an empty list if there is no context
    

# History-message special for ollama
class MessageHistoryOllama(MessageHistory):
    def __init__(self, id=None):
        super().__init__()
    

    def add_message(self, message, message_data, is_robot=False):
        if message_data["done"]:
            context = message_data["context"]
            tmp_dict = {
                "discord_id" : message.id,
                "content" : context if is_robot else []
            }
            self.conversations.append(tmp_dict)



if __name__ == "__main__":
    test = MessageHistoryHandlerOllama()
    test.test()
