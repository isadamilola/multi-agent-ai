import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1")
MODEL = "openai/gpt-oss-20b"

def salary_fit(expected, budget):
    gap = expected - budget
    return {"within_budget": gap <= 0, "gap": gap,
            "gap_percent": round(100 * gap / budget, 1)if budget else None}

tools = [{"type": "function", "function": {
    "name": "salary_fit",
    "description": "Compare a candidate's expected salary to the role budget.",
    "parameters": {"type": "object", "properties": {
        "expected": {"type": "integer", "description": "Expected annual salary, USD"},
        "budget": {"type": "integer", "description": "Role budget, USD"}},
        "required": ["expected", "budget"]}}}]

messages = [{"role": "user", "content":
    "Candidate expects $120,000. Our budget is $100,000. Is salary a problem?"}]

resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
msg = resp.choices[0].message

if msg.tool_calls:
    messages.append(msg)
    for call in msg.tool_calls:
        result = salary_fit(**json.loads(call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": call.id,
                         "content": json.dumps(result)})
    final = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    print(final.choices[0].message.content)
else:
    print("No tool call:", msg.content)