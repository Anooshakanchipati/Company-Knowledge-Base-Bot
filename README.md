Company Knowledge Base Bot

An AI-powered Retrieval-Augmented Generation (RAG) application that answers questions using information from uploaded company documents. Administrators can upload and delete multiple documents, while authenticated users can ask questions, view sources, and manage their conversation history.

Problem Statement

Company information is often distributed across policies, manuals, reports, and other documents. Employees may spend significant time searching through these files to find accurate answers.

The Company Knowledge Base Bot solves this problem by retrieving relevant content from uploaded documents and using an AI model to generate a clear, document-grounded answer.

Key Features

User registration and login

JWT-based authentication and protected routes

Role-based access for users and administrators

Secure administrator assignment using ADMIN_EMAIL

Upload multiple company documents

View and delete uploaded documents

Document text extraction, chunking, and embedding

Semantic search over document chunks

RAG-based answers grounded only in uploaded documents

Gemini as the primary AI model

Grok/xAI as an optional fallback model

Source document and chunk references

Saved conversations and chat history

Delete previous conversations

Responsive React user interface

Friendly response when AI providers are unavailable

How RAG Works

An administrator uploads one or more company documents.

The backend extracts the text from each document.

The text is divided into smaller chunks.

Each chunk is converted into an embedding and stored in the vector database.

When a user asks a question, the system searches for the most relevant chunks.

The retrieved chunks and question are sent to Gemini.

If Gemini fails, the system can try the optional Grok fallback.

The answer and its document sources are returned to the user and saved in chat history.

Technologies Used

Frontend

React.js

Vite

JavaScript

CSS

Axios

React Router

React Markdown

Backend

Python

FastAPI

Uvicorn

SQLAlchemy

Pydantic

JWT authentication

Passlib/bcrypt password hashing

Database and AI

SQLite for local development

Vector database or vector store for document embeddings

Google Gemini API for primary answer generation

xAI Grok API for optional fallback answer generation

Deployment

Render for backend and frontend deployment

GitHub for source-code management

Project Structure

company-knowledge-base-bot/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── admin.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── gemini_service.py
│   │   │   ├── grok_service.py
│   │   │   └── vector_store.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── security.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── .env.example
└── README.md

The exact folders may differ slightly depending on the final project structure.

Prerequisites

Install the following software before running the project:

Python 3.10 or later

Node.js 18 or later

npm

Git

A Google Gemini API key

An xAI API key with API credits, only if the Grok fallback is enabled

Local Installation

1. Clone the repository

git clone <your-github-repository-url>
cd company-knowledge-base-bot

2. Set up the backend

On Windows:

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

On macOS or Linux:

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Create backend/.env:

SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ADMIN_EMAIL=your-admin-email@example.com
GEMINI_API_KEY=your-gemini-api-key
XAI_API_KEY=your-xai-api-key
GROK_MODEL=your-supported-grok-model

XAI_API_KEY and GROK_MODEL are optional when Grok fallback is disabled. A free API key alone may not include xAI API credits.

Start the backend:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Backend API documentation:

http://127.0.0.1:8000/docs

3. Set up the frontend

Open a second terminal:

cd frontend
npm install

Create frontend/.env:

VITE_API_BASE_URL=http://127.0.0.1:8000

Start the frontend:

npm run dev

Open the URL shown by Vite, normally:

http://localhost:5173

Admin Setup

Add the administrator's exact email address to ADMIN_EMAIL.

Register or log in using that email address.

Log out and log in again after changing ADMIN_EMAIL, so a new JWT containing the administrator role is created.

Open the Admin Dashboard.

Upload the company documents.

Normal users must not be able to access administrator endpoints.

Usage

Administrator

Register and log in using the configured administrator email.

Open the Admin Dashboard.

Select and upload one or more supported documents.

Check that the documents appear in the document list.

Delete outdated documents when required.

User

Register or log in.

Open the chat page.

Ask a question about the uploaded documents.

Review the generated answer and its sources.

Open an earlier conversation from the chat history when needed.

Main API Endpoints

Method

Endpoint

Purpose

POST

/api/auth/register

Register a user

POST

/api/auth/login

Log in and receive a JWT

GET

/api/auth/me

Get the logged-in user

GET

/api/admin/check

Verify administrator access

GET

/api/admin/documents

List uploaded documents

POST

/api/admin/documents/upload

Upload one or more documents

DELETE

/api/admin/documents/{document_id}

Delete a document

POST

/api/chat/ask

Ask a document-based question

GET

/api/chat/conversations

List the user's conversations

GET

/api/chat/conversations/{conversation_id}

Get one conversation

DELETE

/api/chat/conversations/{conversation_id}

Delete a conversation

Testing Questions

After uploading company documents, test questions such as:

What is the company's mission?

What services does the company provide?

What is the employee leave policy?

How can an employee apply for leave?

What are the company's working hours?

Summarize the uploaded document.

Which document contains the leave-policy information?

Compare the information in two uploaded documents.

Ask the same question in different ways to test consistency:

What is the company's leave policy?

Can you explain the leave policy?

What are the rules for taking leave?

Also ask a question whose answer is not present in the documents. The expected response is:

I could not find this information in the uploaded company documents.

Deployment on Render

Backend service

Root directory: backend

Build command: pip install -r requirements.txt

Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

Add all backend environment variables in Render. Never commit the .env file or API keys to GitHub.

Frontend service

Root directory: frontend

Build command: npm install && npm run build

Publish directory: dist

Set VITE_API_BASE_URL to the deployed backend URL, then redeploy the frontend.

Deployment Links

Live application: https://company-knowledge-base-bot-1.onrender.com

GitHub repository: <add-your-github-repository-url>

Screenshots

Add screenshots to a screenshots folder and update the paths below:

resigition:<img width="1920" height="1080" alt="Screenshot 2026-08-07 150726" src="https://github.com/user-attachments/assets/9786c205-56fc-4d96-b42d-3d5d83cfaf4c" />
loging page:<img width="1920" height="1080" alt="Screenshot 2026-08-07 150718" src="https://github.com/user-attachments/assets/efe67fc4-d20b-46a9-80c7-2050152e95ae" />
admni page:<img width="1920" height="1080" alt="Screenshot 2026-08-07 150850" src="https://github.com/user-attachments/assets/d38aeb26-5d55-48db-9a4f-856a8bcc7435" />
chatbot:<img width="1920" height="1080" alt="Screenshot 2026-08-06 214444" src="https://github.com/user-attachments/assets/5d8ff792-90c4-4537-bf60-2fac9f548c97" />
<img width="1920" height="1080" alt="Screenshot 2026-08-06 214401" src="https://github.com/user-attachments/assets/9af825e5-1488-4bce-9dd0-d6f462e139db" />
<img width="1920" height="1080" alt="Screenshot 2026-08-06 214033" src="https://github.com/user-attachments/assets/09cee3b1-5950-42c0-896e-df6be6b176ef" />


Error Handling

Empty questions return a clear validation error.

Unauthorized requests are blocked.

Normal users cannot access administrator features.

Questions without relevant document content return a document-not-found response.

Gemini failures are retried before using the optional fallback provider.

If all configured AI providers fail, the application returns a friendly temporary-unavailable message instead of exposing provider errors.

Security Notes

Do not commit .env, API keys, database credentials, or JWT secrets.

Use a long random value for SECRET_KEY in production.

Store passwords only as secure hashes.

Restrict upload and delete operations to administrators.

Validate uploaded file types and file sizes.

Configure CORS to allow only trusted frontend origins in production.

Rotate any key immediately if it is accidentally committed.


Author

Anusha Kanchipati
