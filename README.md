# Scope SEO Intelligence Scraper

Automated daily Reddit + Google keyword intelligence for the **Scope Finder** app — tracks what precision rifle, long-range shooting, and hunting communities are searching for and discussing around optics/scopes.

## What it does

Runs two Claude scheduled tasks daily:
- **2 AM** — scrapes Reddit via Apify across 16 subreddits, supplements with Google search signals, classifies intent, saves structured JSON
- **6 AM** — reads JSON, builds HTML email brief, sends to inbox

## Output

Daily `daily_YYYY-MM-DD.json` files containing:
- **posts** — matched posts with title, body, subreddit, score, intent, matched_keywords, source
- **keyword_counts** — frequency map of all scope/optic keywords
- **top_keywords** — top 20 sorted by frequency
- **trending_questions** — top 10 posts ranked by engagement
- **intent_breakdown** — commercial / informational / transactional / navigational split

## Architecture

```
Claude Scheduled Task (2 AM)
  └─ parseforge/reddit-posts-scraper  ← 16 subreddits, Apify RESIDENTIAL proxy
  └─ apify/rag-web-browser            ← 3x Google searches for supplemental signals
  └─ Python keyword classifier        ← 80+ scope/optic terms
  └─ daily_YYYY-MM-DD.json           ← saved to scope_seo_data/

Claude Scheduled Task (6 AM)
  └─ Reads today's JSON
  └─ Builds HTML brief (dark theme, keyword bars, intent badges)
  └─ gmail_create_draft → Chrome automation → Send
```

> **Why Apify?** Direct Reddit access is blocked by the VM proxy (403). Apify's RESIDENTIAL proxy is on the allowlist.

## Communities Monitored

| Subreddit | Focus |
|---|---|
| r/longrange | Long-range precision shooting |
| r/PrecisionRifle | PRS competition |
| r/Hunting | Hunting optics |
| r/guns / r/firearms | General firearms |
| r/ar15 | AR platform |
| r/reloading | Hand loading |
| r/6_5creedmoor | 6.5CM specific |
| r/competitionshooting | Competition shooting |
| r/benchrest | Benchrest shooting |
| r/308 | .308 / 7.62 |
| r/nrl22 | NRL22 rimfire competition |
| r/NightVision | NV optics |
| r/ThermalHunting | Thermal optics |
| r/gundeals | Deals — commercial intent |
| r/Longrangehunting | Long range hunting |
| r/Ausguns | Australian market |

## Keyword Taxonomy

### Brands
Vortex, Nightforce, Leupold, Zeiss, Swarovski, Schmidt & Bender, Kahles, March, Tract, Burris, Bushnell, Steiner, Meopta, Primary Arms, SWFA, Athlon, Sig Sauer, US Optics, ZCO, Holosun, Trijicon, Arken

### Technical Terms
scope, riflescope, optic, optics, glass, reticle, turret, parallax, eye relief, magnification, zero, zeroing, focal plane, FFP, SFP, MOA, MRAD, mil, DOPE, ATACR, Razor, Mark 5

### Intent Phrases
"best scope", "scope for", "scope under", "scope recommendation", "scope review", "scope vs", "which scope", "scope help", "long range scope", "hunting scope", "PRS scope", "benchrest scope", "NRL22 scope", "precision rifle"

### Night / Thermal
night vision, thermal scope, thermal optic

## Intent Classification

| Intent | Trigger keywords |
|---|---|
| transactional | buy, purchase, deal, sale, coupon, cheapest, price, cost, where to get |
| commercial | best, recommend, review, worth, vs, comparison, which, should i, top, between |
| informational | how, what is, explain, difference, why, guide, tutorial, help, upgrade, budget |
| navigational | brand name only (Vortex, Nightforce, Leupold, etc.) |

## Email Brief Sections

1. 🔥 **Top 15 Keywords** — frequency bar chart
2. 🎯 **Top SEO Opportunities** — ranked by engagement (score + comments)
3. 🕳️ **Keyword Gaps** — recurring unanswered questions = content opportunities
4. 📈 **Rising Queries** — beginner/newcomer signals
5. 🏷️ **Brand Sentiment** — mention counts + trend badges
6. 📊 **Intent Breakdown** — percentage split across 4 intent types

## Known Limitations

- **Gmail send**: Gmail MCP has no `send_draft` tool. The emailer creates a draft then uses Chrome automation to send — requires Claude in Chrome extension to be connected.
- **2 AM API overload**: Claude API sometimes returns 529 at 2 AM. If no JSON exists by 6 AM, the emailer creates a warning draft instead.
- **Free tier Apify cap**: `parseforge/reddit-posts-scraper` returns max 10 items on free tier — supplemented with Google search results via `apify/rag-web-browser`.

## Setup

Tasks live in `C:\Users\Cezary\OneDrive\Documents\Claude\Scheduled\`:
- `scope-seo-scraper\SKILL.md` — scraper task prompt
- `scope-seo-emailer\SKILL.md` — emailer task prompt

**First run**: Click "Run now" on each task from the Cowork Scheduled sidebar to pre-approve all tool permissions (Apify, Gmail). This prevents future automated runs from pausing on permission prompts.
