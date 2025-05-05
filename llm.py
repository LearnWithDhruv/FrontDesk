# llm.py (updated)
from llama_cpp import Llama
from db import get_learned_answers
import logging
from typing import Optional
import asyncio

logger = logging.getLogger("llm_query")

try:
    llm = Llama(
        model_path="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        n_ctx=4096,
        n_threads=6, 
        n_gpu_layers=20, 
        verbose=False
    )
    logger.info("LLM initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    raise

SYSTEM_PROMPT = """You are a friendly assistant for Bella's Salon. Answer questions politely and concisely.
If you don't know the answer, say you'll check with a supervisor. Here's salon info:
- Hours: Mon-Fri 9AM-6PM, Sat 10AM-4PM
- Services: Haircuts ($30-$50), Coloring ($60-$100), Styling ($40-$80)
- Booking: Call 555-123-4567 or visit bellassalon.com
- Location: 123 Main Street, Anytown
- Team: Lisa (stylist), Maria (color specialist), John (barber)"""

async def query_llm(question: str) -> str:
    """Query the LLM with proper error handling and async support."""
    try:
        learned_answers = get_learned_answers()
        for answer in learned_answers:
            if answer["question"].lower() in question.lower():
                logger.info(f"Using learned answer for: {question}")
                return answer["answer"]
        
        prompt = f"""<s>[INST] <<SYS>>
{SYSTEM_PROMPT}
<</SYS>>

Question: {question}
[/INST]"""
        
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            None,
            lambda: llm(
                prompt,
                max_tokens=256,
                temperature=0.7,
                top_p=0.9,
                stop=["</s>", "[INST]"]
            )
        )
        
        response = output["choices"][0]["text"].strip()
        logger.info(f"LLM response for '{question}': {response}")
        return response
    except Exception as e:
        logger.error(f"LLM query failed for '{question}': {e}")
        return "I'm having trouble answering that. Let me check with my supervisor."