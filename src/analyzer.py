import json
import logging
import re
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Any
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an elite Senior Tech & Finance Analyst briefing Rudransh Rastogi, an MBA student at IIM Rohtak specializing in Finance and Tech.
Your mission is to filter through the noise of daily global tech news and deliver high-signal, plain-English synthesis.

Structure your analysis strictly into this JSON format:
{
  "top_story": {
    "headline": "Punchy headline of the single most consequential tech/business story today",
    "source_name": "Publisher Name",
    "what_happened": "2-3 clear, jargon-free sentences explaining the event.",
    "why_it_matters": "2 sentences on business, financial, or strategic impact (e.g. market valuation, enterprise adoption, competitive moat, capital expenditure).",
    "source_url": "EXACT URL link from the article provided below"
  },
  "business_and_markets": [
    {
      "title": "Business / Venture / Market Story Title",
      "publisher": "CNBC / TechCrunch / VentureBeat / Wired",
      "plain_english": "What happened in simple terms regarding enterprise software, venture capital, acquisitions, or market dynamics.",
      "financial_takeaway": "Commercial angle, revenue potential, cost of compute, or investor takeaway.",
      "source_url": "EXACT URL link from the article provided below"
    }
  ],
  "breakthroughs": [
    {
      "title": "Model or Tech Release Name",
      "lab": "Company / Research Lab",
      "plain_english": "What this new AI model or tool does in simple words, and how it differs from previous versions.",
      "market_impact": "Commercial viability, cost-efficiency, or enterprise disruption angle.",
      "source_url": "EXACT URL link from the article provided below"
    }
  ],
  "concept_of_the_day": {
    "term": "A technical AI/tech concept from today's news (e.g., Mixture of Experts, Context Window, Inference Compute, Fine-tuning vs RAG)",
    "plain_english_definition": "Intuitive explanation that any MBA or business executive can instantly grasp.",
    "business_analogy": "A relatable finance, business, or operational analogy."
  },
  "quick_bites": [
    {
      "text": "Short 1-line update on funding, regulatory moves, or tech updates",
      "source_name": "Publisher Name",
      "source_url": "EXACT URL link from the article provided below"
    }
  ]
}

Ensure all explanations are crisp, highly readable, and free of overly dense academic jargon. Feature a balanced mix of business/finance updates and AI tech models. Always include the exact source_url for every story so the reader can click to read the full source. Return ONLY the JSON object.
"""

def synthesize_with_gemini(articles: List[Dict], api_key: str, model: str = "gemini-3.6-flash") -> Dict[str, Any]:
    """Call Google Gemini API via REST."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # Prepare articles text
    condensed_articles = []
    for i, a in enumerate(articles[:18], 1):
        condensed_articles.append(
            f"[{i}] Title: {a['title']}\nSource: {a['source']} ({a.get('category', '')})\nSummary: {a['summary']}\nURL: {a['link']}\n"
        )
    articles_payload = "\n".join(condensed_articles)

    user_prompt = f"Today's date is {datetime.now().strftime('%B %d, %Y')}.\nHere are today's top global tech & AI articles:\n\n{articles_payload}\n\nSynthesize this into the requested JSON briefing."

    body = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\n" + user_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json"
        }
    }

    import time
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=35) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidate_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(candidate_text)
        except Exception as e:
            last_err = e
            logger.warning(f"Gemini attempt {attempt + 1} failed: {e}. Retrying in 2s...")
            time.sleep(2)
    raise last_err

def synthesize_with_openai(articles: List[Dict], api_key: str) -> Dict[str, Any]:
    """Call OpenAI API via REST."""
    url = "https://api.openai.com/v1/chat/completions"

    condensed_articles = []
    for i, a in enumerate(articles[:18], 1):
        condensed_articles.append(
            f"[{i}] Title: {a['title']}\nSource: {a['source']}\nSummary: {a['summary']}\nURL: {a['link']}\n"
        )
    articles_payload = "\n".join(condensed_articles)

    body = {
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Today's date: {datetime.now().strftime('%B %d, %Y')}\n\nArticles:\n{articles_payload}"}
        ],
        "temperature": 0.3
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        content = res_data["choices"][0]["message"]["content"]
        return json.loads(content)

def synthesize_fallback(articles: List[Dict]) -> Dict[str, Any]:
    """
    Intelligent heuristic fallback when no LLM API key is configured or offline.
    Extracts top articles from diverse sources, segregating business/finance and model breakthroughs.
    """
    logger.info("Using smart heuristic synthesis fallback with diverse source curation.")
    if not articles:
        return {
            "top_story": {
                "headline": "Global Tech & Business Intelligence Update",
                "source_name": "Global Tech Network",
                "what_happened": "Monitoring global sources for new AI model releases, enterprise cloud spend, and market updates.",
                "why_it_matters": "Keeping track of technical shifts is vital for tech and finance strategy.",
                "source_url": "https://cnbc.com"
            },
            "business_and_markets": [],
            "breakthroughs": [],
            "concept_of_the_day": {
                "term": "Foundation Models",
                "plain_english_definition": "Large AI models trained on vast amounts of data that can be adapted to a wide range of downstream tasks.",
                "business_analogy": "Like building a core engine platform in manufacturing that can power sedans, SUVs, and trucks."
            },
            "quick_bites": []
        }

    # Identify business/market-centric sources vs pure AI/model research sources
    biz_keywords = ['market', 'finance', 'venture', 'business', 'enterprise', 'cnbc', 'wired', 'siliconangle', 'cloud']
    model_keywords = ['model', 'research', 'hugging', 'mit', 'verge', 'ars', 'paper', 'lab', 'deepmind', 'weights']

    used_links = set()

    # 1. Lead Story: First high-signal article
    top = articles[0]
    used_links.add(top['link'])

    # 2. Business & Markets: Distinct sources matching business keywords
    biz_candidates = [
        a for a in articles 
        if a['link'] not in used_links and any(k in a.get('category', '').lower() or k in a.get('source', '').lower() for k in biz_keywords)
    ]
    biz_selected = []
    seen_biz_sources = set()
    for a in biz_candidates:
        if a['source'] not in seen_biz_sources:
            biz_selected.append(a)
            seen_biz_sources.add(a['source'])
            used_links.add(a['link'])
            if len(biz_selected) == 3:
                break

    # 3. Frontier Models & AI Releases: Distinct sources matching model/research keywords
    model_candidates = [
        a for a in articles 
        if a['link'] not in used_links and any(k in a.get('category', '').lower() or k in a.get('source', '').lower() for k in model_keywords)
    ]
    model_selected = []
    seen_model_sources = set()
    for a in model_candidates:
        if a['source'] not in seen_model_sources:
            model_selected.append(a)
            seen_model_sources.add(a['source'])
            used_links.add(a['link'])
            if len(model_selected) == 3:
                break

    # 4. Quick bites from remaining diverse sources
    qb_selected = []
    seen_qb_sources = set()
    for a in articles:
        if a['link'] not in used_links and a['source'] not in seen_qb_sources:
            qb_selected.append(a)
            seen_qb_sources.add(a['source'])
            used_links.add(a['link'])
            if len(qb_selected) == 4:
                break

    # Fallback fill if any list was short
    for a in articles:
        if a['link'] not in used_links:
            if len(biz_selected) < 2:
                biz_selected.append(a)
                used_links.add(a['link'])
            elif len(model_selected) < 2:
                model_selected.append(a)
                used_links.add(a['link'])
            elif len(qb_selected) < 4:
                qb_selected.append(a)
                used_links.add(a['link'])

    return {
        "top_story": {
            "headline": top["title"],
            "source_name": top["source"],
            "what_happened": top["summary"] if top["summary"] else "Key strategic development reported across global tech networks.",
            "why_it_matters": f"Published via {top['source']}. Tech advancements in this sector directly influence enterprise software spend, valuation multiples, and market positioning.",
            "source_url": top["link"]
        },
        "business_and_markets": [
            {
                "title": a["title"],
                "publisher": a["source"],
                "plain_english": a["summary"][:240] + ("..." if len(a["summary"]) > 240 else ""),
                "financial_takeaway": "Commercial angle: Influences IT budgets, cloud infrastructure ROI, and venture market funding trends.",
                "source_url": a["link"]
            }
            for a in biz_selected
        ],
        "breakthroughs": [
            {
                "title": a["title"],
                "lab": a["source"],
                "plain_english": a["summary"][:240] + ("..." if len(a["summary"]) > 240 else ""),
                "market_impact": "Accelerates model inference efficiency and lowers compute barriers for enterprise software adopters.",
                "source_url": a["link"]
            }
            for a in model_selected
        ],
        "concept_of_the_day": {
            "term": "Inference Compute vs. Training Compute",
            "plain_english_definition": "Training compute is the fixed capital expenditure spent teaching an AI model once. Inference compute is the continuous operating expense every time a user or business queries the model.",
            "business_analogy": "Training is the R&D/Capex needed to engineer a Boeing jet; Inference is the ongoing fuel and maintenance costs every time the airline flies a passenger."
        },
        "quick_bites": [
            {
                "text": a["title"],
                "source_name": a["source"],
                "source_url": a["link"]
            }
            for a in qb_selected
        ]
    }

def analyze_and_synthesize(articles: List[Dict]) -> Dict[str, Any]:
    """
    Analyzes raw articles and produces the structured executive briefing.
    Tries configured AI provider first, then falls back gracefully.
    """
    if settings.GEMINI_API_KEY:
        try:
            logger.info(f"Synthesizing with Gemini API ({settings.GEMINI_MODEL})...")
            result = synthesize_with_gemini(articles, settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
            logger.info("Gemini synthesis completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Gemini API error: {e}. Falling back...")

    if settings.OPENAI_API_KEY:
        try:
            logger.info("Synthesizing with OpenAI API...")
            result = synthesize_with_openai(articles, settings.OPENAI_API_KEY)
            logger.info("OpenAI synthesis completed successfully.")
            return result
        except Exception as e:
            logger.error(f"OpenAI API error: {e}. Falling back...")

    return synthesize_fallback(articles)
