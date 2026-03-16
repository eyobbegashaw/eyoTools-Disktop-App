"""
eyoTools Desktop Application
Central hub for all utility tools with Dark Mode and Multi-language support
Bilingual: English and Amharic
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import ctypes
from ctypes import byref
from datetime import datetime
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageOps
import shutil
import math
import tkinter.font as tkfont

# Add functions directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))

# Try to import tool modules
try:
    from functions.youtube_dl import YouTubeDownloaderFrame
    from functions.bg_remover import BackgroundRemoverFrame
    from functions.pdf_tools import PDFExtractorFrame, PDFToAudioFrame
    from functions.ocr_tool import OCRFrame
    from functions.qr_tool import QRGeneratorFrame
    from functions.steganography import SteganographyFrame
    TOOLS_AVAILABLE = True
    print("✅ All tool modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: Some tools could not be imported: {e}")
    TOOLS_AVAILABLE = False

# ==================== FONT REGISTRATION SYSTEM ====================
def register_font(font_path):
    """
    Register a .ttf font file temporarily with the system
    Returns True if successful, False otherwise
    """
    if not os.path.exists(font_path):
        print(f"Error: Font not found at {font_path}")
        return False

    # For Windows systems
    if sys.platform.startswith('win'):
        try:
            FR_PRIVATE = 0x10
            path_buf = ctypes.create_unicode_buffer(font_path)
            add_font_resource_ex = ctypes.windll.gdi32.AddFontResourceExW
            res = add_font_resource_ex(ctypes.byref(path_buf), FR_PRIVATE, 0)
            if res != 0:
                print(f"✅ Font registered: {font_path}")
                return True
            else:
                print(f"⚠️ Font registration failed: {font_path}")
                return False
        except Exception as e:
            print(f"Error registering font on Windows: {e}")
            return False
    
    # For other systems (Linux/Mac) - just check if font exists
    return True

# Get the base directory (works for both script and compiled exe)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Font paths to try (in order of preference)
FONT_PATHS = [
    # os.path.join(BASE_DIR, 'fonts', 'AbyssinicaSIL-Regular.ttf'),
    os.path.join(BASE_DIR, 'fonts', 'abyssinica.ttf'),
    os.path.join(BASE_DIR, 'fonts', 'Abyssinica.ttf'),
    # os.path.join(BASE_DIR, 'AbyssinicaSIL-Regular.ttf'),
]

# Try to register the font
FONT_REGISTERED = False
FONT_FAMILY = 'Arial'  # Default fallback

for font_path in FONT_PATHS:
    if os.path.exists(font_path):
        if register_font(font_path):
            FONT_REGISTERED = True
            # The actual font family name inside the font file
            # For Abyssinica SIL, it's typically "Abyssinica SIL"
            FONT_FAMILY = "abyssinica SIL"
            break
        else:
            print(f"⚠️ Font found but registration failed: {font_path}")

# Check if font is available in tkinter
if FONT_REGISTERED:
    try:
        available_fonts = tkfont.families()
        if FONT_FAMILY not in available_fonts:
            print(f"⚠️ Font '{FONT_FAMILY}' not found in tkinter families")
            # Try alternative Amharic fonts
            amharic_fonts = ['abyssinica']
            for font in amharic_fonts:
                if font in available_fonts:
                    FONT_FAMILY = font
                    print(f"✅ Using alternative Amharic font: {font}")
                    break
            else:
                FONT_REGISTERED = False
                FONT_FAMILY = 'Arial'
    except Exception as e:
        print(f"Error checking fonts: {e}")
        FONT_REGISTERED = False

# if not FONT_REGISTERED:
#     print("⚠️ Using default font (Arial). Amharic text may not display correctly.")
#     print("Please place AbyssinicaSIL-Regular.ttf in the 'fonts' folder.")

# Language strings with proper Unicode support
STRINGS = {
    'en': {
        'app_name': 'eyoTools',
        'home': 'Home',
        'tools': 'Tools',
        'settings': 'Settings',
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode',
        'language': 'Language',
        'english': 'English',
        'amharic': 'አማርኛ',
        'about': 'About',
        'contact': 'Contact',
        'developer': 'Developer Info',
        'version': 'Version 1.0.0',
        'youtube': 'YouTube Downloader',
        'bg_remover': 'Background Remover',
        'pdf_extract': 'PDF to Text',
        'pdf_audio': 'PDF to Audio',
        'ocr': 'Image to Text (OCR)',
        'qr': 'QR Code Generator',
        'steganography': 'Steganography',
        'loading': 'Loading...',
        'welcome': 'Welcome to eyoTools',
        'welcome_sub': 'Your Ultimate Computer Science Toolkit',
        'cs_quote': '"Code is like humor. When you have to explain it, it\'s bad." – Cory House',
        'select_tool': 'Select a tool to get started',
        'ok': 'OK',
        'cancel': 'Cancel',
        'message': 'Message',
        'exit': 'Exit',
        'cs_students': 'For CS Students, By a CS Student',
        'close': 'Close'
    },
    'am': {
        'app_name': 'ኢዮ መሳሪያዎች',
        'home': 'መነሻ',
        'tools': 'መሳሪያዎች',
        'settings': 'ማስተካከያ',
        'dark_mode': 'ጨለማ ሁነታ',
        'light_mode': 'ብርሃን ሁነታ',
        'language': 'ቋንቋ',
        'english': 'እንግሊዝኛ',
        'amharic': 'አማርኛ',
        'about': 'ስለ እኛ',
        'contact': 'መገናኛ',
        'developer': 'ገንቢ መረጃ',
        'version': 'እትም 1.0.0',
        'youtube': 'ዩቲዩብ አውራጅ',
        'bg_remover': 'ዳራ አስወጋጅ',
        'pdf_extract': 'PDF ወደ ጽሁፍ',
        'pdf_audio': 'PDF ወደ ድምጽ',
        'ocr': 'ምስል ወደ ጽሁፍ',
        'qr': 'QR ኮድ አመንጪ',
        'steganography': 'ስውር መልእክት',
        'loading': 'በመጫን ላይ...',
        'welcome': 'እንኳን ወደ ኢዮ መሳሪያዎች በደህና መጡ',
        'welcome_sub': 'የእርስዎ የኮምፒውተር ሳይንስ መሳሪያዎች ስብስብ',
        'cs_quote': '"ኮድ እንደ ቀልድ ነው። ማስረዳት ሲያስፈልገው ጥሩ አይደለም።"',
        'select_tool': 'ለመጀመር መሳሪያ ይምረጡ',
        'ok': 'እሺ',
        'cancel': 'ሰርዝ',
        'message': 'መልእክት',
        'exit': 'ውጣ',
        'cs_students': 'ለኮምፒውተር ሳይንስ ተማሪዎች፣ በኮምፒውተር ሳይንስ ተማሪ',
        'close': 'ዝጋ'
    }
}

# Font helper function
def get_font(family=None, size=10, weight='normal'):
    """Get font tuple with proper fallback"""
    if family is None:
        family = FONT_FAMILY if FONT_REGISTERED else 'Arial'
    return (family, size, weight)


class SplashScreen(tk.Toplevel):
    """Enhanced splash screen with CS theme and splash.png"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("")
        self.geometry("500x600")
        self.configure(bg='#1a1a2e')
        self.overrideredirect(True)
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f'500x600+{x}+{y}')
        
        self.splash_image = None
        self.create_widgets()
        self.after(100, self.animate)
    
    def create_widgets(self):
        # Canvas for background
        self.canvas = tk.Canvas(self, bg='#1a1a2e', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Try to load splash.png from assets folder
        splash_path = os.path.join(BASE_DIR, 'assets', 'splash.png')
        splash_loaded = False
        
        if os.path.exists(splash_path):
            try:
                # Load and process splash image
                pil_image = Image.open(splash_path)
                pil_image = pil_image.resize((400, 300), Image.Resampling.LANCZOS)
                
                # Add rounded corners
                mask = Image.new('L', pil_image.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([(0, 0), pil_image.size], radius=30, fill=255)
                
                # Apply mask
                result = Image.new('RGBA', pil_image.size)
                result.paste(pil_image, mask=mask)
                
                self.splash_image = ImageTk.PhotoImage(result)
                
                # Display splash image
                self.canvas.create_image(250, 250, image=self.splash_image, anchor='center')
                splash_loaded = True
                print("✅ Splash image loaded successfully")
            except Exception as e:
                print(f"Error loading splash image: {e}")
        
        if not splash_loaded:
            # Draw decorative code background as fallback
            self.draw_code_background()
            
            # Create CS-themed logo
            logo_canvas = tk.Canvas(self.canvas, width=200, height=200,
                                    bg='#1a1a2e', highlightthickness=0)
            logo_canvas_window = self.canvas.create_window(250, 200, window=logo_canvas)
            
            # Draw CS logo
            logo_canvas.create_oval(50, 50, 150, 150, outline='#4ecdc4',
                                     width=3, fill='')
            logo_canvas.create_text(100, 100, text="{CS}", fill='#4ecdc4',
                                    font=get_font(size=24, weight='bold'))
            
            # Draw code symbols around
            for i, symbol in enumerate(['<', '>', '{', '}', '(', ')', '[', ']']):
                angle = i * 45 * 3.14159 / 180
                x = 100 + 80 * math.cos(angle)
                y = 100 + 80 * math.sin(angle)
                logo_canvas.create_text(x, y, text=symbol, fill='#ff6b6b',
                                        font=get_font(size=16, weight='bold'))
        
        # App name
        self.canvas.create_text(250, 380, text="eyoTools",
                               font=get_font(size=32, weight='bold'),
                               fill='#4ecdc4')
        
        self.canvas.create_text(250, 420, text="For Computer Science Students",
                               font=get_font(size=14),
                               fill='#bdc3c7')
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("CS.Horizontal.TProgressbar",
                        background='#4ecdc4',
                        troughcolor='#2c3e50',
                        bordercolor='#1a1a2e',
                        lightcolor='#4ecdc4',
                        darkcolor='#4ecdc4')
        
        self.progress = ttk.Progressbar(self.canvas, length=300, 
                                        mode='determinate',
                                        style="CS.Horizontal.TProgressbar")
        self.progress_window = self.canvas.create_window(250, 480, window=self.progress)
        
        # Loading label
        self.loading_label = self.canvas.create_text(250, 520, 
                                                     text="Initializing CS Tools...",
                                                     font=get_font(size=11),
                                                     fill='#95a5a6')
        
        # Binary animation
        self.binary_text = self.canvas.create_text(250, 560, 
                                                   text="01001111 01101110 01100101",
                                                   font=("Courier", 10),
                                                   fill='#2c3e50')
    
    def draw_code_background(self):
        """Draw code-like patterns in background"""
        for i in range(0, 600, 30):
            opacity = 50
            self.canvas.create_line(20, i, 480, i, fill=f'#4ecdc4',
                                   width=1, dash=(5, 3))
            
            if i % 60 == 0:
                code = f"function_{i//60}()"
                self.canvas.create_text(50, i+15, text=code,
                                       fill=f'#ff6b6b',
                                       font=("Courier", 8),
                                       anchor='w')
    
    def animate(self):
        """Animate progress bar"""
        self.progress['value'] += 2
        if self.progress['value'] < 100:
            # Update loading text
            texts = ["Loading CS modules...", 
                    "Compiling algorithms...",
                    "Initializing data structures...",
                    "Connecting to code repository...",
                    "Almost there..."]
            idx = int(self.progress['value'] / 20)
            if idx < len(texts):
                self.canvas.itemconfig(self.loading_label, text=texts[idx])
            
            # Update binary text
            binary = ["01001111 01101110 01100101",  # One
                     "01010100 01110111 01101111",  # Two
                     "01010100 01101000 01110010",  # Three
                     "01000110 01101111 01110101",  # Four
                     "01000110 01101001 01110110"]   # Five
            bin_idx = int(self.progress['value'] / 20) % len(binary)
            self.canvas.itemconfig(self.binary_text, text=binary[bin_idx])
            
            self.after(50, self.animate)
        else:
            self.after(500, self.destroy)

class NavigationMenu(tk.Frame):
    """Slide-out navigation menu with CS theme and close button"""
    def __init__(self, parent, app):
        # CRITICAL: parent MUST be the root window (app), not app.container
        # This ensures the menu appears OVERLAY on top of everything
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.is_visible = False
        
        # Menu styling
        self.configure(bg='#1a1a2e', width=300)
        
        # IMPORTANT: Start hidden (off-screen to the left)
        # Using place() with x=-300 puts it completely outside the visible area
        self.place(x=-300, y=0, relheight=1)
        
        self.create_widgets()
        self.after(10, self.hide)
        
        
    def create_widgets(self):
        # Header with close button
        header = tk.Frame(self, bg='#16213e', height=120)
        header.pack(fill='x', pady=(0, 20))
        header.pack_propagate(False)
        
        # Close button (X) - RED
        # በ create_widgets ውስጥ ያለውን የ close_btn ኮድ በዚህ ተካው
        close_btn = tk.Button(header, text='✕', font=('Arial', 14, 'bold'),
                            bg='#e74c3c', fg='white', relief='flat',
                            command=self.hide, # ተጫን ሲል እንዲደበቅ
                            bd=0, cursor="hand2",
                            activebackground='#c0392b')
        close_btn.place(x=250, y=10, width=40, height=40) # ቦታውና መጠኑ ተለቅ ብሏል
                
        # Logo
        logo_canvas = tk.Canvas(header, width=60, height=60,
                                bg='#16213e', highlightthickness=0)
        logo_canvas.place(x=20, y=20)
        logo_canvas.create_oval(10, 10, 50, 50, outline='#4ecdc4', width=2)
        logo_canvas.create_text(30, 30, text="CS", fill='#4ecdc4', 
                                font=get_font(size=12, weight='bold'))
        
        self.app_name_label = tk.Label(header, text=self.app.get_string('app_name'),
                                      font=get_font(size=18, weight='bold'),
                                      fg='#4ecdc4', bg='#16213e')
        self.app_name_label.place(x=90, y=25)
        
        self.version_label = tk.Label(header, text=self.app.get_string('version'),
                                     font=get_font(size=9),
                                     fg='#bdc3c7', bg='#16213e')
        self.version_label.place(x=90, y=55)
        
        tk.Label(header, text="CS Student Edition",
                font=get_font(size=9, weight='italic'),
                fg='#ff6b6b', bg='#16213e').place(x=90, y=75)
        
        # Tools section
        self.tools_label = tk.Label(self, text=f"⚡ {self.app.get_string('tools')}",
                                   font=get_font(size=13, weight='bold'),
                                   fg='#4ecdc4', bg='#1a1a2e')
        self.tools_label.pack(pady=(0, 10), padx=20, anchor='w')
        
        # Scrollable tools area
        canvas_container = tk.Frame(self, bg='#1a1a2e')
        canvas_container.pack(fill='both', expand=True, padx=15)
        
        self.tools_canvas = tk.Canvas(canvas_container, bg='#1a1a2e', 
                                      highlightthickness=0, height=300)
        scrollbar = ttk.Scrollbar(canvas_container, orient='vertical', 
                                  command=self.tools_canvas.yview)
        self.tools_scrollable_frame = tk.Frame(self.tools_canvas, bg='#1a1a2e')
        
        self.tools_scrollable_frame.bind(
            '<Configure>',
            lambda e: self.tools_canvas.configure(scrollregion=self.tools_canvas.bbox('all'))
        )
        
        self.tools_canvas.create_window((0, 0), window=self.tools_scrollable_frame, anchor='nw')
        self.tools_canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_mousewheel(event):
            self.tools_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.tools_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.tools_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.create_tools_list()
        self.create_settings_and_info()
    
    def create_tools_list(self):
        """Create tools menu items with icons"""
        for widget in self.tools_scrollable_frame.winfo_children():
            widget.destroy()
        
        tools = [
            ('youtube', 'youtube_dl', '🎥'),
            ('bg_remover', 'bg_remover', '🖼️'),
            ('pdf_extract', 'pdf_extract', '📄'),
            ('pdf_audio', 'pdf_audio', '🔊'),
            ('ocr', 'ocr', '📝'),
            ('qr', 'qr', '📱'),
            ('steganography', 'steganography', '🔐')
        ]
        
        self.tool_buttons = []
        for tool_id, screen_name, icon in tools:
            btn_frame = tk.Frame(self.tools_scrollable_frame, bg='#16213e')
            btn_frame.pack(fill='x', pady=2)
            
            tk.Label(btn_frame, text=icon,
                    font=get_font(size=12),
                    fg='#4ecdc4', bg='#16213e').pack(side='left', padx=5)
            
            btn = tk.Button(btn_frame,
                           text=self.app.get_string(tool_id),
                           command=lambda s=screen_name: self.open_tool(s),
                           bg='#16213e', fg='white',
                           font=get_font(size=11),
                           relief='flat',
                           anchor='w',
                           cursor="hand2")
            btn.pack(side='left', fill='x', expand=True)
            self.tool_buttons.append(btn)
    
    def create_settings_and_info(self):
        """Create settings and info sections"""
        # Settings section
        self.settings_label = tk.Label(self, text=f"⚙️ {self.app.get_string('settings')}",
                                      font=get_font(size=13, weight='bold'),
                                      fg='#4ecdc4', bg='#1a1a2e')
        self.settings_label.pack(pady=(20, 10), padx=20, anchor='w')
        
        settings_frame = tk.Frame(self, bg='#1a1a2e')
        settings_frame.pack(fill='x', padx=20)
        
        # Dark mode toggle
        dark_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        dark_frame.pack(fill='x', pady=5)
        
        tk.Label(dark_frame, text="🌙",
                font=get_font(size=12),
                fg='#f1c40f', bg='#1a1a2e').pack(side='left', padx=(0, 10))
        
        self.dark_mode_text = tk.Label(dark_frame, text=self.app.get_string('dark_mode'),
                                      font=get_font(size=11),
                                      fg='white', bg='#1a1a2e')
        self.dark_mode_text.pack(side='left')
        
        self.dark_mode_var = tk.BooleanVar(value=False)
        dark_toggle = tk.Checkbutton(dark_frame, variable=self.dark_mode_var,
                                     command=self.app.toggle_dark_mode,
                                     bg='#1a1a2e', fg='#4ecdc4',
                                     selectcolor='#1a1a2e',
                                     activebackground='#1a1a2e',
                                     cursor="hand2")
        dark_toggle.pack(side='right')
        
        # Language selection
        lang_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        lang_frame.pack(fill='x', pady=5)
        
        tk.Label(lang_frame, text="🌐",
                font=get_font(size=12),
                fg='#4ecdc4', bg='#1a1a2e').pack(side='left', padx=(0, 10))
        
        self.language_text = tk.Label(lang_frame, text=self.app.get_string('language'),
                                     font=get_font(size=11),
                                     fg='white', bg='#1a1a2e')
        self.language_text.pack(side='left')
        
        self.lang_var = tk.StringVar(value='English')
        self.lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                  values=['English', 'አማርኛ'],
                                  state='readonly', width=10,
                                  font=get_font(size=10))
        self.lang_combo.pack(side='right')
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Info buttons
        info_frame = tk.Frame(self, bg='#1a1a2e')
        info_frame.pack(fill='x', side='bottom', pady=20, padx=15)
        
        self.about_btn = tk.Button(info_frame, text='ℹ️ ' + self.app.get_string('about'),
                                  command=self.show_about,
                                  bg='#16213e', fg='white',
                                  font=get_font(size=10),
                                  relief='flat',
                                  anchor='w',
                                  padx=10,
                                  cursor="hand2")
        self.about_btn.pack(fill='x', pady=2)
        
        self.contact_btn = tk.Button(info_frame, text='📧 ' + self.app.get_string('contact'),
                                    command=self.show_contact,
                                    bg='#16213e', fg='white',
                                    font=get_font(size=10),
                                    relief='flat',
                                    anchor='w',
                                    padx=10,
                                    cursor="hand2")
        self.contact_btn.pack(fill='x', pady=2)
        
        self.developer_btn = tk.Button(info_frame, text='👨‍💻 ' + self.app.get_string('developer'),
                                      command=self.show_developer,
                                      bg='#16213e', fg='white',
                                      font=get_font(size=10),
                                      relief='flat',
                                      anchor='w',
                                      padx=10,
                                      cursor="hand2")
        self.developer_btn.pack(fill='x', pady=2)
    
    def open_tool(self, screen_name):
        """Open selected tool"""
        self.app.show_frame(screen_name)
        self.hide()
    
    def on_language_change(self, event):
        """Handle language change"""
        if self.lang_var.get() == 'አማርኛ':
            self.app.current_lang = 'am'
        else:
            self.app.current_lang = 'en'
        self.app.update_ui_language()
        self.update_language()
    
    def update_language(self):
        """Update menu language"""
        self.app_name_label.config(text=self.app.get_string('app_name'))
        self.version_label.config(text=self.app.get_string('version'))
        self.tools_label.config(text=f"⚡ {self.app.get_string('tools')}")
        self.settings_label.config(text=f"⚙️ {self.app.get_string('settings')}")
        self.dark_mode_text.config(text=self.app.get_string('dark_mode'))
        self.language_text.config(text=self.app.get_string('language'))
        self.about_btn.config(text='ℹ️ ' + self.app.get_string('about'))
        self.contact_btn.config(text='📧 ' + self.app.get_string('contact'))
        self.developer_btn.config(text='👨‍💻 ' + self.app.get_string('developer'))
        
        tools = ['youtube', 'bg_remover', 'pdf_extract', 'pdf_audio', 'ocr', 'qr', 'steganography']
        for i, tool_id in enumerate(tools):
            if i < len(self.tool_buttons):
                self.tool_buttons[i].config(text=self.app.get_string(tool_id))
        
        if self.app.current_lang == 'am':
            self.lang_var.set('አማርኛ')
        else:
            self.lang_var.set('English')
    
    def show_about(self):
        messagebox.showinfo(self.app.get_string('about'),
                           "eyoTools - CS Student Edition\n\n"
                           "A collection of useful utilities for\n"
                           "Computer Science students.\n\n"
                           "Version 1.0.0\n"
                           "© 2025 (2018) eyoTools")
    
    def show_contact(self):
        messagebox.showinfo(self.app.get_string('contact'),
                           "📧 https://eyobbegashaw.vercel.app/\n"
                           "💻 GitHub: @eyobbegashaw")
    
    def show_developer(self):
        messagebox.showinfo(self.app.get_string('developer'),
                           "👨‍💻 Developed by: Dn Eyob Begashaw\n"
                           "🎓 Computer Science Student\n"
                           "📍 Ethiopia\n\n"
                           "Special thanks to all CS students!")
    
    def show(self):
        self.is_visible = True
        self.lift() # ይህ መስመር ሳይድባሩን ከገጹ በላይ ያወጣዋል
        self.animate_menu(0)

    def hide(self):
        self.is_visible = False
        self.animate_menu(-450)
        
    def toggle(self):
        """Toggle menu visibility"""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def animate_menu(self, target, step=25):
        """Animate menu sliding"""
        current_x = self.winfo_x()
        if current_x != target:
            if current_x < target:
                new_x = min(current_x + step, target)
            else:
                new_x = max(current_x - step, target)
            self.place(x=new_x)
            self.after(10, lambda: self.animate_menu(target, step))
 
class HomeScreen(tk.Frame):
    """Home screen with tools grid and CS students theme"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#f0f0f0')
        
        self.cs_image = None
        self.create_widgets()
    
    def get_string(self, key):
        """Get string in current language"""
        return STRINGS[self.controller.current_lang].get(key, STRINGS['en'].get(key, key))
    
    def create_widgets(self):
        # Header with gradient effect
        header = tk.Frame(self, bg='#3498db', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Create gradient effect
        header_canvas = tk.Canvas(header, width=500, height=80,
                                  highlightthickness=0)
        header_canvas.pack(fill='both', expand=True)
        
        # Draw gradient
        for i in range(80):
            color = f'#{52+i:02x}{152+i:02x}{219-i:02x}'
            header_canvas.create_line(0, i, 500, i, fill=color, width=1)
        
        # Menu button (3 horizontal lines)
        menu_btn = tk.Button(header_canvas, text='☰',
                            font=get_font(size=24),
                            bg='#3498db', fg='white',
                            relief='flat',
                            command=self.controller.toggle_menu,  # This calls the app's toggle_menu method
                            bd=0,
                            activebackground='#2980b9',
                            activeforeground='white')
        menu_btn_window = header_canvas.create_window(40, 40, window=menu_btn)
        
        # Title
        self.title_label = tk.Label(header_canvas,
                               text=self.get_string('app_name'),
                               font=get_font(size=22, weight='bold'),
                               bg='#3498db', fg='white')
        header_canvas.create_window(250, 40, window=self.title_label)
        
        # Main content with scroll
        main_container = tk.Frame(self, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(main_container, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel to scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # CS Students Welcome Section
        self.create_welcome_section()
        
        # Tools Section Title
        self.create_tools_title()
        
        # Tools Grid
        self.create_tools_grid()
    
    def create_welcome_section(self):
        """Create welcome section with CS image"""
        welcome_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        welcome_frame.pack(fill='x', padx=20, pady=20)
        
        # Try to load csstudents.png from assets folder
        cs_image_path = os.path.join(BASE_DIR, 'assets', 'csstudents.jpg')
        
        if os.path.exists(cs_image_path):
            try:
                # Load and process the image
                pil_img = Image.open(cs_image_path)
                pil_img = pil_img.resize((400, 200), Image.Resampling.LANCZOS)
                
                # Add rounded corners
                mask = Image.new('L', pil_img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([(0, 0), pil_img.size], radius=20, fill=255)
                
                # Apply mask
                result = Image.new('RGBA', pil_img.size)
                result.paste(pil_img, mask=mask)
                
                self.cs_image = ImageTk.PhotoImage(result)
                
                img_label = tk.Label(welcome_frame, image=self.cs_image,
                                     bg='#f0f0f0')
                img_label.pack()
                print("✅ CS students image loaded successfully")
            except Exception as e:
                print(f"Error loading CS students image: {e}")
                self.create_cs_placeholder(welcome_frame)
        else:
            print("⚠️ CS students image not found, using placeholder")
            self.create_cs_placeholder(welcome_frame)
        
        # Welcome text with CS quote
        quote_frame = tk.Frame(welcome_frame, bg='#f0f0f0')
        quote_frame.pack(fill='x', pady=(20, 10))
        
        self.welcome_label = tk.Label(quote_frame,
                text=self.get_string('welcome'),
                font=get_font(size=18, weight='bold'),
                fg='#2c3e50', bg='#f0f0f0')
        self.welcome_label.pack()
        
        self.welcome_sub_label = tk.Label(quote_frame,
                text=self.get_string('welcome_sub'),
                font=get_font(size=14, weight='italic'),
                fg='#3498db', bg='#f0f0f0')
        self.welcome_sub_label.pack(pady=5)
        
        # CS quote in a styled frame
        quote_bubble = tk.Frame(welcome_frame, bg='#ecf0f1',
                                relief='solid', bd=1,
                                padx=20, pady=10)
        quote_bubble.pack(fill='x', pady=10)
        
        self.quote_label = tk.Label(quote_bubble,
                text=self.get_string('cs_quote'),
                font=get_font(size=11, weight='italic'),
                fg='#7f8c8d', bg='#ecf0f1',
                wraplength=400)
        self.quote_label.pack()
        
        # CS Students badge
        badge_frame = tk.Frame(welcome_frame, bg='#f0f0f0')
        badge_frame.pack(pady=5)
        
        tk.Label(badge_frame,
                text="👨‍🎓 👩‍🎓",
                font=get_font(size=20),
                bg='#f0f0f0').pack()
        
        self.cs_badge_label = tk.Label(badge_frame,
                text=self.get_string('cs_students'),
                font=get_font(size=10, weight='bold'),
                fg='#95a5a6', bg='#f0f0f0')
        self.cs_badge_label.pack()
    
    def create_cs_placeholder(self, parent):
        """Create a styled placeholder with CS theme"""
        canvas = tk.Canvas(parent, width=400, height=200,
                          bg='#1a1a2e', highlightthickness=0)
        canvas.pack()
        
        # Draw rounded rectangle background
        self.create_rounded_rect(canvas, 10, 10, 390, 190, radius=20,
                                 fill='#16213e', outline='#4ecdc4', width=3)
        
        # Draw code symbols
        canvas.create_text(200, 60, text="{ CS }", 
                          fill='#4ecdc4', font=get_font(size=24, weight='bold'))
        
        canvas.create_text(200, 110, text="while(alive):\n    code.eat().sleep()",
                          fill='#ff6b6b', font=("Courier", 12),
                          justify='center')
        
        canvas.create_text(200, 160, text="# For CS Students",
                          fill='#95a5a6', font=get_font(size=10, weight='italic'))
    
    def create_rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        """Helper to create rounded rectangle"""
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def create_tools_title(self):
        """Create tools section title"""
        tools_title = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        tools_title.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(tools_title,
                text="⚡ Available Tools",
                font=get_font(size=16, weight='bold'),
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w')
        
        self.select_tool_label = tk.Label(tools_title,
                text=self.get_string('select_tool'),
                font=get_font(size=11),
                fg='#7f8c8d', bg='#f0f0f0')
        self.select_tool_label.pack(anchor='w')
    
    def create_tools_grid(self):
        """Create grid of tool cards"""
        tools = [
            ('youtube', 'youtube_dl', '🎥 YouTube Downloader'),
            ('bg_remover', 'bg_remover', '🖼️ Background Remover'),
            ('pdf_extract', 'pdf_extract', '📄 PDF to Text'),
            ('pdf_audio', 'pdf_audio', '🔊 PDF to Audio'),
            ('ocr', 'ocr', '📝 Image to Text'),
            ('qr', 'qr', '📱 QR Generator'),
            ('steganography', 'steganography', '🔐 Steganography')
        ]
        
        # Create tools grid frame
        grid_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        grid_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create 2-column grid
        row = 0
        col = 0
        for tool_id, screen_name, display_text in tools:
            # Create styled tool card
            card = tk.Frame(grid_frame, bg='white', relief='raised', bd=2)
            card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Add icon
            icon_label = tk.Label(card, text=display_text.split()[0],
                                 font=get_font(size=24),
                                 bg='white', fg='#3498db')
            icon_label.pack(pady=(10, 5))
            
            # Add text
            text_label = tk.Label(card, text=display_text.split(' ', 1)[1],
                                  font=get_font(size=11, weight='bold'),
                                  bg='white', fg='#2c3e50')
            text_label.pack(pady=(0, 10))
            
            # Add hover effect
            def on_enter(e, c=card):
                c.configure(bg='#f8f9fa')
                for child in c.winfo_children():
                    child.configure(bg='#f8f9fa')
            
            def on_leave(e, c=card):
                c.configure(bg='white')
                for child in c.winfo_children():
                    child.configure(bg='white')
            
            card.bind('<Enter>', on_enter)
            card.bind('<Leave>', on_leave)
            card.bind('<Button-1>', lambda e, s=screen_name: self.controller.show_frame(s))
            
            for child in card.winfo_children():
                child.bind('<Enter>', on_enter)
                child.bind('<Leave>', on_leave)
                child.bind('<Button-1>', lambda e, s=screen_name: self.controller.show_frame(s))
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(2):
            grid_frame.columnconfigure(i, weight=1)
    
    def update_language(self):
        """Update UI language"""
        self.title_label.config(text=self.get_string('app_name'))
        self.welcome_label.config(text=self.get_string('welcome'))
        self.welcome_sub_label.config(text=self.get_string('welcome_sub'))
        self.quote_label.config(text=self.get_string('cs_quote'))
        self.cs_badge_label.config(text=self.get_string('cs_students'))
        self.select_tool_label.config(text=self.get_string('select_tool'))
    
    def update_theme(self, bg_color, fg_color):
        """Update theme colors"""
        self.configure(bg=bg_color)
        for widget in self.winfo_children():
            try:
                if isinstance(widget, (tk.Label, tk.Frame, tk.Canvas)):
                    widget.configure(bg=bg_color)
                if hasattr(widget, 'fg'):
                    widget.configure(fg=fg_color)
            except:
                pass


class eyoToolsApp(tk.Tk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        self.title("eyoTools")

        self.geometry("600x800")
        self.resizable(True, True) # መጠኑ እንዲቀየር ከፈለግህ
         
        icon_path = os.path.join(BASE_DIR, 'assets', 'logo.ico')
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f'500x700+{x}+{y}')
        
        # Initialize properties
        self.dark_mode = False
        self.current_lang = 'en'
        self.frames = {}
        
        # Show splash screen
        self.splash = SplashScreen(self)
        
        
        self.menu = NavigationMenu(self, self)
        # Create main container
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Create navigation menu (hidden initially)
       
        
        # Schedule initialization after splash
        self.after(1000, self.initialize_app)
    
    def get_string(self, key):
        """Get string in current language"""
        return STRINGS[self.current_lang].get(key, STRINGS['en'].get(key, key))
    
    def initialize_app(self):
        """Initialize the application after splash screen"""
        # Create screens
        self.create_frames()
        
        # Show home screen
        self.show_frame('home')
        
        # Configure exit handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_frames(self):
        """Create all application frames"""
        # Home frame
        self.frames['home'] = HomeScreen(self.container, self)
        
        # Tool frames
        if TOOLS_AVAILABLE:
            try:
                self.frames['youtube_dl'] = YouTubeDownloaderFrame(self.container, self)
                self.frames['bg_remover'] = BackgroundRemoverFrame(self.container, self)
                self.frames['pdf_extract'] = PDFExtractorFrame(self.container, self)
                self.frames['pdf_audio'] = PDFToAudioFrame(self.container, self)
                self.frames['ocr'] = OCRFrame(self.container, self)
                self.frames['qr'] = QRGeneratorFrame(self.container, self)
                self.frames['steganography'] = SteganographyFrame(self.container, self)
                print("✅ All tool frames created successfully")
            except Exception as e:
                print(f"Error loading tools: {e}")
        
        # Grid all frames
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky='nsew')
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
    
    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()
            
            # Call on_show method if exists
            if hasattr(frame, 'on_show'):
                frame.on_show()
    
    def toggle_dark_mode(self):
        """Toggle dark mode"""
        self.dark_mode = self.menu.dark_mode_var.get()
        self.update_ui_theme()
    
    def update_ui_theme(self):
        """Update UI theme for all screens"""
        bg_color = '#1a1a2e' if self.dark_mode else '#f0f0f0'
        fg_color = 'white' if self.dark_mode else '#333333'
        
        for frame in self.frames.values():
            if hasattr(frame, 'update_theme'):
                frame.update_theme(bg_color, fg_color)
    
    def update_ui_language(self):
        """Update language for all screens"""
        for frame in self.frames.values():
            if hasattr(frame, 'update_language'):
                try:
                    frame.update_language()
                except Exception as e:
                    print(f"Error updating language for {frame}: {e}")
        
        # Update menu language
        if hasattr(self, 'menu'):
            self.menu.update_language()
    
    def get_storage_path(self, folder):
        """Get storage path for files"""
        base_path = os.path.join(os.path.expanduser('~'), 'eyoTools')
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        return path
    
    def toggle_menu(self):
        """Toggle navigation menu"""
        if hasattr(self, 'menu'):
            self.menu.toggle()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel(self.get_string('exit'), "Do you want to exit?"):
            self.destroy()


if __name__ == '__main__':
    app = eyoToolsApp()
    app.mainloop()