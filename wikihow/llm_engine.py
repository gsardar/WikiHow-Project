"""
WikiHow Analysis — LLM Engine
Adapted from NHCX/NHA_829426/shared/llm_engine.py

Supports DeepSeek (custom browser-based), DeepSeek API, and Gemini as fallback.
Used primarily for:
  - Gender/Identity inference from profile screenshots (GenAI Phase)
  - Contribution change-type classification (vandalism, sexist, sarcasm)
"""

import os
import json
import logging
import requests
import time
from pathlib import Path
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── CONFIG ──────────────────────────────────────────────────────────────────
_CONFIG = {
    "primary_provider": "deepseek_custom",
    "fallback_cascade": ["deepseek_api", "gemini"],
    "bridge_url": "http://127.0.0.1:8002",
    "api_keys": {
        "gemini": os.environ.get("GEMINI_API_KEY", ""),
        "deepseek_api": os.environ.get("DEEPSEEK_API_KEY", ""),
    },
}

# ─── PROMPTS ─────────────────────────────────────────────────────────────────
GENDER_INFERENCE_SYSTEM = (
    "You are an expert sociolinguistic researcher and data analyst specializing in "
    "gender identity detection from online personas. You respond only with valid raw JSON."
)

GENDER_INFERENCE_TEMPLATE = """
Analyze the provided screenshot of a wikiHow user profile and the metadata below to determine the user's gender and specific identity markers.

Metadata:
- Username: {username}
- Real Name (Extracted): {real_name}
- Location: {location}
- Algorithm Guess (Genderize.io): {genderize_guess} (confidence: {genderize_confidence})
- Vision Guess (Local Image AI): {image_ai_guess}

Instructions:
1. IGNORE the "Meet a Community Member" section — it is a generic site feature unrelated to this profile.
2. PRIORITIZE direct self-identification in bio (e.g., "I am a woman", "she/her pronouns").
3. ANALYZE bio text for identities beyond binary: non-binary, agender, genderfluid, etc.
4. CHECK for orientation/identity markers: lesbian, pansexual, bisexual, transgender, queer, etc.
5. CONSIDER Real Name and Location alignment with visual and bio evidence.
6. OVERRIDE the algorithm guesses if bio text explicitly states a different identity.
7. MULTI-DIMENSIONAL: If the user states multiple identities, capture all in identity_tags.
8. Do NOT make assumptions based on physical appearance alone if bio information exists.
9. If the profile is ambiguous with no pronouns or identifiers, mark status as "unknown".

Respond ONLY with a raw JSON object. No markdown code blocks, no preamble.

{{
  "status": "female | male | non-binary | prefer not to say | unknown",
  "identity_tags": ["list of specific identities, empty if none"],
  "confidence": 0.0,
  "source": "Bio | Header | Username | Visual | Combination",
  "how_predicted": "Step-by-step explanation of reasoning"
}}
"""

CHANGE_CLASSIFICATION_SYSTEM = (
    "You are an expert content moderator specializing in detecting problematic contributions "
    "in collaborative knowledge platforms like WikiHow. You classify text diffs accurately."
)

CHANGE_CLASSIFICATION_TEMPLATE = """
Classify the following WikiHow article revision diff. A positive diff means text was ADDED, negative means REMOVED.

Article Title: {article_title}
Editor Gender: {editor_gender}
Bytes Delta: {bytes_delta}
Diff Content:
---
{diff_text}
---

Classify this revision into exactly one of these types:
- constructive: Adds factual, helpful, well-written content
- vandalism: Nonsense, profanity, irrelevant content, link spam, blanking
- sexist: Contains gendered insults, stereotyping language, or discriminatory framing
- sarcasm: Mocking, condescending, or ironic tone without helpful content
- revert: Appears to undo a previous revision (large deletion, restoring older content)
- unknown: Insufficient signal to classify

Respond ONLY with raw JSON. No markdown.

{{
  "change_type": "constructive | vandalism | sexist | sarcasm | revert | unknown",
  "confidence": 0.0,
  "evidence": "Brief explanation of key signals (username, name, location, or visual badges) that led to this classification"
}}
"""

GENDER_IDENTITY_OVERHAUL = """
IGNORE ALL PREVIOUS CONVERSATIONS AND HISTORY. THIS IS A NEW, INDEPENDENT EVALUATION.
Analyze the provided high-resolution screenshot of a WikiHow contributor profile.

Contributor Metadata:
- Username: {username}
- Real Name: {real_name}
- Location: {location}

Task: Use the bio text, badges, uploaded images, and metadata to identify the contributor's gender identity.
Output must be a single JSON object in the following format:
{{
  "status": "male/female/non-binary/unknown",
  "confidence": 0.0 to 1.0,
  "evidence": "Detailed explanation mentioning specific metadata or visual elements found in the screenshot"
}}
"""


# ─── PROVIDERS ───────────────────────────────────────────────────────────────

def _query_deepseek_custom(prompt: str, image_path: str = None) -> str:
    """Query the DeepSeek tab in the unified browser via the Bridge Service."""
    url = _CONFIG["bridge_url"]
    try:
        logger.info(f"[DeepSeek Bridge] Sending prompt to {url}/ask...")
        resp = requests.post(
            f"{url}/ask",
            json={
                "prompt": prompt,
                "file_path": image_path
            },
            timeout=600 # Wait up to 10 mins for AI response
        )
        if resp.status_code == 200:
            return resp.json().get("response", "")
        logger.error(f"[DeepSeek Bridge] HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"[DeepSeek Bridge] Connection error: {e}")
    return ""


def _query_deepseek_api(prompt: str) -> str:
    """Query the DeepSeek official API."""
    api_key = _CONFIG["api_keys"].get("deepseek_api", "")
    if not api_key:
        logger.warning("[DeepSeek API] No API key configured.")
        return ""
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": GENDER_INFERENCE_SYSTEM},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2048
        }
        resp = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers, timeout=120)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        logger.error(f"[DeepSeek API] HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"[DeepSeek API] Error: {e}")
    return ""


def _query_gemini(prompt: str) -> str:
    """Query Google Gemini API as fallback."""
    api_key = _CONFIG["api_keys"].get("gemini", "")
    if not api_key:
        logger.warning("[Gemini] No API key configured.")
        return ""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048}
        }
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        logger.error(f"[Gemini] HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"[Gemini] Error: {e}")
    return ""


_PROVIDER_MAP = {
    "deepseek_custom": _query_deepseek_custom,
    "deepseek_api": _query_deepseek_api,
    "gemini": _query_gemini,
}


# ─── CORE INTERFACE ──────────────────────────────────────────────────────────

def set_config(updates: dict):
    """Update LLM engine configuration."""
    _CONFIG.update(updates)


def query_llm(prompt: str, provider: str = "auto", image_path: str = None) -> str:
    """
    Query an LLM with cascade fallback.

    Args:
        prompt: The prompt text.
        provider: "auto" uses primary_provider, or specify one directly.
        image_path: Optional path to a screenshot (used by deepseek_custom).

    Returns:
        LLM response text, or empty string on total failure.
    """
    primary = provider if provider != "auto" else _CONFIG["primary_provider"]
    providers_to_try = [primary] + [p for p in _CONFIG["fallback_cascade"] if p != primary]

    for p in providers_to_try:
        fn = _PROVIDER_MAP.get(p)
        if not fn:
            continue
        logger.info(f"[LLM Engine] Querying {p}...")
        result = fn(prompt, image_path) if p == "deepseek_custom" else fn(prompt)
        if result and result.strip():
            return result.strip()
        logger.warning(f"[LLM Engine] {p} returned empty response, trying next...")

    logger.error("[LLM Engine] All providers failed.")
    return ""


def query_llm_json(prompt: str, provider: str = "auto", image_path: str = None) -> dict:
    """Query LLM and parse the JSON response. Handles markdown code blocks if present."""
    raw = query_llm(prompt, provider, image_path)
    if not raw:
        return {}

    # Strip markdown fences
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        try:
            start, end = raw.index("{"), raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError):
            logger.error(f"[LLM Engine] Could not parse JSON from response: {raw[:200]}")
            return {}


def start_new_chat():
    """Start a new chat session on the DeepSeek browser engine."""
    url = _CONFIG["deepseek_custom_url"]
    try:
        resp = requests.post(f"{url}/new_chat", timeout=60)
        if resp.status_code == 200:
            logger.info("[LLM Engine] New DeepSeek chat session started.")
            return True
    except Exception as e:
        logger.error(f"[LLM Engine] Failed to start new chat: {e}")
    return False


# ─── TASK-SPECIFIC HELPERS ───────────────────────────────────────────────────

def infer_gender(username: str, real_name: str = "", location: str = "",
                 genderize_guess: str = "unknown", genderize_confidence: float = 0.0,
                 image_ai_guess: str = "unknown", image_path: str = None) -> dict:
    """
    Run full GenAI gender inference for a profile.

    Returns a dict with keys: status, identity_tags, confidence, source, how_predicted
    """
    prompt = GENDER_INFERENCE_TEMPLATE.format(
        username=username,
        real_name=real_name,
        location=location,
        genderize_guess=genderize_guess,
        genderize_confidence=f"{genderize_confidence:.2f}",
        image_ai_guess=image_ai_guess,
    )
    result = query_llm_json(prompt, image_path=image_path)
    if not result:
        return {
            "status": "unknown",
            "identity_tags": [],
            "confidence": 0.0,
            "source": "GenAI_failed",
            "how_predicted": "LLM returned no response."
        }
    return result


def classify_change(article_title: str, editor_gender: str,
                    bytes_delta: int, diff_text: str) -> dict:
    """
    Classify a revision diff into: constructive, vandalism, sexist, sarcasm, revert, unknown.

    Returns a dict with keys: change_type, confidence, evidence
    """
    prompt = CHANGE_CLASSIFICATION_TEMPLATE.format(
        article_title=article_title,
        editor_gender=editor_gender,
        bytes_delta=bytes_delta,
        diff_text=diff_text[:3000],  # Truncate very large diffs
    )
    result = query_llm_json(prompt)
    if not result:
        return {"change_type": "unknown", "confidence": 0.0, "evidence": "LLM returned no response."}
    return result
