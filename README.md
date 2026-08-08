# LMLabs Client Acquisition System

Your complete outbound sales pipeline. Find businesses, analyze their websites, generate outreach messages, track leads, close deals.

## Quick Start

```bash
# 1. Setup (run once)
python setup.py

# 2. Add leads manually
python run.py add-lead --name "Taverna Olympus" --phone "+30..." --city Thessaloniki --niche restaurant

# 3. Generate outreach message
python run.py generate-message --lead-id 1 --type email

# 4. Or find leads automatically (requires Google Places API key)
python run.py find-leads --niche restaurant --city Thessaloniki --save
```

## Commands

| Command | What it does |
|---------|-------------|
| `python setup.py` | One-time setup — installs deps, creates database |
| `python run.py find-leads --niche X --city Y --save` | Search Google for businesses, save hot leads |
| `python run.py add-lead --name "X" --city Y --niche Z` | Add a lead manually |
| `python run.py list` | View all leads |
| `python run.py analyze --website example.com` | Score a website (0-100, lower = better lead) |
| `python run.py analyze-all` | Analyze all unanalyzed leads |
| `python run.py generate-message --lead-id 1 --type email` | Generate cold email |
| `python run.py generate-message --lead-id 1 --type all` | Generate all message types |
| `python run.py update-status --lead-id 1 --status contacted` | Update lead status |
| `python run.py stats` | View pipeline stats |
| `python run.py outreach` | See leads ready for outreach |
| `python run.py templates` | List all outreach templates |
| `python run.py export --file leads.csv` | Export leads to CSV |
| `python app.py` | Launch web dashboard at localhost:5000 |

## Automated Lead Search

To use `find-leads`, you need a Google Places API key:

1. Go to https://console.cloud.google.com/apis/credentials
2. Create a project and enable Places API + Geocoding API
3. Create an API key
4. Either edit `config.py` or set environment variable:
   ```bash
   export GOOGLE_PLACES_API_KEY=your-key-here
   ```

Cost: First $200/month free (covers ~12,000 searches).

## Daily Workflow

1. **Morning**: Run `find-leads` for 2-3 niches in your city, or find leads manually on Google Maps
2. **Score**: Run `analyze-all` to score their websites
3. **Outreach**: Generate messages for top leads and send them
4. **Track**: Update statuses as you hear back
5. **Follow up**: Check `outreach` command for leads needing follow-up
6. **Target**: 20 businesses contacted per day

## Pricing (EUR)

| Package | Price | Pages | Delivery |
|---------|-------|-------|----------|
| Starter | €700 | 1 page | 5-7 days |
| Business | €1,400 | 5 pages | 1-2 weeks |
| Growth | €2,500+ | 8-10 pages | 2-3 weeks |

## File Structure

```
├── setup.py          # One-time setup
├── run.py            # CLI entry point
├── app.py            # Web dashboard (Flask)
├── config.py         # Your settings (edit this)
├── requirements.txt  # Python dependencies
├── crm/              # CRM database + CLI
├── leads/            # Lead finder, website analyzer, message generator
├── outreach/         # Email/phone/SMS templates
├── offers/           # Pricing packages
├── templates/        # Web UI templates (Flask)
└── data/             # Database + exports (created by setup)
```
