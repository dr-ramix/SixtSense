from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pathlib import Path
import os


class SalesAgent:
    """
    AI brain: understands the user, updates preferences, and suggests
    what protections/addons are relevant. Does NOT choose specific cars.
    """

    def __init__(self):
        # LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.4,
            max_tokens=2000,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Parse JSON from the model
        self.parser = JsonOutputParser()

        # --- Load prompt.txt from same folder as this file ---
        base_dir = Path(__file__).resolve().parent
        prompt_path = base_dir / "prompt.txt"

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at: {prompt_path}")

        with prompt_path.open("r", encoding="utf-8") as file:
            self.system_prompt = file.read()

        # --- Build the prompt template ---
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "human",
                    "Booking info: {booking}\n"
                    "User profile: {profile}\n"
                    "Current session state: {state}\n"
                    "User message: {message}\n"
                    "Return ONLY a valid JSON object in the required format."
                ),
            ]
        )

    def run(self, booking, profile, state, message):
        """
        booking, profile, state can be dicts; message is the user text.
        """
        chain = self.prompt | self.llm | self.parser

        return chain.invoke(
            {
                "booking": booking,
                "profile": profile,
                "state": state,
                "message": message,
            }
        )
