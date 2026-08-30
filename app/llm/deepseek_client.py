import json

from openai import OpenAI

from app.config import config

_client = OpenAI(api_key=config.deepseek_api_key, base_url=config.deepseek_base_url)


def chat_json(system_prompt: str, user_prompt: str) -> dict:
    """Call DeepSeek chat completion and parse a JSON object response."""
    response = _client.chat.completions.create(
        model=config.deepseek_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    content = response.choices[0].message.content
    return json.loads(content)


def chat_text(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """Call DeepSeek chat completion and return plain text."""
    response = _client.chat.completions.create(
        model=config.deepseek_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
