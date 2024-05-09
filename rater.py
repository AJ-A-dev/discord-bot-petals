import pandas as pd
import time
"""
Idea ha en liste av relevante meldinger, muligens lage et object for (spørsmål_id, petals_svar_id, ollama_svar_id) 
så etter en hvis tid se hvor mange "thumbs up" de forskjellige har og så lagrer det i en ?CSV?
"""

class Rater:
    def __init__(self):
        #TODO
        self.sleep_time = 10 # this is the time the rater will wait before looking for new/changes in likes
        self.list_of_question_answers = []
        self.path = "data/rating.csv"
        self.table = pd.read_csv(self.path) #question_id,ollama_id,petals_id,ollama_rating,petals_rating

    def find_question_answer_by_id(self, id):
        for qa in self.list_of_question_answers:
            if id in (qa.ollama_id, qa.petals_id):
                return qa
        return None

    def store(self, qa):
        new_row = {"question_id":qa.question_id, 
                   "ollama_id":qa.ollama_id, 
                   "petals_id": qa.petals_id,
                   "ollama_rating": qa.ollama_likes,
                   "petals_rating": qa.petals_likes
                   }
        row_exists = (self.table["question_id"] == new_row["question_id"]).any()

        if row_exists:
            # Find the index of the row to overwrite
            index_to_overwrite = self.table[self.table["question_id"] == new_row["question_id"]].index
            # Overwrite the row
            for key in new_row:
                self.table.loc[index_to_overwrite, key] = new_row[key]
        else:
            # If the row does not exist, append it
            new_row_df = pd.DataFrame([new_row])  # Wrap new_row in a list to form a single row DataFrame

            self.table = pd.concat([self.table, new_row_df], ignore_index=True)

        # print(self.table)
        self.table.to_csv(self.path, index=False)

    async def add_new_question_answer(self, question, ollama, petals, client):
        self.list_of_question_answers.append(QuestionAnswer(question, ollama, petals))
        await self.update_message_objects(client)

    def get_all_ids(self):
        tmp_list = []
        for qa in self.list_of_question_answers:
            tmp_list += qa.return_ids()
        return tmp_list
    
    async def update_message_objects(self, client):
        for qa in self.list_of_question_answers:

            channel =  client.get_channel(qa.question.channel.id)
            updated_ollama_message = await channel.fetch_message(qa.ollama_id)
            updated_petals_message = await channel.fetch_message(qa.petals_id)

            qa.ollama = updated_ollama_message
            qa.petals = updated_petals_message


#this is for the specific question asked
class QuestionAnswer:
    def __init__(self, question, ollama, petals):
        self.question = question
        self.ollama = ollama
        self.petals = petals

        self.question_id = question.id
        self.ollama_id = ollama.id
        self.petals_id = petals.id

        self.ollama_likes = 0
        self.petals_likes = 0

    def return_ids(self):
        return [self.question_id, self.ollama_id, self.petals_id]



if __name__ == "__main__":
    rater = Rater()
    print(rater.table) 

    rater.start_store()
    for x in range(100):
        time.sleep(1)
        print("doing main stuff")
