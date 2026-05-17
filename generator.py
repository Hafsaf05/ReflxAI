from groq import Groq
from dotenv import load_dotenv

import os

load_dotenv() 

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_code(task, memories=None):

    memory_context = ""

    if memories:
        memory_context = "\n".join(memories[0])

    prompt = f"""
You are a Python coding assistant.

Return ONLY executable Python code.

Previous related failures:
{memory_context}

Avoid repeating previous mistakes.

Task:
{task}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    code = response.choices[0].message.content

    code = code.replace("```python", "")
    code = code.replace("```", "")

    return code

def fix_code(old_code, error):

    prompt = f"""
The following Python code failed.

CODE:
{old_code}

ERROR:
{error}

Fix the code.

Return ONLY executable Python code.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    code = response.choices[0].message.content

    code = code.replace("```python", "")
    code = code.replace("```", "")

    return code