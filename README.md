# LMLabs Client Acquisition System

Your outbound sales pipeline for a web-design agency: **find** local businesses that need a website, **score** their current site, **generate** personalized outreach (English or Greek), **send** it, and **track** every lead to close.

---

## 1. Setup (once)

```bash
# Install dependencies + create the database
python setup.py
```

### Add your Google Places API key (kept out of Git)

The app reads your key from **`config_local.py`**, which is gitignored and never committed.

```bash
# copy the template, then edit it
Copy-Item config_local.example.py config_local.py    # PowerShell
```

Open `config_local.py` and paste your key:

```python
GOOGLE_PLACES_API_KEY = "AIza...your-real-key"
```

> Don't have a key yet? Create one at <https://console.cloud.google.com/apis/credentials>, then enable **Places API** and **Geocoding API**. Restrict the key to those two APIs plus your IP. First $200/month of usage is free (~12,000 searches).
>
> Prefer an environment variable instead of a file? Set `GOOGLE_PLACES_API_KEY` in your shell and skip `config_local.py`. You can run everything except automated search without a key.

### Personalize your details

Edit `config.py` so your outreach is signed correctly — these values go straight into the messages:

| Setting | What it is |
|---------|-----------|
| `YOUR_NAME` | The person who signs the emails (e.g., `"Levan"`) |
| `AGENCY_NAME` | Your agency / brand |
| `AGENCY_EMAIL`, `AGENCY_PHONE` | Your contact details |
| `AGENCY_CALENDLY` | **Set a real Calendly link** — it's the call-to-action in every message |
| `PACKAGES` | Your pricing tiers |

---

## 2. Run the web dashboard (recommended)

```bash
python app.py
```

Open <http://localhost:5000>. From there you can:

- **Find Businesses** — search any niche + city; results are ranked 🔥 Hot (no website) → 🌡️ Warm (bad site) → ❄️ Cold. Select the ones you want and save them to your CRM.
- **Analyze Website** — score any site 0–100 (lower = better lead) and see exactly what's wrong.
- **All Leads** — filter your pipeline by status and niche.
- **Lead page** — analyze the site, **generate outreach** (📧 email / 📞 phone script / 💬 SMS) in 🇬🇷 Greek or 🇬🇧 English, copy it, then hit **✓ Mark as Sent** to log it and move the lead forward. Add notes and update status as you go.
- **Generate Messages** — craft a message for any business without saving it first.

> Auto-reload while developing: `set FLASK_DEBUG=1` (PowerShell: `$env:FLASK_DEBUG=1`) before `python app.py`. Leave it off for normal use.

---

## 3. The daily outreach loop

1. **Find** — search 2–3 niches in your city, save the Hot/Warm leads.
2. **Score** — analyze their websites (skip the ones with good sites).
3. **Reach out** — open a lead, generate the email/phone/SMS, send it, click **Mark as Sent**.
4. **Track** — the lead advances `found → analyzed → contacted → followed_up`. Update status as they reply.
5. **Follow up** — work the leads sitting in `contacted` with no reply.
6. **Target** — ~20 businesses contacted per day.

Lead scoring: **0–30** 🔥 excellent lead (terrible site) · **31–50** 🌡️ good · **51–70** maybe · **71–100** skip (their site is fine).

---

## 4. Command line (optional)

Everything the dashboard does is also available via `run.py`:

| Command | What it does |
|---------|-------------|
| `python run.py find-leads --niche restaurant --city Thessaloniki --save` | Search Google, save hot/warm leads |
| `python run.py add-lead --name "Taverna Olympus" --city Thessaloniki --niche taverna` | Add a lead manually |
| `python run.py list` | List all leads |
| `python run.py analyze --website example.com --lead-id 1` | Score a site (and save it to the lead) |
| `python run.py analyze-all` | Analyze every unanalyzed lead |
| `python run.py generate-message --lead-id 1 --type all` | Generate every message type |
| `python run.py log-outreach --lead-id 1 --type email` | Record an outreach attempt |
| `python run.py update-status --lead-id 1 --status contacted` | Update a lead's status |
| `python run.py stats` | Pipeline stats |
| `python run.py outreach` | Leads ready for outreach / follow-up |
| `python run.py export --file leads.csv` | Export to CSV |

---

## Pricing (EUR)

| Package | Price | Pages | Delivery |
|---------|-------|-------|----------|
| Starter | €700 | 1 page | 5–7 days |
| Business | €1,400 | 5 pages | 1–2 weeks |
| Growth | €2,500+ | 8–10 pages | 2–3 weeks |

Edit these in `config.py` (`PACKAGES`).

---

## Project layout

```
├── setup.py                 # One-time setup (deps + database)
├── app.py                   # Web dashboard (Flask) — the main interface
├── run.py                   # CLI entry point
├── config.py                # Settings (niches, pricing, agency info) — tracked
├── config_local.py          # Your real API keys — gitignored, never committed
├── config_local.example.py  # Template for config_local.py
├── crm/                     # SQLite CRM (database + CLI commands)
├── leads/                   # Business search, website analyzer, message generator
├── outreach/                # Reusable email/phone/SMS/LinkedIn templates
├── templates/               # Web UI (Jinja/HTML)
└── data/                    # leads.db + CSV exports (gitignored)
```

---

## Security

- **Never commit API keys.** Real secrets live only in `config_local.py` (gitignored).
- `data/leads.db` (your leads' contact info) is gitignored and stays on your machine.
- Keep `FLASK_DEBUG` off unless you're actively developing.
