# Vendo AI Analytics Assistant

A sophisticated AI-powered analytics assistant that provides real-time business insights through natural language conversations. Built with Next.js, FastAPI, and WebSocket connections for seamless real-time communication.

## ✨ Features

- **🤖 AI-Powered Chat Interface** - Natural language queries for business analytics
- **📊 Dynamic Chart Generation** - Automatic visualization of data insights
- **🔗 Real-time WebSocket Connection** - Live streaming responses with status indicators
- **🎯 Multi-Agent Architecture** - Specialized agents for data analysis, planning, and retrieval
- **📈 BigQuery Integration** - Direct access to your data warehouse
- **🔥 Firebase Backend** - Real-time database and authentication
- **📱 Responsive Design** - Works seamlessly on desktop and mobile
- **🎤 Voice Integration** - Speech-to-text and text-to-speech capabilities
- **⭐ Message Ratings** - Feedback system for continuous improvement
- **📋 Business Context Management** - Maintain context across conversations
- **🚀 Slack Integration** - Connect with your team workflows

## 🏗️ Architecture

### Frontend (Next.js 15)
- React 19 with App Router
- Tailwind CSS + Shadcn UI components
- WebSocket client for real-time communication
- Audio recording and playback
- Dynamic chart rendering

### Backend (FastAPI)
- Multi-agent system with specialized roles:
  - **Analyst Agent** - Data analysis and insights
  - **Data Planner** - Query planning and optimization  
  - **Data Retrieval** - Fetching and processing data
- WebSocket server for real-time streaming
- Firebase integration for data persistence
- BigQuery integration for analytics
- Slack bot integration

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Google Cloud account with BigQuery access
- Firebase project
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd ai-sdk-preview-python-streaming
```

2. **Frontend Setup**
```bash
# Install Node.js dependencies
npm install
# or
pnpm install
```

3. **Backend Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r api/requirements.txt
```

4. **Environment Configuration**

Create a `.env.local` file in the root directory:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google Cloud
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_API_KEY=your_google_api_key
FIREBASE_DB_URL=https://your-project.firebaseio.com/

# Langfuse (Optional - for observability)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://us.cloud.langfuse.com

# Slack (Optional)
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_APP_TOKEN=your_slack_app_token

# API Configuration
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

5. **Firebase Setup**

Place your Firebase service account key as `adk_cred.json` in the root directory.

6. **Run the Application**

```bash
# Terminal 1: Start the backend
cd api
uvicorn index:app --reload --port 8000

# Terminal 2: Start the frontend
npm run dev
# or
pnpm dev
```

Visit `http://localhost:3000` to start using the AI assistant!

## 🔧 Configuration

### Business Context
- Configure your business information in the Firebase console
- Set up data schemas in `api/agents/business_data/schemas_v2.py`
- Customize agent prompts in the respective agent directories

### BigQuery Integration
- Ensure your service account has BigQuery access
- Configure your dataset and table names in the agent tools
- Set up proper IAM permissions for data access

## 🏢 Deployment

### Netlify (Frontend)
The frontend is configured for Netlify deployment with automatic Python file exclusion.

### Google Cloud Run (Backend)
Use the provided `Dockerfile` and deployment scripts for Cloud Run deployment.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- [AI SDK Documentation](https://sdk.vercel.ai/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Firebase Documentation](https://firebase.google.com/docs)
