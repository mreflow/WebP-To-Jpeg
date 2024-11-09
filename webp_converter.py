import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinter.font import Font
import os
from PIL import Image
from datetime import datetime
import threading
from tkinterdnd2 import TkinterDnD, DND_FILES
import traceback
import json

print("Starting application...")

class WebpConverterApp:
    def __init__(self, root):
        print("Initializing app...")
        self.root = root
        self.root.title("WebP Converter")
        self.root.configure(bg='#f0f0f0')  # Light gray background
        
        # Set minimum window size
        self.root.minsize(500, 400)
        
        # Configure fonts
        self.title_font = Font(family="Segoe UI", size=14, weight="bold")
        self.normal_font = Font(family="Segoe UI", size=10)
        self.button_font = Font(family="Segoe UI", size=9)
        
        # Load saved output directory or use default
        self.config_file = os.path.join(os.path.expanduser("~"), ".webp_converter_config.json")
        self.load_config()
        
        # Create main frame with padding
        self.main_frame = tk.Frame(root, bg='#f0f0f0')
        self.main_frame.pack(padx=20, pady=20, expand=True, fill="both")
        
        # Add title
        self.title_label = tk.Label(
            self.main_frame,
            text="WebP to JPEG Converter",
            font=self.title_font,
            bg='#f0f0f0',
            fg='#333333'
        )
        self.title_label.pack(pady=(0, 20))
        
        # Create output directory selection frame
        self.dir_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        self.dir_frame.pack(fill="x", pady=(0, 15))
        
        self.dir_label = tk.Label(
            self.dir_frame,
            text="Output folder:",
            font=self.normal_font,
            bg='#f0f0f0',
            fg='#333333'
        )
        self.dir_label.pack(side="left")
        
        style = ttk.Style()
        style.configure('Modern.TButton', font=self.button_font)
        
        self.dir_button = ttk.Button(
            self.dir_frame,
            text="Change Folder",
            command=self.select_output_dir,
            style='Modern.TButton'
        )
        self.dir_button.pack(side="right")
        
        # Create and configure the main drop zone
        self.drop_frame = tk.Frame(
            self.main_frame,
            bg='#ffffff',
            highlightthickness=2,
            highlightbackground='#dddddd'
        )
        self.drop_frame.pack(expand=True, fill="both", pady=(0, 15))
        
        self.drop_zone = tk.Label(
            self.drop_frame,
            font=self.normal_font,
            bg='#ffffff',
            fg='#666666',
            cursor="hand2"
        )
        self.drop_zone.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Bind drag and drop events
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Add hover effect for drop zone
        self.drop_frame.bind('<Enter>', self.on_enter)
        self.drop_frame.bind('<Leave>', self.on_leave)
        
        # Update the display
        self.update_display()
    
    def on_enter(self, event):
        self.drop_frame.configure(highlightbackground='#4a90e2')
        
    def on_leave(self, event):
        self.drop_frame.configure(highlightbackground='#dddddd')
    
    def update_display(self):
        self.drop_zone.config(
            text=f"Drag and drop WebP files here\n\n"
                 f"Files will be saved to:\n{self.output_dir}"
        )
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.output_dir = config.get('output_dir')
            else:
                self.output_dir = os.path.join(os.path.expanduser("~"), "Pictures", "WebpConverter")
        except Exception as e:
            print(f"Error loading config: {e}")
            self.output_dir = os.path.join(os.path.expanduser("~"), "Pictures", "WebpConverter")
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'output_dir': self.output_dir}, f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def select_output_dir(self):
        new_dir = filedialog.askdirectory(initialdir=self.output_dir)
        if new_dir:
            self.output_dir = new_dir
            self.save_config()
            self.update_display()
    
    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        threading.Thread(target=self.process_files, args=(files,), daemon=True).start()
        
    def process_files(self, files):
        successful = 0
        failed = 0
        
        for file_path in files:
            try:
                if not file_path.lower().endswith('.webp'):
                    continue
                    
                # Open and convert the image
                with Image.open(file_path) as img:
                    # Create output filename with timestamp to avoid conflicts
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_filename = f"{base_name}_{timestamp}.jpg"
                    output_path = os.path.join(self.output_dir, output_filename)
                    
                    # Convert and save with high quality
                    img.convert("RGB").save(output_path, "JPEG", quality=95)
                    
                    # Delete the original WebP file
                    os.remove(file_path)
                    successful += 1
                    
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                failed += 1
        
        # Show completion message
        message = f"Conversion complete!\nSuccessful: {successful}\nFailed: {failed}"
        self.root.after(0, lambda: messagebox.showinfo("Conversion Status", message))

if __name__ == "__main__":
    try:
        root = TkinterDnD.Tk()
        app = WebpConverterApp(root)
        root.mainloop()
    except Exception as e:
        print("An error occurred:", str(e))
        print("\nFull traceback:")
        traceback.print_exc()
        input("\nPress Enter to exit...")