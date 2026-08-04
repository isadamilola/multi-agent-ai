# Multi-Agent AI System

A simple AI application built with Groq's Llama 3.3 model that simulates different business roles.

## Features

- CEO orchestrator
- CFO agent
- CMO agent
- Recruiter agent
- Flask REST API

## Tech Stack

- Python
- Groq API
- Flask

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
GROQ_API_KEY=your_api_key
```

Run:

```bash
python app.py
```

## API Endpoint

POST `/ceo`

Example body:

```json
{
  "question": "We need to hire a Product Manager. What should we consider?"
}
```
