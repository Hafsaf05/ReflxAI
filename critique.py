from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def critique_code(code):

    prompt = f"""
You are a senior Python reviewer.

Analyze this code for:

- inefficiencies
- bad practices
- missing edge cases
- redundancy
- optimization opportunities

Explain improvements clearly.

CODE:
{code}
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

    return response.choices[0].message.content


def optimize_code(code, critique):

    prompt = f"""
You are an expert Python optimizer.

Improve this code based on the critique.

CRITIQUE:
{critique}

CODE:
{code}

Return ONLY improved executable Python code.
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

    improved_code = response.choices[0].message.content

    improved_code = improved_code.replace("```python", "")
    improved_code = improved_code.replace("```", "")

    return improved_code