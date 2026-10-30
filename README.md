# Multi-Agent AI Hiring System

A Flask API where a CFO, a CMO and a Recruiter agent each assess a candidate, and a CEO agent returns a structured hiring decision. The CFO uses tool calling for the salary check, and a rule in code stops the final verdict from contradicting it.

## How it works

```
Request (question, candidate_info, role_budget)
        |
   Flask API  (validates input)
        |
   ceo_agent
   |-- CFO agent        Groq, calls the salary_fit tool
   |-- CMO agent        OpenRouter
   '-- Recruiter agent  OpenRouter
        |
   CEO decision         Groq, output constrained by a JSON schema
        |
   Salary guard         plain Python rule
        |
   JSON response
```

## Features

- **Tool calling.** The CFO calls a `salary_fit` function instead of doing the arithmetic in text. The application overrides the model's arguments with its own validated values, because models can invent tool arguments (in testing, the model once passed `budget=0` and the function crashed).
- **Structured output.** The CEO returns JSON constrained by a schema. `recommendation` can only be `Hire`, `Conditional Hire` or `Do Not Hire`.
- **Salary guard.** If the CEO says `Hire` but the expected salary is above budget, the code downgrades it to `Conditional Hire` and adds a `guard_note`.
- **Input validation.** Bad or missing input returns a 400 with a clear message.

## Tech stack

Python, Flask, OpenAI-compatible SDK (Groq and OpenRouter endpoints), python-dotenv, pytest

## Setup

```
pip install -r requirements.txt
```

Create a `.env` file:

```
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key
```

Run:

```
python app.py
```

## API

`POST /ceo`

Request:

```json
{
  "question": "Should we hire this Product Manager?",
  "candidate_info": {
    "name": "Jane",
    "experience": "5 years SaaS",
    "skills": ["Product strategy", "Analytics"],
    "achievements": ["Improved product adoption"],
    "salary_expectation": 120000,
    "market_experience": "SaaS"
  },
  "role_budget": 100000
}
```

Response:

```json
{
  "recommendation": "Conditional Hire",
  "key_strengths": ["5 years of SaaS experience", "Improved product adoption"],
  "key_concerns": ["Expected salary exceeds the budget by 20%"],
  "reasoning": "Strong SaaS background, but the salary gap needs negotiation.",
  "salary_check": { "within_budget": false, "gap": 20000, "gap_percent": 20.0 }
}
```

`salary_expectation` and `role_budget` are required whole numbers. Missing or invalid input returns a 400.

## Tests

```
python -m pytest
```

Covers the salary guard (`test_guard.py`), which runs without any API call.

## Limitations

- The CMO and Recruiter use OpenRouter's free router, so the model behind them can change between runs.
- Agents run one after another, so a request takes several seconds.
- The CEO is instructed to flag missing information rather than invent candidate details, but LLM-generated evaluations can still contain errors and require human review.
- No authentication or rate limiting, so it isn't production-ready.
