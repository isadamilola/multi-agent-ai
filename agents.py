import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"))

groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)
TOOL_MODEL = "openai/gpt-oss-20b"

def salary_fit(expected, budget):
    if not budget or budget <= 0:
        return {"error": "budget must be a positive number. Do not guess it."}
    gap = expected - budget
    return {"within_budget": gap <= 0, "gap": gap,
            "gap_percent": round(100 * gap / budget, 1)}

SALARY_TOOL = [{"type": "function", "function": {
    "name": "salary_fit",
    "description": "Compare a candidate's expected salary to the role budget.",
    "parameters": {"type": "object", "properties": {
        "expected": {"type": "integer", "description": "Expected annual salary, USD"},
        "budget": {"type": "integer", "description": "Role budget, USD"}},
        "required": ["expected", "budget"]}}}]

CEO_SCHEMA = {
    "name": "hiring_decision",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "recommendation": {"type": "string",
                               "enum": ["Hire", "Conditional Hire", "Do Not Hire"]},
            "key_strengths": {"type": "array", "items": {"type": "string"}},
            "key_concerns": {"type": "array", "items": {"type": "string"}},
            "reasoning": {"type": "string"},
        },
        "required": ["recommendation", "key_strengths", "key_concerns", "reasoning"],
        "additionalProperties": False,
    },
}

def ceo_decision(question, candidate_info, cfo, cmo, recruiter, expected=None, budget=None):
    prompt = f"""You are the CEO making the final hiring decision.
Candidate: {candidate_info}
CFO: {cfo}
CMO: {cmo}
Recruiter: {recruiter}
Do not blindly agree with the agents. Note where they disagree."""
    resp = groq_client.chat.completions.create(
        model=TOOL_MODEL,
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": question}],
        response_format={"type": "json_schema", "json_schema": CEO_SCHEMA},
    )
    decision = json.loads(resp.choices[0].message.content)

    if expected and budget:
        check = salary_fit(expected, budget)
        decision["salary_check"] = check
        if not check["within_budget"] and decision["recommendation"] == "Hire":
            decision["recommendation"] = "Conditional Hire"
            decision["guard_note"] = "Downgraded: expected salary is above budget."
    return decision


def cfo_agent_with_tools(
    question, candidate_info, expected=None, budget=None
):
    messages = [
        {
            "role": "system",
            "content": (
                "You are the CFO. Use the salary_fit tool to compare "
                "the candidate's expected salary with the role budget. "
                "Use supplied figures exactly. Never invent a budget."
            )
        },
        {
            "role": "user",
            "content": (
                f"{question}\n\n"
                f"Candidate information: {candidate_info}\n"
                f"Expected salary: {expected}\n"
                f"Role budget: {budget}"
            )
        }
    ]

    if expected is not None and budget is not None:
        resp = groq_client.chat.completions.create(
            model=TOOL_MODEL,
            messages=messages,
            tools=SALARY_TOOL,
            tool_choice="required"
        )
    else:
        resp = groq_client.chat.completions.create(
            model=TOOL_MODEL,
            messages=messages,
            tools=SALARY_TOOL
        )

    msg = resp.choices[0].message

    if not msg.tool_calls:
        return msg.content or "CFO analysis unavailable."

    messages.append(msg)

    for call in msg.tool_calls:
        if call.function.name != "salary_fit":
            raise ValueError(
                f"Unexpected tool: {call.function.name}"
            )

        args = json.loads(call.function.arguments)

        # Prefer values supplied directly by our application.
        if expected is not None:
            args["expected"] = expected
        if budget is not None:
            args["budget"] = budget

        print("TOOL CALLED:", call.function.name, args)

        result = salary_fit(**args)
        print("TOOL RESULT:", result)

        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": json.dumps(result)
        })

    final = groq_client.chat.completions.create(
        model=TOOL_MODEL,
        messages=messages
    )

    return final.choices[0].message.content or "CFO analysis unavailable."


def run_agent(role, system_prompt, question):
    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ])
        return response.choices[0].message.content
    except Exception as e:
        return f"{role} agent failed: {str(e)}"

def cfo_agent(question, candidate_info):
    system_prompt = f"""
You are the CFO of a company. Analyze the candidate from a financial and business perspective only.

Candidate information: {candidate_info}

Evaluate:
- Expected business value
- Hiring cost and salary
- Potential return on investment
- Financial risks
- Cost of not hiring the candidate

Structure your response as:
Strengths:
Concerns:
Financial Recommendation:
"""
    return run_agent("CFO", system_prompt, question)

def cmo_agent(question, candidate_info):
    system_prompt = f"""
You are the CMO of a company. Analyze the candidate from a marketing and business-growth perspective only.

Candidate information: {candidate_info}

Evaluate:
- Understanding of customers
- Product positioning
- Go-to-market experience
- Market knowledge
- Ability to collaborate with marketing and sales

Structure your response as:
Strengths:
Concerns:
Marketing Recommendation:
"""
    return run_agent("CMO", system_prompt, question)

def recruiter_agent(question, candidate_info):
    system_prompt = f"""
You are the company's Recruiter. Analyze the candidate from a hiring and talent perspective only.

Candidate information: {candidate_info}

Evaluate:
- Relevant experience
- SKills
- Leadership ability
- Team collaboration
- Cultural/team fit
- Hiring risks

Structure your response as:
Strengths:
Concerns:
Recruitment Recommendation:
"""
    return run_agent("Recruiter", system_prompt, question)

def ceo_agent(question, candidate_info, expected=None, budget=None):
    cfo_response = cfo_agent_with_tools(question, candidate_info, expected, budget)
    cmo_response = cmo_agent(question, candidate_info)
    recruiter_response = recruiter_agent(question, candidate_info)

    if "agent failed:" in cfo_response:
        cfo_response = "CFO analysis unavailable."

    if "agent failed:" in cmo_response:
        cmo_response = "CMO analysis unavailable."

    if "agent failed:" in recruiter_response:
        recruiter_response = "Recruiter analysis unavailable."
    
    return ceo_decision(question, candidate_info, cfo_response, cmo_response, recruiter_response, expected, budget)


if __name__ == "__main__":
    info = "Name: Jane\nExperience: 5 years SaaS\nSalary expectation: $120,000"
    print(json.dumps(ceo_agent("Should we hire this Product Manager?", info,
                               expected=120000, budget=100000), indent=2))