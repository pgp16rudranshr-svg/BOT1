import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from config import settings

logger = logging.getLogger(__name__)

def render_html_fallback(context: Dict[str, Any], template_content: str) -> str:
    """
    Lightweight fallback template renderer when Jinja2 is not installed.
    Handles {{ variable }}, simple {% for %}, and {% if %}.
    """
    html = template_content
    # Simple tag replacements
    html = html.replace("{{ date }}", context.get("date", ""))
    html = html.replace("{{ recipient_name }}", context.get("recipient_name", ""))
    html = html.replace("{{ affiliation }}", context.get("affiliation", ""))
    
    top = context.get("top_story", {})
    html = html.replace("{{ top_story.headline }}", top.get("headline", ""))
    html = html.replace("{{ top_story.what_happened }}", top.get("what_happened", ""))
    html = html.replace("{{ top_story.why_it_matters }}", top.get("why_it_matters", ""))
    html = html.replace("{{ top_story.source_url }}", top.get("source_url", "#"))

    concept = context.get("concept_of_the_day", {})
    html = html.replace("{{ concept_of_the_day.term }}", concept.get("term", ""))
    html = html.replace("{{ concept_of_the_day.plain_english_definition }}", concept.get("plain_english_definition", ""))
    html = html.replace("{{ concept_of_the_day.business_analogy }}", concept.get("business_analogy", ""))

    # Breakthroughs block replacement
    bt_items = context.get("breakthroughs", [])
    bt_html = ""
    for item in bt_items:
        s_url = item.get('source_url', '#')
        bt_html += f"""
        <div class="card">
          <span class="meta-tag">{item.get('lab', '')}</span>
          <h3 class="card-title">
            <a href="{s_url}" target="_blank" style="color: #0f172a; text-decoration: none;">{item.get('title', '')} &rarr;</a>
          </h3>
          <p class="card-body"><strong>In Plain English:</strong> {item.get('plain_english', '')}</p>
          <div class="highlight-box">
            <strong>📈 Market Angle:</strong> {item.get('market_impact', '')}
          </div>
          <div style="margin-top: 12px; text-align: left;">
            <a href="{s_url}" target="_blank" style="display: inline-block; background-color: #f1f5f9; color: #0284c7; text-decoration: none; padding: 6px 14px; border: 1px solid #cbd5e1; border-radius: 6px; font-weight: 600; font-size: 12px;">
              🔗 Read Full Story / Report &rarr;
            </a>
            <div style="margin-top: 4px; font-size: 11px; color: #64748b;">
              Direct Link: <a href="{s_url}" target="_blank" style="color: #0284c7; word-break: break-all;">{s_url}</a>
            </div>
          </div>
        </div>
        """
    html = html.replace("{% if breakthroughs %}", "")
    html = html.replace("{% endif %}", "")
    # replace loop with generated html
    import re
    html = re.sub(r"\{% for item in breakthroughs %\}.*?\{% endfor %\}", bt_html, html, flags=re.DOTALL)

    # Quick bites replacement
    qb_items = context.get("quick_bites", [])
    qb_html = ""
    for bite in qb_items:
        if isinstance(bite, dict):
            text = bite.get("text", "")
            src_name = f" &mdash; <em>{bite.get('source_name', '')}</em>" if bite.get("source_name") else ""
            src_url = f'<br/><a href="{bite.get("source_url", "#")}" target="_blank" style="color: #0284c7; font-weight: 600; font-size: 12px; text-decoration: underline;">Read story &rarr;</a>' if bite.get("source_url") else ""
            content_str = f"{text}{src_name}{src_url}"
        else:
            content_str = str(bite)
        qb_html += f"""
        <li class="quick-bites-item">
          <span class="quick-bites-bullet">&bull;</span>
          <div>{content_str}</div>
        </li>
        """
    html = re.sub(r"\{% for bite in quick_bites %\}.*?\{% endfor %\}", qb_html, html, flags=re.DOTALL)
    html = html.replace("{% if concept_of_the_day %}", "")
    html = html.replace("{% if quick_bites %}", "")

    return html

def render_briefing(briefing_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Renders briefing data into both HTML and plain-text formats.
    """
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    context = {
        "date": today_str,
        "recipient_name": settings.RECIPIENT_NAME,
        "affiliation": settings.AFFILIATION,
        "top_story": briefing_data.get("top_story", {}),
        "breakthroughs": briefing_data.get("breakthroughs", []),
        "concept_of_the_day": briefing_data.get("concept_of_the_day", {}),
        "quick_bites": briefing_data.get("quick_bites", [])
    }

    template_path = settings.TEMPLATES_DIR / "email_template.html"
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    try:
        from jinja2 import Template
        template = Template(template_content)
        html_content = template.render(**context)
    except ImportError:
        logger.info("Jinja2 not installed; using built-in renderer.")
        html_content = render_html_fallback(context, template_content)

    # Plain text version for email multipart / accessibility
    top = context["top_story"]
    concept = context["concept_of_the_day"]
    text_lines = [
        f"DAILY TECH & AI BRIEFING — {today_str}",
        f"Curated for {settings.RECIPIENT_NAME} ({settings.AFFILIATION})",
        "=" * 60,
        "",
        "⭐ THE LEAD STORY:",
        f"{top.get('headline', '')}",
        f"{top.get('what_happened', '')}",
        f"Finance & Business Impact: {top.get('why_it_matters', '')}",
        f"Source: {top.get('source_url', '')}",
        "",
        "🚀 FRONTIER MODELS & RELEASES:",
    ]
    for b in context["breakthroughs"]:
        text_lines.append(f"- [{b.get('lab', '')}] {b.get('title', '')}")
        text_lines.append(f"  In Plain English: {b.get('plain_english', '')}")
        text_lines.append(f"  Market Angle: {b.get('market_impact', '')}")
        text_lines.append(f"  Link: {b.get('source_url', '')}")
        text_lines.append("")

    text_lines.extend([
        "💡 IN PLAIN ENGLISH: CONCEPT OF THE DAY:",
        f"Term: {concept.get('term', '')}",
        f"Definition: {concept.get('plain_english_definition', '')}",
        f"Business Analogy: {concept.get('business_analogy', '')}",
        "",
        "⚡ FAST SIGNAL & MARKET BITES:"
    ])
    for q in context["quick_bites"]:
        if isinstance(q, dict):
            text_lines.append(f"• {q.get('text', '')}")
            if q.get("source_url"):
                text_lines.append(f"  Link: {q.get('source_url')}")
        else:
            text_lines.append(f"• {q}")

    text_lines.extend([
        "",
        "=" * 60,
        "Delivered automatically every morning at 10:00 AM."
    ])
    text_content = "\n".join(text_lines)

    # Save to disk for preview / historical archive
    today_filename = f"briefing_{datetime.now().strftime('%Y-%m-%d')}.html"
    output_file = settings.OUTPUT_DIR / today_filename
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Saved briefing HTML to {output_file}")

    return {
        "html": html_content,
        "text": text_content,
        "filepath": str(output_file)
    }
