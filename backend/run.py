from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 YouTube Comment Analyzer API Starting...")
    print("📊 Features: Large-scale scraping, AI analysis, trend analysis")
    print("🔗 Health check: http://localhost:5001/api/health")
    app.run(debug=True, host='0.0.0.0', port=5001)  # 改成 5001