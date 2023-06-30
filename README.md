# ChatGPT plugin: Code Interpreter

Since OpenAI lets us wait for infinity for the code interpreter I did myself in a few hours.

## How-To

This Repo can be used as a plugin to ChatGPT. 
1. `pip install -r requirements.txt` or
`conda env create -f conda.yaml` and `conda activate code_interpreter` if you use conda 
2. Adapt the url in the `.well-known/ai-plugin.json` to your domain. 
3. Also specify your OpenAI API key in your environment. For instance, you can create a `.env` file with the following content: `OPEN_AI_KEY=<Your Key>`