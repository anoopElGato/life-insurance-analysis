"""
Streamlit dashboard for insurance brand analytics
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import json
import re
import requests

from config.settings import LOCAL_LLM_HOST, LOCAL_LLM_MODEL, LOCAL_LLM_TEMPERATURE

# Set page config
st.set_page_config(
    page_title="LICSA — Life Insurance Content Strategy Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "hero"


class LocalLLMClient:
    """Minimal Ollama client for local LLM generation."""

    def __init__(self, model_name: str = LOCAL_LLM_MODEL, host: str = LOCAL_LLM_HOST, temperature: float = LOCAL_LLM_TEMPERATURE):
        self.model_name = model_name
        self.host = host.rstrip("/")
        self.temperature = temperature

    def generate(self, prompt: str, timeout: int = 120) -> str:
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "stream": False,
                },
                timeout=timeout,
            )
            if response.status_code == 200:
                return response.json().get("response", "")

            return ""
        except Exception:
            return ""


def _extract_json_array(text: str) -> Optional[List[Dict]]:
    json_match = re.search(r"\[.*\]", text, re.DOTALL)
    if not json_match:
        return None

    try:
        parsed = json.loads(json_match.group())
        return parsed if isinstance(parsed, list) else None
    except json.JSONDecodeError:
        return None


def _build_signal_prompt(raw_text: str, segment_key: str, objective_key: str) -> str:
    segment_labels = {
        "general": "general households",
        "families": "young families",
        "gig": "gig workers and creators",
        "retirees": "retirees and pre-retirees",
        "hnw": "high-net-worth households",
        "women": "women building financial independence",
    }
    objective_labels = {
        "awareness": "awareness",
        "education": "education",
        "leadgen": "lead generation",
        "retention": "retention",
        "trust": "trust",
    }

    return f"""You are a marketing analyst. Based on the following competitor content or topic, identify up to 5 signal themes for life insurance content strategy and rate their relative strength.

Return ONLY valid JSON: a list of objects with keys title, signal, strength, momentum, hook, format, channel, caption.

Example output:
[
  {{
    "title": "Term vs whole life confusion",
    "signal": "A high-intent clarification topic that tends to spark strong engagement.",
    "strength": 78,
    "momentum": "RISING",
    "hook": "Make the choice feel simple in 30 seconds.",
    "format": "Short-form video",
    "channel": "Instagram / TikTok",
    "caption": "Frame this around awareness for general households."
  }}
]

Input text:
{raw_text}

Audience segment: {segment_labels.get(segment_key, 'general households')}
Primary objective: {objective_labels.get(objective_key, 'awareness')}
"""


def _parse_signal_response(text: str) -> List[Dict]:
    parsed = _extract_json_array(text)
    if not parsed:
        return []

    results = []
    for item in parsed:
        if not isinstance(item, dict):
            continue

        results.append({
            "title": item.get("title", "Untitled signal"),
            "signal": item.get("signal", ""),
            "strength": item.get("strength", 0),
            "momentum": item.get("momentum", "STEADY"),
            "hook": item.get("hook", ""),
            "format": item.get("format", "Short-form video"),
            "channel": item.get("channel", "Instagram / TikTok"),
            "caption": item.get("caption", ""),
        })
    return results


# Page styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --paper: #EAE6D8;
        --paper-deep: #DFDAC4;
        --panel: #F3F0E5;
        --ink: #1C2B39;
        --ink-soft: #4E606F;
        --ink-faint: #7C8894;
        --gold: #B8862B;
        --gold-deep: #8F681E;
        --red: #A13D2B;
        --teal: #2F5D56;
        --line: #C6BFA9;
        --line-strong: #1C2B39;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--paper) !important;
        color: var(--ink) !important;
        font-family: 'IBM Plex Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: var(--paper-deep) !important;
        border-right: 1px solid var(--line);
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    .hero-section {
        padding: 72px 28px 40px;
        background: var(--paper);
    }

    .hero-eyebrow {
        display: flex;
        align-items: center;
        gap: 14px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        color: var(--ink-soft);
        margin-bottom: 26px;
        flex-wrap: wrap;
    }

    .case-no {
        color: var(--red);
    }

    .hero-title {
        font-family: 'Fraunces', serif;
        font-size: clamp(2.6rem, 6vw, 3.6rem);
        line-height: 1.04;
        margin: 0 0 28px;
        max-width: 14ch;
        letter-spacing: -0.01em;
        font-weight: 600;
    }

    .hero-title em {
        font-style: italic;
        color: var(--red);
        font-weight: 500;
    }

    .hero-sub {
        max-width: 620px;
        font-size: 1.08rem;
        color: var(--ink-soft);
        margin: 0 0 34px;
    }

    .hero-actions {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
        margin-bottom: 56px;
    }

    .btn {
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 600;
        font-size: 0.92rem;
        padding: 13px 22px;
        border-radius: 3px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid var(--ink);
        cursor: pointer;
        transition: transform 0.12s ease, background 0.15s ease, color 0.15s ease;
        background: transparent;
        color: var(--ink);
    }

    .btn-primary {
        background: var(--ink);
        color: var(--paper);
        border-color: var(--ink);
    }

    .btn-primary:hover {
        transform: translateY(-1px);
        background: var(--red);
        border-color: var(--red);
    }

    .btn-ghost {
        background: transparent;
        color: var(--ink);
        border-color: var(--ink);
    }

    .btn-ghost:hover {
        background: var(--panel);
    }

    .page-intro {
        padding: 1rem 0 1.4rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.5rem;
    }

    .main-header {
        font-family: 'Fraunces', serif;
        font-size: 2.4rem;
        font-weight: 600;
        color: var(--ink);
        line-height: 1.05;
        letter-spacing: -0.01em;
        margin-bottom: 0.35rem;
    }

    .page-subtitle {
        font-size: 1rem;
        color: var(--ink-soft);
        margin-bottom: 0;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Fraunces', serif;
        color: var(--ink);
        letter-spacing: -0.01em;
    }

    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 3px;
        padding: 1rem;
        box-shadow: 6px 6px 0 rgba(28, 43, 57, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: var(--ink-soft);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-weight: 600;
    }

    [data-testid="stMetricDelta"] {
        color: var(--teal);
    }

    .stButton > button, .stDownloadButton > button {
        background: var(--ink);
        color: var(--paper);
        border: 1px solid var(--ink);
        border-radius: 3px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: background 0.15s ease, border-color 0.15s ease;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background: var(--red);
        border-color: var(--red);
        color: var(--paper);
    }

    .stSelectbox > div, .stTextInput > div, .stTextArea > div {
        border-radius: 3px;
        border: 1px solid var(--line);
        background: var(--paper);
    }

    .stSelectbox > div[data-baseweb="select"],
    .stSelectbox > div[data-baseweb="select"] * {
        color: #D3D3D3 !important;
        opacity: 1 !important;
        text-shadow: none !important;
    }

    .stSelectbox label {
        color: #4E606F !important;
    }

    .stTextArea textarea,
    .stTextInput input,
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        background: #ffffff !important;
        color: #1C2B39 !important;
        border: 1px solid #C6BFA9 !important;
    }

    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: #4E606F !important;
        opacity: 1 !important;
    }

    .stDataFrame, .stTable {
        border: 1px solid var(--line);
        border-radius: 3px;
        overflow: hidden;
    }

    .stTabs [data-testid="stTabList"] {
        gap: 0.6rem;
    }

    .stTabs [data-testid="stTab"] {
        color: var(--ink-soft);
        border-bottom: 2px solid transparent;
        padding-bottom: 0.4rem;
    }

    .stTabs [data-testid="stTab"][aria-selected="true"] {
        color: var(--ink);
        border-color: var(--red);
    }

    .stAlert {
        background: var(--panel);
        border: 1px solid var(--line);
        color: var(--ink);
    }

    .st-bd, .st-cp, .st-dp, .st-es {
        color: var(--ink) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

class Dashboard:
    """Streamlit Dashboard for Insurance Analytics"""
    
    def __init__(self):
        self.data_dir = Path("data/outputs")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.llm = LocalLLMClient()
    
    def _build_theme_catalog(self):
        """Return the themed signal catalog used by the new analysis page."""
        return [
            {
                "id": "term-vs-whole",
                "title": "Term vs. whole life confusion",
                "keywords": ["term life", "whole life", "permanent life", "which policy", "difference between", "confused about"],
                "why": "The single most-searched point of confusion in the category — reliable engagement bait when explained simply.",
                "content_hook": "Make the choice feel simple in 30 seconds."
            },
            {
                "id": "gig-income",
                "title": "Coverage for gig and creator income",
                "keywords": ["gig worker", "freelance", "creator economy", "side hustle", "self employed", "1099", "no employer benefits"],
                "why": "Traditional life insurance marketing still assumes a W-2 job — content that acknowledges gig income earns outsized interest.",
                "content_hook": "Position the brand as the benefits department gig workers never had."
            },
            {
                "id": "grief-finances",
                "title": "Grief-proofing your family's finances",
                "keywords": ["grief", "loss of a loved one", "funeral costs", "what happens if i die", "family after i'm gone", "final expenses"],
                "why": "Emotionally resonant and rarely addressed head-on by competitors — differentiated ground if handled with care.",
                "content_hook": "Reframe coverage as removing logistical weight from grief."
            },
            {
                "id": "retirement-gap",
                "title": "The retirement income gap",
                "keywords": ["retirement income", "outliving savings", "pension gap", "401k shortfall", "retire early", "income gap"],
                "why": "Rising concern among pre-retirees as pensions disappear — high-intent audience actively researching solutions.",
                "content_hook": "Replace vague retirement anxiety with one concrete number."
            },
            {
                "id": "kids-education",
                "title": "Locking in your kids' future costs",
                "keywords": ["child education", "college fund", "kids future", "education costs", "save for college", "new parent"],
                "why": "New-parent audiences over-index on planning content shared within family networks.",
                "content_hook": "Frame early coverage as a financial hedge against future cost inflation."
            },
            {
                "id": "women-independence",
                "title": "Women building financial independence",
                "keywords": ["women and money", "financial independence", "gender pay gap", "single income woman", "women investing"],
                "why": "Growing, underserved content niche — competitors mostly market to households, not individual women directly.",
                "content_hook": "Speak to women as primary financial decision-makers, not dependents."
            },
            {
                "id": "debt-protection",
                "title": "Debt doesn't disappear when you do",
                "keywords": ["debt", "mortgage protection", "co-signed loan", "student loan death", "who pays my debt"],
                "why": "A blunt, high-clarity angle that performs well as a pattern interrupt in feeds full of soft lifestyle content.",
                "content_hook": "Use the blunt truth about debt transfer as a wake-up-call entry point."
            },
            {
                "id": "ai-claims-speed",
                "title": "Faster claims, less paperwork",
                "keywords": ["claims process", "how long do claims take", "paperwork", "digital claims", "ai underwriting", "instant approval"],
                "why": "Operational-trust content performs well post-purchase and counters the industry's reputation for slow claims.",
                "content_hook": "Build trust by making the claims process visible and specific."
            },
            {
                "id": "tax-advantage",
                "title": "Tax-advantaged uses of life insurance",
                "keywords": ["tax free", "tax advantage", "estate planning", "cash value", "tax efficient", "wealth transfer"],
                "why": "High-value topic for HNW audiences — dense but converts well when simplified into scenarios.",
                "content_hook": "Position coverage as a legitimate estate and tax planning tool."
            },
            {
                "id": "mental-health-money",
                "title": "Financial stress and mental health",
                "keywords": ["financial stress", "money anxiety", "mental health", "financial wellbeing", "money worry"],
                "why": "Cross-category topic with strong organic reach — connects protection planning to a broader wellbeing conversation.",
                "content_hook": "Sell peace of mind as a mental-health outcome, not a financial product feature."
            },
            {
                "id": "bundled-health",
                "title": "Bundling life and health coverage",
                "keywords": ["bundle", "health insurance", "combined coverage", "life and health", "package plan"],
                "why": "Practical, cost-driven angle that resonates during open-enrollment adjacent periods.",
                "content_hook": "Use cost-consolidation as a low-friction reason to open a policy review conversation."
            },
            {
                "id": "climate-longevity",
                "title": "Longer lifespans, longer plans",
                "keywords": ["life expectancy", "longevity", "living longer", "climate risk", "outlive your plan"],
                "why": "Emerging long-horizon topic — early-mover content advantage while most competitors have not touched it yet.",
                "content_hook": "Use rising life expectancy as a fresh, optimistic reason to revisit coverage assumptions."
            },
            {
                "id": "creator-economy-risk",
                "title": "Protecting a personal brand's income",
                "keywords": ["personal brand", "influencer income", "content creator", "brand deals", "youtube income"],
                "why": "Fast-growing, under-addressed niche as more of the workforce monetizes personal audiences directly.",
                "content_hook": "Speak directly to creators about protecting monetized personal brands."
            },
            {
                "id": "myths-mythbusting",
                "title": "Busting the 'it's too expensive' myth",
                "keywords": ["too expensive", "can't afford", "life insurance cost", "myth", "misconception"],
                "why": "Consistently one of the highest-performing evergreen formats in the category — cost perception, not cost reality, is the barrier.",
                "content_hook": "Anchor the cost conversation to a relatable daily spend comparison."
            },
            {
                "id": "family-story",
                "title": "Real family protection stories",
                "keywords": ["real story", "customer story", "policyholder", "family protected", "testimonial"],
                "why": "Trust-building social proof — outperforms product-forward content on conversion in retargeting.",
                "content_hook": "Let a single specific story carry the proof burden instead of brand claims."
            },
            {
                "id": "beneficiary-mistakes",
                "title": "Beneficiary mistakes people don't notice",
                "keywords": ["beneficiary", "outdated policy", "forgot to update", "ex spouse policy", "policy review"],
                "why": "Low-competition, high-utility topic that drives existing-policyholder engagement and retention.",
                "content_hook": "Turn a mundane policy-hygiene task into a proactive retention touchpoint."
            },
            {
                "id": "young-adult-first-policy",
                "title": "Buying your first policy in your 20s",
                "keywords": ["first policy", "buy life insurance young", "insurance in my 20s", "early coverage"],
                "why": "Category-education content aimed at first-time buyers, positioned to capture long-term customer value early.",
                "content_hook": "Frame early purchase as a financial optimization, not a morbid milestone."
            },
            {
                "id": "policy-comparison-tools",
                "title": "Making quotes easy to compare",
                "keywords": ["compare quotes", "which company", "insurance comparison", "shopping for insurance", "get a quote"],
                "why": "High commercial intent — audiences actively in a buying window respond well to comparison-format content.",
                "content_hook": "Remove the friction and pressure people associate with getting a quote."
            },
            {
                "id": "small-business-owner",
                "title": "Coverage for small business owners",
                "keywords": ["small business owner", "key person insurance", "business succession", "buy sell agreement"],
                "why": "Under-marketed B2B-adjacent niche with high policy values and strong LinkedIn performance.",
                "content_hook": "Address succession and key-person risk as a business continuity issue."
            },
            {
                "id": "digital-first-experience",
                "title": "No medical exam, fully digital signup",
                "keywords": ["no medical exam", "digital signup", "online application", "instant quote", "app based"],
                "why": "Convenience-led content that converts well against competitors still requiring in-person underwriting.",
                "content_hook": "Make application speed itself the headline differentiator."
            },
        ]

    def _score_theme(self, theme, text_lower):
        """Score a theme against a text input using keyword presence and loose word matching."""
        if not text_lower:
            return 0

        score = 0
        for keyword in theme.get("keywords", []):
            if keyword in text_lower:
                score += 3 if " " in keyword else 2
            else:
                first_word = keyword.split(" ")[0]
                if len(first_word) > 4 and first_word in text_lower:
                    score += 1

        if any(token in text_lower for token in ["why", "how", "best", "compare", "cost", "claim", "retirement", "family"]):
            score += 1

        return score

    def _build_signal_results(self, raw_text, segment_key, objective_key):
        """Build the signal-ledger and content-docket results for the new page."""
        segment_labels = {
            "general": "general households",
            "families": "young families",
            "gig": "gig workers and creators",
            "retirees": "retirees and pre-retirees",
            "hnw": "high-net-worth households",
            "women": "women building financial independence",
        }
        objective_labels = {
            "awareness": "awareness",
            "education": "education",
            "leadgen": "lead generation",
            "retention": "retention",
            "trust": "trust",
        }

        text_lower = (raw_text or "").lower()
        themes = self._build_theme_catalog()
        scored_themes = []

        for theme in themes:
            score = self._score_theme(theme, text_lower)
            if score > 0:
                scored_themes.append(theme | {"score": score})

        if not scored_themes:
            scored_themes = [theme | {"score": 1} for theme in themes[:4]]

        scored_themes = sorted(scored_themes, key=lambda item: item["score"], reverse=True)[:5]

        ledger = []
        docket = []
        for index, item in enumerate(scored_themes):
            pct = min(96, 58 + item["score"] * 8 + index * 2)
            if pct >= 80:
                momentum = "PEAKING"
            elif pct >= 64:
                momentum = "RISING"
            else:
                momentum = "STEADY"

            ledger.append({
                "Theme": item["title"],
                "Signal": item["why"],
                "Score": f"{pct}%",
                "Momentum": momentum,
            })

            docket.append({
                "Format": "Short-form video" if index < 2 else "Email nurture",
                "Hook": f"{item['content_hook']} for {segment_labels.get(segment_key, 'your audience')}.",
                "Caption": f"Frame this around {objective_labels.get(objective_key, 'awareness')} and make the point feel immediately useful.",
                "Channel": "Instagram / TikTok" if index < 2 else "Email / LinkedIn",
            })

        return ledger, docket

    def _build_fallback_signals(self, raw_text: str, segment_key: str, objective_key: str) -> List[Dict]:
        """Generate a deterministic keyword-based signal set when Ollama is unavailable."""
        segment_labels = {
            "general": "general households",
            "families": "young families",
            "gig": "gig workers and creators",
            "retirees": "retirees and pre-retirees",
            "hnw": "high-net-worth households",
            "women": "women building financial independence",
        }
        objective_labels = {
            "awareness": "awareness",
            "education": "education",
            "leadgen": "lead generation",
            "retention": "retention",
            "trust": "trust",
        }

        text_lower = (raw_text or "").lower()
        themes = self._build_theme_catalog()
        scored_themes = []

        for theme in themes:
            raw = self._score_theme(theme, text_lower)
            if raw > 0:
                scored_themes.append(theme | {"raw": raw})

        if not scored_themes:
            scored_themes = [theme | {"raw": 0} for theme in themes[:4]]

        scored_themes = sorted(scored_themes, key=lambda item: item["raw"], reverse=True)
        matched = scored_themes[:5]
        max_raw = max((item["raw"] for item in matched), default=1)

        results = []
        for index, item in enumerate(matched):
            raw = item["raw"]
            if raw > 0:
                pct = max(38, min(97, round(48 + (raw / (max_raw + 2)) * 48)))
            else:
                pct = max(38, min(97, round(70 - index * 9)))

            if pct >= 78:
                momentum = "PEAKING"
            elif pct >= 55:
                momentum = "RISING"
            else:
                momentum = "STEADY"

            results.append({
                "title": item["title"],
                "signal": item["why"],
                "strength": pct,
                "momentum": momentum,
                "hook": f"{item['content_hook']} for {segment_labels.get(segment_key, 'your audience')}.",
                "format": "Short-form video" if index < 2 else "Email nurture",
                "channel": "Instagram / TikTok" if index < 2 else "Email / LinkedIn",
                "caption": f"Frame this around {objective_labels.get(objective_key, 'awareness')} and make the point feel immediately useful.",
            })

        return results

    def _render_signal_ledger(self, signals: List[Dict]) -> str:
        rows = []
        for idx, item in enumerate(signals, start=1):
            strength = int(item.get("strength", 0) or 0)
            strength = max(0, min(100, strength))
            momentum = item.get("momentum", "STEADY")
            rows.append(
                "<div class='ledger-row'>"
                f"<div class='ledger-idx'>{idx}</div>"
                f"<div class='ledger-topic'><strong>{item.get('title', 'Untitled signal')}</strong>"
                f"<div class='ledger-why'>{item.get('signal', '')}</div></div>"
                f"<div class='ledger-momentum'>{momentum}</div>"
                "<div class='ledger-bar-wrap'>"
                f"<div class='ledger-bar'><div class='ledger-bar-fill' style='width:{strength}%;'></div></div>"
                f"<div class='ledger-score'>{strength}%</div>"
                "</div></div>"
            )

        return (
            "<div class='result-block'>"
            "<div class='result-head'>"
            "<span class='section-no'>A</span>"
            "<h3>Signal Ledger</h3>"
            "<span class='result-note'>Themes matched to your file, ranked by current signal strength</span>"
            "</div>"
            "<div class='ledger-table'>"
            "<div class='ledger-head'>"
            "<div>#</div><div>Theme</div><div>Momentum</div><div>Strength</div>"
            "</div>"
            + "".join(rows)
            + "</div></div>"
        )

    def _render_content_docket(self, signals: List[Dict]) -> str:
        cards = []
        for item in signals:
            cards.append(
                "<div class='docket-card'>"
                f"<div class='docket-format'>{item.get('format', 'Short-form video')}</div>"
                f"<div class='docket-hook'>{item.get('hook', '')}</div>"
                f"<p class='docket-caption'>{item.get('caption', '')}</p>"
                f"<div class='docket-channel'>{item.get('channel', 'Instagram / TikTok')}</div>"
                "</div>"
            )

        return (
            "<div class='result-block'>"
            "<div class='result-head'>"
            "<span class='section-no'>B</span>"
            "<h3>Content Docket</h3>"
            "<span class='result-note'>Ready-to-shoot ideas pulled from the top signals</span>"
            "</div>"
            "<div class='docket-grid'>"
            + "".join(cards)
            + "</div></div>"
        )

    def _build_open_file_html(self, signals: List[Dict]) -> str:
        body = self._render_signal_ledger(signals) + self._render_content_docket(signals)
        return f"""
        <!DOCTYPE html>
        <html lang='en'>
        <head>
          <meta charset='utf-8' />
          <style>
            html, body {{ margin: 0; padding: 0; font-family: 'IBM Plex Sans', sans-serif; color: #1C2B39; background-color: #EAE6D8; }}
            body {{ background-color: #EAE6D8; }}
            .result-block{{ margin: 44px 0 32px; background: transparent; }}
            .result-head{{ display:flex; flex-direction: row; align-items: baseline; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }}
            .result-head h3{{ font-family: 'Fraunces', serif; font-size: 2.05rem; font-weight: 600; margin:0; line-height: 1.05; }}
            .result-head .section-no{{ width:28px; height:28px; font-size:.75rem; border: 1px solid #1C2B39; color: #1C2B39; display:flex; align-items:center; justify-content:center; border-radius: 6px; flex-shrink: 0; }}
            .result-note{{ font-size: .88rem; color: #4E606F; margin:0; white-space: nowrap; }}
            .ledger-table{{ border-top: 1px solid #1C2B39; }}
            .ledger-head{{ display:grid; grid-template-columns: 32px 1.8fr 110px 1.3fr; gap: 14px; padding: 14px 8px; font-family: 'IBM Plex Mono', monospace; font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; color: #4E606F; }}
            .ledger-row{{ display:grid; grid-template-columns: 32px 1.8fr 110px 1.3fr; gap: 14px; align-items:center; padding: 16px 8px; border-bottom: 1px solid #C6BFA9; }}
            .ledger-idx{{ font-family: 'IBM Plex Mono', monospace; color: #4E606F; font-size: .78rem; }}
            .ledger-topic{{ display:flex; flex-direction:column; gap: 6px; }}
            .ledger-topic strong{{ font-size: .95rem; font-weight: 600; }}
            .ledger-why{{ font-size: .86rem; color: #4E606F; line-height: 1.4; }}
            .ledger-momentum{{ font-family: 'IBM Plex Mono', monospace; font-size: .72rem; letter-spacing:.06em; font-weight:600; padding: 6px 10px; border-radius: 20px; background: rgba(47, 93, 86, 0.1); justify-self:start; }}
            .ledger-bar-wrap{{ display:flex; align-items:center; gap:8px; }}
            .ledger-bar{{ height:8px; background: #C6BFA9; border-radius: 999px; flex:1; overflow:hidden; }}
            .ledger-bar-fill{{ height:100%; background: #B8862B; border-radius:999px; }}
            .ledger-score{{ font-family: 'IBM Plex Mono', monospace; font-size: .72rem; color: #4E606F; width: 34px; text-align:right; }}
            .docket-grid{{ display:grid; grid-template-columns: repeat(auto-fill, minmax(260px,1fr)); gap: 18px; }}
            .docket-card{{ background: #F3F0E5; border: 1px solid #C6BFA9; border-radius: 14px; padding: 20px; display:flex; flex-direction:column; gap: 12px; min-height: 220px; }}
            .docket-format{{ font-family: 'IBM Plex Mono', monospace; font-size: .68rem; letter-spacing:.08em; text-transform:uppercase; color: #2F5D56; border: 1px solid #2F5D56; border-radius: 999px; padding: 5px 12px; width: fit-content; }}
            .docket-hook{{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.05rem; line-height:1.3; margin:0; }}
            .docket-caption{{ font-size: .9rem; color: #4E606F; margin:0; flex:1; }}
            .docket-channel{{ font-family: 'IBM Plex Mono', monospace; font-size: .72rem; color: #4E606F; margin-top: auto; padding-top: 8px; border-top: 1px dashed #C6BFA9; }}
          </style>
        </head>
        <body>
          {body}
        </body>
        </html>
        """

    def show_hero(self):
        """Show hero section"""
        st.markdown("""
        <div class="hero-section">
            <div class="hero-eyebrow">
                <span class="case-no">CASE FILE # LICSA-07</span>
                <span>—</span>
                <span>CONTENT INTELLIGENCE, LIFE & PROTECTION CATEGORY</span>
            </div>
            <h1 class="hero-title">Every competitor post <em>is a signal.</em> We read the file.</h1>
            <p class="hero-sub">Paste a competitor's caption, ad, or article — or just name a topic. LICSA cross-references it against a life-insurance content ledger and hands back the themes worth reacting to, what to post, and what campaign to build around it.</p>
            <div class="hero-actions">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔽 Main Menu", use_container_width=True, key="btn_ledger"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        with col2:
            if st.button("📊 Data Sources", use_container_width=True, key="btn_data"):
                st.session_state.current_page = "data_management"
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

    def show_open_file_page(self):
        """Render the signal lab page using the local Ollama model for analysis."""
        col1, col2 = st.columns([9, 1])
        with col2:
            if st.button("← Back", key="back_from_open_file"):
                st.session_state.current_page = "hero"
                st.rerun()

        st.sidebar.markdown("### Navigation")
        if st.sidebar.button("← Back to Home", use_container_width=True, key="sidebar_back_open_file"):
            st.session_state.current_page = "hero"
            st.rerun()

        st.markdown("<div style='margin: 0 0 1rem 0;'><h1 style='font-family: Fraunces, serif; margin-bottom: 0.25rem;'>Open a File</h1><p style='color: #4E606F; margin: 0;'>A styled version of the website's signal lab experience, now powered by the local Ollama model.</p></div>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Open a text file", type=["txt", "md", "json", "csv"], key="open_file_upload")
        if uploaded_file is not None:
            source_text = uploaded_file.read().decode("utf-8", errors="ignore")
        else:
            source_text = st.text_area(
                "Paste a competitor caption, ad, article, or topic",
                height=180,
                placeholder="e.g. term life vs whole life for young families",
                key="signal_input"
            )

        segment_key = st.selectbox(
            "Audience segment",
            ["general", "families", "gig", "retirees", "hnw", "women"],
            format_func=lambda key: {
                "general": "General households",
                "families": "Young families",
                "gig": "Gig workers and creators",
                "retirees": "Retirees and pre-retirees",
                "hnw": "High-net-worth households",
                "women": "Women building financial independence",
            }[key],
            key="signal_segment"
        )

        objective_key = st.selectbox(
            "Primary objective",
            ["awareness", "education", "leadgen", "retention", "trust"],
            format_func=lambda key: {
                "awareness": "Awareness",
                "education": "Education",
                "leadgen": "Lead generation",
                "retention": "Retention",
                "trust": "Trust",
            }[key],
            key="signal_objective"
        )

        if st.button("Run signal engine", key="run_signal_engine"):
            if not source_text or not source_text.strip():
                st.warning("Paste some text or upload a file to generate signals.")
            else:
                prompt = _build_signal_prompt(source_text, segment_key, objective_key)
                raw_response = self.llm.generate(prompt)
                signals = _parse_signal_response(raw_response)
                using_fallback = False

                if not signals:
                    signals = self._build_fallback_signals(source_text, segment_key, objective_key)
                    using_fallback = True

                signals = sorted(signals, key=lambda item: item.get("strength", 0), reverse=True)

                if using_fallback:
                    st.info("Ollama was not reachable, so the app used its built-in signal generator. For richer AI output, connect a hosted LLM API instead of a localhost Ollama server.")

                html_output = self._build_open_file_html(signals)
                components.html(html_output, height=780, scrolling=True)
    
    def run(self):
        """Run the dashboard"""
        # Show hero first
        if st.session_state.current_page == "hero":
            self.show_hero()
        elif st.session_state.current_page == "dashboard":
            self.show_dashboard()
        elif st.session_state.current_page == "brand_profiles":
            self.show_brand_profiles()
        elif st.session_state.current_page == "competitor_benchmark":
            self.show_competitor_benchmark()
        elif st.session_state.current_page == "reviews_analysis":
            self.show_reviews_analysis()
        elif st.session_state.current_page == "data_management":
            self.show_data_management()
        elif st.session_state.current_page == "open_file":
            self.show_open_file_page()
    
    def show_dashboard(self):
        """Show main dashboard"""
        # Add back button to hero
        col1, col2 = st.columns([9, 1])
        with col2:
            if st.button("← Back", key="back_from_dash"):
                st.session_state.current_page = "hero"
                st.rerun()
        
        # Sidebar navigation
        st.sidebar.markdown("### Explore More")
        if st.sidebar.button("📋 Brand Profiles", use_container_width=True):
            st.session_state.current_page = "brand_profiles"
            st.rerun()
        
        if st.sidebar.button("📊 Competitor Benchmark", use_container_width=True):
            st.session_state.current_page = "competitor_benchmark"
            st.rerun()
        
        if st.sidebar.button("💬 Review Analysis", use_container_width=True):
            st.session_state.current_page = "reviews_analysis"
            st.rerun()

        if st.sidebar.button("📂 Content Docket", use_container_width=True):
            st.session_state.current_page = "open_file"
            st.rerun()
        
        st.markdown(
            "<div class='page-intro'><div class='main-header'>The Ledger</div><div class='page-subtitle'>Insurance industry content strategy insights</div></div>",
            unsafe_allow_html=True,
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Companies Analyzed", 4, "HDFC, LIC, ICICI, SBI")
        
        with col2:
            st.metric("Dimensions Tracked", 8)
        
        with col3:
            st.metric("Documents Processed", "1000+")
        
        with col4:
            st.metric("Analysis Status", "Active")
        
        st.divider()
        
        # Overview section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Perception Dimension Rankings")
            
            # Sample data
            benchmark_data = {
                'Company': ['HDFC Life', 'LIC', 'ICICI Prudential', 'SBI Life'],
                'Trust': [8.5, 8.2, 7.8, 7.5],
                'Innovation': [8.1, 6.5, 8.3, 6.8],
                'Customer Service': [7.9, 7.2, 8.0, 7.5],
                'Digital Experience': [8.2, 5.8, 7.5, 6.5]
            }
            
            df = pd.DataFrame(benchmark_data)
            
            fig = go.Figure()
            for company in df['Company']:
                fig.add_trace(go.Scatterpolar(
                    r=[df.loc[df['Company'] == company, col].values[0] for col in ['Trust', 'Innovation', 'Customer Service', 'Digital Experience']],
                    theta=['Trust', 'Innovation', 'Customer Service', 'Digital Experience'],
                    fill='toself',
                    name=company
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Overall Perception Score")
            
            overall_scores = {
                'Company': ['HDFC Life', 'LIC', 'ICICI Prudential', 'SBI Life'],
                'Score': [8.2, 7.4, 7.9, 7.3]
            }
            
            df_overall = pd.DataFrame(overall_scores)
            fig_bar = px.bar(
                df_overall,
                x='Company',
                y='Score',
                color='Score',
                color_continuous_scale='RdYlGn',
                range_color=[0, 10],
                labels={'Score': 'Perception Score (0-10)'}
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
    
    def show_brand_profiles(self):
        """Show individual brand profiles"""
        col1, col2 = st.columns([9, 1])
        with col2:
            if st.button("← Back", key="back_from_profiles"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        # Sidebar navigation
        st.sidebar.markdown("### Navigation")
        if st.sidebar.button("← Back to Dashboard", use_container_width=True, key="sidebar_back_profiles"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        st.header("Brand Profiles")
        
        company = st.selectbox(
            "Select Company",
            ["HDFC Life", "LIC", "ICICI Prudential Life", "SBI Life"]
        )
        
        # Sample brand profile data
        profiles = {
            "HDFC Life": {
                "positioning": "Digital-first, innovative insurance solutions",
                "claims": ["Fast claim settlement", "Digital-first approach", "Comprehensive products"],
                "trust_signals": ["20+ years in market", "High claim settlement ratio", "Strong financial rating"],
                "themes": ["Innovation", "Convenience", "Security"],
                "segments": ["Young professionals", "Families", "Self-employed"]
            },
            "LIC": {
                "positioning": "Legacy and trust in Indian insurance",
                "claims": ["Largest insurer in India", "Government backed", "Widest network"],
                "trust_signals": ["67+ years", "Government ownership", "Massive distribution"],
                "themes": ["Trust", "Legacy", "National pride"],
                "segments": ["Middle class", "Rural", "Traditional"]
            },
            "ICICI Prudential Life": {
                "positioning": "Customer-centric, innovative financial solutions",
                "claims": ["Customer-first approach", "Innovative products", "Tech-enabled"],
                "trust_signals": ["23+ years", "International parent", "High customer ratings"],
                "themes": ["Innovation", "Efficiency", "Transparency"],
                "segments": ["Urban professionals", "HNIs", "Tech-savvy"]
            },
            "SBI Life": {
                "positioning": "Reliable banking partnership in insurance",
                "claims": ["SBI partnership", "Accessibility", "Trust"],
                "trust_signals": ["SBI network", "Financial strength", "Established presence"],
                "themes": ["Trust", "Accessibility", "Banking integration"],
                "segments": ["SBI customers", "Middle class", "Families"]
            }
        }
        
        profile = profiles.get(company, {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Positioning")
            st.write(profile.get("positioning", ""))
            
            st.subheader("Main Claims")
            for claim in profile.get("claims", []):
                st.write(f"✓ {claim}")
        
        with col2:
            st.subheader("Trust Signals")
            for signal in profile.get("trust_signals", []):
                st.write(f"• {signal}")
            
            st.subheader("Emotional Themes")
            themes = profile.get("themes", [])
            st.write(", ".join(themes))
        
        st.subheader("Target Segments")
        segments = profile.get("segments", [])
        for segment in segments:
            st.write(f"→ {segment}")
        
        # Perception scores for this company
        st.subheader("Perception Dimension Scores")
        
        scores_data = {
            "HDFC Life": {'Trust': 8.5, 'Innovation': 8.1, 'Customer Service': 7.9, 'Digital': 8.2, 'Affordability': 7.0, 'Security': 8.3, 'Transparency': 7.8, 'Legacy': 7.2},
            "LIC": {'Trust': 8.2, 'Innovation': 6.5, 'Customer Service': 7.2, 'Digital': 5.8, 'Affordability': 8.0, 'Security': 8.5, 'Transparency': 7.5, 'Legacy': 9.2},
            "ICICI Prudential Life": {'Trust': 7.8, 'Innovation': 8.3, 'Customer Service': 8.0, 'Digital': 7.5, 'Affordability': 6.8, 'Security': 8.2, 'Transparency': 8.1, 'Legacy': 6.5},
            "SBI Life": {'Trust': 7.5, 'Innovation': 6.8, 'Customer Service': 7.5, 'Digital': 6.5, 'Affordability': 7.2, 'Security': 8.0, 'Transparency': 7.5, 'Legacy': 7.3}
        }
        
        scores = scores_data.get(company, {})
        
        df_scores = pd.DataFrame(list(scores.items()), columns=['Dimension', 'Score'])
        
        fig_scores = px.bar(
            df_scores,
            x='Dimension',
            y='Score',
            color='Score',
            color_continuous_scale='Blues',
            range_color=[0, 10]
        )
        
        st.plotly_chart(fig_scores, use_container_width=True)
    
    def show_competitor_benchmark(self):
        """Show competitor benchmark"""
        col1, col2 = st.columns([9, 1])
        with col2:
            if st.button("← Back", key="back_from_benchmark"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        # Sidebar navigation
        st.sidebar.markdown("### Navigation")
        if st.sidebar.button("← Back to Dashboard", use_container_width=True, key="sidebar_back_benchmark"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        st.header("Competitor Benchmark")
        
        dimension = st.selectbox(
            "Select Dimension",
            ["Trust & Reliability", "Innovation", "Customer Service", "Digital Experience",
             "Affordability", "Security & Protection", "Transparency", "Brand Legacy"]
        )
        
        # Benchmark data
        benchmark_scores = {
            "Trust & Reliability": {'HDFC Life': 8.5, 'LIC': 8.2, 'ICICI Prudential Life': 7.8, 'SBI Life': 7.5},
            "Innovation": {'HDFC Life': 8.1, 'ICICI Prudential Life': 8.3, 'SBI Life': 6.8, 'LIC': 6.5},
            "Customer Service": {'HDFC Life': 7.9, 'ICICI Prudential Life': 8.0, 'SBI Life': 7.5, 'LIC': 7.2},
            "Digital Experience": {'HDFC Life': 8.2, 'ICICI Prudential Life': 7.5, 'SBI Life': 6.5, 'LIC': 5.8},
            "Affordability": {'LIC': 8.0, 'SBI Life': 7.2, 'HDFC Life': 7.0, 'ICICI Prudential Life': 6.8},
            "Security & Protection": {'LIC': 8.5, 'HDFC Life': 8.3, 'ICICI Prudential Life': 8.2, 'SBI Life': 8.0},
            "Transparency": {'ICICI Prudential Life': 8.1, 'HDFC Life': 7.8, 'LIC': 7.5, 'SBI Life': 7.5},
            "Brand Legacy": {'LIC': 9.2, 'HDFC Life': 7.2, 'SBI Life': 7.3, 'ICICI Prudential Life': 6.5}
        }
        
        scores = benchmark_scores.get(dimension, {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Benchmark chart
            df_bench = pd.DataFrame(list(scores.items()), columns=['Company', 'Score']).sort_values('Score', ascending=True)
            
            fig_bench = px.bar(
                df_bench,
                x='Score',
                y='Company',
                orientation='h',
                color='Score',
                color_continuous_scale='RdYlGn',
                range_color=[0, 10]
            )
            
            fig_bench.update_layout(xaxis_title=f"Score (0-10)", yaxis_title="")
            
            st.plotly_chart(fig_bench, use_container_width=True)
        
        with col2:
            st.subheader("Key Insights")
            
            if scores:
                leader = max(scores, key=scores.get)
                leader_score = scores[leader]
                
                st.info(f"🏆 Leader: {leader} ({leader_score}/10)")
                
                # Show gaps
                st.subheader("Performance Gaps")
                for company, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                    gap = leader_score - score
                    if gap > 0:
                        st.write(f"{company}: {score}/10 (gap: -{gap:.1f})")
    
    def show_reviews_analysis(self):
        """Show customer review analysis"""
        col1, col2 = st.columns([9, 1])
        with col2:
            if st.button("← Back", key="back_from_reviews"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        # Sidebar navigation
        st.sidebar.markdown("### Navigation")
        if st.sidebar.button("← Back to Dashboard", use_container_width=True, key="sidebar_back_reviews"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        st.header("Customer Reviews Analysis")
        
        company = st.selectbox(
            "Select Company",
            ["HDFC Life", "LIC", "ICICI Prudential Life", "SBI Life"],
            key="reviews_company"
        )
        
        # Sample sentiment data
        sentiment_data = {
            "HDFC Life": {'positive': 68, 'neutral': 22, 'negative': 10},
            "LIC": {'positive': 55, 'neutral': 30, 'negative': 15},
            "ICICI Prudential Life": {'positive': 70, 'neutral': 20, 'negative': 10},
            "SBI Life": {'positive': 60, 'neutral': 25, 'negative': 15}
        }
        
        sentiment = sentiment_data.get(company, {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment distribution
            df_sentiment = pd.DataFrame([sentiment])
            
            fig_sentiment = go.Figure(data=[
                go.Pie(
                    labels=['Positive', 'Neutral', 'Negative'],
                    values=[sentiment.get('positive', 0), sentiment.get('neutral', 0), sentiment.get('negative', 0)],
                    marker=dict(colors=['green', 'gray', 'red'])
                )
            ])
            
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            st.metric("Overall Sentiment Score", f"{sentiment.get('positive', 0) - sentiment.get('negative', 0)/2:.0f}%", "Positive")
            
            st.subheader("Review Distribution")
            st.write(f"✅ Positive: {sentiment.get('positive', 0)}%")
            st.write(f"⚪ Neutral: {sentiment.get('neutral', 0)}%")
            st.write(f"❌ Negative: {sentiment.get('negative', 0)}%")
        
        st.subheader("Top Praised Aspects")
        praised = {
            "HDFC Life": ["Customer Service", "Digital Platform", "Fast Settlement", "Product Range"],
            "LIC": ["Trust", "Widest Network", "Financial Strength", "Government Backing"],
            "ICICI Prudential Life": ["Innovation", "Transparency", "Technology", "Customer Support"],
            "SBI Life": ["Bank Partnership", "Accessibility", "Reliability", "Product Quality"]
        }
        
        for i, aspect in enumerate(praised.get(company, []), 1):
            st.write(f"{i}. {aspect}")
        
        st.subheader("Common Complaints")
        complaints = {
            "HDFC Life": ["Premium Rates", "Complex Policies", "Claim Process Delays"],
            "LIC": ["Digital Limitations", "Slow Service", "Documentation Requirements"],
            "ICICI Prudential Life": ["Premium Pricing", "Limited Branch Network"],
            "SBI Life": ["Limited Digital Features", "Customer Service Response Time"]
        }
        
        for i, complaint in enumerate(complaints.get(company, []), 1):
            st.write(f"{i}. {complaint}")
    
    def show_data_management(self):
        """Show data management interface"""
        col1, col2 = st.columns([9, 1])
        with col2:
            if st.button("← Back", key="back_from_data"):
                st.session_state.current_page = "hero"
                st.rerun()
        
        # Sidebar navigation
        st.sidebar.markdown("### Navigation")
        if st.sidebar.button("← Back to Home", use_container_width=True, key="sidebar_back_data"):
            st.session_state.current_page = "hero"
            st.rerun()
        
        st.header("Data Management")
        
        tab1, tab2, tab3 = st.tabs(["Data Overview", "Collection Status", "Export Data"])
        
        with tab1:
            st.subheader("Data Statistics")
            
            stats = {
                "Total Documents Processed": "1,247",
                "Total Text Chunks": "3,892",
                "Companies Analyzed": "4",
                "Data Sources": "5",
                "Last Updated": "Today 10:30 AM"
            }
            
            col1, col2, col3 = st.columns(3)
            
            for idx, (key, value) in enumerate(stats.items()):
                if idx < 2:
                    with col1:
                        st.metric(key, value)
                elif idx < 4:
                    with col2:
                        st.metric(key, value)
                else:
                    with col3:
                        st.metric(key, value)
        
        with tab2:
            st.subheader("Collection Status")
            
            status_data = {
                'Source': ['Website', 'Annual Reports', 'Brochures', 'Press Releases', 'Reviews'],
                'Status': ['Active', 'Active', 'Active', 'Pending', 'In Progress'],
                'Documents': [420, 180, 150, 45, 452]
            }
            
            df_status = pd.DataFrame(status_data)
            st.dataframe(df_status, use_container_width=True)
        
        with tab3:
            st.subheader("Export Analysis")
            
            export_format = st.radio("Select Format", ["JSON", "CSV", "PDF", "Excel"])
            
            if st.button("Generate Export"):
                st.success(f"Export in {export_format} format ready for download")
                st.download_button(
                    label=f"Download {export_format}",
                    data="Sample data...",
                    file_name=f"insurance_analysis.{export_format.lower()}"
                )


def main():
    """Main entry point"""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
