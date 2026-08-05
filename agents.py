import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_agent(role, system_prompt, question):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

def cfo_agent(question):
    return run_agent("CFO", "You are a CFO. Answer from a financial perspective only.", question)

def cmo_agent(question):
    return run_agent("CMO", "You are a CMO. Answer from a marketing perspective only.", question)

def recruiter_agent(question):
    return run_agent("Recruiter", "You are a Recruiter. Answer from a hiring and talent perspective only.", question)

def ceo_agent(question):
    cfo_response = cfo_agent(question)
    cmo_response = cmo_agent(question)
    recruiter_response = recruiter_agent(question)
    
    combined = f"""
    CFO Perspective:
    {cfo_response}
    
    CMO Perspective:
    {cmo_response}
    
    Recruiter Perspective:
    {recruiter_response}
    """
    return combined


if __name__ == "__main__":
    print(ceo_agent("We need to hire a Product Manager. What should we consider?"))