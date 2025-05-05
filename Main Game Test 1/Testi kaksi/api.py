from flask import Flask, request, jsonify
from flask_cors import CORS
from logic import GameLogic

app = Flask(__name__)
CORS(app)

game = GameLogic()

@app.route("/game", methods=["POST"])
def game_route():
    data = request.get_json()
    user_input = data.get("input", "")
    response = game.process_input(user_input)
    return jsonify({"response": response})

@app.route("/status", methods=["GET"])
def status():
    return jsonify(game.get_status())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
