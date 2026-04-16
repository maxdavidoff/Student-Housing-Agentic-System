from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL


class OpenAIDiscoveryClient:
    """
    Discovery client placeholder for OpenAI Responses API + web_search.

    This is only used when DISCOVERY_BACKEND=openai_web_search.
    The method returns parsed JSON if the model follows the requested schema,
    otherwise it falls back to an empty candidate list.
    """

    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def discover_sites(self, prompt: str) -> dict[str, Any]:
        response = self.client.responses.create(
            model=OPENAI_MODEL,
            tools=[{"type": "web_search"}],
            input=prompt,
        )

        text = getattr(response, "output_text", "") or ""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"candidates": [], "raw_text": text}
