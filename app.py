from flask import Flask, request, jsonify
from agents import ceo_agent
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Multi-Agent AI API is running!",
        "endpoint": "/ceo",
        "method": "POST"
    })


@app.route('/ceo', methods=['POST'])
def ceo():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    question = data.get('question')
    candidate = data.get('candidate_info')
    role_budget = data.get('role_budget')

    if not question:
        return jsonify({"error": "Missing question"}), 400

    if not isinstance(candidate, dict):
        return jsonify({"error": "Missing or invalid candidate information"}), 400

    salary = candidate.get('salary_expectation')

    if salary is None or role_budget is None:
        return jsonify({
            "error": "Both salary_expectation and role_budget are required"
        }), 400

    try:
        expected = int(salary)
        budget = int(role_budget)
    except (ValueError, TypeError):
        return jsonify({
            "error": "Salary expectation and role budget must be whole numbers"
        }), 400

    if expected < 0 or budget <= 0:
        return jsonify({
            "error": "Salary must be non-negative and budget must be positive"
        }), 400

    candidate_info = f"""
Name: {candidate.get('name')}
Experience: {candidate.get('experience')}
Skills: {candidate.get('skills')}
Achievements: {candidate.get('achievements')}
Salary expectation: {expected}
Market experience: {candidate.get('market_experience')}
"""

    result = ceo_agent(
        question,
        candidate_info,
        expected=expected,
        budget=budget
    )

    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)