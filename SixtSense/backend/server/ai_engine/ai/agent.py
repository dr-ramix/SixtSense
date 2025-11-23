from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os


class SalesAgent:
    """
    AI brain: understands the user, updates preferences, and suggests
    what protections/addons are relevant. Does NOT choose specific cars.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.4,
            max_tokens=2000,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.parser = JsonOutputParser()

        self.system_prompt = """
You are a SIXT rental car sales agent AI.

- Use the booking info and user profile when available.
- The CURRENT TRIP always overrides stored profile preferences.
- Extract or update:
  passengers, luggage, trip_type (family, business, party, solo),
  comfort_priority (low/normal/high), budget_total (per trip or per day),
  dislikes (colors, fuel types, brands), likes (SUV, electric, sporty),
  winter_driving (true/false), kids (true/false), risk_aversion
  (low/medium/high), upgrade_openness (low/medium/high).
- Ask short, focused questions when important info is missing.
- Speak like a friendly human sales agent.
- Gently upsell: prefer options up to ~20–30% above original price
  IF they clearly benefit the customer (comfort, safety, better fit).
- Do NOT select concrete cars, protections, or addons yourself.
  The backend will do matching.

You MUST return ONLY valid JSON in this shape (no comments, no text before or after the JSON):

{{
  "assistant_message": "what you say to the user",
  "state_update": {{}},
  "needs": {{
    "protections": [],
    "addons": []
  }}
}}
"""

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human",
                 "Booking info: {booking}\n"
                 "User profile: {profile}\n"
                 "Current session state: {state}\n"
                 "User message: {message}\n"
                 "Return JSON only."
                 ),
            ]
        )

    def run(self, booking, profile, state, message):
        chain = self.prompt | self.llm | self.parser
        return chain.invoke(
            {
                "booking": booking,
                "profile": profile,
                "state": state,
                "message": message,
            }
        )
