# Lease Peace - Roommate Matching & Conflict Prediction Platform

**Predict roommate conflicts before move-in using deep compatibility analysis**

Lease Peace helps residents find compatible roommates and enables co-living operators to reduce conflicts, increase renewals, and improve resident satisfaction.

## 🎯 Product Vision

- **For Residents**: $99 per match cycle - Find highly compatible roommates based on 25+ dimensions
- **For Operators**: $500-$2,000 annually - Reduce conflicts, increase renewals, improve operations
- **Pilot Program**: Currently onboarding 3-5 co-living spaces for proof-of-concept

## 🏗️ Architecture

**Monorepo Structure:**
```
lease-peace/
├── apps/
│   ├── api/          # FastAPI backend (Python 3.11)
│   └── web/          # Next.js frontend (App Router)
├── packages/
│   └── shared/       # Shared TypeScript types & schemas
└── docker-compose.yml
```

**Tech Stack:**
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11, SQLAlchemy 2.x
- **Database**: PostgreSQL 15
- **Auth**: JWT tokens with password hashing
- **Deployment**: Docker Compose (local), Vercel + Render/Fly.io (production)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### One-Command Setup

```bash
# Clone and start
git clone <repository-url>
cd roommate-match-app

# Start all services
docker-compose up

# In a new terminal, run migrations and seed data
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed.py
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Default Credentials

After seeding:
- **Admin**: admin@leasepeace.com / admin123
- **Operator**: operator@downtowncoliving.com / operator123
- **Resident 1**: alice@example.com / password123
- **Resident 2**: bob@example.com / password123
- **Resident 3**: carol@example.com / password123

## 📋 Environment Variables

### API (.env in apps/api/)
```env
DATABASE_URL=postgresql://leasepeace:devpassword123@db:5432/leasepeace
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

### Web (.env.local in apps/web/)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here
```

## 🧪 Testing

### Run All Tests
```bash
# API tests
cd apps/api
pytest

# Matching engine tests
pytest tests/test_matching_engine.py -v

# API smoke tests
pytest tests/test_api.py -v
```

### Manual Testing Flow

1. **Resident Flow**:
   - Sign up at http://localhost:3000/auth/signup
   - Complete questionnaire at http://localhost:3000/resident/onboarding
   - View matches at http://localhost:3000/resident/dashboard

2. **Operator Flow**:
   - Login as operator
   - Add properties, units, rooms, beds
   - View applicants
   - Run matching for candidates
   - View match reports

3. **Run Sample Match**:
   ```bash
   # Login as operator, navigate to matching page
   # Select Alice, Bob, and Carol as candidates
   # Run pairwise matching
   # View compatibility scores and risk predictions
   ```

## 📊 Database Schema

Key tables:
- **users**: Authentication and roles
- **resident_profiles** + **questionnaire_answers**: Resident data
- **operator_orgs**, **properties**, **units**, **rooms**, **beds**: Operator hierarchy
- **applicant_pool**: Residents applying to properties
- **match_runs** + **match_results**: Matching execution and results
- **events**: Analytics tracking
- **conflict_reports**, **move_ins**, **feedback_surveys**: Operational data

See `apps/api/models.py` for complete schema.

## 🧮 Matching Engine

### v1 Algorithm (Rule-Based)

**Inputs**: Two or more resident questionnaire profiles

**Process**:
1. **Hard Constraints**: Filter by dealbreakers
2. **Weighted Scoring**: Calculate compatibility across dimensions
   - High weight: Cleanliness, Guests, Sleep/Noise, Communication
   - Medium weight: Thermostat, WFH, Social, Sharing
   - Lower weight: Lifestyle, Values
3. **Explainability**: Generate top 3 alignments and mismatches
4. **Group Matching**: For N candidates, propose top K groups (2-6 people)

**Output**:
- Compatibility score (0-100)
- Category breakdown (sleep, cleanliness, guests, etc.)
- Risk level (low/medium/high)
- Mitigation tips
- Recommended house rules

**Code**: `apps/api/engines/matching_engine.py`

## ⚠️ Conflict Prediction

### v1 Engine (Heuristic-Based)

Calculates conflict risk based on:
- Mismatch magnitude on high-conflict dimensions
- Communication style clashes (e.g., avoidant vs. assertive)
- WFH + noise sensitivity conflicts
- Budget stress + expense splitting mismatches

**Output**:
- Overall risk score (0-1) and level (low/med/high)
- Category risks (cleanliness, noise, guests, etc.)
- Mitigation strategies
- House rule templates

**Code**: `apps/api/engines/conflict_predictor.py`

**Future**: Replace heuristics with ML model trained on conflict outcomes

## 📈 Analytics & Metrics

### Event Tracking

Events are automatically logged to the `events` table:
- `signup`, `login`
- `questionnaire_started`, `questionnaire_completed`
- `match_run`, `match_viewed`, `report_exported`
- `conflict_reported`, `move_in_created`, `renewal_marked`

### Pilot KPIs

Example SQL queries for pilot reporting:

```sql
-- Conflicts per month
SELECT
  DATE_TRUNC('month', created_at) as month,
  COUNT(*) as conflict_count
FROM conflict_reports
GROUP BY month
ORDER BY month DESC;

-- Match run completion rate
SELECT
  status,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM match_runs
GROUP BY status;

-- Renewal rate
SELECT
  COUNT(*) FILTER (WHERE is_renewed = true) as renewals,
  COUNT(*) as total_leases,
  ROUND(COUNT(*) FILTER (WHERE is_renewed = true) * 100.0 / COUNT(*), 2) as renewal_rate
FROM move_ins
WHERE move_out_date IS NOT NULL;
```

## 🎨 Frontend Structure

### Pages Implemented

**Public**:
- `/` - Landing page
- `/pricing` - Pricing tiers
- `/operator/request-pilot` - Pilot program signup

**Auth**:
- `/auth/login` - Login
- `/auth/signup` - Signup with role selection

**Resident**:
- `/resident/onboarding` - 5-step questionnaire wizard
- `/resident/dashboard` - View matches
- `/resident/settings` - Profile & data management

**Operator**:
- `/operator/dashboard` - Metrics overview
- `/operator/properties` - Property management
- `/operator/applicants` - Applicant tracking
- `/operator/matching` - Run matching for vacancies

**Admin**:
- `/admin/dashboard` - Platform metrics
- `/admin/users` - User management
- `/admin/events` - Event logs

## 🔐 Security & Privacy

- **Authentication**: JWT tokens with bcrypt password hashing
- **Authorization**: Role-based access control (RBAC) enforced at API level
- **Data Privacy**: GDPR-compliant data deletion endpoint
- **CORS**: Configured for allowed origins only
- **No PII in Matching**: Protected attributes excluded from algorithm

## 🚢 Deployment

### Option 1: Docker (Single Host)

```bash
# Production compose file
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Separate Hosting

**Frontend (Vercel)**:
```bash
cd apps/web
vercel deploy
```

**Backend (Render/Fly.io)**:
```bash
cd apps/api
# Follow Render or Fly.io deployment guides
# Set environment variables in platform dashboard
```

**Database**: Managed PostgreSQL (RDS, Render, Neon, Supabase)

### Environment Setup

1. Create production database
2. Run migrations: `alembic upgrade head`
3. Create admin user manually or via script
4. Set production environment variables
5. Deploy frontend and backend
6. Configure DNS and SSL

## 📚 API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Auth**:
- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `GET /auth/verify` - Verify token

**Resident**:
- `GET /resident/profile`
- `POST /resident/questionnaire`
- `GET /resident/matches`
- `POST /resident/feedback`

**Operator**:
- `GET /operator/dashboard`
- `POST /operator/properties`
- `POST /operator/match-runs`
- `GET /operator/match-runs/{id}/results`

**Admin**:
- `GET /admin/metrics`
- `GET /admin/events`
- `GET /admin/users`

## 🗺️ Product Roadmap (Post-MVP)

### Phase 2 - Enhanced Matching
- ML-based conflict prediction model
- Natural language processing for open-text responses
- Personality type integration (MBTI, Big Five)
- Video intro profiles

### Phase 3 - Conflict Resolution OS
- In-app mediation tools
- Conflict resolution workflows
- House rules builder & e-signature
- Anonymous feedback channels

### Phase 4 - Expense Management
- Expense splitting & tracking
- Automated bill reminders
- Venmo/PayPal integration
- Shared household budget

### Phase 5 - Community Features
- Household chat
- Shared calendar
- Chore rotation scheduler
- Community events board

### Phase 6 - Enterprise
- Multi-property management
- Advanced analytics & reporting
- White-label options
- API for property management systems

## 🤝 Contributing

This is a pilot MVP. For production deployment:

1. Replace dev secrets with production secrets
2. Set up proper CI/CD pipeline
3. Add comprehensive error logging (Sentry)
4. Implement rate limiting
5. Add database backups
6. Set up monitoring (Datadog, New Relic)
7. Add end-to-end tests (Playwright)
8. Implement email notifications
9. Add payment processing (Stripe)

## 📄 License

Copyright © 2024 Lease Peace. All rights reserved.

## 📞 Support

For pilot program inquiries: pilot@leasepeace.com

---

**Built with ❤️ to create harmonious living spaces**
