# 🤖 AI API Configuration & Quick Start Guide

This project folder is configured to use the **api.iceyyy.dev** AI endpoints for Anthropic and OpenAI-compatible models.

---

## 🔑 Credentials & Endpoints Summary

- **API Key**: `sk-ice-93j0ib5etqf32a4qwjh09vx7ruap0yp9ghim0p54j8906x8k`
- **Anthropic Base URL**: `https://api.iceyyy.dev/`
- **OpenAI Base URL**: `https://api.iceyyy.dev/v1`
- **Balance Endpoint**: `https://api.iceyyy.dev/balance`
- **Web Balance Checker**: [https://api.iceyyy.dev/pricing#balance-checker](https://api.iceyyy.dev/pricing#balance-checker)

### Supported Models:
1. `claude-3-7-sonnet-20250219` (Configured as default with **High Reasoning / Extended Thinking**, requires official Anthropic API key or Sonnet-enabled provider)
2. `claude-haiku-5.5` (Active and available on the free `api.iceyyy.dev` community key)
3. `mimo-v2.6-flash` (Fast model via OpenAI protocol on `api.iceyyy.dev`)
4. `deepseek-v4.1-flash` (Reasoning model via OpenAI protocol on `api.iceyyy.dev`)

---

## 📁 Files Created in This Folder

- [`.env`](.env) — Stores API keys and base URLs for environment auto-loading.
- [`.env.example`](.env.example) — Template for environment variables.
- [`ai_config.json`](ai_config.json) — Structured JSON configuration.
- [`ai_client.py`](ai_client.py) — Zero-dependency Python helper module & CLI tool.
- [`ai_client.js`](ai_client.js) — Zero-dependency Node.js helper module & CLI tool.
- [`.vscode/settings.json`](.vscode/settings.json) — Automatically supplies env vars to VS Code terminals.
- [`.gitignore`](.gitignore) — Protects `.env` from accidental git commits.

---

## 🚀 How to Use

### 1. Check Remaining Balance
```bash
# Via Python:
python ai_client.py --balance

# Via Node.js:
node ai_client.js --balance

# Via PowerShell:
powershell -Command "Invoke-RestMethod -Uri 'https://api.iceyyy.dev/balance' -Headers @{'Authorization'='Bearer sk-ice-93j0ib5etqf32a4qwjh09vx7ruap0yp9ghim0p54j8906x8k'}"
```

---

### 2. Quick Command Line Queries

#### Anthropic (`claude-haiku-5.5`)
```bash
python ai_client.py --prompt "Summarize chapter 1 of Haymanote Abew"
```

#### DeepSeek (`deepseek-v4.1-flash`)
```bash
python ai_client.py --provider openai --model deepseek-v4.1-flash --prompt "Explain the Council of Nicaea"
```

#### MiMo (`mimo-v2.6-flash`)
```bash
python ai_client.py --provider openai --model mimo-v2.6-flash --prompt "Translate this text to Ge'ez"
```

#### Interactive Terminal Chat
```bash
python ai_client.py --interactive
```

---

### 3. Using in Your Own Python Scripts

You can import `ask_anthropic` or `ask_openai` anywhere in this project:

```python
from ai_client import ask_anthropic, ask_openai, check_balance

# 1. Using Claude
response = ask_anthropic(
    prompt="Explain the Christology of Saint Cyril of Alexandria",
    model="claude-haiku-5.5",
    system_prompt="You are a scholar of Patristic theology and Ethiopian Orthodox tradition."
)
print(response["text"])

# 2. Using DeepSeek or MiMo
response2 = ask_openai(
    prompt="Analyze the differences between the homilies",
    model="deepseek-v4.1-flash"
)
print(response2["text"])
```

#### Or using the official `anthropic` Python package:
```python
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    base_url=os.environ["ANTHROPIC_BASE_URL"]
)

message = client.messages.create(
    model="claude-haiku-5.5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(message.content[0].text)
```

---

### 4. Using in Your Own Node.js / JavaScript Scripts

```javascript
const { askAnthropic, askOpenAI } = require('./ai_client');

async function run() {
  // Claude query
  const res = await askAnthropic("What are the key themes of Haymanote Abew?");
  console.log(res.text);

  // DeepSeek query
  const res2 = await askOpenAI("List the patristic authors included in Haymanote Abew", {
    model: "deepseek-v4.1-flash"
  });
  console.log(res2.text);
}

run();
```

---

### 5. Using with cURL

```bash
# Anthropic API format:
curl https://api.iceyyy.dev/v1/messages \
  -H "x-api-key: sk-ice-93j0ib5etqf32a4qwjh09vx7ruap0yp9ghim0p54j8906x8k" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-5.5","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}'

# OpenAI API format:
curl https://api.iceyyy.dev/v1/chat/completions \
  -H "Authorization: Bearer sk-ice-93j0ib5etqf32a4qwjh09vx7ruap0yp9ghim0p54j8906x8k" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4.1-flash","messages":[{"role":"user","content":"Hello"}]}'
```

---

*Credits: Telegram @iceyy69 and @KrishnDhola1*
