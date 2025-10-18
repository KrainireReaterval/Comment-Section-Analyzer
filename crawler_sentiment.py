"""
Integrated YouTube Comment Scraper + Sentiment Analyzer
Scrapes comments from YouTube and performs real-time sentiment analysis
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR, SORT_BY_RECENT
from itertools import islice
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

# Import NLTK for sentiment analysis
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except ImportError:
    print("Installing NLTK...")
    os.system(f"{sys.executable} -m pip install nltk")
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading VADER lexicon...")
    nltk.download('vader_lexicon', quiet=True)


class Log_week:
    """Logger class for tracking operations"""
    def get_logger(self):
        self.logger = logging.getLogger(__name__)
        formatter = '[%(asctime)s-%(filename)s][%(funcName)s-%(lineno)d]--%(message)s'
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        sh = logging.StreamHandler()
        log_formatter = logging.Formatter(formatter, datefmt='%Y-%m-%d %H:%M:%S')
        
        # File handler
        info_file_name = time.strftime("%Y-%m-%d") + '.log'
        case_dir = r'./logs/'
        info_handler = TimedRotatingFileHandler(
            filename=case_dir + info_file_name,
            when='MIDNIGHT',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        
        self.logger.addHandler(sh)
        sh.setFormatter(log_formatter)
        self.logger.addHandler(info_handler)
        info_handler.setFormatter(log_formatter)
        return self.logger


class SentimentAnalyzer:
    """Sentiment analysis using VADER"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text: str) -> dict:
        """Analyze sentiment of a single text"""
        if not text or not isinstance(text, str):
            return {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
        
        scores = self.analyzer.polarity_scores(text)
        return scores
    
    def classify_sentiment(self, compound_score: float) -> str:
        """Classify sentiment based on compound score"""
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """Add sentiment analysis columns to dataframe"""
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found")
        
        # Analyze each comment
        df['sentiment_neg'] = 0.0
        df['sentiment_neu'] = 0.0
        df['sentiment_pos'] = 0.0
        df['sentiment_compound'] = 0.0
        df['sentiment_label'] = 'Neutral'
        
        for idx, row in df.iterrows():
            text = str(row[text_column])
            scores = self.analyze_text(text)
            
            df.at[idx, 'sentiment_neg'] = scores['neg']
            df.at[idx, 'sentiment_neu'] = scores['neu']
            df.at[idx, 'sentiment_pos'] = scores['pos']
            df.at[idx, 'sentiment_compound'] = scores['compound']
            df.at[idx, 'sentiment_label'] = self.classify_sentiment(scores['compound'])
        
        return df


class IntegratedYouTubeAnalyzer:
    """Main class combining scraping and sentiment analysis"""
    
    def __init__(self, video_url, comment_num, order_type, txt_msglist, logger, progress_callback=None):
        self.video_url = video_url
        self.video_id = self.extract_video_id(video_url)
        self.comment_num = comment_num
        self.order_type = order_type
        self.txt_msglist = txt_msglist
        self.logger = logger
        self.progress_callback = progress_callback
        self.describe = []
        self.comments_data = []
        self.sentiment_analyzer = SentimentAnalyzer()
        self.results_df = None
        
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[-1].split('?')[0]
        elif 'watch?v=' in url:
            return url.split('watch?v=')[-1].split('&')[0]
        else:
            # Assume it's already a video ID
            return url
    
    def tk_show(self, context):
        """Display message in GUI"""
        self.logger.info(context)
        self.txt_msglist.delete('1.0', 'end')
        self.describe.append(context)
        self.txt_msglist.insert('insert', '\n'.join(self.describe[-50:]))  # Keep last 50 messages
        self.txt_msglist.see("end")
        self.txt_msglist.update()
    
    def trans_time(self, v_timestamp):
        """Convert timestamp to readable format"""
        v_timestamp = int(str(v_timestamp)[:10])
        timeArray = time.localtime(v_timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime
    
    def scrape_and_analyze(self):
        """Main method to scrape comments and perform sentiment analysis"""
        try:
            # Clean up old files
            json_file = f'{self.video_id}.json'
            if os.path.exists(json_file):
                os.remove(json_file)
                self.tk_show(f'Removed existing file: {json_file}')
            
            # Set sort order
            order_type2 = SORT_BY_RECENT
            if self.order_type == 'Sort by Popular':
                order_type2 = SORT_BY_POPULAR
            
            self.tk_show(f'Starting to scrape comments from video: {self.video_id}')
            self.tk_show(f'URL: {self.video_url}')
            
            # Initialize downloader
            downloader = YoutubeCommentDownloader()
            comments = downloader.get_comments_from_url(
                f'https://www.youtube.com/watch?v={self.video_id}',
                sort_by=order_type2
            )
            
            # Limit comments if specified
            if self.comment_num != '-1':
                comment_num2 = int(self.comment_num)
                comments = islice(comments, comment_num2)
                self.tk_show(f'Scraping top {comment_num2} comments...')
            else:
                self.tk_show('Scraping ALL comments (this may take a while)...')
            
            # Scrape comments with real-time sentiment analysis
            cnt = 1
            for comment in comments:
                # Store comment data
                comment_text = comment['text']
                self.comments_data.append(comment)
                
                # Perform sentiment analysis
                sentiment_scores = self.sentiment_analyzer.analyze_text(comment_text)
                sentiment_label = self.sentiment_analyzer.classify_sentiment(
                    sentiment_scores['compound']
                )
                
                # Display progress
                self.tk_show(
                    f'[{cnt}] {sentiment_label} ({sentiment_scores["compound"]:.3f}): '
                    f'{comment_text[:80]}...'
                )
                
                # Save to JSON
                with open(json_file, 'a+', encoding='utf-8') as f:
                    f.write(json.dumps(comment, ensure_ascii=False))
                    f.write('\n')
                
                cnt += 1
                
                # Update progress
                if self.progress_callback:
                    self.progress_callback(cnt)
            
            total_comments = cnt - 1
            self.tk_show(f'\n✓ Successfully scraped {total_comments} comments!')
            
            # Process data
            self.tk_show('\nProcessing data and performing sentiment analysis...')
            self.process_data()
            
            # Generate report
            self.generate_summary_report()
            
            self.tk_show('\n✓ Analysis complete! Check the output files.')
            
        except Exception as e:
            error_msg = f'Error during analysis: {str(e)}'
            self.logger.error(error_msg)
            self.tk_show(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def process_data(self):
        """Process scraped data and add sentiment analysis"""
        try:
            json_file = f'{self.video_id}.json'
            
            # Read JSON data
            df = pd.read_json(json_file, lines=True)
            
            # Clean up columns
            columns_to_drop = ['photo', 'heart', 'reply']
            existing_cols = [col for col in columns_to_drop if col in df.columns]
            if existing_cols:
                df.drop(existing_cols, axis=1, inplace=True)
            
            # Add formatted time
            if 'time_parsed' in df.columns:
                df['time_formatted'] = df['time_parsed'].apply(lambda x: self.trans_time(x))
            
            # Perform sentiment analysis on all comments
            self.tk_show('Analyzing sentiment for all comments...')
            df = self.sentiment_analyzer.analyze_dataframe(df, text_column='text')
            
            # Save results
            excel_file = f'{self.video_id}_analyzed.xlsx'
            csv_file = f'{self.video_id}_analyzed.csv'
            
            df.to_excel(excel_file, index=False, engine='xlsxwriter')
            df.to_csv(csv_file, index=False)
            
            self.results_df = df
            
            self.tk_show(f'✓ Results saved to: {excel_file}')
            self.tk_show(f'✓ Results saved to: {csv_file}')
            
        except Exception as e:
            self.tk_show(f'Error processing data: {str(e)}')
            raise
    
    def generate_summary_report(self):
        """Generate and display summary report"""
        if self.results_df is None:
            return
        
        df = self.results_df
        total = len(df)
        
        # Calculate statistics
        sentiment_counts = df['sentiment_label'].value_counts()
        avg_compound = df['sentiment_compound'].mean()
        
        # Create report
        report = "\n" + "=" * 60 + "\n"
        report += "SENTIMENT ANALYSIS SUMMARY\n"
        report += "=" * 60 + "\n"
        report += f"Video ID: {self.video_id}\n"
        report += f"Total Comments: {total}\n\n"
        
        report += "Sentiment Distribution:\n"
        report += "-" * 40 + "\n"
        for sentiment, count in sentiment_counts.items():
            percentage = (count / total) * 100
            report += f"  {sentiment:10s}: {count:5d} ({percentage:5.1f}%)\n"
        
        report += f"\nAverage Sentiment Score: {avg_compound:.4f}\n"
        
        # Overall sentiment
        if avg_compound >= 0.05:
            overall = "POSITIVE ✓"
        elif avg_compound <= -0.05:
            overall = "NEGATIVE ✗"
        else:
            overall = "NEUTRAL ~"
        
        report += f"Overall Sentiment: {overall}\n"
        
        # Top comments
        report += "\n" + "Top 3 Most Positive Comments:\n"
        report += "-" * 40 + "\n"
        top_positive = df.nlargest(3, 'sentiment_compound')
        for idx, row in top_positive.iterrows():
            report += f"  [{row['sentiment_compound']:.3f}] {row['text'][:60]}...\n"
        
        report += "\n" + "Top 3 Most Negative Comments:\n"
        report += "-" * 40 + "\n"
        top_negative = df.nsmallest(3, 'sentiment_compound')
        for idx, row in top_negative.iterrows():
            report += f"  [{row['sentiment_compound']:.3f}] {row['text'][:60]}...\n"
        
        report += "=" * 60 + "\n"
        
        # Save report
        report_file = f'{self.video_id}_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.tk_show(report)
        self.tk_show(f'✓ Report saved to: {report_file}')


class MyThread(threading.Thread):
    """Thread wrapper for background processing"""
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        self.daemon = True
        self.start()
    
    def run(self):
        self.func(*self.args)


def start_analysis(video_url, comment_num, order_type, txt_msglist, status_label):
    """Start the analysis process"""
    url = video_url.get().strip()
    cn = comment_num.get()
    ot = order_type.get()
    
    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube URL or video ID")
        return
    
    status_label.config(text="Status: Running...", fg="orange")
    
    log = Log_week()
    logger = log.get_logger()
    
    def progress_update(count):
        status_label.config(text=f"Status: Processing comment {count}...")
    
    analyzer = IntegratedYouTubeAnalyzer(
        url, cn, ot, txt_msglist, logger, progress_callback=progress_update
    )
    
    try:
        analyzer.scrape_and_analyze()
        status_label.config(text="Status: Complete ✓", fg="green")
    except Exception as e:
        status_label.config(text=f"Status: Error - {str(e)}", fg="red")


def show_visualization(video_id_var):
    """Open visualization window"""
    video_id = video_id_var.get().strip()
    
    if not video_id:
        messagebox.showwarning("Warning", "Please run analysis first")
        return
    
    # Extract video ID if URL provided
    if 'youtu' in video_id:
        if 'youtu.be/' in video_id:
            video_id = video_id.split('youtu.be/')[-1].split('?')[0]
        elif 'watch?v=' in video_id:
            video_id = video_id.split('watch?v=')[-1].split('&')[0]
    
    csv_file = f'{video_id}_analyzed.csv'
    
    if not os.path.exists(csv_file):
        messagebox.showwarning("Warning", f"No analysis results found for {video_id}")
        return
    
    # Load data
    df = pd.read_csv(csv_file)
    
    # Create visualization window
    viz_window = tk.Toplevel()
    viz_window.title(f"Sentiment Analysis Visualization - {video_id}")
    viz_window.geometry("1200x800")
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(f'Sentiment Analysis - Video: {video_id}', fontsize=14, fontweight='bold')
    
    # 1. Sentiment Distribution Pie Chart
    sentiment_counts = df['sentiment_label'].value_counts()
    colors = {'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'}
    pie_colors = [colors.get(sent, '#3498db') for sent in sentiment_counts.index]
    
    axes[0, 0].pie(sentiment_counts.values, labels=sentiment_counts.index,
                   autopct='%1.1f%%', startangle=90, colors=pie_colors)
    axes[0, 0].set_title('Sentiment Distribution')
    
    # 2. Compound Score Histogram
    axes[0, 1].hist(df['sentiment_compound'], bins=50, color='skyblue', edgecolor='black')
    axes[0, 1].axvline(x=0.05, color='green', linestyle='--', alpha=0.7, label='Positive')
    axes[0, 1].axvline(x=-0.05, color='red', linestyle='--', alpha=0.7, label='Negative')
    axes[0, 1].set_xlabel('Compound Score')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Sentiment Score Distribution')
    axes[0, 1].legend()
    
    # 3. Sentiment Scores Box Plot
    score_data = df[['sentiment_neg', 'sentiment_neu', 'sentiment_pos']].melt(
        var_name='Score Type', value_name='Score'
    )
    score_data['Score Type'] = score_data['Score Type'].str.replace('sentiment_', '')
    sns.boxplot(data=score_data, x='Score Type', y='Score', ax=axes[1, 0])
    axes[1, 0].set_title('Score Distribution by Type')
    axes[1, 0].set_ylabel('Score')
    
    # 4. Sentiment Bar Chart
    sentiment_counts.plot(kind='bar', ax=axes[1, 1], 
                         color=[colors.get(sent, '#3498db') for sent in sentiment_counts.index])
    axes[1, 1].set_title('Comment Count by Sentiment')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].set_xlabel('Sentiment')
    axes[1, 1].tick_params(axis='x', rotation=0)
    
    plt.tight_layout()
    
    # Embed in tkinter
    canvas = FigureCanvasTkAgg(fig, master=viz_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Add summary label
    total = len(df)
    avg_score = df['sentiment_compound'].mean()
    summary_text = f"Total Comments: {total} | Average Sentiment: {avg_score:.3f}"
    
    summary_label = tk.Label(viz_window, text=summary_text, font=('Arial', 12, 'bold'))
    summary_label.pack(pady=10)


# ======================= GUI SETUP =======================

# Create log directory
work_path = os.getcwd()
if not os.path.exists(work_path + "/logs"):
    os.makedirs(work_path + "/logs")

# Main window
root = tk.Tk()
root.title('YouTube Comment Analyzer - Scraper + Sentiment Analysis')
root.minsize(width=900, height=700)

# Title
title_label = tk.Label(root, text='YouTube Comment Sentiment Analyzer', 
                       font=('Arial', 16, 'bold'), fg='#2c3e50')
title_label.place(x=200, y=10)

# Status
status_label = tk.Label(root, text='Status: Ready', font=('Arial', 10), fg='green')
status_label.place(x=30, y=50)

# Video URL input
tk.Label(root, text='YouTube URL:', font=('Arial', 10, 'bold')).place(x=30, y=90)
video_url = tk.StringVar()
video_url.set('')
url_entry = tk.Entry(root, bg='#ffffff', width=60, textvariable=video_url)
url_entry.place(x=160, y=90)
tk.Label(root, text='(Full URL or Video ID)', font=('Arial', 8), fg='gray').place(x=160, y=115)

# Comment count
tk.Label(root, text='Comment Count:', font=('Arial', 10, 'bold')).place(x=30, y=145)
comment_num = tk.StringVar()
comment_num.set('100')
entry = tk.Entry(root, bg='#ffffff', width=15, textvariable=comment_num)
entry.place(x=160, y=145)
tk.Label(root, text='(-1 = scrape all, may take very long)', 
         font=('Arial', 8), fg='gray').place(x=280, y=145)

# Sort method
tk.Label(root, text='Sort Method:', font=('Arial', 10, 'bold')).place(x=30, y=180)
order_type = ttk.Combobox(root, width=20)
order_type['value'] = ('Sort by Date', 'Sort by Popular')
order_type.current(0)
order_type.place(x=160, y=180)

# Output display
show_list_Frame = tk.Frame(width=840, height=370, bg='white', relief=tk.SUNKEN, bd=2)
show_list_Frame.pack_propagate(0)
show_list_Frame.place(x=30, y=220)

scroll = tk.Scrollbar(show_list_Frame)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

txt_msglist = tk.Text(show_list_Frame, width=120, height=25, font=('Courier', 9))
txt_msglist.config(yscrollcommand=scroll.set)
scroll.config(command=txt_msglist.yview)
txt_msglist.pack()

# Buttons
button_frame = tk.Frame(root)
button_frame.place(x=250, y=610)

start_button = tk.Button(
    button_frame, bg='#27ae60', fg='white', text='Start Analysis', 
    width=15, height=1, font=('Arial', 10, 'bold'),
    command=lambda: MyThread(start_analysis, video_url, comment_num, order_type, 
                            txt_msglist, status_label)
)
start_button.grid(row=0, column=0, padx=5)

viz_button = tk.Button(
    button_frame, bg='#3498db', fg='white', text='Show Visualization', 
    width=15, height=1, font=('Arial', 10, 'bold'),
    command=lambda: show_visualization(video_url)
)
viz_button.grid(row=0, column=1, padx=5)

quit_button = tk.Button(
    button_frame, bg='#e74c3c', fg='white', text='Quit', 
    width=10, height=1, font=('Arial', 10, 'bold'),
    command=root.quit
)
quit_button.grid(row=0, column=2, padx=5)

# Footer
footer = tk.Label(root, text='Integrated YouTube Comment Analyzer with Sentiment Analysis', 
                 font=('Arial', 9), fg='gray')
footer.place(x=260, y=670)

# Note
note = tk.Label(root, text='Note: VPN may be required. Large comment counts may take time.',
               font=('Arial', 8), fg='red')
note.place(x=250, y=650)

# Run
root.mainloop()