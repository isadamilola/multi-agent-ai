from flask import Flask, request, jsonify
from agents import ceo_agent
import os

app = Flask(__name__)

@app.route('/ceo', methods=['POST'])
def ceo():
    data = request.get_json()
    question = data.get('question')
    result = ceo_agent(question)

    return jsonify({
        'answer': result
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)