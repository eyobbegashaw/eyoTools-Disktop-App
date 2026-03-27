"""
Steganography Tool
Hide and reveal secret messages in images using Pure Python LSB
Bilingual: English and Amharic
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import threading
import shutil
from PIL import Image, ImageTk

# Constants for LSB encoding
TERMINATOR = "1111111111111110"  # 16-bit terminator sequence

STRINGS = {
    'en': {
        'title': 'Steganography',
        'hide': 'Hide Message',
        'reveal': 'Reveal Message',
        'select_image': 'Select Image:',
        'choose_image': 'Choose Image',
        'preview': 'Preview:',
        'enter_message': 'Enter Secret Message:',
        'message_hint': 'Type your secret message...',
        'hidden_message': 'Hidden Message:',
        'save_stego': 'Save Stego Image',
        'clear': 'Clear',
        'back': 'Back to Home',
        'select_image_first': 'Please select an image first',
        'enter_message_first': 'Please enter a message to hide',
        'processing_hide': 'Hiding message in image...',
        'processing_reveal': 'Revealing hidden message...',
        'hide_complete': 'Message hidden successfully!',
        'reveal_complete': 'Message revealed successfully!',
        'no_message_found': 'No hidden message found in image',
        'error': 'Error processing image',
        'saved': 'Stego image saved successfully!',
        'save_error': 'Error saving image',
        'ready': 'Ready'
    },
    'am': {
        'title': 'ስውር መልእክት',
        'hide': 'መልእክት ደብቅ',
        'reveal': 'መልእክት አውጣ',
        'select_image': 'ምስል ይምረጡ:',
        'choose_image': 'ምስል ምረጥ',
        'preview': 'ቅድመ እይታ:',
        'enter_message': 'ሚስጥራዊ መልእክት ያስገቡ:',
        'message_hint': 'ሚስጥራዊ መልእክትዎን ይተይቡ...',
        'hidden_message': 'የተደበቀ መልእክት:',
        'save_stego': 'ስውር ምስል አስቀምጥ',
        'clear': 'አጽዳ',
        'back': 'ወደ መነሻ',
        'select_image_first': 'እባክዎ መጀመሪያ ምስል ይምረጡ',
        'enter_message_first': 'እባክዎ ለመደበቅ መልእክት ያስገቡ',
        'processing_hide': 'መልእክት በምስል ውስጥ በመደበቅ ላይ...',
        'processing_reveal': 'የተደበቀ መልእክት በማውጣት ላይ...',
        'hide_complete': 'መልእክት በተሳካ ሁኔታ ተደብቋል!',
        'reveal_complete': 'መልእክት በተሳካ ሁኔታ ተገልጧል!',
        'no_message_found': 'በምስል ውስጥ ምንም የተደበቀ መልእክት አልተገኘም',
        'error': 'ምስል በማስኬድ ላይ ስህተት',
        'saved': 'ስውር ምስል በተሳካ ሁኔታ ተቀምጧል!',
        'save_error': 'ምስል በማስቀመጥ ላይ ስህተት',
        'ready': 'ዝግጁ'
    }
}

class SteganographyFrame(tk.Frame):
    """Steganography Frame"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#f0f0f0')
        
        self.mode = 'hide'  # 'hide' or 'reveal'
        self.image_path = None
        self.stego_path = None
        self.revealed_message = ""
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
        
        # Mode selection
        mode_frame = tk.Frame(main, bg='#f0f0f0')
        mode_frame.pack(fill='x', pady=10)
        
        self.mode_var = tk.StringVar(value='hide')
        
        self.hide_radio = tk.Radiobutton(mode_frame, text='',
                                         variable=self.mode_var,
                                         value='hide',
                                         bg='#f0f0f0', fg='#333333',
                                         selectcolor='#f0f0f0',
                                         command=self.on_mode_change)
        self.hide_radio.pack(side='left', padx=(0, 20))
        
        self.reveal_radio = tk.Radiobutton(mode_frame, text='',
                                           variable=self.mode_var,
                                           value='reveal',
                                           bg='#f0f0f0', fg='#333333',
                                           selectcolor='#f0f0f0',
                                           command=self.on_mode_change)
        self.reveal_radio.pack(side='left')
        
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
        
        # Message input (Hide mode)
        self.input_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                         bg='#f0f0f0', fg='#333333')
        
        self.message_text = tk.Text(self.input_frame, height=4,
                                     font=('Arial', 11),
                                     bg='white', fg='#333333',
                                     wrap='word')
        self.message_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.message_text.bind('<KeyRelease>', self.on_text_change)
        
        # Message output (Reveal mode)
        self.output_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                          bg='#f0f0f0', fg='#333333')
        
        self.output_text = tk.Text(self.output_frame, height=4,
                                    font=('Arial', 11),
                                    bg='white', fg='#333333',
                                    wrap='word')
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action button
        self.action_btn = tk.Button(main, text='',
                                     bg='#27ae60', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     command=self.process,
                                     state='disabled')
        self.action_btn.pack(fill='x', pady=10)
        
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
        
        # Save button (for Hide mode)
        self.save_btn = tk.Button(main, text='',
                                  bg='#9b59b6', fg='white',
                                  font=('Arial', 11),
                                  command=self.save_stego_image,
                                  state='disabled')
        self.save_btn.pack(fill='x', pady=5)
        
        # Clear button
        self.clear_btn = tk.Button(main, text='',
                                   bg='#95a5a6', fg='white',
                                   font=('Arial', 11),
                                   command=self.clear_all)
        self.clear_btn.pack(fill='x', pady=5)
        
        # Initially pack input frame
        self.input_frame.pack(fill='both', expand=True, pady=10)
    
    def get_string(self, key):
        """Get string in current language"""
        return STRINGS[self.controller.current_lang].get(key, STRINGS['en'].get(key, key))
    
    def update_language(self):
        """Update UI language"""
        self.title_label.config(text=self.get_string('title'))
        self.hide_radio.config(text=self.get_string('hide'))
        self.reveal_radio.config(text=self.get_string('reveal'))
        self.select_label.config(text=self.get_string('select_image'))
        self.select_btn.config(text=self.get_string('choose_image'))
        self.preview_frame.config(text=self.get_string('preview'))
        self.input_frame.config(text=self.get_string('enter_message'))
        self.output_frame.config(text=self.get_string('hidden_message'))
        self.save_btn.config(text=self.get_string('save_stego'))
        self.clear_btn.config(text=self.get_string('clear'))
        self.status_label.config(text=self.get_string('ready'))
        
        # Set hint text
        self.message_text.delete('1.0', 'end')
        self.message_text.insert('1.0', self.get_string('message_hint'))
        self.message_text.config(fg='#999999')
        
        self.update_action_button()
    
    def update_action_button(self):
        """Update action button text based on mode"""
        if self.mode == 'hide':
            self.action_btn.config(text=self.get_string('hide'))
        else:
            self.action_btn.config(text=self.get_string('reveal'))
    
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
        self.update_mode_display()
        self.update_can_process()
    
    def go_back(self):
        """Return to home screen"""
        self.controller.show_frame('home')
    
    def on_mode_change(self):
        """Handle mode change"""
        self.mode = self.mode_var.get()
        self.update_mode_display()
        self.update_can_process()
        self.update_action_button()
    
    def update_mode_display(self):
        """Update UI based on current mode"""
        if self.mode == 'hide':
            self.input_frame.pack(fill='both', expand=True, pady=10)
            self.output_frame.pack_forget()
            self.save_btn.pack(fill='x', pady=5)
        else:
            self.input_frame.pack_forget()
            self.output_frame.pack(fill='both', expand=True, pady=10)
            self.save_btn.pack_forget()
    
    def on_text_change(self, event):
        """Handle text input changes"""
        self.update_can_process()
    
    def update_can_process(self):
        """Update whether process button should be enabled"""
        if self.image_path:
            if self.mode == 'hide':
                text = self.message_text.get('1.0', 'end-1c').strip()
                has_text = text and text != self.get_string('message_hint')
                self.action_btn.config(state='normal' if has_text else 'disabled')
            else:
                self.action_btn.config(state='normal')
        else:
            self.action_btn.config(state='disabled')
    
    def choose_image(self):
        """Open file chooser for image"""
        filename = filedialog.askopenfilename(
            title=self.get_string('select_image'),
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if filename:
            self.image_path = filename
            self.show_image_preview(filename)
            self.status_label.config(text=self.get_string('ready'))
            self.update_can_process()
    
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
    
    def process(self):
        """Process based on current mode"""
        if not self.image_path:
            messagebox.showwarning("Warning", self.get_string('select_image_first'))
            return
        
        if self.mode == 'hide':
            message = self.message_text.get('1.0', 'end-1c').strip()
            if not message or message == self.get_string('message_hint'):
                messagebox.showwarning("Warning", self.get_string('enter_message_first'))
                return
            
            self.progress_label.config(text=self.get_string('processing_hide'))
            self.status_label.config(text=self.get_string('processing_hide'))
        else:
            self.progress_label.config(text=self.get_string('processing_reveal'))
            self.status_label.config(text=self.get_string('processing_reveal'))
        
        self.action_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        
        threading.Thread(target=self._process_thread).start()
    
    def _text_to_binary(self, text):
        """Convert text to binary string"""
        binary = ''
        for char in text:
            binary += format(ord(char), '08b')
        binary += TERMINATOR
        return binary
    
    def _binary_to_text(self, binary):
        """Convert binary string to text"""
        terminator_pos = binary.find(TERMINATOR)
        if terminator_pos == -1:
            return None
        
        binary = binary[:terminator_pos]
        
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        
        return text
    
    def _encode_lsb(self, img_path, message, output_path):
        """Hide message in image using LSB"""
        img = Image.open(img_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = list(img.getdata())
        width, height = img.size
        
        binary_message = self._text_to_binary(message)
        message_len = len(binary_message)
        
        if message_len > len(pixels) * 3:
            raise Exception("Message too long for this image")
        
        encoded_pixels = []
        message_index = 0
        
        for pixel in pixels:
            r, g, b = pixel
            
            if message_index < message_len:
                r = (r & 0xFE) | int(binary_message[message_index])
                message_index += 1
            
            if message_index < message_len:
                g = (g & 0xFE) | int(binary_message[message_index])
                message_index += 1
            
            if message_index < message_len:
                b = (b & 0xFE) | int(binary_message[message_index])
                message_index += 1
            
            encoded_pixels.append((r, g, b))
        
        encoded_img = Image.new('RGB', (width, height))
        encoded_img.putdata(encoded_pixels)
        encoded_img.save(output_path, 'PNG')
        
        return output_path
    
    def _decode_lsb(self, img_path):
        """Reveal message from image using LSB"""
        img = Image.open(img_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = list(img.getdata())
        
        binary_message = ''
        
        for pixel in pixels:
            r, g, b = pixel
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)
        
        return self._binary_to_text(binary_message)
    
    def _process_thread(self):
        """Background processing thread"""
        try:
            self.after(0, lambda: self._update_progress(30))
            
            if self.mode == 'hide':
                message = self.message_text.get('1.0', 'end-1c').strip()
                temp_path = os.path.join(self.controller.get_storage_path('images'), 'temp_stego.png')
                self._encode_lsb(self.image_path, message, temp_path)
                self.after(0, lambda: self._hide_complete(temp_path))
            else:
                message = self._decode_lsb(self.image_path)
                self.after(0, lambda: self._reveal_complete(message if message else ''))
            
        except Exception as e:
            self.after(0, lambda: self._process_error(str(e)))
    
    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar['value'] = value
    
    def _hide_complete(self, stego_path):
        """Handle hide completion"""
        self.stego_path = stego_path
        self.show_image_preview(stego_path)
        self.progress_bar['value'] = 100
        self.progress_label.config(text=self.get_string('hide_complete'))
        self.status_label.config(text=self.get_string('hide_complete'))
        self.save_btn.config(state='normal')
        self.action_btn.config(state='normal')
        messagebox.showinfo("Success", self.get_string('hide_complete'))
    
    def _reveal_complete(self, message):
        """Handle reveal completion"""
        if message:
            self.revealed_message = message
            self.output_text.delete('1.0', 'end')
            self.output_text.insert('1.0', message)
            self.progress_label.config(text=self.get_string('reveal_complete'))
            self.status_label.config(text=self.get_string('reveal_complete'))
            messagebox.showinfo("Success", self.get_string('reveal_complete'))
        else:
            self.progress_label.config(text=self.get_string('no_message_found'))
            self.status_label.config(text=self.get_string('no_message_found'))
            messagebox.showinfo("Info", self.get_string('no_message_found'))
        
        self.progress_bar['value'] = 100
        self.action_btn.config(state='normal')
    
    def _process_error(self, error):
        """Handle processing error"""
        print(f"Steganography error: {error}")
        self.progress_label.config(text=self.get_string('error'))
        self.status_label.config(text=self.get_string('error'))
        self.action_btn.config(state='normal')
        messagebox.showerror("Error", self.get_string('error'))
    
    def save_stego_image(self):
        """Save stego image"""
        if not self.stego_path:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"stego_{timestamp}.png"
            save_path = os.path.join(self.controller.get_storage_path('images'), filename)
            
            shutil.copy2(self.stego_path, save_path)
            
            messagebox.showinfo("Success",
                               f"✓ Saved in: eyoTools > Images\nFile: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", self.get_string('save_error'))
    
    def clear_all(self):
        """Clear all fields"""
        self.image_path = None
        self.stego_path = None
        self.revealed_message = ""
        self.preview_canvas.delete('all')
        self.message_text.delete('1.0', 'end')
        self.output_text.delete('1.0', 'end')
        self.progress_bar['value'] = 0
        self.progress_label.config(text='')
        self.status_label.config(text='')
        self.save_btn.config(state='disabled')
        self.action_btn.config(state='disabled')
        
        # Reset message hint
        self.message_text.insert('1.0', self.get_string('message_hint'))
        self.message_text.config(fg='#999999')
