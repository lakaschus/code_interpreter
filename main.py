import quart
import quart_cors
import threading
import time
from quart import jsonify, request
from code_interpreter import CodeInterpreter
import os

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

CODE_BLACKLIST = ["show()", "show(", "input("]
FILE_PATH = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def home():
    return 'API works!'


def long_running_task(code, task_id):
    global code_interpreter
    code_interpreter = CodeInterpreter(task_id, code)
    code_interpreter.execute_code()


@app.route("/code", methods=["POST"])
async def add():
    data = await request.get_json()
    code = data["code"]
    if any([blacklisted_code in code for blacklisted_code in CODE_BLACKLIST]):
        return jsonify({"error": "Code contains interactive code parts, like show(), input(), etc. This plugin does not allow the execution of interactive code"}), 202
    task_id = str(time.time()).split('.')[0]  # Generate a unique task ID
    threading.Thread(target=long_running_task, args=(code, task_id)).start()
    # Give it time to execute code
    time.sleep(5)
    return jsonify({"task_id": task_id}), 200


@app.route("/logs/<task_id>", methods=["GET"])
async def get_logs(task_id):
    path = f"{FILE_PATH}/out/{task_id}/logs.log"
    print(os.path.exists(path))
    if os.path.exists(path) and code_interpreter.finished:
        with open(path, "r") as f:
            logs = f.read()
            # If the logs is too long, truncate it
            if len(logs) > 2000:
                logs = ("Logs are too long, show only beginning and end. \n"
                        + logs[:900] + "..." + logs[-900:])
            return {"logs": logs}
    else:
        time.sleep(2)
        return jsonify({"status": "Processing..."}), 202


@app.route("/files/<task_id>", methods=["GET"])
async def get_file_names(task_id):
    path = f"{FILE_PATH}/out/{task_id}"
    # Show all files in the directory
    if os.path.exists(path) and code_interpreter.finished:
        for root, dirs, files in os.walk(path):
            return {"files": files}
    else:
        return jsonify({"status": "Processing..."}), 202


@app.get("/get_url/<task_id>/<file_name>")
async def get_url(task_id, file_name):
    url = f'https://ai.yaoyaopianist.de/get_file/{task_id}/{file_name}'
    # Send url for any url type
    return {"url": url}


@app.get("/get_file/<task_id>/<file_name>")
async def get_file(task_id, file_name):
    filename = f'{FILE_PATH}/out/{task_id}/{file_name}'
    # Send file for any file type
    return await quart.send_file(filename)


@app.get("/logo.png")
async def plugin_logo():
    filename = f'{FILE_PATH}/res/logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open(f"{FILE_PATH}/.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    with open(f"{FILE_PATH}/.well-known/openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5005)


if __name__ == "__main__":
    main()
