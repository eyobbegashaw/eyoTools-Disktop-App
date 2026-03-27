"""
OCR Tool - Image to Text
Extract text from images using EasyOCR
Bilingual: English and Amharic
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import threading
from PIL import Image, ImageTk

# Try to import easyocr
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

STRINGS = {
    'en': {
        'title': 'Image to Text (OCR)',
        'select_image': 'Select Image:',
        'choose_image': 'Choose Image',
        'preview': 'Preview:',
        'select_lang': 'Select Language:',
        'extract': 'Extract Text',
        'extracted_text': 'Extracted Text:',
        'save': 'Save as TXT',
        'copy': 'Copy',
        'clear': 'Clear',
        'back': 'Back to Home',
        'select_image_first': 'Please select an image first',
        'no_easyocr': 'OCR not available. Install easyocr',
        'processing': 'Processing image...',
        'complete': 'Text extraction complete!',
        'error': 'Error extracting text',
        'saved': 'Text saved successfully!',
        'save_error': 'Error saving text',
        'copied': 'Text copied to clipboard!',
        'copy_error': 'Error copying text',
        'ready': 'Ready'
    },
    'am': {
        'title': 'ምስል ወደ ጽሁፍ',
        'select_image': 'ምስል ይምረጡ:',
        'choose_image': 'ምስል ምረጥ',
        'preview': 'ቅድመ እይታ:',
        'select_lang': 'ቋንቋ ይምረጡ:',
        'extract': 'ጽሁፍ አውጣ',
        'extracted_text': 'የተወጣ ጽሁፍ:',
        'save': 'እንደ TXT አስቀምጥ',
        'copy': 'ቅዳ',
        'clear': 'አጽዳ',
        'back': 'ወደ መነሻ',
        'select_image_first': 'እባክዎ መጀመሪያ ምስል ይምረጡ',
        'no_easyocr': 'OCR አይገኝም። easyocr ይጫኑ',
        'processing': 'ምስል በማስኬድ ላይ...',
        'complete': 'ጽሁፍ ማውጣት ተጠናቋል!',
        'error': 'ጽሁፍ በማውጣት ላይ ስህተት',
        'saved': 'ጽሁፍ በተሳካ ሁኔታ ተቀምጧል!',
        'save_error': 'ጽሁፍ በማስቀመጥ ላይ ስህተት',
        'copied': 'ጽሁፍ ወደ ክሊፕቦርድ ተቀድቷል!',
        'copy_error': 'ጽሁፍ በመቅዳት ላይ ስህተት',
        'ready': 'ዝግጁ'
    }
}

class OCRFrame(tk.Frame):
    """OCR Frame for text extraction from images"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#f0f0f0')
        
        self.image_path = None
        self.extracted_text = ""
        self.selected_lang = 'en'
        self._reader = None
        self.preview_photo = None
        
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
        
        # Image selection
        select_frame = tk.Frame(main, bg='#f0f0f0')
        select_frame.pack(fill='x', pady=10)
        
        self.select_label = tk.Label(select_frame, text='',
                                     font=('Arial', 12),
                                     bg='#f0f0f0', fg='#333333')
        self.select_label.pack(side='left')
        
        self.select_btn = tk.Button(select_frame, text='',
                                    bg='#3498db', fg='white',
                                    font=('Arial', 11),
                                    command=self.choose_image)
        self.select_btn.pack(side='right')
        
        # Image preview
        self.preview_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                          bg='#f0f0f0', fg='#333333')
        self.preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='#e0e0e0',
                                        height=150, highlightthickness=0)
        self.preview_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Language selection
        lang_frame = tk.Frame(main, bg='#f0f0f0')
        lang_frame.pack(fill='x', pady=10)
        
        self.lang_label = tk.Label(lang_frame, text='',
                                   font=('Arial', 12),
                                   bg='#f0f0f0', fg='#333333')
        self.lang_label.pack(side='left')
        
        self.lang_var = tk.StringVar(value='English')
        self.lang_combo = ttk.Combobox(lang_frame,
                                       textvariable=self.lang_var,
                                       values=['English', 'አማርኛ'],
                                       state='readonly',
                                       font=('Arial', 11),
                                       width=15)
        self.lang_combo.pack(side='right')
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_select)
        
        # Extract button
        self.extract_btn = tk.Button(main, text='',
                                     bg='#27ae60', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     command=self.extract_text,
                                     state='disabled')
        self.extract_btn.pack(fill='x', pady=10)
        
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
        
        # Extracted text
        self.text_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                       bg='#f0f0f0', fg='#333333')
        self.text_frame.pack(fill='both', expand=True, pady=10)
        
        # Text area with scrollbar
        text_container = tk.Frame(self.text_frame, bg='#f0f0f0')
        text_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.text_area = tk.Text(text_container, height=6,
                                  font=('Arial', 11),
                                  bg='white', fg='#333333',
                                  wrap='word')
        self.text_area.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_container, orient='vertical',
                                  command=self.text_area.yview)
        scrollbar.pack(side='right', fill='y')
        self.text_area.config(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(main, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=10)
        
        self.save_btn = tk.Button(button_frame, text='',
                                  bg='#9b59b6', fg='white',
                                  font=('Arial', 11),
                                  command=self.save_text,
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
    
    def get_string(self, key):
        """Get string in current language"""
        return STRINGS[self.controller.current_lang].get(key, STRINGS['en'].get(key, key))
    
    def update_language(self):
        """Update UI language"""
        self.title_label.config(text=self.get_string('title'))
        self.select_label.config(text=self.get_string('select_image'))
        self.select_btn.config(text=self.get_string('choose_image'))
        self.preview_frame.config(text=self.get_string('preview'))
        self.lang_label.config(text=self.get_string('select_lang'))
        self.extract_btn.config(text=self.get_string('extract'))
        self.text_frame.config(text=self.get_string('extracted_text'))
        self.save_btn.config(text=self.get_string('save'))
        self.copy_btn.config(text=self.get_string('copy'))
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
        # Reset language combo to current app language
        if self.controller.current_lang == 'am':
            self.lang_var.set('አማርኛ')
            self.selected_lang = 'am'
        else:
            self.lang_var.set('English')
            self.selected_lang = 'en'
    
    def go_back(self):
        """Return to home screen"""
        self.controller.show_frame('home')
    
    def choose_image(self):
        """Open file chooser for image"""
        filename = filedialog.askopenfilename(
            title=self.get_string('select_image'),
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        
        if filename:
            self.image_path = filename
            self.show_image_preview(filename)
            self.extract_btn.config(state='normal')
            self.status_label.config(text=self.get_string('ready'))
    
    def show_image_preview(self, path):
        """Show image preview on canvas"""
        try:
            img = Image.open(path)
            img.thumbnail((300, 150), Image.Resampling.LANCZOS)
            
            self.preview_photo = ImageTk.PhotoImage(img)
            
            self.preview_canvas.delete('all')
            self.preview_canvas.create_image(
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2,
                image=self.preview_photo, anchor='center'
            )
        except Exception as e:
            print(f"Error loading preview: {e}")
    
    def on_language_select(self, event):
        """Handle language selection"""
        if self.lang_var.get() == 'አማርኛ':
            self.selected_lang = 'am'
        else:
            self.selected_lang = 'en'
    
    def get_reader(self):
        """Lazy load EasyOCR reader"""
        if self._reader is None and EASYOCR_AVAILABLE:
            try:
                self._reader = easyocr.Reader([self.selected_lang], gpu=False)
            except Exception as e:
                print(f"Error initializing EasyOCR: {e}")
                self._reader = None
        return self._reader
    
    def extract_text(self):
        """Extract text from image"""
        if not self.image_path:
            messagebox.showwarning("Warning", self.get_string('select_image_first'))
            return
        
        if not EASYOCR_AVAILABLE:
            messagebox.showerror("Error", self.get_string('no_easyocr'))
            return
        
        self.extract_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_label.config(text=self.get_string('processing'))
        self.status_label.config(text=self.get_string('processing'))
        
        threading.Thread(target=self._extract_thread).start()
    
    def _extract_thread(self):
        """Background extraction thread"""
        try:
            self.after(0, lambda: self._update_progress(20))
            
            reader = self.get_reader()
            if reader is None:
                raise Exception("Failed to initialize EasyOCR")
            
            self.after(0, lambda: self._update_progress(40))
            
            result = reader.readtext(self.image_path, paragraph=True)
            
            self.after(0, lambda: self._update_progress(80))
            
            text = '\n'.join([item[1] for item in result])
            
            self.after(0, lambda: self._extract_complete(text.strip()))
            
        except Exception as e:
            self.after(0, lambda: self._extract_error(str(e)))
    
    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar['value'] = value
    
    def _extract_complete(self, text):
        """Handle extraction completion"""
        self.extracted_text = text
        self.text_area.delete('1.0', 'end')
        self.text_area.insert('1.0', text)
        self.progress_bar['value'] = 100
        self.progress_label.config(text=self.get_string('complete'))
        self.status_label.config(text=self.get_string('complete'))
        self.save_btn.config(state='normal')
        self.copy_btn.config(state='normal')
        self.extract_btn.config(state='normal')
        messagebox.showinfo("Success", self.get_string('complete'))
    
    def _extract_error(self, error):
        """Handle extraction error"""
        self.progress_label.config(text=self.get_string('error'))
        self.status_label.config(text=self.get_string('error'))
        self.extract_btn.config(state='normal')
        messagebox.showerror("Error", self.get_string('error'))
    
    def save_text(self):
        """Save extracted text"""
        if not self.extracted_text:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ocr_{timestamp}.txt"
            save_path = os.path.join(self.controller.get_storage_path('downloads'), filename)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.extracted_text)
            
            messagebox.showinfo("Success",
                               f"✓ Saved in: eyoTools > Downloads\nFile: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", self.get_string('save_error'))
    
    def copy_text(self):
        """Copy text to clipboard"""
        if self.extracted_text:
            self.clipboard_clear()
            self.clipboard_append(self.extracted_text)
            messagebox.showinfo("Success", self.get_string('copied'))
    
    def clear_all(self):
        """Clear all fields"""
        self.image_path = None
        self.extracted_text = ""
        self.preview_canvas.delete('all')
        self.text_area.delete('1.0', 'end')
        self.progress_bar['value'] = 0
        self.progress_label.config(text='')
        self.status_label.config(text='')
        self.save_btn.config(state='disabled')
        self.copy_btn.config(state='disabled')
        self.extract_btn.config(state='disabled')
