import asyncio
from typing import AsyncGenerator, List, Dict

from fastapi.logger import logger

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

    async def gen_counter_argument_stream(
        self,
        conversation_history: List[Dict],
    ) -> AsyncGenerator[str, None]:
        """
        Stream LLM response chunk by chunk
        """
        messages = self.format_debate_messages(conversation_history)

        try:
            buffer = ""
            async for chunk in self.llm.stream_chat_completion(messages=messages):
                content = chunk.get("choices", [{}])[0].get(
                    "delta", {}).get("content", "")
                if content:
                    buffer += content
                    if (any(punct in content for punct in ".!?\n") or
                            # Flush if buffer gets too large
                            len(buffer) > 100):
                        yield buffer
                        buffer = ""

            if buffer:
                yield buffer

        except Exception as e:
            logger.error(f"LLM streaming error: {str(e)}")
            yield f"[ERROR: {str(e)}]"
