"""
YouTube Downloader Tool
Download YouTube videos with quality selection
Bilingual: English and Amharic
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import re
import threading
from datetime import datetime

# Try to import pytubefix
try:
    from pytubefix import YouTube
    from pytubefix.cli import on_progress
    PYTUBE_AVAILABLE = True
except ImportError:
    PYTUBE_AVAILABLE = False

STRINGS = {
    'en': {
        'title': 'YouTube Downloader',
        'enter_url': 'Enter YouTube URL:',
        'fetch_info': 'Fetch Video Info',
        'video_info': 'Video Information:',
        'title_label': 'Title:',
        'author': 'Author:',
        'duration': 'Duration:',
        'views': 'Views:',
        'download_type': 'Download Type:',
        'video': 'Video',
        'audio': 'Audio',
        'quality': 'Select Quality:',
        'download': 'Download',
        'clear': 'Clear',
        'back': 'Back to Home',
        'fetching': 'Fetching video information...',
        'fetch_error': 'Error fetching video. Check URL and internet.',
        'select_quality': 'Please select quality first',
        'downloading': 'Downloading...',
        'download_complete': 'Download complete!',
        'download_error': 'Download failed. Please try again.',
        'no_pytube': 'YouTube downloader not available. Install pytubefix',
        'enter_url': 'Please enter a URL first',
        'ready': 'Ready'
    },
    'am': {
        'title': 'ዩቲዩብ አውራጅ',
        'enter_url': 'የዩቲዩብ አድራሻ ያስገቡ:',
        'fetch_info': 'የቪዲዮ መረጃ አምጣ',
        'video_info': 'የቪዲዮ መረጃ:',
        'title_label': 'ርዕስ:',
        'author': 'አቅራቢ:',
        'duration': 'ቆይታ:',
        'views': 'ተመልካቾች:',
        'download_type': 'የማውረጃ አይነት:',
        'video': 'ቪዲዮ',
        'audio': 'ኦዲዮ',
        'quality': 'ጥራት ይምረጡ:',
        'download': 'አውርድ',
        'clear': 'አጽዳ',
        'back': 'ወደ መነሻ',
        'fetching': 'የቪዲዮ መረጃ በማምጣት ላይ...',
        'fetch_error': 'ቪዲዮ ማምጣት አልተሳካም።',
        'select_quality': 'እባክዎ መጀመሪያ ጥራት ይምረጡ',
        'downloading': 'በማውረድ ላይ...',
        'download_complete': 'ማውረድ ተጠናቋል!',
        'download_error': 'ማውረድ አልተሳካም።',
        'no_pytube': 'ዩቲዩብ አውራጅ አይገኝም።',
        'enter_url': 'እባክዎ መጀመሪያ አድራሻ ያስገቡ',
        'ready': 'ዝግጁ'
    }
}

class YouTubeDownloaderFrame(tk.Frame):
    """YouTube Downloader Frame"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#f0f0f0')
        
        self.yt = None
        self.video_streams = []
        self.audio_streams = []
        self.download_type = 'video'
        self.selected_stream = None
        
        self.create_widgets()
        self.update_language()
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg='#3498db', height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        self.back_btn = tk.Button(header, text='←', font=('Arial', 16),
                                 bg='#3498db', fg='white', relief='flat',
                                 command=self.go_back)
        self.back_btn.pack(side='left', padx=10)
        
        self.title_label = tk.Label(header, text='',
                                   font=('Arial', 14, 'bold'),
                                   bg='#3498db', fg='white')
        self.title_label.pack(side='left', padx=20)
        
        # Main content
        main = tk.Frame(self, bg='#f0f0f0', padx=20, pady=20)
        main.pack(fill='both', expand=True)
        
        # URL input
        url_frame = tk.Frame(main, bg='#f0f0f0')
        url_frame.pack(fill='x', pady=(0, 10))
        
        self.url_label = tk.Label(url_frame, text='', font=('Arial', 12),
                                 bg='#f0f0f0', fg='#333333')
        self.url_label.pack(anchor='w')
        
        input_frame = tk.Frame(main, bg='#f0f0f0')
        input_frame.pack(fill='x', pady=5)
        
        self.url_entry = tk.Entry(input_frame, font=('Arial', 11), width=30)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.fetch_btn = tk.Button(input_frame, text='',
                                   bg='#3498db', fg='white',
                                   font=('Arial', 11),
                                   command=self.fetch_video_info)
        self.fetch_btn.pack(side='right')
        
        # Video info section
        self.info_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                       bg='#f0f0f0', fg='#333333')
        self.info_frame.pack(fill='x', pady=10)
        
        self.info_text = tk.Text(self.info_frame, height=6, font=('Arial', 11),
                                 bg='white', fg='#333333', wrap='word')
        self.info_text.pack(fill='x', padx=5, pady=5)
        
        # Download type
        type_frame = tk.Frame(main, bg='#f0f0f0')
        type_frame.pack(fill='x', pady=10)
        
        self.type_label = tk.Label(type_frame, text='', font=('Arial', 12),
                                  bg='#f0f0f0', fg='#333333')
        self.type_label.pack(side='left')
        
        self.type_var = tk.StringVar(value='video')
        
        self.video_radio = tk.Radiobutton(type_frame, text='',
                                         variable=self.type_var, value='video',
                                         bg='#f0f0f0', fg='#333333',
                                         selectcolor='#f0f0f0',
                                         command=self.on_type_change)
        self.video_radio.pack(side='left', padx=(20, 10))
        
        self.audio_radio = tk.Radiobutton(type_frame, text='',
                                         variable=self.type_var, value='audio',
                                         bg='#f0f0f0', fg='#333333',
                                         selectcolor='#f0f0f0',
                                         command=self.on_type_change)
        self.audio_radio.pack(side='left')
        
        # Quality selection
        quality_frame = tk.Frame(main, bg='#f0f0f0')
        quality_frame.pack(fill='x', pady=10)
        
        self.quality_label = tk.Label(quality_frame, text='', font=('Arial', 12),
                                     bg='#f0f0f0', fg='#333333')
        self.quality_label.pack(side='left')
        
        self.quality_combo = ttk.Combobox(quality_frame, state='readonly',
                                          font=('Arial', 11), width=30)
        self.quality_combo.pack(side='left', padx=(20, 0))
        
        # Download button
        self.download_btn = tk.Button(main, text='',
                                      bg='#27ae60', fg='white',
                                      font=('Arial', 12, 'bold'),
                                      command=self.start_download,
                                      state='disabled')
        self.download_btn.pack(fill='x', pady=10)
        
        # Progress section
        progress_frame = tk.Frame(main, bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=10)
        
        self.progress_label = tk.Label(progress_frame, text='',
                                       font=('Arial', 11),
                                       bg='#f0f0f0', fg='#333333')
        self.progress_label.pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=300,
                                            mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(progress_frame, text='',
                                     font=('Arial', 10),
                                     bg='#f0f0f0', fg='#666666')
        self.status_label.pack(anchor='w')
        
        # Clear button
        self.clear_btn = tk.Button(main, text='',
                                   bg='#95a5a6', fg='white',
                                   font=('Arial', 11),
                                   command=self.clear_all)
        self.clear_btn.pack(fill='x', pady=5)
    
    def get_string(self, key):
        """Get string in current language"""
        return STRINGS[self.controller.current_lang].get(key, STRINGS['en'].get(key, key))
    
    def update_language(self):
        """Update UI language"""
        self.title_label.config(text=self.get_string('title'))
        self.url_label.config(text=self.get_string('enter_url'))
        self.fetch_btn.config(text=self.get_string('fetch_info'))
        self.info_frame.config(text=self.get_string('video_info'))
        self.type_label.config(text=self.get_string('download_type'))
        self.video_radio.config(text=self.get_string('video'))
        self.audio_radio.config(text=self.get_string('audio'))
        self.quality_label.config(text=self.get_string('quality'))
        self.download_btn.config(text=self.get_string('download'))
        self.clear_btn.config(text=self.get_string('clear'))
    
    def update_theme(self, bg_color, fg_color):
        """Update theme colors"""
        self.configure(bg=bg_color)
        for widget in self.winfo_children():
            try:
                if isinstance(widget, (tk.Label, tk.Frame)):
                    widget.configure(bg=bg_color)
                if hasattr(widget, 'fg'):
                    widget.configure(fg=fg_color)
            except:
                pass
    
    def on_show(self):
        """Called when frame is shown"""
        self.update_language()
    
    def go_back(self):
        """Return to home screen"""
        self.controller.show_frame('home')
    
    def on_type_change(self):
        """Handle download type change"""
        self.download_type = self.type_var.get()
        self.update_quality_options()
    
    def fetch_video_info(self):
        """Fetch video information from URL"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Warning", self.get_string('enter_url'))
            return
        
        if not PYTUBE_AVAILABLE:
            messagebox.showerror("Error", self.get_string('no_pytube'))
            return
        
        self.fetch_btn.config(state='disabled')
        self.status_label.config(text=self.get_string('fetching'))
        
        threading.Thread(target=self._fetch_info_thread, args=(url,)).start()
    
    def _fetch_info_thread(self, url):
        """Background thread for fetching video info"""
        try:
            self.yt = YouTube(url, on_progress_callback=self.on_download_progress)
            
            # Update info text
            info = f"{self.get_string('title_label')} {self.yt.title}\n"
            info += f"{self.get_string('author')} {self.yt.author}\n"
            
            minutes = self.yt.length // 60
            seconds = self.yt.length % 60
            info += f"{self.get_string('duration')} {minutes}:{seconds:02d}\n"
            info += f"{self.get_string('views')} {self.yt.views:,}"
            
            self.after(0, lambda: self._update_info_text(info))
            
            # Get streams
            self.video_streams = []
            for stream in self.yt.streams.filter(progressive=True, file_extension='mp4'):
                if stream.resolution:
                    size = stream.filesize / (1024 * 1024) if stream.filesize else 0
                    self.video_streams.append({
                        'stream': stream,
                        'display': f"{stream.resolution} - {size:.1f} MB"
                    })
            
            self.audio_streams = []
            for stream in self.yt.streams.filter(only_audio=True):
                if stream.abr:
                    size = stream.filesize / (1024 * 1024) if stream.filesize else 0
                    self.audio_streams.append({
                        'stream': stream,
                        'display': f"{stream.abr} - {size:.1f} MB"
                    })
            
            self.after(0, self.update_quality_options)
            
        except Exception as e:
            self.after(0, lambda: self._fetch_error(str(e)))
    
    def _update_info_text(self, info):
        """Update info text in UI"""
        self.info_text.delete('1.0', 'end')
        self.info_text.insert('1.0', info)
    
    def update_quality_options(self):
        """Update quality combo box"""
        if self.download_type == 'video':
            options = [s['display'] for s in self.video_streams]
        else:
            options = [s['display'] for s in self.audio_streams]
        
        self.quality_combo['values'] = options
        if options:
            self.quality_combo.set(options[0])
            self.download_btn.config(state='normal')
        else:
            self.download_btn.config(state='disabled')
        
        self.fetch_btn.config(state='normal')
        self.status_label.config(text=self.get_string('ready'))
    
    def _fetch_error(self, error):
        """Handle fetch error"""
        print(f"Fetch error: {error}")
        self.fetch_btn.config(state='normal')
        self.status_label.config(text=self.get_string('fetch_error'))
        messagebox.showerror("Error", self.get_string('fetch_error'))
    
    def on_download_progress(self, stream, chunk, bytes_remaining):
        """Update download progress"""
        total_size = stream.filesize
        if total_size:
            bytes_downloaded = total_size - bytes_remaining
            percentage = (bytes_downloaded / total_size) * 100
            self.after(0, lambda: self._update_progress(percentage))
    
    def _update_progress(self, percentage):
        """Update progress bar"""
        self.progress_bar['value'] = percentage
        self.progress_label.config(
            text=f"{self.get_string('downloading')} {percentage:.1f}%"
        )
    
    def start_download(self):
        """Start video/audio download"""
        if not self.yt:
            messagebox.showwarning("Warning", self.get_string('fetch_info'))
            return
        
        if not self.quality_combo.get():
            messagebox.showwarning("Warning", self.get_string('select_quality'))
            return
        
        # Get selected stream
        selected = self.quality_combo.get()
        
        if self.download_type == 'video':
            streams = self.video_streams
        else:
            streams = self.audio_streams
        
        for i, s in enumerate(streams):
            if s['display'] == selected:
                self.selected_stream = s['stream']
                break
        
        self.download_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_label.config(text=self.get_string('downloading'))
        self.status_label.config(text=self.get_string('downloading'))
        
        threading.Thread(target=self._download_thread).start()
    
    def _download_thread(self):
        """Background download thread"""
        try:
            # Sanitize filename
            safe_title = re.sub(r'[^\w\s-]', '', self.yt.title)
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            
            if self.download_type == 'video':
                filename = f"{safe_title}.mp4"
            else:
                filename = f"{safe_title}.mp3"
            
            download_path = self.controller.get_storage_path('downloads')
            
            self.selected_stream.download(output_path=download_path, filename=filename)
            
            self.after(0, lambda: self._download_complete(filename))
            
        except Exception as e:
            print(f"Download error: {e}")
            self.after(0, lambda: self._download_error(str(e)))
    
    def _download_complete(self, filename):
        """Handle download completion"""
        self.progress_bar['value'] = 100
        self.progress_label.config(text=self.get_string('download_complete'))
        self.status_label.config(text=self.get_string('download_complete'))
        self.download_btn.config(state='normal')
        
        messagebox.showinfo("Success",
                           f"✓ Saved in: eyoTools > Downloads\nFile: {filename}")
    
    def _download_error(self, error):
        """Handle download error"""
        print(f"Download error: {error}")
        self.progress_label.config(text=self.get_string('download_error'))
        self.status_label.config(text=self.get_string('download_error'))
        self.progress_bar['value'] = 0
        self.download_btn.config(state='normal')
        messagebox.showerror("Error", self.get_string('download_error'))
    
    def clear_all(self):
        """Clear all fields"""
        self.url_entry.delete(0, 'end')
        self.info_text.delete('1.0', 'end')
        self.quality_combo.set('')
        self.quality_combo['values'] = []
        self.progress_bar['value'] = 0
        self.progress_label.config(text='')
        self.status_label.config(text='')
        self.download_btn.config(state='disabled')
        self.yt = None
        self.video_streams = []
        self.audio_streams = []