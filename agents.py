import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"))

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

def ceo_agent(question, candidate_info):
    cfo_response = cfo_agent(question, candidate_info)
    cmo_response = cmo_agent(question, candidate_info)
    recruiter_response = recruiter_agent(question, candidate_info)

    if "agent failed:" in cfo_response:
        cfo_response = "CFO analysis unavailable."

    if "agent failed:" in cmo_response:
        cmo_response = "CMO analysis unavailable."

    if "agent failed:" in recruiter_response:
        recruiter_response = "Recruiter analysis unavailable."
    
    ceo_prompt = f"""
    You are the CEO making the final hiring decision.

    Candidate information: {candidate_info}

    You received the following independent assessments:

    CFO Perspective:
    {cfo_response}
    
    CMO Perspective:
    {cmo_response}
    
    Recruiter Perspective:
    {recruiter_response}

    Your job is to evaluate all three assessments and make the final decision.
    Do not blindly agree with the agents.
    Identify agreements and disagreements between them.
    Consider the candidate's strengths, weaknesses, risks, and potential value.

    Return your response using this structure:

    Overall assesment:
    Key strengths:
    Key concerns:
    Financial considerations:
    Marketing/business considerations:
    Hiring considerations:
    Final recommendation:
    Reasoning:

    The Final Recommendation must be exactly one of:
    - Hire
    - Conditional Hire
    - Do Not Hire
    """
    return run_agent("CEO", ceo_prompt, question)


if __name__ == "__main__":
    candidate_info = """
    Product Manager candidate:
    - 5 years of SaaS experience
    - Successfully launched 3 products
    - Increased user retention by 18%
    - High salary expectation
    - Limited experience in our target market
    """

    question = "Should we hire this Product Manager?"

    print(ceo_agent(question, candidate_info))