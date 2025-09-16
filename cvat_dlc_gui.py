#!/usr/bin/env python3
"""
CVAT to DeepLabCut Conversion GUI
A user-friendly graphical interface for converting CVAT annotations to DeepLabCut format
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from pathlib import Path
import queue
import subprocess

# Import our pipeline (assuming it's in the same directory)
try:
    from cvat_to_deeplabcut_pipeline import CVATToDeepLabCutPipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False


class CVATDLCGui:
    def __init__(self, root):
        self.root = root
        self.root.title("CVAT to DeepLabCut Converter")
        self.root.geometry("800x700")
        
        # Variables
        self.xml_file = tk.StringVar()
        self.video_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.project_name = tk.StringVar(value="BeePoseEstimation")
        self.scorer_name = tk.StringVar(value="manual")
        self.frame_selection = tk.StringVar(value="full")
        self.start_frame = tk.IntVar(value=0)
        self.end_frame = tk.IntVar(value=0)
        
        # Queue for thread communication
        self.log_queue = queue.Queue()
        
        # Setup GUI
        self.setup_gui()
        
        # Start checking log queue
        self.root.after(100, self.check_log_queue)
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="CVAT to DeepLabCut Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # XML file
        ttk.Label(file_frame, text="CVAT XML File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.xml_file, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_xml_file).grid(row=0, column=2, padx=(5, 0))
        
        # Video file
        ttk.Label(file_frame, text="Video File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.video_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_video_file).grid(row=1, column=2, padx=(5, 0))
        
        # Output directory
        ttk.Label(file_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_output_dir).grid(row=2, column=2, padx=(5, 0))
        
        # Project settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Project Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Project name
        ttk.Label(settings_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.project_name, width=30).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Scorer name
        ttk.Label(settings_frame, text="Scorer Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.scorer_name, width=30).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # Frame selection section
        frame_frame = ttk.LabelFrame(main_frame, text="Frame Selection", padding="10")
        frame_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Frame selection radio buttons
        ttk.Radiobutton(frame_frame, text="Use All Frames", variable=self.frame_selection, 
                       value="full", command=self.on_frame_selection_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(frame_frame, text="Use Frame Range", variable=self.frame_selection, 
                       value="range", command=self.on_frame_selection_change).grid(row=1, column=0, sticky=tk.W)
        
        # Range inputs
        self.range_frame = ttk.Frame(frame_frame)
        self.range_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))
        
        ttk.Label(self.range_frame, text="Start Frame:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.start_entry = ttk.Entry(self.range_frame, textvariable=self.start_frame, width=10, state='disabled')
        self.start_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(self.range_frame, text="End Frame:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.end_entry = ttk.Entry(self.range_frame, textvariable=self.end_frame, width=10, state='disabled')
        self.end_entry.grid(row=0, column=3, padx=(5, 0))
        
        # Convert button
        self.convert_button = ttk.Button(main_frame, text="🚀 Start Conversion", 
                                        command=self.start_conversion, style='Accent.TButton')
        self.convert_button.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Conversion Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
    def browse_xml_file(self):
        filename = filedialog.askopenfilename(
            title="Select CVAT XML file",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.xml_file.set(filename)
            
    def browse_video_file(self):
        filename = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if filename:
            self.video_file.set(filename)
            
    def browse_output_dir(self):
        dirname = filedialog.askdirectory(title="Select output directory")
        if dirname:
            self.output_dir.set(dirname)
            
    def on_frame_selection_change(self):
        if self.frame_selection.get() == "range":
            self.start_entry.config(state='normal')
            self.end_entry.config(state='normal')
        else:
            self.start_entry.config(state='disabled')
            self.end_entry.config(state='disabled')
            
    def log_message(self, message):
        """Add message to log queue"""
        self.log_queue.put(message)
        
    def check_log_queue(self):
        """Check for messages in log queue and display them"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state='normal')
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_log_queue)
            
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.xml_file.get():
            messagebox.showerror("Error", "Please select a CVAT XML file")
            return False
            
        if not self.video_file.get():
            messagebox.showerror("Error", "Please select a video file")
            return False
            
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory")
            return False
            
        if not os.path.exists(self.xml_file.get()):
            messagebox.showerror("Error", "CVAT XML file does not exist")
            return False
            
        if not os.path.exists(self.video_file.get()):
            messagebox.showerror("Error", "Video file does not exist")
            return False
            
        if self.frame_selection.get() == "range":
            start = self.start_frame.get()
            end = self.end_frame.get()
            if start < 0 or end < start:
                messagebox.showerror("Error", "Invalid frame range")
                return False
                
        return True
        
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if not self.validate_inputs():
            return
            
        if not PIPELINE_AVAILABLE:
            messagebox.showerror("Error", "Pipeline module not available. Please ensure cvat_to_deeplabcut_pipeline.py is in the same directory.")
            return
            
        # Disable convert button and show progress
        self.convert_button.config(state='disabled')
        self.progress.start()
        self.status_var.set("Converting...")
        
        # Clear log
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # Start conversion in separate thread
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()
        
    def run_conversion(self):
        """Run the conversion process"""
        try:
            # Create pipeline
            pipeline = CVATToDeepLabCutPipeline()
            
            # Redirect print statements to our log
            import io
            import contextlib
            
            @contextlib.contextmanager
            def capture_output():
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                try:
                    sys.stdout = stdout_capture
                    sys.stderr = stderr_capture
                    yield stdout_capture, stderr_capture
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
            
            # Parse XML
            self.log_message("🚀 Starting CVAT to DeepLabCut conversion...")
            
            with capture_output() as (stdout_capture, stderr_capture):
                success = pipeline.parse_cvat_xml(self.xml_file.get())
            self.log_message(stdout_capture.getvalue().strip())
            
            if not success:
                self.log_message("❌ XML parsing failed")
                self.conversion_completed(False)
                return
                
            # Get video info
            with capture_output() as (stdout_capture, stderr_capture):
                success = pipeline.get_video_info(self.video_file.get())
            self.log_message(stdout_capture.getvalue().strip())
            
            if not success:
                self.log_message("❌ Failed to get video information")
                self.conversion_completed(False)
                return
                
            # Set frame selection
            if self.frame_selection.get() == "range":
                pipeline.frame_selection = "range"
                pipeline.frame_range = (self.start_frame.get(), self.end_frame.get())
            else:
                pipeline.frame_selection = "full"
                pipeline.frame_range = (0, pipeline.video_info['total_frames'] - 1)
                
            self.log_message(f"📋 Frame selection: {pipeline.frame_selection}")
            if pipeline.frame_selection == "range":
                self.log_message(f"   Range: {pipeline.frame_range[0]}-{pipeline.frame_range[1]}")
            
            # Create output directory
            os.makedirs(self.output_dir.get(), exist_ok=True)
            
            # Extract frames
            with capture_output() as (stdout_capture, stderr_capture):
                success = pipeline.extract_frames(self.video_file.get(), self.output_dir.get())
            self.log_message(stdout_capture.getvalue().strip())
            
            if not success:
                self.log_message("❌ Frame extraction failed")
                self.conversion_completed(False)
                return
                
            # Create CSV
            with capture_output() as (stdout_capture, stderr_capture):
                success = pipeline.create_deeplabcut_csv(self.output_dir.get(), 
                                                       self.scorer_name.get(), 
                                                       self.project_name.get())
            self.log_message(stdout_capture.getvalue().strip())
            
            if not success:
                self.log_message("❌ CSV creation failed")
                self.conversion_completed(False)
                return
                
            # Create config
            with capture_output() as (stdout_capture, stderr_capture):
                success = pipeline.create_deeplabcut_config(self.output_dir.get(), 
                                                          self.project_name.get(), 
                                                          self.scorer_name.get())
            self.log_message(stdout_capture.getvalue().strip())
            
            if not success:
                self.log_message("❌ Config creation failed")
                self.conversion_completed(False)
                return
                
            # Copy video
            with capture_output() as (stdout_capture, stderr_capture):
                success = pipeline.copy_video_to_project(self.video_file.get(), self.output_dir.get())
            self.log_message(stdout_capture.getvalue().strip())
            
            if not success:
                self.log_message("❌ Video copy failed")
                self.conversion_completed(False)
                return
                
            # Generate H5 file using the pipeline's method
            with capture_output() as (stdout_capture, stderr_capture):
                success = pipeline.generate_h5_file(self.output_dir.get(), self.scorer_name.get())
            output = stdout_capture.getvalue().strip()
            if output:
                self.log_message(output)
                
            # Create summary
            with capture_output() as (stdout_capture, stderr_capture):
                pipeline.create_dataset_summary(self.output_dir.get(), 
                                               self.project_name.get(), 
                                               self.scorer_name.get())
            self.log_message(stdout_capture.getvalue().strip())
            
            self.log_message("\n🎉 Conversion completed successfully!")
            self.log_message(f"📁 Output directory: {self.output_dir.get()}")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo("Success", "Conversion completed successfully!"))
            self.conversion_completed(True)
            
        except Exception as e:
            self.log_message(f"❌ Error during conversion: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Conversion failed: {str(e)}"))
            self.conversion_completed(False)
            
    def conversion_completed(self, success):
        """Called when conversion is completed"""
        self.root.after(0, self._conversion_completed_ui, success)
        
    def _conversion_completed_ui(self, success):
        """Update UI after conversion completion"""
        self.convert_button.config(state='normal')
        self.progress.stop()
        if success:
            self.status_var.set("Conversion completed successfully")
        else:
            self.status_var.set("Conversion failed")


def main():
    # Create and run GUI
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
        
    # Configure accent button style
    style.configure('Accent.TButton', foreground='black', background='#0078d4')
    
    app = CVATDLCGui(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
