import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from system_prompt import ANTHROPIC_SYSTEM_PROMPT

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if ANTHROPIC_API_KEY is None:
    raise ValueError("ANTHROPIC_API_KEY not set")


def get_llm():
    return ChatAnthropic(
        model="claude-3-7-sonnet-20250219",
        temperature=0,
        max_tokens=1024,
        timeout=None,
        max_retries=2,
        api_key=ANTHROPIC_API_KEY,
    )


def refactor(code: str, llm: ChatAnthropic) -> str:

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                ANTHROPIC_SYSTEM_PROMPT,
            ),
            ("user", "<python_code>\n{PYTHON_CODE}\n</python_code>"),
        ]
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "PYTHON_CODE": code,
        }
    )
    return response.content
