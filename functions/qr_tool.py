"""
QR Code Generator Tool
Generate QR codes from text or URLs
Bilingual: English and Amharic
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import threading
import shutil
from PIL import Image, ImageTk

# Try to import qrcode
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

STRINGS = {
    'en': {
        'title': 'QR Code Generator',
        'enter_text': 'Enter Text or URL:',
        'hint': 'Enter text to encode...',
        'generate': 'Generate QR Code',
        'preview': 'Preview:',
        'save': 'Save QR Code',
        'copy': 'Copy Text',
        'clear': 'Clear',
        'back': 'Back to Home',
        'enter_text_first': 'Please enter text first',
        'no_qrcode': 'QR generator not available. Install qrcode',
        'generating': 'Generating QR code...',
        'generated': 'QR code generated successfully!',
        'error': 'Error generating QR code',
        'saved': 'QR code saved successfully!',
        'save_error': 'Error saving QR code',
        'copied': 'Text copied to clipboard!',
        'copy_error': 'Error copying text',
        'ready': 'Ready'
    },
    'am': {
        'title': 'QR ኮድ አመንጪ',
        'enter_text': 'ጽሁፍ ወይም አድራሻ ያስገቡ:',
        'hint': 'ለማስመስጠር ጽሁፍ ያስገቡ...',
        'generate': 'QR ኮድ አመንጭ',
        'preview': 'ቅድመ እይታ:',
        'save': 'QR ኮድ አስቀምጥ',
        'copy': 'ጽሁፍ ቅዳ',
        'clear': 'አጽዳ',
        'back': 'ወደ መነሻ',
        'enter_text_first': 'እባክዎ መጀመሪያ ጽሁፍ ያስገቡ',
        'no_qrcode': 'QR አመንጪ አይገኝም። qrcode ይጫኑ',
        'generating': 'QR ኮድ በማመንጨት ላይ...',
        'generated': 'QR ኮድ በተሳካ ሁኔታ ተመንጭቷል!',
        'error': 'QR ኮድ በማመንጨት ላይ ስህተት',
        'saved': 'QR ኮድ በተሳካ ሁኔታ ተቀምጧል!',
        'save_error': 'QR ኮድ በማስቀመጥ ላይ ስህተት',
        'copied': 'ጽሁፍ ወደ ክሊፕቦርድ ተቀድቷል!',
        'copy_error': 'ጽሁፍ በመቅዳት ላይ ስህተት',
        'ready': 'ዝግጁ'
    }
}

class QRGeneratorFrame(tk.Frame):
    """QR Code Generator Frame"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#f0f0f0')
        
        self.qr_path = None
        self.qr_photo = None
        
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
        
        # Input section
        input_frame = tk.Frame(main, bg='#f0f0f0')
        input_frame.pack(fill='x', pady=10)
        
        self.input_label = tk.Label(input_frame, text='',
                                     font=('Arial', 12),
                                     bg='#f0f0f0', fg='#333333')
        self.input_label.pack(anchor='w')
        
        self.text_entry = tk.Text(input_frame, height=3,
                                   font=('Arial', 11),
                                   bg='white', fg='#333333',
                                   wrap='word')
        self.text_entry.pack(fill='x', pady=(5, 10))
        self.text_entry.bind('<KeyRelease>', self.on_text_change)
        
        self.generate_btn = tk.Button(input_frame, text='',
                                      bg='#27ae60', fg='white',
                                      font=('Arial', 12, 'bold'),
                                      command=self.generate_qr,
                                      state='disabled')
        self.generate_btn.pack(fill='x')
        
        # QR Code preview
        self.preview_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                          bg='#f0f0f0', fg='#333333')
        self.preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='white',
                                        height=200, highlightthickness=1,
                                        highlightcolor='#cccccc')
        self.preview_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = tk.Frame(main, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=10)
        
        self.save_btn = tk.Button(button_frame, text='',
                                  bg='#9b59b6', fg='white',
                                  font=('Arial', 11),
                                  command=self.save_qr,
                                  state='disabled')
        self.save_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        self.copy_btn = tk.Button(button_frame, text='',
                                  bg='#3498db', fg='white',
                                  font=('Arial', 11),
                                  command=self.copy_text,
                                  state='disabled')
        self.copy_btn.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Clear button
        self.clear_btn = tk.Button(main, text='',
                                   bg='#95a5a6', fg='white',
                                   font=('Arial', 11),
                                   command=self.clear_all)
        self.clear_btn.pack(fill='x', pady=5)
        
        # Status
        self.status_label = tk.Label(main, text='',
                                     font=('Arial', 10),
                                     bg='#f0f0f0', fg='#666666')
        self.status_label.pack(anchor='w', pady=5)
    
    def get_string(self, key):
        """Get string in current language"""
        return STRINGS[self.controller.current_lang].get(key, STRINGS['en'].get(key, key))
    
    def update_language(self):
        """Update UI language"""
        self.title_label.config(text=self.get_string('title'))
        self.input_label.config(text=self.get_string('enter_text'))
        self.generate_btn.config(text=self.get_string('generate'))
        self.preview_frame.config(text=self.get_string('preview'))
        self.save_btn.config(text=self.get_string('save'))
        self.copy_btn.config(text=self.get_string('copy'))
        self.clear_btn.config(text=self.get_string('clear'))
        self.status_label.config(text=self.get_string('ready'))
    
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
    
    def on_text_change(self, event):
        """Handle text input changes"""
        text = self.text_entry.get('1.0', 'end-1c').strip()
        if text:
            self.generate_btn.config(state='normal')
            self.copy_btn.config(state='normal')
        else:
            self.generate_btn.config(state='disabled')
            self.copy_btn.config(state='disabled')
    
    def generate_qr(self):
        """Generate QR code from input text"""
        text = self.text_entry.get('1.0', 'end-1c').strip()
        
        if not text:
            messagebox.showwarning("Warning", self.get_string('enter_text_first'))
            return
        
        if not QRCODE_AVAILABLE:
            messagebox.showerror("Error", self.get_string('no_qrcode'))
            return
        
        self.generate_btn.config(state='disabled')
        self.status_label.config(text=self.get_string('generating'))
        
        threading.Thread(target=self._generate_thread, args=(text,)).start()
    
    def _generate_thread(self, text):
        """Background QR generation thread"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr.add_data(text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            temp_path = os.path.join(self.controller.get_storage_path('images'), 'temp_qr.png')
            img.save(temp_path)
            
            self.after(0, lambda: self._generate_complete(temp_path))
            
        except Exception as e:
            self.after(0, lambda: self._generate_error(str(e)))
    
    def _generate_complete(self, qr_path):
        """Handle generation completion"""
        self.qr_path = qr_path
        self.show_qr_preview(qr_path)
        self.status_label.config(text=self.get_string('generated'))
        self.save_btn.config(state='normal')
        self.generate_btn.config(state='normal')
        messagebox.showinfo("Success", self.get_string('generated'))
    
    def show_qr_preview(self, path):
        """Show QR code preview on canvas"""
        try:
            img = Image.open(path)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            self.qr_photo = ImageTk.PhotoImage(img)
            
            self.preview_canvas.delete('all')
            self.preview_canvas.create_image(
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2,
                image=self.qr_photo, anchor='center'
            )
        except Exception as e:
            print(f"Error loading QR preview: {e}")
    
    def _generate_error(self, error):
        """Handle generation error"""
        self.status_label.config(text=self.get_string('error'))
        self.generate_btn.config(state='normal')
        messagebox.showerror("Error", self.get_string('error'))
    
    def save_qr(self):
        """Save QR code"""
        if not self.qr_path:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"qrcode_{timestamp}.png"
            save_path = os.path.join(self.controller.get_storage_path('images'), filename)
            
            shutil.copy2(self.qr_path, save_path)
            
            messagebox.showinfo("Success",
                               f"✓ Saved in: eyoTools > Images\nFile: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", self.get_string('save_error'))
    
    def copy_text(self):
        """Copy input text to clipboard"""
        text = self.text_entry.get('1.0', 'end-1c').strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("Success", self.get_string('copied'))
    
    def clear_all(self):
        """Clear all fields"""
        self.text_entry.delete('1.0', 'end')
        self.qr_path = None
        self.preview_canvas.delete('all')
        self.status_label.config(text=self.get_string('ready'))
        self.generate_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.copy_btn.config(state='disabled')
