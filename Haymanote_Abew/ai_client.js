#!/usr/bin/env node
/**
 * AI Client Helper for Haymanote Abew project (Node.js)
 * Zero external dependencies (uses native fetch in Node 18+)
 * 
 * Supports:
 *   - Anthropic protocol (https://api.iceyyy.dev/)
 *   - OpenAI protocol (https://api.iceyyy.dev/v1)
 *   - Models: claude-haiku-5.5, mimo-v2.6-flash, deepseek-v4.1-flash
 */

const fs = require('fs');
const path = require('path');

// Basic .env parser
function loadEnv() {
  const envPath = path.join(__dirname, '.env');
  if (fs.existsSync(envPath)) {
    const lines = fs.readFileSync(envPath, 'utf8').split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
        const [k, ...vParts] = trimmed.split('=');
        const key = k.trim();
        const val = vParts.join('=').trim().replace(/^['"]|['"]$/g, '');
        if (!process.env[key]) {
          process.env[key] = val;
        }
      }
    }
  }
}

loadEnv();

const API_KEY = process.env.ANTHROPIC_API_KEY || 'sk-ice-93j0ib5etqf32a4qwjh09vx7ruap0yp9ghim0p54j8906x8k';
const ANTHROPIC_BASE_URL = process.env.ANTHROPIC_BASE_URL || 'https://api.iceyyy.dev/';
const OPENAI_BASE_URL = process.env.OPENAI_BASE_URL || 'https://api.iceyyy.dev/v1';

const DEFAULT_MODEL = process.env.ANTHROPIC_MODEL || 'claude-3-7-sonnet-20250219';
const DEFAULT_REASONING = process.env.ANTHROPIC_REASONING || 'high';
const DEFAULT_THINKING_BUDGET = parseInt(process.env.ANTHROPIC_THINKING_BUDGET || '16000', 10);

async function checkBalance() {
  const res = await fetch('https://api.iceyyy.dev/balance', {
    headers: { 'Authorization': `Bearer ${API_KEY}` }
  });
  if (!res.ok) {
    throw new Error(`Failed to check balance: ${res.status} ${await res.text()}`);
  }
  return await res.json();
}

async function askAnthropic(prompt, options = {}) {
  const model = options.model || DEFAULT_MODEL;
  const isHighReasoning = (options.reasoning || DEFAULT_REASONING).toLowerCase() === 'high';
  const thinkingBudget = options.thinkingBudget || DEFAULT_THINKING_BUDGET;

  const url = ANTHROPIC_BASE_URL.replace(/\/+$/, '') + '/v1/messages';
  const payload = {
    model,
    messages: [{ role: 'user', content: prompt }]
  };

  if (isHighReasoning && model.includes('3-7-sonnet')) {
    payload.thinking = {
      type: 'enabled',
      budget_tokens: thinkingBudget
    };
    payload.max_tokens = options.maxTokens || Math.max(2048, thinkingBudget + 2048);
  } else {
    payload.max_tokens = options.maxTokens || 1024;
    payload.temperature = options.temperature ?? 0.7;
  }

  if (options.system) {
    payload.system = options.system;
  }

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'x-api-key': API_KEY,
      'anthropic-version': '2023-06-01',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`Anthropic Error ${res.status}: ${await res.text()}`);
  }

  const data = await res.json();
  const text = (data.content || [])
    .filter(b => b.type === 'text')
    .map(b => b.text)
    .join('\n');

  return { text, model: data.model, usage: data.usage, raw: data };
}

async function askOpenAI(prompt, options = {}) {
  const model = options.model || 'claude-haiku-5.5';
  const maxTokens = options.maxTokens || 1024;
  const temperature = options.temperature ?? 0.7;

  const url = OPENAI_BASE_URL.replace(/\/+$/, '') + '/chat/completions';
  const messages = [];
  if (options.system) {
    messages.push({ role: 'system', content: options.system });
  }
  messages.push({ role: 'user', content: prompt });

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model,
      messages,
      max_tokens: maxTokens,
      temperature
    })
  });

  if (!res.ok) {
    throw new Error(`OpenAI Error ${res.status}: ${await res.text()}`);
  }

  const data = await res.json();
  const choice = data.choices && data.choices[0];
  const text = choice ? choice.message.content : '';

  return { text, model: data.model, usage: data.usage, raw: data };
}

module.exports = {
  checkBalance,
  askAnthropic,
  askOpenAI,
  API_KEY,
  ANTHROPIC_BASE_URL,
  OPENAI_BASE_URL
};

// CLI execution
if (require.main === module) {
  const args = process.argv.slice(2);
  (async () => {
    try {
      if (args.includes('--balance') || args.includes('-b')) {
        console.log('Checking balance...');
        const bal = await checkBalance();
        console.log(JSON.stringify(bal, null, 2));
        return;
      }

      const promptIdx = args.findIndex(a => a === '--prompt' || a === '-p');
      if (promptIdx !== -1 && args[promptIdx + 1]) {
        const prompt = args[promptIdx + 1];
        const modelIdx = args.findIndex(a => a === '--model' || a === '-m');
        const model = modelIdx !== -1 ? args[modelIdx + 1] : DEFAULT_MODEL;
        const isOai = args.includes('--openai');

        console.log(`Querying ${isOai ? 'OpenAI' : 'Anthropic'} (Model: ${model})...\n`);
        const result = isOai
          ? await askOpenAI(prompt, { model })
          : await askAnthropic(prompt, { model });

        console.log('Response:');
        console.log('--------------------------------------------------');
        console.log(result.text);
        console.log('--------------------------------------------------');
        console.log('Usage:', result.usage);
        return;
      }

      console.log(`
Haymanote Abew AI Client (Node.js)

Usage:
  node ai_client.js --balance
  node ai_client.js --prompt "Your question here"
  node ai_client.js --prompt "Your question" --model deepseek-v4.1-flash --openai
      `);
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
  })();
}
