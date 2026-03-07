"""
Tribe — AI Content Moderation Microservice

Production-grade content safety service using GPT-4o-mini via Emergent Integrations.
Runs on port 8002, called from the main Next.js backend.

Categories:
  - harassment, hate, self_harm, sexual, violence, spam, impersonation
  
Thresholds:
  - AUTO_REJECT >= 0.85 → content held, admin must review
  - ESCALATE >= 0.50 → content held, flagged for review
  - PASS < 0.50 → content published normally

Fallback: keyword filter when AI is unavailable.
"""

import os
import json
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from emergentintegrations.llm.chat import LlmChat, UserMessage

app = FastAPI(title="Tribe Moderation Service")

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

MODERATION_PROMPT = """You are a content moderation AI for Tribe, a social media platform for Indian college students. 
Analyze the following user-generated content for safety violations.

Rate each category from 0.0 to 1.0:
- harassment: bullying, intimidation, personal attacks
- hate: discrimination, slurs, hate speech against groups
- self_harm: self-harm encouragement, suicide content
- sexual: explicit sexual content, sexual solicitation
- sexual_minors: any sexual content involving minors (CRITICAL)
- violence: graphic violence, threats
- spam: promotional spam, scam content
- impersonation: pretending to be someone else

Context: Content is from Indian college students. Be aware of:
- Hindi/Hinglish slang and abuse terms
- College ragging context
- Cultural sensitivities

Return ONLY valid JSON (no markdown, no explanation):
{"harassment":0.0,"hate":0.0,"self_harm":0.0,"sexual":0.0,"sexual_minors":0.0,"violence":0.0,"spam":0.0,"impersonation":0.0}"""

CRITICAL_CATEGORIES = ["sexual_minors", "self_harm"]
THRESHOLD_REJECT = 0.85
THRESHOLD_ESCALATE = 0.50

FALLBACK_KEYWORDS = [
    "kill yourself", "kys", "bomb threat", "school shooting",
    "child porn", "csam", "cp links", "rape threat", "death threat",
    "suicide", "self harm", "cut yourself",
]


class ModerationRequest(BaseModel):
    text: str


class ModerationResponse(BaseModel):
    flagged: bool
    action: str  # PASS, ESCALATE, AUTO_REJECT
    categories: list
    scores: dict
    model: str
    error: str | None = None


async def ai_moderate(text: str) -> ModerationResponse:
    """Use GPT-4o-mini via Emergent to classify content safety."""
    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"mod-{hash(text) % 100000}",
            system_message=MODERATION_PROMPT,
        )
        chat.with_model("openai", "gpt-4o-mini")

        msg = UserMessage(text=f"Content to moderate:\n\n{text[:2000]}")
        response = await chat.send_message(msg)

        # Parse JSON from response
        response_text = response.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[-1].rsplit("```", 1)[0]

        scores = json.loads(response_text)

        flagged_cats = []
        action = "PASS"

        for cat, score in scores.items():
            if score >= THRESHOLD_ESCALATE:
                flagged_cats.append(cat)
            if cat in CRITICAL_CATEGORIES and score >= 0.3:
                action = "AUTO_REJECT"
            elif score >= THRESHOLD_REJECT:
                action = "AUTO_REJECT"
            elif score >= THRESHOLD_ESCALATE and action == "PASS":
                action = "ESCALATE"

        return ModerationResponse(
            flagged=len(flagged_cats) > 0,
            action=action,
            categories=flagged_cats,
            scores=scores,
            model="gpt-4o-mini",
            error=None,
        )
    except Exception as e:
        print(f"[Moderation AI] Error: {e}")
        return keyword_fallback(text, str(e))


def keyword_fallback(text: str, error: str = "") -> ModerationResponse:
    """Fallback keyword filter when AI is unavailable."""
    lower = text.lower()
    matched = [kw for kw in FALLBACK_KEYWORDS if kw in lower]

    if matched:
        return ModerationResponse(
            flagged=True,
            action="ESCALATE",
            categories=["keyword_match"],
            scores={"keyword_match": 0.7},
            model="keyword_fallback",
            error=f"AI unavailable: {error}" if error else None,
        )

    return ModerationResponse(
        flagged=False,
        action="PASS",
        categories=[],
        scores={},
        model="keyword_fallback",
        error=f"AI unavailable: {error}" if error else None,
    )


@app.post("/moderate", response_model=ModerationResponse)
async def moderate(req: ModerationRequest):
    """Moderate content text. Returns safety classification."""
    if not req.text.strip():
        return ModerationResponse(
            flagged=False, action="PASS", categories=[], scores={}, model="none"
        )
    return await ai_moderate(req.text)


@app.get("/config")
async def config():
    """Get moderation configuration."""
    return {
        "thresholds": {"AUTO_REJECT": THRESHOLD_REJECT, "ESCALATE": THRESHOLD_ESCALATE},
        "criticalCategories": CRITICAL_CATEGORIES,
        "fallbackKeywords": len(FALLBACK_KEYWORDS),
        "apiAvailable": bool(EMERGENT_KEY),
        "model": "gpt-4o-mini",
        "categories": [
            "harassment", "hate", "self_harm", "sexual",
            "sexual_minors", "violence", "spam", "impersonation",
        ],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "moderation"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
