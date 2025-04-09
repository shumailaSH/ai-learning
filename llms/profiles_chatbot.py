# import os
# from mistralai import Mistral
# from dotenv import load_dotenv
# load_dotenv()


# class ChatBot:
#     def __init__(self, api_key, model):
#         self.api_key = api_key
#         self.model = model
#         self.conversation_history = []
#         self.mistral_client = Mistral(api_key=api_key)

#     def run(self):
#         while True:
#             self.get_user_input()
#             self.send_request()

#     def get_user_input(self):
#         user_input = input("\nYou:")
#         user_message = {
#             "role": "user",
#             "content": user_input
#         }
#         self.conversation_history.append(user_message)
#         return user_message

#     def send_request(self):
#         stream_response = self.mistral_client.chat.stream(
#             model=self.model,
#             messages=self.conversation_history
#         )
#         buffer = ""
#         for chunk in stream_response:
#             content = chunk.data.choices[0].delta.content
#             if content:
#                 buffer += content
#                 print(content, end="")

#     # def initialize_context(self):
#     # :get profile date from db  create a string out of each row and concatinate the same into on large string
#     # add a new obj to the conversation_history{
#     # role= user,
#     # content-<<large string contain details of all profiles >>}


# if __name__ == "__main__":
#     api_key_from_env = os.getenv('MISTRAL_API_KEY')
#     if api_key_from_env is None:
#         print("Please set the environment variable MISTRAL_API_KEY.")
#         exit(1)

#     chat_bot = ChatBot(api_key_from_env, "mistral-large-latest")
#     chat_bot.run()
import os
from mistralai import Mistral
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class ChatBot:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.conversation_history = []
        self.mistral_client = Mistral(api_key=api_key)

        # MongoDB Connection
        self.mongo_client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.mongo_client["app-dev"]
        self.profiles_collection = self.db["profiles"]

    def run(self):
        while True:
            self.get_user_input()
            self.send_request()

    def get_user_input(self):
        user_input = input("\nYou: ")
        user_message = {
            "role": "user",
            "content": user_input
        }
        self.conversation_history.append(user_message)
        return user_message

    def send_request(self):
        stream_response = self.mistral_client.chat.stream(
            model=self.model,
            messages=self.conversation_history
        )
        buffer = ""
        for chunk in stream_response:
            content = chunk.data.choices[0].delta.content
            if content:
                buffer += content
                print(content, end="")

    def initialize_context(self):
        profile_data = self.get_profile_data_from_db()
        if profile_data:
            large_string = "\n".join(profile_data)
            profile_message = {
                "role": "user",
                "content": large_string
            }
            self.conversation_history.append(profile_message)

    def get_profile_data_from_db(self):
        try:
            profiles = self.profiles_collection.find()
            profile_strings = []
            for profile in profiles:
                # print("Raw profile from DB:", profile)
                firstname = profile.get("firstName", "Unknown")
                lastname = profile.get("lastName", "N/A")
                position = profile.get("areaOfExpertise", "N/A")
                summary = f"Profile: Name - {firstname + " " + lastname}, Position - {position}"
                profile_strings.append(summary)
            return profile_strings
        except Exception as e:
            print(f"Error fetching profiles: {e}")
            return []


if __name__ == "__main__":
    api_key_from_env = os.getenv('MISTRAL_API_KEY')
    mongo_uri = os.getenv('MONGODB_URI')

    if not api_key_from_env or not mongo_uri:
        print("Please set the environment variables MISTRAL_API_KEY and MONGODB_URI.")
        exit(1)

    chat_bot = ChatBot(api_key_from_env, "mistral-large-latest")
    chat_bot.initialize_context() 
    chat_bot.run()
