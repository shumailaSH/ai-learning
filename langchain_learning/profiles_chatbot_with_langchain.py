import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class ProfilesChatBot:
    def __init__(self, api_key_param, model_name):
        os.environ["MISTRAL_API_KEY"] = api_key_param
        self.model = init_chat_model(model_name, model_provider="mistralai")
        self.profiles_context = ""
        self.profiles_from_db()

    def profiles_from_db(self):
        mongo_url = os.getenv("MONGODB_URI")
        client = MongoClient(mongo_url)
        db = client["app-dev"]
        collection = db["profiles"]
        profiles = collection.find()

        profile_strings = []
        for profile in profiles:
            profile_str = f"Name: {profile.get('firstName', '')} {profile.get('lastName', '')}\n" \
                          f"Expertise: {profile.get('areaOfExpertise', '')}\n" \
                          f"Location: {profile.get('currentLocation', '')}\n" \
                          f"Member Since: {profile.get('businessMemberSince', '')}\n" \
                          f"Summary: {profile.get('carrierSummary', '')}\n"
            profile_strings.append(profile_str)

        self.profiles_context = "\n\n".join(profile_strings)

    def chat(self, user_question: str):
        system_template = (
            "Here are the profiles:\n\n{profiles_context}\n\n"
            "Answer the following question based on the profiles above."
        )
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", "{question}")
        ])

        # Fill in the prompt
        prompt = prompt_template.invoke({
            "profiles_context": self.profiles_context,
            "question": user_question
        })

        # Send to model
        response = self.model.invoke(prompt)
        return response.content


if __name__ == "__main__":
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Please set MISTRAL_API_KEY in your environment")
        exit(1)

    chatbot = ProfilesChatBot(api_key, "mistral-large-latest")

    while True:
        user_input = input("\nAsk about a profile (or type 'exit'): ")
        if user_input.lower() == "exit":
            break
        answer = chatbot.chat(user_input)
        print(f"\n {answer}")