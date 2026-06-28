PATH

Know where your money is taking you.

PATH is a personal finance platform built for people who want financial clarity without the complexity of traditional budgeting apps.

Most finance apps focus on tracking spending.

PATH focuses on helping users understand whether their money is moving them closer to the life they want.

Using the Allocate Once™ methodology, users allocate money to categories and goals once, without needing to track every individual transaction. This reduces friction, improves consistency, and creates a healthier relationship with money.

Core Principles
Progress over perfection
Every rand has a destination
Financial clarity without financial jargon
Goal-focused money management
Simplicity before complexity
Designed for real people, not accountants
Key Features
Salary-based monthly planning
Allocate Once™ budgeting
Goal tracking
Emergency fund monitoring
Car and home savings goals
Progress-based dashboard
AI-powered financial insights
Mobile-first experience
Vision

PATH exists to answer one question:

"Am I moving closer to the life I want?"

Rather than focusing on transactions, PATH helps users focus on progress, purpose, and financial direction.

## Architecture

| Layer | Stack |
|---|---|
| Frontend | Angular (standalone components) + RxJS `BehaviorSubject` services + NGX-Charts (charts land with Feature 4/5) |
| Backend | Python / FastAPI |
| Database | PostgreSQL via SQLAlchemy 2.0 + Alembic migrations |
| Auth | Custom JWT (bcrypt password hashing) — no third-party auth provider |
| Styling | Custom SCSS design tokens (CSS variables) + a small hand-built UI kit — no Angular Material/ShadCN |

```
PATH/
├── backend/    FastAPI app, SQLAlchemy models, Alembic migrations, pytest suite
└── frontend/   Angular app (core/ services+guards, shared/ui/ kit, features/ routed screens)
```

### Backend data model (current)

- **User** — email/password (bcrypt hash), display name.
- **Category** — seeded per-user at registration from the default taxonomy (Essentials, Personal Care, Career, Lifestyle, Wealth, Misc); editing/deleting a category never affects other users since rows aren't shared.
- **MonthlyPlan** — one row per `(user, year, month)` holding that month's salary. Upserted via `PUT /api/v1/plans/current`; the same endpoint returns computed `allocated_total`, `remaining_amount`, `savings_total` (sum of Wealth-group allocations), and `on_track` (`remaining_amount >= 0`).
- **Allocation** — one row per `(monthly_plan, category)` holding how much was allocated to that category this month. The Monthly Planning screen sets/replaces these totals wholesale via `PUT /api/v1/plans/current/allocations`; the Dashboard's quick-log "+" button *adds* to a single category's total via `POST /api/v1/plans/current/allocations/quick-log` — both read/write the same rows.
- **Goal** — standalone savings target per user (`name`, `target_amount`, `current_amount`). Not linked to Categories/Allocations — intentionally separate, per the spec. `progress_percent` is computed (capped at 100). Managed via `POST/GET /api/v1/goals`, `POST /api/v1/goals/{id}/contribute` (additive, same pattern as the quick-log), `DELETE /api/v1/goals/{id}`.
- **Monthly Reflection** — no new table; `GET /api/v1/plans/previous/reflection` derives friendly, rule-based messages from last calendar month's `MonthlyPlan`/`Allocation` rows (essentials funded? how much went to Wealth/"savings"? how did `remaining_amount` shake out?). 404 if last month has no plan. Two of the spec's example messages ("stayed within your transport budget," "closer to your car") were dropped — they'd need a planned-vs-actual ledger or per-month goal-contribution history that nothing else in this app tracks; see the message-generation logic in `app/routers/plans.py` (`_build_reflection_messages`) for the ones that are actually derivable.

### Running locally

```bash
# 1. Start Postgres (mapped to host port 55432 to avoid clashing with any local Postgres install)
docker compose up -d

# 2. Backend
cd backend
python3.11 -m venv .venv && source .venv/bin/activate   # any 3.11+ interpreter works (e.g. Homebrew's python3.12)
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload   # http://localhost:8000, docs at /docs

# 3. Frontend (separate terminal)
cd frontend
npm install
npm start   # http://localhost:4200, proxies /api to the backend
```

Run backend tests with `pytest` from `backend/` (uses an in-memory SQLite DB, no Postgres required).

### What's built so far

End-to-end: register → log in → enter this month's salary ("Payday Setup") → allocate it across categories ("Monthly Planning", grouped by Essentials/Personal Care/Career/Lifestyle/Wealth/Other, with a live Salary/Allocated/Remaining summary) → land on a dashboard showing Salary, Allocated, Remaining, Savings, and an "On Track ✓" / "Let's adjust" status pill (never red, never shaming), with an "Adjust your plan" link back into Monthly Planning. From the dashboard, a floating "+" button opens a fast amount+category panel ("Expense Allocation") that adds to a category's allocation in one tap — the "Allocate Once" loop for money that leaves your account mid-month, distinct from Monthly Planning's upfront "set the whole plan" flow. A "Your goals" link leads to Goal Tracking: create a savings goal with a target amount, contribute to it (additive, same one-tap pattern), watch its progress bar fill, delete it when done. A "Monthly reflection" link shows last month's friendly coach summary once a month has actually passed (a "come back later" empty state until then). All six MVP features from the spec are now built. Session, plan/allocation, goal, and reflection data all persist across reloads.

### Out of scope for this pass

The Smart Allocation Engine (pattern suggestions), NGX-Charts integration, offline sync, push notifications, category edit/delete UI, and editing a goal's name/target after creation are all deliberately deferred.