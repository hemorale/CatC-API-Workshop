# 🧠 RAG (Retrieval-Augmented Generation) Scripts for Vertex AI & OpenAI

This repo contains implementations of RAG (Retrieval-Augmented Generation) using **OpenAI (ChatGPT)** models. The scripts load data from a JSON file and use it to answer user queries in real-time.

---

## ⚠️ VS Code Environment Variable Issue

### Problem

When running the scripts from a terminal (`bash`, `zsh`, etc.), everything works fine. However, when executing the same scripts from **Visual Studio Code**, they may raise errors like:

```text
Please set the necessary environment variables.
```

Or:

```text
Please set the OPENAI_API_KEY environment variable.
```

Despite confirming the environment variables are set (e.g., using `echo $VAR_NAME`), the issue persists inside VS Code.

---

## ✅ Solution: Use a `.env` File and Load It in Python

1. **Create a `.env` file** in the root of your project:

```dotenv

# For OpenAI
OPENAI_API_KEY=your-openai-api-key
```

2. **Update both scripts to load environment variables from `.env`**:

At the top of your Python file, add:

```python
from dotenv import load_dotenv
load_dotenv()
```

> Make sure the `python-dotenv` package is installed:
> ```bash
> pip install python-dotenv
> ```

---

## 🛠 Alternative: Set Environment Variables in VS Code (Optional)

You can also define environment variables directly in your VS Code debugger:

1. Open (or create) `.vscode/launch.json`
2. Add your config like so:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: RAG Script",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/RAG-code.py",
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    }
  ]
}
```

---

## ✅ Summary

| Environment | Status |
|-------------|--------|
| Terminal    | ✅ Works normally |
| VS Code     | ⚠️ May require `.env` loading or `launch.json` setup |

This should resolve any environment variable issues in both terminals and VS Code. Happy coding! 🚀
