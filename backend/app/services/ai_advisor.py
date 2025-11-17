"""Utility helpers for calling a real LLM for financial advice."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Sequence

import requests


LOGGER = logging.getLogger(__name__)


class AIAdvisorError(RuntimeError):
    """Base exception for AI advisor failures."""


class AIAdvisorUnavailable(AIAdvisorError):
    """Raised when the advisor cannot call an AI backend."""


@dataclass(frozen=True)
class SpendingSnapshot:
    """Simple container for category level spend used in prompts."""

    category: str
    amount: float


class AIAdvisor:
    """Thin wrapper around the OpenAI Chat Completions API.

    The implementation intentionally stays lightweight so we do not need the
    heavier ``openai`` dependency.  All network calls are routed through the
    HTTPS REST endpoint and guarded with timeouts to avoid blocking requests.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        # Ensure we do not end up with ``//chat`` when the env var already
        # includes /v1.
        self.chat_url = base_url.rstrip("/") + "/chat/completions"
        self.provider = os.getenv("OPENAI_PROVIDER_NAME", "openai")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_goal_recommendation(
        self,
        goal_amount: float,
        target_date: str,
        forecast: Dict[str, float],
        top_spending: Sequence[SpendingSnapshot],
    ) -> str:
        """Ask the LLM for a coaching style recommendation."""

        if not self.is_configured:
            raise AIAdvisorUnavailable("OPENAI_API_KEY is not configured")

        forecast_summary = json.dumps(forecast)
        spending_lines = [
            f"- {snap.category}: ${snap.amount:,.2f} in the last 30 days"
            for snap in top_spending
        ]
        if not spending_lines:
            spending_lines.append("- No recent spending recorded")

        prompt = f"""
You are an empathetic yet practical financial coach. Craft 2-3 short sentences
with concrete actions for the user.

Goal: Save ${goal_amount:,.2f} by {target_date}.
Forecast snapshot: {forecast_summary}.
Top spending patterns:
{chr(10).join(spending_lines)}

Respond with a short paragraph focused on monthly actions, without any
markdown bullets.
""".strip()

        payload = {
            "model": self.model,
            "temperature": 0.35,
            "messages": [
                {
                    "role": "system",
                    "content": "You are SmartCoach, an expert personal finance assistant.",
                },
                {"role": "user", "content": prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(
                self.chat_url,
                headers=headers,
                json=payload,
                timeout=20,
            )
            resp.raise_for_status()
        except Exception as exc:  # pragma: no cover - network code
            LOGGER.warning("AI advisor request failed: %s", exc)
            raise AIAdvisorError("Unable to contact AI provider") from exc

        data = resp.json()
        try:
            message = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:  # pragma: no cover - defensive
            LOGGER.error("Unexpected AI response: %s", data)
            raise AIAdvisorError("Malformed response from AI provider") from exc

        return message


def top_spending_snapshots(category_totals: Dict[str, float], limit: int = 3) -> List[SpendingSnapshot]:
    """Helper to convert a mapping into dataclasses for prompt context."""

    ordered = sorted(
        ((cat, amt) for cat, amt in category_totals.items() if amt),
        key=lambda entry: entry[1],
        reverse=True,
    )
    return [SpendingSnapshot(category=cat, amount=float(amt)) for cat, amt in ordered[:limit]]

