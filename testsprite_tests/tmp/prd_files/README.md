# YouTube Comment Section Analyzer

A comprehensive web application that analyzes YouTube video comment sections using AI-powered sentiment analysis, topic extraction, and trend visualization.

## 🚀 Features

- **AI-Powered Analysis**: Advanced sentiment analysis and topic extraction using machine learning
- **Large Scale Processing**: Analyze up to 10,000 comments per video
- **Interactive Visualizations**: Beautiful charts and graphs for data insights
- **Real-time Processing**: Get instant insights from comment analysis
- **Trend Analysis**: See how comments evolve over time
- **Controversy Detection**: Identify controversial topics and discussions
- **Responsive Design**: Works perfectly on desktop and mobile devices

## 🛠️ Tech Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **YouTube Data API**: Comment scraping
- **OpenAI API**: AI analysis and topic extraction
- **Redis**: Task queue management

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js**: Interactive data visualization
- **Lucide Icons**: Beautiful icon library

## 📋 Prerequisites

- Python 3.8+
- Node.js (for frontend dependencies)
- YouTube Data API key
- OpenAI API key

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from app import create_app, db; create_app().app_context().push(); db.create_all()"

# Start backend server
python run.py
```

### 2. Frontend Setup

```bash
# Navigate to project root
cd /Users/wangxiansen/Desktop/Comment-Section-Analyzer

# Start frontend server
python start_server.py
```

### 3. Access the Application

Open your browser and go to: `http://localhost:8080`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///youtube_comments.db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_here
```

### API Configuration

The frontend is configured to connect to the backend API at `http://localhost:5000/api`. If your backend runs on a different port, update the `API_BASE_URL` in `index.html`.

## 📊 How It Works

### 1. Video Analysis Process

1. **URL Input**: User pastes a YouTube video URL
2. **Video Validation**: System validates the URL and extracts video ID
3. **Comment Scraping**: Backend scrapes comments using YouTube Data API
4. **AI Analysis**: Comments are analyzed for sentiment and topics
5. **Data Processing**: Results are processed and stored in database
6. **Visualization**: Frontend displays interactive charts and insights

### 2. Analysis Features

- **Sentiment Analysis**: Categorizes comments as positive, negative, or neutral
- **Topic Extraction**: Identifies main discussion topics using AI
- **Trend Analysis**: Shows comment patterns over time
- **Controversy Detection**: Identifies highly debated topics
- **Statistical Insights**: Provides comprehensive metrics and percentages

## 🎨 User Interface

### Homepage
- Clean, modern design with gradient background
- URL input form for video and creator profile
- Configurable comment limit (500-10,000)
- Feature highlights and benefits

### Analysis Report
- **Video Information**: Title, views, likes, comments, duration
- **Sentiment Overview**: Overall sentiment distribution
- **Topic Analysis**: Main discussion topics with percentages
- **Sample Comments**: Representative comments with sentiment labels
- **Interactive Charts**: Doughnut charts for sentiment distribution

## 🔌 API Endpoints

### Backend API

- `POST /api/analyze` - Analyze a video's comments
- `GET /api/video/<video_id>/report` - Get detailed analysis report
- `GET /api/videos` - List all analyzed videos
- `GET /api/health` - Health check endpoint

### Request/Response Examples

**Analyze Video:**
```json
POST /api/analyze
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "max_comments": 1000
}
```

**Get Report:**
```json
GET /api/video/VIDEO_ID/report
{
  "video": { ... },
  "summary": { ... },
  "topics": [ ... ],
  "time_trends": [ ... ],
  "comments_sample": [ ... ]
}
```

## 🎯 Use Cases

- **Content Creators**: Understand audience sentiment and engagement
- **Marketing Teams**: Analyze brand mentions and customer feedback
- **Researchers**: Study social media trends and public opinion
- **Educators**: Analyze discussion patterns in educational content

## 🚀 Deployment

### Production Setup

1. **Backend Deployment**:
   - Deploy Flask app to cloud platform (Heroku, AWS, etc.)
   - Set up production database (PostgreSQL recommended)
   - Configure environment variables

2. **Frontend Deployment**:
   - Update API_BASE_URL to production backend URL
   - Deploy static files to CDN or web server
   - Configure CORS settings

### Docker Support

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the backend logs for errors
2. Verify API keys are correctly set
3. Ensure all dependencies are installed
4. Check network connectivity

## 🔮 Future Enhancements

- [ ] Real-time comment monitoring
- [ ] Advanced filtering options
- [ ] Export to PDF/Excel
- [ ] Multi-language support
- [ ] Social media integration
- [ ] Advanced analytics dashboard
                