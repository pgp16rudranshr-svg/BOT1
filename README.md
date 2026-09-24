# 🚀 Daily Tech & AI Briefing Agent
### Autonomous Intelligence Digest for Rudransh Rastogi (IIM Rohtak — Finance & Tech)

An autonomous daily intelligence agent designed to solve information overload in the fast-moving AI & tech landscape. It aggregates global breakthroughs, model releases, research papers, and venture/market news, synthesizes them into **plain-English, executive-level summaries**, and delivers a beautifully formatted morning newsletter to your email daily at **10:00 AM**.

---

## ✨ What's Inside Every Briefing

1. ⭐ **The Lead Story**: The single most consequential tech/AI development of the day.
   - *What happened* in plain English (jargon-free).
   - *Why it matters* for business models, enterprise adoption, and valuation/finance.
2. 🚀 **Frontier Models & Releases**: High-signal breakdown of new LLMs, open-source weights, and multimodal tools (capabilities, benchmarks, and enterprise angle).
3. 💡 **In Plain English: Concept of the Day**: Breaks down 1 technical term (e.g., *Mixture of Experts*, *Inference Compute*, *RAG vs Fine-tuning*) using an intuitive business/finance analogy.
4. ⚡ **Fast Signal & Market Bites**: 4 rapid-fire bullet points covering funding rounds, regulatory moves, and chip supply chains.

---

## ⚡ Quick Start (3 Steps)

### 1. Configure Credentials in `.env`
Open the `.env` file and fill in:
```bash
# 1. Your email address to receive the briefing
RECIPIENT_EMAIL="your_email@gmail.com"

# 2. Free Google Gemini API Key for synthesis (optional but recommended)
# Get one in 30 seconds at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY="your_gemini_api_key"

# 3. Gmail credentials for automated sending
# Use a 16-character Google App Password (not your normal password):
# Generate at: https://myaccount.google.com/apppasswords
SMTP_USER="your_sending_gmail@gmail.com"
SMTP_PASSWORD="xxxx xxxx xxxx xxxx"
```

### 2. Preview Today's Briefing Instantly
Generate today's briefing and open it directly in your web browser (no email sent):
```bash
python3 run.py --preview
```

### 3. Send Today's Briefing to Your Email
```bash
python3 run.py --now
```

---

## ⏰ Set Up Daily 10:00 AM Delivery (100% Cloud — Mac Can Be Off!)

The best, zero-maintenance way to run this agent is via **GitHub Actions** in the cloud. It runs completely in the cloud at **10:00 AM IST** daily, even if your laptop is closed, asleep, or turned off.

### Step-by-Step Setup:
1. **Push this folder to a private GitHub repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Daily AI Briefing Agent"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/daily-ai-briefing.git
   git push -u origin main
   ```
2. **Add Your Secrets on GitHub**:
   - Go to your repository on GitHub &rarr; **Settings** &rarr; **Secrets and variables** &rarr; **Actions** &rarr; **New repository secret**.
   - Add these 4 secrets:
     - `RECIPIENT_EMAIL`: Your email to receive the briefing.
     - `GEMINI_API_KEY`: Your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
     - `SMTP_USER`: Your Gmail address for sending.
     - `SMTP_PASSWORD`: Your 16-character [Google App Password](https://myaccount.google.com/apppasswords).
3. **Done!**
   - The workflow (`.github/workflows/daily_briefing.yml`) is already configured.
   - It will trigger automatically every day at **10:00 AM IST** (04:30 UTC).
   - You can also trigger it manually anytime by going to the **Actions** tab on GitHub and clicking **Run workflow**.

---

## 💻 Alternative: Local macOS 10:00 AM Delivery (If you prefer local)

If you prefer running locally on your Mac:
```bash
# 1. Register the 10:00 AM daily schedule with macOS
python3 run.py --install-schedule

# 2. Check schedule status
python3 run.py --schedule-status

# 3. To remove the schedule later if desired:
python3 run.py --uninstall-schedule
```

---

## 📁 Project Architecture

```
/Users/rudranshrastogi/Downloads/Newsletter1/
├── config/
│   ├── settings.py           # Configuration loader & defaults
│   └── sources.json          # Curated global RSS feeds & research sources
├── src/
│   ├── __init__.py
│   ├── fetcher.py            # Global RSS/Atom aggregator (zero-dep)
│   ├── analyzer.py           # Gemini/OpenAI synthesis & MBA intelligence engine
│   ├── formatter.py          # HTML & plain-text newsletter renderer
│   ├── mailer.py             # Gmail SMTP dispatcher & browser preview
│   └── scheduler.py          # macOS launchd daemon manager
├── templates/
│   └── email_template.html   # Clean, responsive executive newsletter template
├── briefings/                # Archive of daily generated HTML newsletters
├── .env                      # Your private API keys and email credentials
├── run.py                    # Main CLI controller
└── README.md
```

---

## 📡 Curated Global Sources

The agent tracks trusted global feeds configured in `config/sources.json`:
- **Frontier Research & Labs**: Hugging Face Blog, MIT Technology Review, OpenAI News, Anthropic, Google DeepMind.
- **Enterprise & Venture**: TechCrunch AI, VentureBeat, Ars Technica, The Verge.
- **Markets & Finance**: CNBC Tech, Reuters / Bloomberg syndications.
- **Community Signal**: Hacker News Top AI developments.

You can easily add or customize feeds in `config/sources.json`.
