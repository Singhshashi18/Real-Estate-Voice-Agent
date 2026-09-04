# Inbound Receptionist Agent
<img width="1252" height="631" alt="image" src="https://github.com/user-attachments/assets/f9ed9a6c-0075-4634-9bee-4f007e335774" />
<img width="1240" height="626" alt="image" src="https://github.com/user-attachments/assets/17365b73-c938-4370-8ced-72c8efd76b8a" />
<img width="1243" height="642" alt="image" src="https://github.com/user-attachments/assets/270c3b7a-8d2c-41f8-a0ad-d87d861dfd59" />
<img width="1253" height="640" alt="image" src="https://github.com/user-attachments/assets/cbc340d4-5cfe-4174-a434-564363f7fce3" />
<img width="1269" height="587" alt="image" src="https://github.com/user-attachments/assets/5aca08b1-92d8-471a-9680-77129be60357" />
 
 

AI voice receptionist **Sara** for **Karyan Realty** (NCR). Sara helps callers find properties, answers questions, and books 30-minute site visits on Google Calendar with **Google Meet** invites.

## Channels

| Channel | Voice | How |
|---------|-------|-----|
| **Browser (inbound)** | OpenAI Realtime (`shimmer`) | Next.js app → WebRTC |
| **Phone (inbound)** | ElevenLabs (voice you pick) | Twilio number → ElevenLabs agent → backend webhooks |
| **Phone (outbound)** | ElevenLabs (Sara, outbound persona) | CSV leads → ElevenLabs batch calling → Twilio |

> **Live number:** `+1 (661) 486-4467` is provisioned and **attached to the agent**. Inbound calls route through Twilio (`voice_url → https://api.us.elevenlabs.io/twilio/inbound_call`) to the ElevenLabs agent.

No LangChain / LangGraph — OpenAI Realtime (browser) + ElevenLabs Conversational AI (phone), with plain Python tool services.

## What it does

1. Voice conversation in the browser (OpenAI Realtime API) or over the phone (ElevenLabs)
2. Searches the Karyan knowledge base (property, budget in lakh/crore, BHK, NCR areas)
3. Collects caller **name** and **email** 
4. Checks your Google Calendar availability (Mon–Fri, 9 AM–9 PM IST, up to 14 days ahead)
5. Books the meeting and emails a **Google Calendar invite** with **Google Meet**
6. **Outbound:** follows up on property leads via ElevenLabs batch calling (CSV upload)

## Prerequisites

- Python 3.11+
- Node.js 18+ (frontend)
- OpenAI API key with Realtime API access
- Google Cloud OAuth client credentials as `credentials.json` in the project root
- Google Calendar API + Gmail API enabled for your project
- **Phone (optional):** Twilio number, ElevenLabs account + API key

## Setup

```bash
cd INBOUND-AGENT 
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Quick Start

Run these commands to launch the backend service after setup:

```bash
python app.py
```
