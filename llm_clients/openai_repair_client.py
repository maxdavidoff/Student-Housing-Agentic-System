from __future__ import annotations

from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL


class OpenAIRepairClient:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)  # placeholder: expects OPENAI_API_KEY in your environment
        self.model = OPENAI_MODEL

    def repair_listing(self, decision, raw_row):
        raise NotImplementedError(
            "OpenAI repair client is a placeholder. "
            "Use OPENAI_API_KEY from your environment here when you wire the repair step."
        )
