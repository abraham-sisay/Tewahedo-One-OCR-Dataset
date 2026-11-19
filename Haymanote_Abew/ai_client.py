#!/usr/bin/env python3
"""
AI Client Helper for Haymanote Abew project
Supports:
  - Anthropic API (via https://api.iceyyy.dev/)
  - OpenAI-compatible API (via https://api.iceyyy.dev/v1)
  - Models: claude-haiku-5.5, mimo-v2.6-flash, deepseek-v4.1-flash
  - Zero third-party dependencies required (pure standard library)
"""

import os
import sys
import json
import ssl
import argparse
import urllib.request
import urllib.error

# Load environment variables from .env if present
def load_dotenv(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val

load_dotenv()

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "sk-ice-93j0ib5etqf32a4qwjh09vx7ruap0yp9ghim0p54j8906x8k")
ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.iceyyy.dev/")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.iceyyy.dev/v1")

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
DEFAULT_REASONING = os.environ.get("ANTHROPIC_REASONING", "high")
DEFAULT_THINKING_BUDGET = int(os.environ.get("ANTHROPIC_THINKING_BUDGET", "16000"))

SUPPORTED_MODELS = [
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-20241022",
    "claude-haiku-5.5",
    "mimo-v2.6-flash",
    "deepseek-v4.1-flash"
]

# Disable strict SSL verification for proxy endpoints with non-standard certificate chains
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def check_balance(api_key=API_KEY):
    """Check remaining balance and usage stats."""
    url = "https://api.iceyyy.dev/balance"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode('utf-8')}"}
    except Exception as e:
        return {"error": str(e)}

def ask_anthropic(prompt, model=None, system_prompt=None, max_tokens=None, temperature=0.7, thinking=None, thinking_budget=None):
    """Query Anthropic Messages API."""
    if model is None:
        model = DEFAULT_MODEL
    url = ANTHROPIC_BASE_URL.rstrip("/") + "/v1/messages"
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    if thinking is None and DEFAULT_REASONING.lower() in ("high", "enabled", "true"):
        thinking = True
    if thinking_budget is None:
        thinking_budget = DEFAULT_THINKING_BUDGET

    if thinking and "3-7-sonnet" in model:
        if max_tokens is None:
            max_tokens = max(2048, thinking_budget + 2048)
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "thinking": {
                "type": "enabled",
                "budget_tokens": thinking_budget
            },
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    else:
        if max_tokens is None:
            max_tokens = 1024
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

    if system_prompt:
        payload["system"] = system_prompt

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            content_blocks = res.get("content", [])
            text_blocks = [block.get("text", "") for block in content_blocks if block.get("type") == "text"]
            thinking_blocks = [block.get("thinking", "") for block in content_blocks if block.get("type") == "thinking"]
            return {
                "text": "\n".join(text_blocks),
                "thinking": "\n".join(thinking_blocks) if thinking_blocks else None,
                "model": res.get("model", model),
                "usage": res.get("usage", {}),
                "raw": res
            }
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Anthropic API Error {e.code}: {err_msg}")
    except Exception as e:
        err_text = str(e)
        if "timed out" in err_text.lower() and "iceyyy.dev" in ANTHROPIC_BASE_URL and "sonnet" in model.lower():
            raise RuntimeError(
                f"Request timed out. Note: The free key on api.iceyyy.dev only hosts 'claude-haiku-5.5'. "
                f"To query Sonnet with High reasoning, supply an official Anthropic API key in .env or switch to --model claude-haiku-5.5."
            )
        raise RuntimeError(f"Request failed: {err_text}")

def ask_openai(prompt, model="claude-haiku-5.5", system_prompt=None, max_tokens=1024, temperature=0.7):
    """Query OpenAI-compatible Chat Completions API."""
    url = OPENAI_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            choices = res.get("choices", [])
            reply = choices[0]["message"]["content"] if choices else ""
            return {
                "text": reply,
                "model": res.get("model", model),
                "usage": res.get("usage", {}),
                "raw": res
            }
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API Error {e.code}: {err_msg}")
    except Exception as e:
        raise RuntimeError(f"Request failed: {str(e)}")

def ask(prompt, model=None, system_prompt=None, provider="anthropic", max_tokens=None, thinking=None):
    """Unified entry point."""
    if model is None:
        model = DEFAULT_MODEL
    if provider == "anthropic":
        return ask_anthropic(prompt, model=model, system_prompt=system_prompt, max_tokens=max_tokens, thinking=thinking)
    else:
        return ask_openai(prompt, model=model, system_prompt=system_prompt, max_tokens=max_tokens or 1024)

def interactive_chat(model=None, provider="anthropic"):
    if model is None:
        model = DEFAULT_MODEL
    print(f"\n=======================================================")
    print(f" Interactive Chat session")
    print(f" Provider: {provider.upper()} | Model: {model}")
    print(f" Type 'exit' or 'quit' to end session.")
    print(f" Type 'balance' to check current balance.")
    print(f"=======================================================\n")
    
    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            if user_input.lower() == "balance":
                bal = check_balance()
                print(f"[Balance]: ${bal.get('balance', 'N/A')} (Total spent: ${bal.get('total_spent', 'N/A')})\n")
                continue
            
            print("\nAI is thinking...\n")
            res = ask(user_input, model=model, provider=provider)
            if res.get("thinking"):
                print(f"--- Thinking Process ---\n{res['thinking']}\n------------------------\n")
            print(f"AI > {res['text']}\n")
            print(f"Tokens: prompt={res['usage'].get('input_tokens') or res['usage'].get('prompt_tokens', 0)}, completion={res['usage'].get('output_tokens') or res['usage'].get('completion_tokens', 0)}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break
        except Exception as e:
            print(f"Error: {e}\n")

def main():
    parser = argparse.ArgumentParser(description="Haymanote Abew AI Client")
    parser.add_argument("--prompt", "-p", type=str, help="Prompt text to send to AI")
    parser.add_argument("--file", "-f", type=str, help="Path to text file containing prompt")
    parser.add_argument("--model", "-m", type=str, default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic", help="API protocol to use")
    parser.add_argument("--reasoning", "-r", choices=["high", "off"], default=DEFAULT_REASONING, help="Thinking/reasoning effort level")
    parser.add_argument("--max-tokens", type=int, default=4096, help="Maximum completion tokens")
    parser.add_argument("--system", "-s", type=str, help="Optional system instruction")
    parser.add_argument("--balance", "-b", action="store_true", help="Check current API key balance")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive terminal chat session")
    
    args = parser.parse_args()

    if args.balance:
        print("Checking API key balance...")
        bal = check_balance()
        print(json.dumps(bal, indent=2))
        return

    if args.interactive:
        interactive_chat(model=args.model, provider=args.provider)
        return

    prompt_text = args.prompt
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as pf:
                prompt_text = pf.read()
        except Exception as e:
            print(f"Error reading prompt file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)

    if prompt_text:
        thinking_enabled = True if args.reasoning == "high" else False
        print(f"Sending prompt to {args.provider.upper()} (Model: {args.model}, Reasoning: {args.reasoning})...\n")
        try:
            res = ask(prompt_text, model=args.model, system_prompt=args.system, provider=args.provider, max_tokens=args.max_tokens, thinking=thinking_enabled)
            if res.get("thinking"):
                print("Thinking Process:")
                print("--------------------------------------------------")
                print(res["thinking"])
                print("--------------------------------------------------\n")
            print("Response:")
            print("--------------------------------------------------")
            print(res["text"])
            print("--------------------------------------------------")
            print(f"Usage: {res['usage']}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
