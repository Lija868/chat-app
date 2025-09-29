import os, httpx
from openai import OpenAI, AsyncOpenAI

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_KEY:
    async def ask_openai_for_response(chat_id, user_id, prompt):
        return "OPENAI_API_KEY not configured. Set OPENAI_API_KEY to enable assistant responses."
else:
    async def ask_openai_for_response(chat_id, user_id, prompt):

        BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

        headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

        data = {
            "model": "gemini-2.5-flash",
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 500
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(BASE_URL, headers=headers, json=data)
            if r.status_code != 200:
                return f"OpenAI error: {r.status_code} {r.text}"
            j = r.json()
            return j["choices"][0]["message"]["content"]
            # resp.raise_for_status()
            # data = resp.json()
            #
            # # return only the assistant message
            # return {"response": data["choices"][0]["message"]["content"]}

        # url = "https://api.openai.com/v1/chat/completions"
        # headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
        # data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
        # async with httpx.AsyncClient(timeout=30) as client:
        #     r = await client.post(url, json=data, headers=headers)
        #     if r.status_code != 200:
        #         return f"OpenAI error: {r.status_code} {r.text}"
        #     j = r.json()
        #     return j["choices"][0]["message"]["content"]
