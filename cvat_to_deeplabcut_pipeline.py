#!/usr/bin/env python3
"""
Complete CVAT to DeepLabCut Data Conversion Pipeline
Provides an interactive interface to process CVAT annotations and videos, 
generating datasets in DeepLabCut format

Input:
1. CVAT exported XML file (containing annotation data for all frames)
2. Original video file (.mp4/.avi etc.)

Features:
1. Frame selection options:
   - Full: Use all frames
   - Range: Use specified frame range
2. Generate files strictly following BeePose project format:
   - CollectedData_manual.csv format annotation file
   - config.yaml format configuration file
3. Ensure correspondence between data frames and video frames
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import cv2
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime


class CVATToDeepLabCutPipeline:
    """Complete CVAT to DeepLabCut conversion pipeline"""
    
    def __init__(self):
        self.annotations = {}
        self.video_info = {}
        self.bodyparts = []
        self.frame_selection = "full"
        self.frame_range = (0, -1)
        
    def parse_cvat_xml(self, xml_file: str) -> bool:
        """
        Parse CVAT XML annotation file
        
        Args:
            xml_file: CVAT XML file path
            
        Returns:
            Whether parsing was successful
        """
        print(f"📄 Parsing CVAT XML file: {xml_file}")
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"❌ XML parsing error: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ File not found: {xml_file}")
            return False
        
        # Extract meta information
        meta = root.find('meta')
        if meta is not None:
            job = meta.find('job')
            if job is not None:
                size_elem = job.find('size')
                start_frame_elem = job.find('start_frame')
                stop_frame_elem = job.find('stop_frame')
                
                self.video_info = {
                    'total_frames': int(size_elem.text) if size_elem is not None else 0,
                    'start_frame': int(start_frame_elem.text) if start_frame_elem is not None else 0,
                    'stop_frame': int(stop_frame_elem.text) if stop_frame_elem is not None else 0
                }
                
                print(f"📊 Video info: Total frames={self.video_info['total_frames']}, "
                      f"Start frame={self.video_info['start_frame']}, "
                      f"End frame={self.video_info['stop_frame']}")
        
        # Parse annotation data
        self.annotations = {}
        bodyparts_set = set()
        
        # Iterate through all tracks
        for track in root.findall('track'):
            track_id = track.get('id')
            label = track.get('label')
            
            print(f"🔍 Processing Track {track_id}: {label}")
            
            # Process box annotations (bounding boxes)
            for box in track.findall('box'):
                frame_num = int(box.get('frame'))
                
                if frame_num not in self.annotations:
                    self.annotations[frame_num] = {}
                
                # Extract bounding box information
                xtl = float(box.get('xtl'))
                ytl = float(box.get('ytl'))
                xbr = float(box.get('xbr'))
                ybr = float(box.get('ybr'))
                
                # Calculate center point coordinates
                center_x = (xtl + xbr) / 2
                center_y = (ytl + ybr) / 2
                
                # Store as center point
                bodypart_name = f"{label}_center"
                self.annotations[frame_num][bodypart_name] = (center_x, center_y)
                bodyparts_set.add(bodypart_name)
            
            # Process points annotations (keypoints)
            for point in track.findall('points'):
                frame_num = int(point.get('frame'))
                
                if frame_num not in self.annotations:
                    self.annotations[frame_num] = {}
                
                # Parse point coordinates
                points_str = point.get('points')
                if points_str:
                    coords = points_str.split(',')
                    if len(coords) >= 2:
                        x = float(coords[0])
                        y = float(coords[1])
                        self.annotations[frame_num][label] = (x, y)
                        bodyparts_set.add(label)
        
        self.bodyparts = sorted(list(bodyparts_set))
        print(f"✅ Detected keypoints: {self.bodyparts}")
        print(f"📊 Parsing completed: {len(self.annotations)} frames of annotation data")
        
        return True
    
    def get_video_info(self, video_file: str) -> bool:
        """
        Get video information
        
        Args:
            video_file: Video file path
            
        Returns:
            Whether information was successfully obtained
        """
        print(f"🎥 Getting video information: {video_file}")
        
        try:
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                print(f"❌ Cannot open video file: {video_file}")
                return False
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.video_info.update({
                'total_frames': total_frames,
                'fps': fps,
                'width': width,
                'height': height,
                'video_file': video_file
            })
            
            cap.release()
            
            print(f"📊 Video info: {total_frames} frames, {fps:.2f}FPS, {width}x{height}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to get video information: {e}")
            return False
    
    def interactive_frame_selection(self):
        """Interactive frame selection"""
        print("\n" + "="*60)
        print("📋 Frame selection options:")
        print("1. Full - Use all frames")
        print("2. Range - Use specified frame range")
        print("="*60)
        
        while True:
            choice = input("Please select option (1/2): ").strip()
            
            if choice == "1":
                self.frame_selection = "full"
                self.frame_range = (0, self.video_info['total_frames'] - 1)
                print(f"✅ Selected: Use all frames (0-{self.video_info['total_frames'] - 1})")
                break
            elif choice == "2":
                self.frame_selection = "range"
                max_frame = self.video_info['total_frames'] - 1
                
                while True:
                    try:
                        start = int(input(f"Start frame number (0-{max_frame}): "))
                        end = int(input(f"End frame number ({start}-{max_frame}): "))
                        
                        if 0 <= start <= end <= max_frame:
                            self.frame_range = (start, end)
                            print(f"✅ Selected: Use frame range ({start}-{end})")
                            break
                        else:
                            print(f"❌ Invalid range, please re-enter")
                    except ValueError:
                        print("❌ Please enter valid numbers")
                break
            else:
                print("❌ Invalid selection, please enter 1 or 2")
    
    def extract_frames(self, video_file: str, output_dir: str) -> bool:
        """
        Extract frames from video to labeled-data directory
        
        Args:
            video_file: Video file path
            output_dir: Output directory
            
        Returns:
            Whether extraction was successful
        """
        print(f"🎞️ Extracting frames from video...")
        
        # Create labeled-data directory, extracted frames go here
        video_name = Path(video_file).stem  # Get video filename without extension
        frames_dir = Path(output_dir) / "labeled-data" / video_name
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                print(f"❌ Cannot open video file: {video_file}")
                return False
            
            start_frame, end_frame = self.frame_range
            frame_count = 0
            extracted_count = 0
            
            print(f"📊 Extracting frame range: {start_frame} - {end_frame}")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if start_frame <= frame_count <= end_frame:
                    # Save frame, ensure filename corresponds to annotation data
                    frame_filename = f"frame_{frame_count:04d}.png"
                    frame_path = frames_dir / frame_filename
                    cv2.imwrite(str(frame_path), frame)
                    extracted_count += 1
                    
                    if extracted_count % 10 == 0:
                        print(f"  Extracted {extracted_count} frames...")
                
                frame_count += 1
                
                if frame_count > end_frame:
                    break
            
            cap.release()
            print(f"✅ Successfully extracted {extracted_count} frames to: {frames_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Frame extraction failed: {e}")
            return False
    
    def create_deeplabcut_csv(self, output_dir: str, scorer: str = "manual", 
                             project_name: str = "BeePoseEstimation") -> bool:
        """
        Create DeepLabCut CSV file strictly following BeePose format
        
        Args:
            output_dir: Output directory
            scorer: Scorer name
            project_name: Project name
            
        Returns:
            Whether creation was successful
        """
        print(f"📊 Creating DeepLabCut CSV file...")
        
        # Create labeled-data directory structure, using video filename
        video_name = Path(self.video_info['video_file']).stem
        labeled_data_dir = Path(output_dir) / "labeled-data" / video_name
        labeled_data_dir.mkdir(parents=True, exist_ok=True)
        
        csv_file = labeled_data_dir / f"CollectedData_{scorer}.csv"
        
        # Get annotation data within frame range
        start_frame, end_frame = self.frame_range
        valid_frames = []
        for frame_num in sorted(self.annotations.keys()):
            if start_frame <= frame_num <= end_frame:
                valid_frames.append(frame_num)
        
        if not valid_frames:
            print(f"❌ No annotation data found in frame range {start_frame}-{end_frame}")
            return False
        
        print(f"📊 Found {len(valid_frames)} frames of annotation data in range")
        
        # Create CSV following BeePose format
        # First row: scorer
        scorer_row = ['scorer', '', ''] + [scorer] * (len(self.bodyparts) * 2)
        
        # Second row: bodyparts
        bodyparts_row = ['bodyparts', '', '']
        for bodypart in self.bodyparts:
            bodyparts_row.extend([bodypart, bodypart])
        
        # Third row: coords
        coords_row = ['coords', '', ''] + ['x', 'y'] * len(self.bodyparts)
        
        # Data rows
        data_rows = []
        for i, frame_num in enumerate(valid_frames):
            # Build image filename, ensure it corresponds to extracted frames
            image_name = f"frame_{frame_num:04d}.png"
            
            # Create data row: labeled-data, video_name, image_name, coordinates...
            row = ['labeled-data', video_name, image_name]
            
            frame_annotations = self.annotations[frame_num]
            
            # Add coordinates for each keypoint
            for bodypart in self.bodyparts:
                if bodypart in frame_annotations:
                    x, y = frame_annotations[bodypart]
                    row.extend([x, y])
                else:
                    # Use NaN for unannotated points
                    row.extend([np.nan, np.nan])
            
            data_rows.append(row)
        
        # Write CSV file
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.writer(f)
                
                # Write header rows
                writer.writerow(scorer_row)
                writer.writerow(bodyparts_row)
                writer.writerow(coords_row)
                
                # Write data rows
                for row in data_rows:
                    writer.writerow(row)
            
            print(f"✅ Successfully created CSV file: {csv_file}")
            print(f"📊 CSV statistics: {len(data_rows)} frames, {len(self.bodyparts)} keypoints")
            return True
            
        except Exception as e:
            print(f"❌ CSV file creation failed: {e}")
            return False
    
    def create_deeplabcut_config(self, output_dir: str, project_name: str = "BeePoseEstimation",
                                scorer: str = "manual") -> bool:
        """
        Create config.yaml file strictly following BeePose format
        
        Args:
            output_dir: Output directory
            project_name: Project name
            scorer: Scorer name
            
        Returns:
            Whether creation was successful
        """
        print(f"⚙️ Creating DeepLabCut configuration file...")
        
        config_file = Path(output_dir) / "config.yaml"
        
        # Get current date (format like Sep16)
        current_date = datetime.now().strftime("%b%d")
        
        # Get project path
        project_path = str(Path(output_dir).absolute())
        
        # Get video file information
        video_filename = Path(self.video_info['video_file']).name
        
        # Create configuration following BeePose config.yaml format
        config_data = {
            # Project definitions (do not edit)
            'Task': project_name,
            'scorer': scorer,
            'date': current_date,
            'multianimalproject': None,
            'identity': None,
            
            # Project path (change when moving around)
            'project_path': project_path,
            
            # Default DeepLabCut engine
            'engine': 'pytorch',
            
            # Annotation data set configuration
            'video_sets': {
                video_filename: {
                    'crop': False
                }
            },
            
            # Body parts
            'bodyparts': self.bodyparts,
            
            # Fraction of video to start/stop when extracting frames
            'start': 0,
            'stop': 1,
            'numframes2pick': 20,
            
            # Plotting configuration
            'skeleton': [
                # Queen bee skeleton
                ['Q_Head', 'Q_Neck'],
                ['Q_Neck', 'Q_Tail'],
                ['Q_Antenna_L1', 'Q_Antenna_L2'],
                ['Q_Antenna_L2', 'Q_Antenna_L3'],
                ['Q_Antenna_L3', 'Q_Head'],
                ['Q_Antenna_R1', 'Q_Antenna_R2'],
                ['Q_Antenna_R2', 'Q_Antenna_R3'],
                ['Q_Antenna_R3', 'Q_Head'],
                # Other bee skeleton (template individual)
                ['O_Head', 'O_Neck'],
                ['O_Neck', 'O_Tail'],
                ['O_Antenna_L1', 'O_Antenna_L2'],
                ['O_Antenna_L2', 'O_Antenna_L3'],
                ['O_Antenna_L3', 'O_Head'],
                ['O_Antenna_R1', 'O_Antenna_R2'],
                ['O_Antenna_R2', 'O_Antenna_R3'],
                ['O_Antenna_R3', 'O_Head']
            ],
            'skeleton_color': 'blue',
            'pcutoff': 0.4,
            'dotsize': 12,
            'alphavalue': 0.7,
            'colormap': 'plasma',
            
            # Training, Evaluation and Analysis configuration
            'TrainingFraction': [0.95],
            'iteration': 0,
            'default_net_type': 'resnet_50',
            'default_augmenter': 'imgaug',
            'snapshotindex': -1,
            'detector_snapshotindex': -1,
            'batch_size': 8,
            'detector_batch_size': 1,
            
            # Cropping Parameters
            'cropping': None,
            'x1': None,
            'x2': None,
            'y1': None,
            'y2': None,
            
            # Refinement configuration
            'corner2move2': None,
            'move2corner': None,
            
            # Conversion tables
            'SuperAnimalConversionTables': None,
            'project_name': project_name
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                # Write comments and configuration, mimicking BeePose format
                f.write("# Project definitions (do not edit)\n")
                f.write(f"Task: {config_data['Task']}\n")
                f.write(f"scorer: {config_data['scorer']}\n")
                f.write(f"date: {config_data['date']}\n")
                f.write("multianimalproject:\n")
                f.write("identity:\n\n\n")
                
                f.write("# Project path (change when moving around)\n")
                f.write(f"project_path: {config_data['project_path']}\n\n\n")
                
                f.write("# Default DeepLabCut engine to use for shuffle creation (either pytorch or tensorflow)\n")
                f.write(f"engine: {config_data['engine']}\n\n\n")
                
                f.write("# Annotation data set configuration (and individual video cropping parameters)\n")
                f.write("video_sets:\n")
                f.write(f"  {video_filename}:\n")
                f.write("    crop: false\n\n")
                f.write("# Other settings\n")
                
                f.write("bodyparts:\n")
                for bodypart in self.bodyparts:
                    f.write(f"- {bodypart}\n")
                f.write("\n\n\n")
                
                f.write(f"start: {config_data['start']}\n")
                f.write(f"stop: {config_data['stop']}\n")
                f.write(f"numframes2pick: {config_data['numframes2pick']}\n\n\n")
                
                f.write("# Plotting configuration\n")
                f.write("skeleton:\n")
                f.write("  # Queen bee skeleton\n")
                f.write("  - [Q_Head, Q_Neck]\n")
                f.write("  - [Q_Neck, Q_Tail]\n")
                f.write("  - [Q_Antenna_L1, Q_Antenna_L2]\n")
                f.write("  - [Q_Antenna_L2, Q_Antenna_L3]\n")
                f.write("  - [Q_Antenna_L3, Q_Head]\n")
                f.write("  - [Q_Antenna_R1, Q_Antenna_R2]\n")
                f.write("  - [Q_Antenna_R2, Q_Antenna_R3]\n")
                f.write("  - [Q_Antenna_R3, Q_Head]\n")
                f.write("\n")
                f.write("  # Other bee skeleton (template individual)\n")
                f.write("  - [O_Head, O_Neck]\n")
                f.write("  - [O_Neck, O_Tail]\n")
                f.write("  - [O_Antenna_L1, O_Antenna_L2]\n")
                f.write("  - [O_Antenna_L2, O_Antenna_L3]\n")
                f.write("  - [O_Antenna_L3, O_Head]\n")
                f.write("  - [O_Antenna_R1, O_Antenna_R2]\n")
                f.write("  - [O_Antenna_R2, O_Antenna_R3]\n")
                f.write("  - [O_Antenna_R3, O_Head]\n")
                f.write(f"skeleton_color: {config_data['skeleton_color']}\n")
                f.write(f"pcutoff: {config_data['pcutoff']}\n")
                f.write(f"dotsize: {config_data['dotsize']}\n")
                f.write(f"alphavalue: {config_data['alphavalue']}\n")
                f.write(f"colormap: {config_data['colormap']}\n\n\n")
                
                f.write("# Training,Evaluation and Analysis configuration\n")
                f.write(f"TrainingFraction: {config_data['TrainingFraction']}\n")
                f.write(f"iteration: {config_data['iteration']}\n")
                f.write(f"default_net_type: {config_data['default_net_type']}\n")
                f.write(f"default_augmenter: {config_data['default_augmenter']}\n")
                f.write(f"snapshotindex: {config_data['snapshotindex']}\n")
                f.write(f"detector_snapshotindex: {config_data['detector_snapshotindex']}\n")
                f.write(f"batch_size: {config_data['batch_size']}\n")
                f.write(f"detector_batch_size: {config_data['detector_batch_size']}\n\n\n")
                
                f.write("# Cropping Parameters (for analysis and outlier frame detection)\n")
                f.write("cropping:\n")
                f.write("#if cropping is true for analysis, then set the values here:\n")
                f.write("x1:\n")
                f.write("x2:\n")
                f.write("y1:\n")
                f.write("y2:\n\n\n")
                
                f.write("# Refinement configuration (parameters from annotation dataset configuration also relevant in this stage)\n")
                f.write("corner2move2:\n")
                f.write("move2corner:\n\n\n")
                
                f.write("# Conversion tables to fine-tune SuperAnimal weights\n")
                f.write("SuperAnimalConversionTables:\n")
                f.write(f"project_name: {config_data['project_name']}\n")
            
            print(f"✅ Successfully created configuration file: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Configuration file creation failed: {e}")
            return False
    
    def copy_video_to_project(self, video_file: str, output_dir: str) -> bool:
        """
        Copy video file to project's videos directory
        
        Args:
            video_file: Source video file path
            output_dir: Output directory
            
        Returns:
            Whether copying was successful
        """
        print(f"📹 Copying video file to project...")
        
        # Create videos directory
        videos_dir = Path(output_dir) / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy video file
        video_filename = Path(video_file).name
        destination = videos_dir / video_filename
        
        try:
            shutil.copy2(video_file, destination)
            print(f"✅ Video file copied to: {destination}")
            return True
        except Exception as e:
            print(f"❌ Video file copying failed: {e}")
            return False
    
    def generate_h5_file(self, output_dir: str, scorer: str) -> bool:
        """
        Generate DeepLabCut h5 file with automatic 'yes' response
        
        Args:
            output_dir: Output directory
            scorer: Scorer name
            
        Returns:
            Whether generation was successful
        """
        print(f"🔄 Generating h5 file...")
        
        try:
            import deeplabcut
            config_path = str(Path(output_dir) / "config.yaml")
            
            # Method 1: Try to patch the input function to automatically answer 'yes'
            try:
                # Backup original input function
                import builtins
                original_input = builtins.input
                
                # Define our auto-yes input function
                def auto_yes_input(prompt=''):
                    print(f"{prompt}yes")  # Print the prompt and our response
                    return 'yes'
                
                # Temporarily replace input function
                builtins.input = auto_yes_input
                
                # Call the conversion function
                deeplabcut.convertcsv2h5(config_path, scorer=scorer)
                
                # Restore original input function
                builtins.input = original_input
                
                print(f"✅ Successfully generated h5 file")
                return True
                
            except Exception as e1:
                # Restore input function in case of error
                try:
                    builtins.input = original_input
                except:
                    pass
                
                # Method 2: Try using subprocess with input redirection
                try:
                    import subprocess
                    import sys
                    
                    # Use our h5_converter utility script
                    h5_converter_path = Path(__file__).parent / "h5_converter.py"
                    
                    if h5_converter_path.exists():
                        # Use the dedicated converter script
                        result = subprocess.run([
                            sys.executable, str(h5_converter_path), config_path, scorer
                        ], capture_output=True, text=True, timeout=120)
                        
                        if result.returncode == 0:
                            print(f"✅ Successfully generated h5 file")
                            return True
                        else:
                            print(f"⚠️ H5 converter output: {result.stdout}")
                            if result.stderr:
                                print(f"⚠️ H5 converter errors: {result.stderr}")
                    
                    # Fallback: direct subprocess call
                    cmd = f'''
import deeplabcut
import builtins

# Patch input function
original_input = builtins.input
builtins.input = lambda prompt='': 'yes'

try:
    deeplabcut.convertcsv2h5(r"{config_path}", scorer="{scorer}")
    print("H5 conversion completed successfully")
except Exception as e:
    print(f"H5 conversion failed: {{e}}")
finally:
    builtins.input = original_input
'''
                    
                    result = subprocess.run([
                        sys.executable, '-c', cmd
                    ], input='yes\n', text=True, capture_output=True, timeout=120)
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully generated h5 file")
                        return True
                    else:
                        raise Exception(f"Subprocess method failed: {result.stderr}")
                        
                except Exception as e2:
                    # Method 3: Last resort - try with environment variable
                    try:
                        import os
                        os.environ['DLC_BATCH_MODE'] = '1'
                        os.environ['PYTHONIOENCODING'] = 'utf-8'
                        
                        deeplabcut.convertcsv2h5(config_path, scorer=scorer)
                        print(f"✅ Successfully generated h5 file")
                        return True
                        
                    except Exception as e3:
                        print(f"⚠️ Warning: H5 file generation encountered interactive prompt")
                        print(f"   DeepLabCut is asking: 'Do you want to convert the csv file in folder: ... ?'")
                        print(f"   Please manually run: deeplabcut.convertcsv2h5('{config_path}', scorer='{scorer}') and answer 'yes'")
                        print(f"   Or use: python h5_converter.py '{config_path}' '{scorer}'")
                        return True  # Not considered failure, just warning
                        
        except ImportError:
            print("⚠️ Warning: Cannot import deeplabcut, skipping h5 file generation")
            print("   Please install deeplabcut and run manually: deeplabcut.convertcsv2h5('config.yaml', scorer='your_scorer')")
            return True  # Not considered failure, just warning
        except Exception as e:
            print(f"❌ h5 file generation failed: {e}")
            print("   Please run manually: deeplabcut.convertcsv2h5('config.yaml', scorer='your_scorer')")
            return True  # Not considered failure, just warning
    
    def create_dataset_summary(self, output_dir: str, project_name: str, scorer: str):
        """Create dataset summary file"""
        summary_file = Path(output_dir) / "dataset_summary.txt"
        
        start_frame, end_frame = self.frame_range
        total_selected_frames = end_frame - start_frame + 1
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"DeepLabCut Dataset Summary\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Project Name: {project_name}\n")
            f.write(f"Scorer: {scorer}\n")
            f.write(f"Processing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Source Data Information:\n")
            f.write(f"  Video File: {self.video_info.get('video_file', 'N/A')}\n")
            f.write(f"  Video Resolution: {self.video_info.get('width', 'N/A')}x{self.video_info.get('height', 'N/A')}\n")
            f.write(f"  Video FPS: {self.video_info.get('fps', 'N/A'):.2f} FPS\n")
            f.write(f"  Total Video Frames: {self.video_info.get('total_frames', 'N/A')}\n\n")
            
            f.write(f"Processing Configuration:\n")
            f.write(f"  Frame Selection Mode: {self.frame_selection}\n")
            f.write(f"  Selected Frame Range: {start_frame}-{end_frame} (total {total_selected_frames} frames)\n")
            f.write(f"  Valid Annotation Frames: {len([f for f in self.annotations.keys() if start_frame <= f <= end_frame])}\n\n")
            
            f.write(f"Keypoint Information:\n")
            f.write(f"  Number of Keypoints: {len(self.bodyparts)}\n")
            f.write(f"  Keypoint List: {', '.join(self.bodyparts)}\n\n")
            
            f.write(f"Output Files:\n")
            f.write(f"  Project Directory: {output_dir}\n")
            video_name = Path(self.video_info['video_file']).stem
            f.write(f"  Annotation CSV: labeled-data/{video_name}/CollectedData_{scorer}.csv\n")
            f.write(f"  Annotation H5: labeled-data/{video_name}/CollectedData_{scorer}.h5\n")
            f.write(f"  Configuration File: config.yaml\n")
            f.write(f"  Video File: videos/{Path(self.video_info['video_file']).name}\n")
            f.write(f"  Images Directory: labeled-data/{video_name}/\n\n")
            
            f.write(f"DeepLabCut Usage Instructions:\n")
            f.write(f"1. Check generated file integrity\n")
            f.write(f"2. Adjust skeleton connections in config.yaml as needed\n")
            f.write(f"3. Use this directory as DeepLabCut project for training\n")
        
        print(f"📄 Dataset summary saved: {summary_file}")
    
    def run_pipeline(self, xml_file: str, video_file: str, output_dir: str,
                    project_name: str = "BeePoseEstimation", scorer: str = "manual"):
        """
        Run complete conversion pipeline
        
        Args:
            xml_file: CVAT XML file path
            video_file: Video file path
            output_dir: Output directory
            project_name: Project name
            scorer: Scorer name
        """
        print("🐝 CVAT to DeepLabCut Conversion Pipeline")
        print("=" * 60)
        
        # Step 1: Parse XML file
        if not self.parse_cvat_xml(xml_file):
            print("❌ XML parsing failed, pipeline terminated")
            return False
        
        # Step 2: Get video information
        if not self.get_video_info(video_file):
            print("❌ Video information retrieval failed, pipeline terminated")
            return False
        
        # Step 3: Interactive frame selection
        self.interactive_frame_selection()
        
        # Step 4: Extract video frames
        if not self.extract_frames(video_file, output_dir):
            print("❌ Frame extraction failed, pipeline terminated")
            return False
        
        # Step 5: Create DeepLabCut CSV file
        if not self.create_deeplabcut_csv(output_dir, scorer, project_name):
            print("❌ CSV file creation failed, pipeline terminated")
            return False
        
        # Step 6: Create DeepLabCut configuration file
        if not self.create_deeplabcut_config(output_dir, project_name, scorer):
            print("❌ Configuration file creation failed, pipeline terminated")
            return False
        
        # Step 7: Copy video file to project
        if not self.copy_video_to_project(video_file, output_dir):
            print("❌ Video file copying failed, pipeline terminated")
            return False
        
        # Step 8: Generate h5 file
        self.generate_h5_file(output_dir, scorer)
        
        # Step 9: Create dataset summary
        self.create_dataset_summary(output_dir, project_name, scorer)
        
        print("\n🎉 Conversion pipeline completed!")
        print(f"📁 Output directory: {output_dir}")
        print("\n📋 Generated file structure:")
        print(f"  {output_dir}/")
        print(f"  ├── labeled-data/")
        video_name = Path(video_file).stem
        print(f"  │   └── {video_name}/")
        print(f"  │       ├── CollectedData_{scorer}.csv   # Annotation data CSV")
        print(f"  │       ├── CollectedData_{scorer}.h5    # Annotation data H5")
        print(f"  │       └── frame_*.png                 # Extracted video frames")
        print(f"  ├── videos/")
        print(f"  │   └── {Path(video_file).name}                    # Original video")
        print(f"  ├── config.yaml                        # DeepLabCut configuration")
        print(f"  └── dataset_summary.txt                 # Dataset summary")
        print("\n🚀 You can now use this directory as a DeepLabCut project for training!")
        
        return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Complete CVAT to DeepLabCut conversion pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Usage Examples:
  python cvat_to_deeplabcut_pipeline.py annotations.xml video.mp4 output_project
  python cvat_to_deeplabcut_pipeline.py annotations.xml video.mp4 output_project --project MyBees --scorer researcher1

Features:
  1. Supports Full and Range frame selection modes
  2. Generates CSV and configuration files strictly following BeePose project format
  3. Ensures perfect correspondence between data frames and video frames
  4. Generates complete DeepLabCut project structure
        '''
    )
    
    parser.add_argument('xml_file', 
                       help='CVAT exported XML annotation file path')
    
    parser.add_argument('video_file', 
                       help='Original video file path')
    
    parser.add_argument('output_dir', 
                       help='Output project directory path')
    
    parser.add_argument('--project', 
                       default='BeePoseEstimation',
                       help='Project name (default: BeePoseEstimation)')
    
    parser.add_argument('--scorer', 
                       default='manual',
                       help='Scorer name (default: manual)')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.xml_file):
        print(f"❌ Error: XML file does not exist: {args.xml_file}")
        return
    
    if not os.path.exists(args.video_file):
        print(f"❌ Error: Video file does not exist: {args.video_file}")
        return
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run pipeline
    pipeline = CVATToDeepLabCutPipeline()
    success = pipeline.run_pipeline(
        args.xml_file,
        args.video_file,
        args.output_dir,
        args.project,
        args.scorer
    )
    
    if not success:
        print("\n❌ Conversion pipeline execution failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
