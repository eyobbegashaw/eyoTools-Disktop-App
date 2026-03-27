"""
Background Remover Tool
Remove image backgrounds using PIL-based approach
Bilingual: English and Amharic
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import threading
from PIL import Image, ImageTk, ImageFilter
import shutil

STRINGS = {
    'en': {
        'title': 'Background Remover',
        'select_image': 'Select Image:',
        'choose_image': 'Choose Image',
        'preview': 'Preview:',
        'remove_bg': 'Remove Background',
        'result': 'Result:',
        'save': 'Save Image',
        'clear': 'Clear',
        'back': 'Back to Home',
        'select_image_first': 'Please select an image first',
        'processing': 'Processing image...',
        'complete': 'Background removed successfully!',
        'error': 'Error processing image',
        'saved': 'Image saved successfully!',
        'save_error': 'Error saving image',
        'ready': 'Ready'
    },
    'am': {
        'title': 'ዳራ አስወጋጅ',
        'select_image': 'ምስል ይምረጡ:',
        'choose_image': 'ምስል ምረጥ',
        'preview': 'ቅድመ እይታ:',
        'remove_bg': 'ዳራ አስወግድ',
        'result': 'ውጤት:',
        'save': 'ምስል አስቀምጥ',
        'clear': 'አጽዳ',
        'back': 'ወደ መነሻ',
        'select_image_first': 'እባክዎ መጀመሪያ ምስል ይምረጡ',
        'processing': 'ምስል በማስኬድ ላይ...',
        'complete': 'ዳራ በተሳካ ሁኔታ ተወግዷል!',
        'error': 'ምስል በማስኬድ ላይ ስህተት',
        'saved': 'ምስል በተሳካ ሁኔታ ተቀምጧል!',
        'save_error': 'ምስል በማስቀመጥ ላይ ስህተት',
        'ready': 'ዝግጁ'
    }
}

class BackgroundRemoverFrame(tk.Frame):
    """Background Remover Frame"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#f0f0f0')
        
        self.image_path = None
        self.result_path = None
        self.preview_photo = None
        self.result_photo = None
        
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
        
        # Preview section
        self.preview_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                          bg='#f0f0f0', fg='#333333')
        self.preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='#e0e0e0',
                                        height=150, highlightthickness=0)
        self.preview_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Process button
        self.process_btn = tk.Button(main, text='',
                                     bg='#27ae60', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     command=self.process_image,
                                     state='disabled')
        self.process_btn.pack(fill='x', pady=10)
        
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
        
        # Result section
        self.result_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                         bg='#f0f0f0', fg='#333333')
        self.result_frame.pack(fill='both', expand=True, pady=10)
        
        self.result_canvas = tk.Canvas(self.result_frame, bg='#e0e0e0',
                                       height=150, highlightthickness=0)
        self.result_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Save button
        self.save_btn = tk.Button(main, text='',
                                  bg='#9b59b6', fg='white',
                                  font=('Arial', 11),
                                  command=self.save_image,
                                  state='disabled')
        self.save_btn.pack(fill='x', pady=5)
        
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
        self.process_btn.config(text=self.get_string('remove_bg'))
        self.result_frame.config(text=self.get_string('result'))
        self.save_btn.config(text=self.get_string('save'))
        self.clear_btn.config(text=self.get_string('clear'))
    
    def update_theme(self, bg_color, fg_color):
        """Update theme colors"""
        self.configure(bg=bg_color)
        for widget in self.winfo_children():
            try:
                if isinstance(widget, (tk.Label, tk.Frame)):
                    widget.configure(bg=bg_color)
            except:
                pass
    
    def on_show(self):
        """Called when frame is shown"""
        self.update_language()
    
    def go_back(self):
        """Return to home screen"""
        self.controller.show_frame('home')
    
    def choose_image(self):
        """Open file chooser for image"""
        filename = filedialog.askopenfilename(
            title=self.get_string('select_image'),
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if filename:
            self.image_path = filename
            self.show_image_preview(filename, self.preview_canvas, 'preview')
            self.status_label.config(text=self.get_string('ready'))
            self.process_btn.config(state='normal')
    
    def show_image_preview(self, path, canvas, photo_type='preview'):
        """Show image preview on canvas"""
        try:
            img = Image.open(path)
            img.thumbnail((300, 150), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            
            # Store reference to prevent garbage collection
            if photo_type == 'preview':
                self.preview_photo = photo
            else:
                self.result_photo = photo
            
            canvas.delete('all')
            canvas.create_image(canvas.winfo_width()//2,
                               canvas.winfo_height()//2,
                               image=photo, anchor='center')
        except Exception as e:
            print(f"Error loading preview: {e}")
    
    def process_image(self):
        """Remove background from image"""
        if not self.image_path:
            messagebox.showwarning("Warning", self.get_string('select_image_first'))
            return
        
        self.process_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_label.config(text=self.get_string('processing'))
        self.status_label.config(text=self.get_string('processing'))
        
        threading.Thread(target=self._process_thread).start()
    
    def _remove_background_pil(self, image):
        """Remove background using PIL"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        datas = image.getdata()
        width, height = image.size
        
        # Sample corners for background color
        corners = [
            image.getpixel((0, 0)),
            image.getpixel((width-1, 0)),
            image.getpixel((0, height-1)),
            image.getpixel((width-1, height-1))
        ]
        
        bg_r = sum(c[0] for c in corners) // 4
        bg_g = sum(c[1] for c in corners) // 4
        bg_b = sum(c[2] for c in corners) // 4
        
        threshold = 60
        new_data = []
        
        for item in datas:
            r, g, b, a = item
            
            if (abs(r - bg_r) < threshold and 
                abs(g - bg_g) < threshold and 
                abs(b - bg_b) < threshold):
                new_data.append((r, g, b, 0))
            else:
                new_data.append((r, g, b, a))
        
        image.putdata(new_data)
        image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        return image
    
    def _process_thread(self):
        """Background processing thread"""
        try:
            self.after(0, lambda: self._update_progress(20))
            
            image = Image.open(self.image_path)
            
            self.after(0, lambda: self._update_progress(40))
            
            result_image = self._remove_background_pil(image)
            
            self.after(0, lambda: self._update_progress(70))
            
            result_image = result_image.filter(ImageFilter.SMOOTH_MORE)
            
            # Save temporary file
            temp_dir = self.controller.get_storage_path('images')
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, 'temp_output.png')
            result_image.save(temp_path, 'PNG')
            
            self.after(0, lambda: self._process_complete(temp_path))
            
        except Exception as e:
            print(f"Processing error: {e}")
            self.after(0, lambda: self._process_error(str(e)))
    
    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar['value'] = value
    
    def _process_complete(self, result_path):
        """Handle processing completion"""
        self.result_path = result_path
        self.show_image_preview(result_path, self.result_canvas, 'result')
        self.progress_bar['value'] = 100
        self.progress_label.config(text=self.get_string('complete'))
        self.status_label.config(text=self.get_string('complete'))
        self.save_btn.config(state='normal')
        self.process_btn.config(state='normal')
        messagebox.showinfo("Success", self.get_string('complete'))
    
    def _process_error(self, error):
        """Handle processing error"""
        self.progress_label.config(text=self.get_string('error'))
        self.status_label.config(text=self.get_string('error'))
        self.process_btn.config(state='normal')
        messagebox.showerror("Error", self.get_string('error'))
    
    def save_image(self):
        """Save processed image"""
        if not self.result_path:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"output_{timestamp}.png"
            save_path = os.path.join(self.controller.get_storage_path('images'), filename)
            
            shutil.copy2(self.result_path, save_path)
            
            messagebox.showinfo("Success",
                               f"✓ Saved in: eyoTools > Images\nFile: {filename}")
            
        except Exception as e:
            print(f"Save error: {e}")
            messagebox.showerror("Error", self.get_string('save_error'))
    
    def clear_all(self):
        """Clear all fields"""
        self.image_path = None
        self.result_path = None
        self.preview_canvas.delete('all')
        self.result_canvas.delete('all')
        self.progress_bar['value'] = 0
        self.progress_label.config(text='')
        self.status_label.config(text='')
        self.save_btn.config(state='disabled')
        self.process_btn.config(state='disabled')
