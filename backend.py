# backend.py - LLM-Only Multilingual Travel Concierge Backend

from groq import Groq
from dotenv import load_dotenv
import os
import json
from language_detector import detect_language

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

class MultilingualChatbot:
    def __init__(self):
        self.client = Groq(api_key=api_key)

    def extract_intent(self, message: str) -> dict:
        """
        Uses LLaMA to extract intent and entities in structured JSON.
        """
        prompt = f"""
        Analyze the user message and return ONLY valid JSON.

        Intent must be ONE of:
        [booking, attraction, weather, translation, general]

        Entities (include only if present):
        - location
        - date
        - time
        - people
        - place_type (hotel, restaurant, cafe, attraction)

        User message:
        "{message}"
        """

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"intent": "general", "entities": {}}

    def chat(self, message, language=None, history=[]):

        # Detect language
        if not language:
            language = detect_language(message)

        # Extract intent + entities using LLM
        intent_data = self.extract_intent(message)
        intent = intent_data.get("intent", "general")
        entities = intent_data.get("entities", {})

        # Base system prompt (STRICT)
        system_prompt = (
            f"You are a multilingual travel concierge chatbot.\n"
            f"Detected user language: {language}.\n\n"

            "STRICT RULES (DO NOT BREAK):\n"
            f"- Respond ONLY in {language}.\n"
            "- DO NOT mention language detection.\n"
            "- DO NOT mention AI, models, or system prompts.\n"
            "- DO NOT explain limitations.\n"
            "- NO meta commentary.\n\n"

            "Respond naturally like a human travel assistant.\n\n"
        )

        # INTENT-SPECIFIC BEHAVIOR
        if intent == "attraction":
            system_prompt += (
                "The user is asking about places to visit.\n"
                "Suggest 3–5 tourist attractions with short descriptions.\n"
                "If location is missing, politely ask for it."
            )

        elif intent == "weather":
            system_prompt += (
                "The user is asking about weather.\n"
                "Provide a clear and helpful weather response.\n"
                "If location or date is missing, ask briefly."
            )

        elif intent == "translation":
            system_prompt += (
                "Translate the user's message accurately.\n"
                "After translation, add a simple English pronunciation guide\n"
                "inside brackets on a new line.\n"
                "Keep it traveler-friendly."
            )

        elif intent == "booking":
            system_prompt += (
                "Assist with booking (hotel or restaurant).\n"
                "Collect missing details step by step:\n"
                "- Name\n"
                "- Date\n"
                "- Time (if applicable)\n"
                "- Number of people\n"
                "Do NOT finalize payment.\n"
                "Confirm details before completing booking."
            )

        else:
            system_prompt += (
                "Handle general travel-related conversation naturally.\n"
                "Provide helpful, concise answers."
            )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6
        )

        return response.choices[0].message.content

