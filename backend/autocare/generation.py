"""Answer generation (proposal §6.7).

The LLM never writes free prose. It returns JSON claims, each pointing at the
evidence ids it relies on. validation.py then checks every claim before anything
reaches the user, and citations are rendered by the server from the database —
the model cannot invent a document, section or page.
"""
from __future__ import annotations

import json
import re
from typing import Protocol

from .language import LANGUAGE_NAMES, LANG_ROMAN_UR, LANG_UR
from .repository import VehicleProfile
from .retrieval import Evidence

MECHANIC_NOTE = "mechanic_note"   # document.document_type for recorded mechanic advice


class Generator(Protocol):
    def generate(self, question: str, language: str, vehicle: VehicleProfile,
                 evidence: list[Evidence]) -> list[dict]:
        """Return raw claims: [{"text": str, "evidence_ids": [str, ...]}, ...]."""


_STYLE = {
    LANG_UR: "Write every claim in Urdu (Nastaliq/Arabic script). Keep codes such as P0301 and "
             "part names that have no common Urdu word in English.",
    LANG_ROMAN_UR: "Write every claim in Roman Urdu (Urdu in Latin letters, as Pakistani drivers "
                   "text, e.g. 'Brake pads ghis chuke hon to grinding ki awaz aati hai'). Keep "
                   "technical terms and codes in English.",
}

SYSTEM_PROMPT = """You are AutoCare AI. You explain car problems the way an experienced, honest
mechanic explains them to a car owner who is not technical: calm, practical, and in plain words.

You may ONLY use facts stated in the numbered evidence passages. Two kinds of passage exist:
- MANUAL: the manufacturer's owner's manual or code reference (official instructions).
- MECHANIC NOTE: practical advice recorded from a named, experienced mechanic.
Do not use outside knowledge, even if you are confident. If the passages do not cover something,
leave it out.

How to structure the answer (skip any part the passages do not support):
  a) Safety first: what to do right now, and whether it is safe to keep driving.
  b) What it most likely means.
  c) What the owner can check themselves.
  d) When to take it to a workshop, and what to ask for.
If a mechanic note disagrees with the manual, follow the manual and leave the conflicting note out.

Rules:
1. Write short, self-contained claims (at most 7), in the order above.
2. Every claim MUST list the evidence ids (e.g. "E2") whose text directly states it.
3. If the passages do not answer the question, return {"claims": []}. Never guess.
4. Do not mention evidence ids, documents, mechanics' names or page numbers inside the claim
   text; the app shows the sources.
5. Do not add a general safety disclaimer; the app adds one.
6. {style}
7. "text_en" is the same claim in plain English (identical to "text" when answering in English);
   it is used only to verify the claim against the passages.

Respond with JSON only, in exactly this shape:
{"claims": [{"text": "...", "text_en": "...", "evidence_ids": ["E1"]}]}"""


TRANSLATE_PROMPT = """You convert a car owner's question written in Urdu or Roman Urdu (often mixed
with English) into ONE short English search query for the vehicle's owner's manual.
Keep diagnostic trouble codes (e.g. P0301) and part names exactly. Do not answer the question.
Output only the English query, nothing else."""


def build_messages(question: str, language: str, vehicle: VehicleProfile,
                   evidence: list[Evidence]) -> list[dict]:
    style = _STYLE.get(language, "Write every claim in plain English.")
    blocks = []
    for e in evidence:
        c = e.chunk
        kind = "MECHANIC NOTE" if c.document_type == MECHANIC_NOTE else "MANUAL"
        where = (f"Page: {c.page_number}" if c.page_number is not None else "Page: -")
        blocks.append(
            f"[{e.label}] {kind} | {c.document_name} | Section: {c.section or '-'} | {where}\n"
            f"{c.text.strip()}"
        )
    user = (
        f"Vehicle: {vehicle.label}"
        + (f", {vehicle.current_mileage} km" if vehicle.current_mileage else "")
        + f"\nAnswer language: {LANGUAGE_NAMES.get(language, 'English')}"
        + f"\n\nQuestion:\n{question}\n\nEvidence passages:\n\n" + "\n\n".join(blocks)
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT.replace("{style}", style)},
        {"role": "user", "content": user},
    ]


def parse_claims(content: str) -> list[dict]:
    """Tolerant JSON extraction; anything malformed yields no claims (-> abstain)."""
    if not content:
        return []
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    claims = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(claims, list):
        return []
    out = []
    for c in claims:
        if isinstance(c, dict) and isinstance(c.get("text"), str):
            ids = c.get("evidence_ids") or []
            en = c.get("text_en")
            out.append({"text": c["text"].strip(),
                        "text_en": en.strip() if isinstance(en, str) and en.strip() else None,
                        "evidence_ids": [str(i).strip() for i in ids] if isinstance(ids, list) else []})
    return out


class OpenAICompatibleGenerator:
    """Any /chat/completions endpoint: OpenAI, Groq, Together, OpenRouter, Ollama (/v1)."""

    def __init__(self, base_url: str, api_key: str, model: str, timeout_s: float = 60.0):
        self.base_url, self.api_key, self.model, self.timeout_s = base_url.rstrip("/"), api_key, model, timeout_s

    def _chat(self, payload: dict) -> str:
        import httpx

        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        r = httpx.post(f"{self.base_url}/chat/completions", json={"model": self.model, **payload},
                       headers=headers, timeout=self.timeout_s)
        if r.status_code >= 400:
            # Surface the provider's own reason (e.g. "model_not_found", "invalid_api_key").
            raise RuntimeError(f"LLM provider returned {r.status_code}: {r.text[:500]}")
        return r.json()["choices"][0]["message"]["content"] or ""

    def translate_query(self, question: str, language: str) -> str:
        """Rewrite an Urdu / Roman-Urdu question as a short English search query."""
        content = self._chat({
            "temperature": 0,
            "messages": [
                {"role": "system", "content": TRANSLATE_PROMPT},
                {"role": "user", "content": question},
            ],
        })
        return content.strip().strip('"').splitlines()[0] if content.strip() else ""

    def generate(self, question, language, vehicle, evidence):
        content = self._chat({
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": build_messages(question, language, vehicle, evidence),
        })
        return parse_claims(content)


class ExtractiveGenerator:
    """No-LLM fallback: quotes the first sentences of the top passages verbatim.

    Always English (the corpus language), so it does NOT satisfy AC1 for Urdu or
    Roman Urdu queries. The service reports answer_language='en' honestly.
    """

    language = "en"

    def generate(self, question, language, vehicle, evidence):
        claims = []
        for e in evidence[:3]:
            sentences = re.split(r"(?<=[.!?])\s+", " ".join(e.chunk.text.split()))
            text = " ".join(sentences[:2]).strip()
            if text:
                claims.append({"text": text, "evidence_ids": [e.label]})
        return claims


def build_generator(settings) -> Generator:
    if settings.generation_mode == "extractive":
        return ExtractiveGenerator()
    if settings.generation_mode == "llm":
        return OpenAICompatibleGenerator(settings.llm_base_url, settings.llm_api_key,
                                         settings.llm_model, settings.llm_timeout_s)
    raise ValueError(f"Unknown AUTOCARE_GENERATION_MODE: {settings.generation_mode!r}")
