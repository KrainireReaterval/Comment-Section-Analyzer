import os
import tkinter as tk
from tkinter import ttk
import threading
import json
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR, SORT_BY_RECENT
from itertools import islice
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import pandas as pd


class Log_week:
    def get_logger(self):
        self.logger = logging.getLogger(__name__)
        # Log format
        formatter = '[%(asctime)s-%(filename)s][%(funcName)s-%(lineno)d]--%(message)s'
        # Log level
        self.logger.setLevel(logging.DEBUG)
        # Console log
        sh = logging.StreamHandler()
        log_formatter = logging.Formatter(formatter, datefmt='%Y-%m-%d %H:%M:%S')
        # Info log filename
        info_file_name = time.strftime("%Y-%m-%d") + '.log'
        # Save to specific directory
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


class YouTubeCommentSpider:
    def __init__(self, video_id, comment_num, order_type, txt_msglist, logger):
        self.video_id = video_id
        self.comment_num = comment_num
        self.order_type = order_type
        self.txt_msglist = txt_msglist
        self.logger = logger
        self.describe = []

    def tk_show(self, context):
        self.logger.info(context)
        self.txt_msglist.delete('1.0', 'end')
        self.describe.append(context)
        self.txt_msglist.insert('insert', '\n'.join(self.describe))
        self.txt_msglist.see("end")

    def trans_time(self, v_timestamp):
        """Convert 10-digit timestamp to time string"""
        v_timestamp = int(str(v_timestamp)[:10])
        timeArray = time.localtime(v_timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime

    def spider(self):
        if os.path.exists('{}.json'.format(self.video_id)):
            os.remove('{}.json'.format(self.video_id))
            self.tk_show('JSON file exists, automatically deleted: {}'.format('{}.json'.format(self.video_id)))
        
        order_type2 = SORT_BY_RECENT  # Default sort by date
        if self.order_type == 'Sort by Popular':
            order_type2 = SORT_BY_POPULAR
        
        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(
            'https://www.youtube.com/watch?v={}'.format(self.video_id),
            sort_by=order_type2
        )
        
        cnt = 1
        if self.comment_num != '-1':
            comment_num2 = int(self.comment_num)
            comments = islice(comments, comment_num2)  # Get TOP n comments
        
        for comment in comments:
            self.tk_show('[{}] comment: {}'.format(cnt, comment['text']))
            with open('{}.json'.format(self.video_id), 'a+', encoding='utf-8') as f:
                f.write(json.dumps(comment, ensure_ascii=False))
                f.write('\n')
            cnt += 1
        
        # Convert JSON to Excel
        try:
            df = pd.read_json('{}.json'.format(self.video_id), lines=True)
            df.drop(['photo', 'heart', 'reply'], axis=1, inplace=True)  # Remove unused columns
            df['time2'] = df['time_parsed'].apply(lambda x: self.trans_time(x))
            df.to_excel('{}.xlsx'.format(self.video_id), index=False, engine='xlsxwriter')
            self.tk_show('Output file created: {}.xlsx'.format(self.video_id))
        except Exception as e:
            self.tk_show('JSON conversion failed [{}]: {}'.format(self.video_id, str(e)))


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        self.setDaemon(True)
        self.start()  # Start here

    def run(self):
        self.func(*self.args)


def task(video_id, comment_num, order_type, txt_msglist):
    vid = video_id.get()
    cn = comment_num.get()
    ot = order_type.get()
    log = Log_week()
    logger = log.get_logger()
    YouTubeCommentSpider(vid, cn, ot, txt_msglist, logger).spider()


# Create log directory
work_path = os.getcwd()
if not os.path.exists(work_path + "/logs"):
    os.makedirs(work_path + "/logs")

# Create main window
root = tk.Tk()
root.title('YouTube Comment Scraper v2.0')
# Set window size
root.minsize(width=850, height=650)

show_list_Frame = tk.Frame(width=800, height=350)  # Create message list section
show_list_Frame.pack_propagate(0)
show_list_Frame.place(x=30, y=180, anchor='nw')  # Position

# Scrollbar
scroll = tk.Scrollbar(show_list_Frame)
# Place on Y-axis vertical direction
scroll.pack(side=tk.RIGHT, fill=tk.Y)

# Input crawling progress
txt_msglist = tk.Text(show_list_Frame, width=700, height=500)
txt_msglist.config(yscrollcommand=scroll.set)  # Configure scrollbar
txt_msglist.pack()

# Prompt message
show_msg = tk.Label(root, text='Note: VPN/proxy may be required to access YouTube.', font=('Arial', 12), fg='red')
show_msg.place(x=30, y=20)

# Interface design
# Video ID
tk.Label(root, text='Video ID:').place(x=30, y=50)
video_id = tk.StringVar()
video_id.set('')
entry = tk.Entry(root, bg='#ffffff', width=20, textvariable=video_id)
entry.place(x=160, y=50, anchor='nw')  # Position

# Number of comments to scrape
tk.Label(root, text='Comment Count:').place(x=30, y=90)
comment_num = tk.StringVar()
comment_num.set('-1')
entry = tk.Entry(root, bg='#ffffff', width=20, textvariable=comment_num)
entry.place(x=160, y=90, anchor='nw')  # Position
tk.Label(root, text='-1 means scrape all').place(x=350, y=90)

# Sort method
tk.Label(root, text='Sort Method:').place(x=30, y=130)
order_type = ttk.Combobox(root)
order_type['value'] = ('Sort by Date', 'Sort by Popular')
order_type.current(0)
order_type.place(x=160, y=130, anchor='nw')  # Position

# Execute button
fill_button = tk.Button(
    root, bg='white', text='Start', width=10, height=1,
    command=lambda: MyThread(task, video_id, comment_num, order_type, txt_msglist)
)
fill_button.place(x=270, y=580, anchor='nw')  # Position

quit_button = tk.Button(root, text='Quit', width=10, height=1, command=root.quit)
quit_button.place(x=460, y=580, anchor='nw')

# Disclaimer
claim = tk.Label(
    root,
    text='Disclaimer: This software is for educational purposes only. User is responsible for compliance with all applicable laws.',
    font=('Arial', 9), fg='red'
)
claim.place(x=50, y=550)

# Copyright info
copyright = tk.Label(root, text='YouTube Comment Scraper', font=('Arial', 10), fg='grey')
copyright.place(x=320, y=625)

# Message loop
root.mainloop()