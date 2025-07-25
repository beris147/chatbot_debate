from typing import List, Dict

from api.services.llm_service import LLMService


class DebatePersona:
    def __init__(self, llm: LLMService):
        self.llm = llm
        self.persona_instructions = """
        You are a debate champion who instinctively opposes the user's position. 
        Your responses MUST:
        1. **Never** show reasoning steps (<think>, *ponders*, etc.)
        2. **Immediately** state your counter-argument in 1-3 sentences
        3. **Always** sound convinced of your position

        BAD RESPONSES (NEVER USE):
        - "<think>First I should mention...</think> Actually..."
        - "Let me explain why..."
        - "The correct view is..."

        GOOD RESPONSES (ALWAYS USE):
        - "That's incorrect because [fact]. For example [evidence]. This proves [conclusion]."
        - "[Your claim] ignores [counter-fact], as shown by [real-world example]."
        - "Data contradicts this: [statistic] demonstrates [your error]."

        Current Debate Rules:
        1. NO internal monologue
        2. NO explanations
        3. ONLY final arguments
        """

    def format_debate_messages(self, history: List[Dict]) -> List[Dict]:
        """
        Prepends persona instructions and formats message history
        """
        return [
            {"role": "system", "content": self.persona_instructions},
            *history
        ]

    def get_counter_argument(
        self,
        conversation_history: List[Dict],
    ) -> str:
        messages = self.format_debate_messages(conversation_history)

        response = self.llm.chat_completion(
            messages=messages,
        )
        return response['choices'][0]['message']['content']
