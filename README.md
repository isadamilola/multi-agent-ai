# Multi-Agent AI Hiring System

A multi-agent AI system that simulates a business leadership team evaluating hiring decisions.

The system uses multiple specialized AI agents to analyze a candidate from different business perspectives before a CEO agent produces a final recommendation.

# Features

- CFO Agent — evaluates financial implications, salary, business value, ROI, and financial risks.
- CMO Agent — evaluates marketing value, market knowledge, positioning, and customer considerations.
- Recruiter Agent — evaluates experience, skills, team fit, leadership, and hiring risks.
- CEO Agent — orchestrates the specialist agents and produces the final hiring recommendation.
- Flask REST API — exposes the AI system through an API endpoint.

# Architecture

User
↓
Flask REST API
↓
CEO Orchestrator
↓
┌────────────┬────────────┬────────────┐
↓ ↓ ↓
CFO CMO Recruiter
↓ ↓ ↓
└────────────┴────────────┘
↓
CEO Final Decision
↓
JSON

# Tech Stack

- Python
- Flask
- OpenRouter API
- LLM-based multi-agent architecture
- python-dotenv

# Project Structure

multi-agent-ai/
│
├── agents.py
├── app.py
├── requirements.txt
├── README.md
└── .gitignore

# Setup

Clone the repository and install the dependencies:

pip install -r requirements.txt

Create a ".env" file in the project directory:

OPENROUTER_API_KEY=your_api_key

Run the application:

python app.py

API

POST "/ceo"

The endpoint accepts a hiring question and structured candidate information.

# Example Request

{
"question": "Should we hire this candidate?",
"candidate_info": {
"name": "Jane Doe",
"experience": "5 years of product management",
"skills": [
"Product strategy",
"User research",
"Analytics"
],
"achievements": "Increased product retention by 18%",
"salary_expectation": 90000,
"market_experience": "Limited experience in our target market"
}
}

The candidate information is analyzed independently by the CFO, CMO, and Recruiter agents.

The CEO agent then combines their assessments and produces a final recommendation:

- "Hire"
- "Conditional Hire"
- "Do Not Hire"

# Purpose

This project demonstrates practical implementation of:

- Multi-agent AI systems
- LLM orchestration
- Role-based AI agents
- Structured candidate evaluation
- REST API development with Flask
- Integration with hosted LLM APIs
- Combining multiple AI perspectives into a final decision

# Note

The project uses OpenRouter's API to access available AI models. An API key is required to run the application.
