"""
incase we want to give something for both the ollama and petalsbot
"""

class ChatbotInterface:
    async def generate_response(self, client, message, prompt):
        raise NotImplementedError("This method should be implemented by subclasses.")
