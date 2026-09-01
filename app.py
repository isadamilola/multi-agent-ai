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
    data = request.get_json()
    question = data.get('question')
    candidate = data.get('candidate_info')

    if not question:
        return jsonify({
            "error": "Missing question"
        }), 400

    if not candidate:
        return jsonify({
            "error": "Missing candidate information"
        }), 400

    candidate_info = f"""
Name: {candidate.get('name')}
Experience: {candidate.get('experience')}
Skills: {candidate.get('skills')}
Achievements: {candidate.get('achievements')}
Salary expectation: {candidate.get('salary_expectation')}
Market experience: {candidate.get('market_experience')}
"""
    
    result = ceo_agent(question, candidate_info)

    return jsonify({
        'answer': result
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)