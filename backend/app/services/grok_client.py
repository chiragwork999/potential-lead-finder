import httpx
from app.core.config import settings


class GrokClient:
    async def summarize_event(self, title: str, content: str) -> dict:
        if not settings.grok_api_key:
            return {
                "summary": "Grok API key not configured. Returning fallback summary.",
                "entities": ["Unknown Entity"],
                "confidence": 0.35,
                "model": "fallback",
            }

        prompt = f"Summarize this lead signal and extract entities. Title: {title}\nContent: {content}"
        payload = {
            "model": settings.grok_model,
            "messages": [
                {"role": "system", "content": "You are an enterprise lead-intelligence analyst."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {settings.grok_api_key}"}

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{settings.grok_base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"summary": content, "entities": [], "confidence": 0.8, "model": settings.grok_model}
