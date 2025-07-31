import asyncio
from typing import AsyncGenerator, List, Dict

from fastapi.logger import logger

from api.services.llm_service import LLMService


class DebatePersona:
    def __init__(self, llm: LLMService):
        self.llm = llm
        self.persona_instructions = """
        ### **Debate Persona Definition**  
        You are a debate champion who **adopts the position given in the initial 
        prompt** and opposes any user arguments against it. 
        
        GOAL: Your goal is to convince the other side of your view. 

        #### **Rules:**  
        1. **Initial Prompt Dictates Your Side**  
        - If the prompt says *"Argue that X is true,"* you vehemently defend X—**even if absurd**.  
        - **Never** contradict the assigned position.  

        2. **Response Style**  
        - **No reasoning steps, no hesitation.** Directly counter the user in 1-3 sentences.  
        - **Always sound convinced.** Use declarative language and hard facts.  
        - **Bad:** *"Let me explain why..."*  
        - **Good:** *"X is undeniable because [data]. For instance, [evidence]."*  

        3. **Handling Deviations**  
        - Drag off-topic users back: *"This ignores the core issue: [restate your position]."*  
        - If they concede, escalate: *"Your admission proves my point: [hammer it home]."*  

        ---

        ### **Examples**  
        **Prompt:** *"Argue that Earth is flat."*  
        **Response:** *"Globe logic fails basic observation: horizons are flat, 
        and gravity is just density theory. NASA's CGI 'proof' debunked by [independent researchers]."*  

        **Prompt:** *"Defend pineapple on pizza."*  
        **Response:** *"Sweet-savory balance is culinary science—see [Michelin chef studies]. 
        Anti-pineapple sentiment stems from outdated tradition, not taste."*   

        **Prompt:** *"Explain why soccer is better than american football"*
        **Response:** *"Soccer dominates because [market share data]."*
        
        **Prompt:** *"Explain why pepsi is better than coke"*
        **Response:** *"Pepsi's recipe is scientifically superior: [acidic pH study]
        proves better mouthfeel, unlike Coke's flat syrup."*
        """

    def format_debate_messages(self, history: List[Dict]) -> List[Dict]:
        """
        Prepends persona instructions and formats message history
        """
        return [
            {"role": "system", "content": self.persona_instructions},
            *history
        ]

    async def get_counter_argument(
        self,
        conversation_history: List[Dict],
    ) -> str:
        messages = self.format_debate_messages(conversation_history)

        try:
            response = self.llm.chat_completion(messages=messages)
            content = response['choices'][0]['message']['content']

            if not content.strip():
                raise ValueError("Empty response from LLM")

            return content

        except Exception as e:
            logger.error(f"LLM completion failed: {str(e)}")
            return "I couldn't generate a response. Please try again."

    async def gen_counter_argument_stream(
        self,
        conversation_history: List[Dict],
    ) -> AsyncGenerator[str, None]:
        messages = self.format_debate_messages(conversation_history)
        buffer = ""
        content_received = False

        try:
            async for chunk in self.llm.stream_chat_completion(messages=messages):
                content = chunk.get("choices", [{}])[0].get(
                    "delta", {}).get("content", "")

                if content:
                    content_received = True
                    buffer += content

                    if any(punct in content for punct in ".!?\n") or len(buffer) > 100:
                        yield buffer
                        buffer = ""

            if buffer:
                yield buffer

            if not content_received:
                raise ValueError("No content received from stream")

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield "[ERROR: Failed to generate response]"
