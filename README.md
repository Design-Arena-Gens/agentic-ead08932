# Outreach Agent

An AI-powered outreach agent that automates cold email campaigns and follow-up calls. The system tracks email responses and automatically schedules voice calls for leads that don't respond within 24 hours.

## Live Demo

- **Frontend**: https://agentic-ead08932.vercel.app
- **Backend API**: https://app-lefjqlct.fly.dev

## Features

### Chat Interface
- Interactive AI chatbot assistant for managing outreach campaigns
- Natural language commands for lead management
- Real-time conversation with intelligent responses

### Lead Management Dashboard
- Add and manage leads with contact information
- Track lead status (new, contacted, responded, call_scheduled)
- View comprehensive statistics and metrics
- Send cold emails directly from the dashboard
- Delete leads as needed

### Automated Email Outreach
- Send personalized cold emails to leads
- Track email send times and responses
- Mark emails as responded when leads reply
- View email history per lead

### Automated Follow-up Calls
- Background scheduler checks for non-responsive emails every 5 minutes
- Automatically schedules voice calls 24 hours after sending an email if no response
- Updates lead status to "call_scheduled" when a call is queued
- Requires lead to have a phone number for call scheduling

### Analytics
- Total leads count
- Total emails sent
- Response rate percentage
- Scheduled calls count

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and settings management
- **APScheduler**: Background job scheduling for automated calls
- **In-memory database**: Fast data storage (data resets on restart)

### Frontend
- **React + TypeScript**: Type-safe UI development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Beautiful pre-built components
- **Lucide React**: Icon library

## Project Structure

```
agentic-ead08932/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py          # FastAPI application with all endpoints
│   ├── pyproject.toml        # Python dependencies
│   └── poetry.lock
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx      # Chat UI component
│   │   │   ├── LeadsDashboard.tsx     # Lead management UI
│   │   │   └── ui/                    # shadcn/ui components
│   │   ├── App.tsx                    # Main app component
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## API Endpoints

### Leads
- `POST /api/leads` - Create a new lead
- `GET /api/leads` - Get all leads
- `GET /api/leads/{lead_id}` - Get a specific lead
- `PUT /api/leads/{lead_id}` - Update a lead
- `DELETE /api/leads/{lead_id}` - Delete a lead

### Emails
- `POST /api/emails` - Send an email to a lead
- `GET /api/emails` - Get all emails
- `GET /api/emails/lead/{lead_id}` - Get emails for a specific lead
- `PUT /api/emails/{email_id}/responded` - Mark an email as responded

### Chat
- `POST /api/chat` - Send a message to the chatbot

### Stats
- `GET /api/stats` - Get outreach statistics

### Health
- `GET /healthz` - Health check endpoint

## Local Development

### Backend Setup

```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

The backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173

## How It Works

### Automated Call Scheduling

The system uses APScheduler to run a background job every 5 minutes that:

1. Checks all sent emails in the database
2. Calculates time elapsed since each email was sent
3. For emails sent more than 24 hours ago without a response:
   - Verifies the lead has a phone number
   - Schedules a call for 5 minutes from now
   - Updates the lead status to "call_scheduled"
   - Logs the scheduled call time

### Lead Status Flow

```
new → contacted → responded
  ↓
call_scheduled (if no response after 24 hours)
```

## Data Persistence

The application uses an in-memory database, which means:
- Data is stored in Python dictionaries
- All data is lost when the backend restarts
- Perfect for proof-of-concept and testing
- For production, consider migrating to PostgreSQL or MongoDB

## Deployment

### Backend (Fly.io)
The backend is deployed using FastAPI on Fly.io and is accessible at the production URL.

### Frontend (Vercel)
The frontend is deployed on Vercel with automatic builds from the main branch.

## Future Enhancements

- Integrate with actual email service providers (SendGrid, Mailgun)
- Connect to voice calling APIs (Twilio, Bland AI)
- Add persistent database (PostgreSQL)
- Implement user authentication
- Add email templates
- Schedule calls at specific times
- Track call outcomes
- Add more analytics and reporting
- Implement webhook handlers for email responses
- Add bulk import for leads

## Contributing

This project was built by Devin for Design Arena Founders.

## License

MIT
