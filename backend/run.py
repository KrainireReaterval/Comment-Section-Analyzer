from app import create_app
import logging

logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info("🚀 YouTube Comment Analyzer API Starting...")
    logger.info("📊 Features: Large-scale scraping, AI analysis, trend analysis")
    logger.info("🔗 Health check: http://localhost:5001/api/health")
    app.run(debug=True, host='0.0.0.0', port=5001)  # 改成 5001