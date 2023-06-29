import quart
import quart_cors
import threading
import time
from quart import Quart, jsonify, Response
from quart import request
from code_interpreter import CodeInterpreter
import os

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


@app.route("/")
def home():
    return 'API works!'


def long_running_task(code, task_id):
    code_interpreter = CodeInterpreter(task_id, code)
    code_interpreter.execute_code()


@app.route("/code", methods=["POST"])
async def add():
    data = await request.get_json()
    code = data["code"]
    task_id = str(time.time())  # Generate a unique task ID
    threading.Thread(target=long_running_task, args=(code, task_id)).start()
    return jsonify({"task_id": task_id}), 202


@app.route("/result/<task_id>", methods=["GET"])
async def get_result(task_id):
    # Check if out/{task_id}.txt exists and return the result
    # Else: return "Processing..."
    if os.path.exists(f"out/{task_id}.log"):
        with open(f"out/{task_id}.log", "r") as f:
            result = f.read()
            # If the result is too long, truncate it
            if len(result) > 2000:
                result = ("Logs are too long, show only beginning and end. \n"
                          + result[:900] + "..." + result[-900:])
            return {"result": result}
    else:
        return jsonify({"status": "Processing..."}), 202


@app.get("/logo.png")
async def plugin_logo():
    filename = 'res/logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    with open("./.well-known/openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5005)


if __name__ == "__main__":
    main()
