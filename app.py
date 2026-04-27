from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os

app = Flask(__name__)
CORS(app)  # Allow requests from any domain

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ALLOWED_MODELS = ["claude-haiku-4-5-20251001"]
MAX_TOKENS = 300

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Maya API Proxy"})

@app.route("/rate-pickup", methods=["POST"])
def rate_pickup():
    try:
        data = request.json
        line = data.get("line", "").strip()

        if not line or len(line) < 3:
            return jsonify({"error": "too short"}), 400

        if len(line) > 500:
            return jsonify({"error": "too long"}), 400

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=MAX_TOKENS,
            system="""You are Maya Tsoi, 24, half Korean half Ukrainian model, digital nomad living in Milan. Someone sent you a pickup line. Rate it.

Reply EXACTLY in this format:
GRADE: [A/B/C/D/E/F]
LABEL: [2-4 word catchy label]
FEEDBACK: [2-3 casual sentences as Maya, playful and honest]

Grading: A=clever and unique, B=good effort, C=average, D=boring, E=cringe, F=terrible.
Most people get C or D. Be real, playful, never mean.""",
            messages=[{"role": "user", "content": f'Rate this pickup line: "{line}"'}]
        )

        text = response.content[0].text
        grade = (text.split("GRADE:")[1].split("\n")[0].strip()[:1]) if "GRADE:" in text else "C"
        label = (text.split("LABEL:")[1].split("\n")[0].strip()) if "LABEL:" in text else "interesting approach"
        feedback = (text.split("FEEDBACK:")[1].strip()) if "FEEDBACK:" in text else "...okay then 😏"

        return jsonify({
            "grade": grade,
            "label": label,
            "feedback": feedback
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
