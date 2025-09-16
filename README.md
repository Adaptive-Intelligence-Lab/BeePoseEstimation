# 🐝 CVAT to DeepLabCut Pipeline

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![DeepLabCut](https://img.shields.io/badge/DeepLabCut-3.0+-green.svg)](https://github.com/DeepLabCut/DeepLabCut)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/Interface-GUI%20%2B%20CLI-purple.svg)](#usage)

*Transform your CVAT annotations into DeepLabCut-ready datasets with a beautiful GUI interface*

[🚀 Quick Start](#quick-start) • [📖 Documentation](#documentation) • [🎯 Features](#features) • [🔧 Installation](#installation)

</div>

---

## ✨ Overview

**CVAT to DeepLabCut Pipeline** is a comprehensive tool that bridges the gap between [CVAT](https://cvat.org/) annotation platform and [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut) pose estimation framework. With both command-line and beautiful GUI interfaces, it makes converting your carefully annotated datasets effortless.

### 🎯 Perfect For
- 🐝 **Animal Pose Estimation** (Bees, mice, custom animals)
- 🔬 **Research Projects** requiring precise keypoint tracking
- 👥 **Teams** needing user-friendly annotation workflows
- 🚀 **Rapid Prototyping** of pose estimation models

---

## 🌟 Features

<table>
<tr>
<td width="50%">

### 🎨 **Beautiful GUI Interface**
- 📁 Drag-and-drop file selection
- 🎛️ Real-time configuration
- 📊 Live progress tracking
- 📝 Interactive logging

</td>
<td width="50%">

### ⚡ **Powerful CLI Tools**
- 🔧 Scriptable automation
- 🔄 Batch processing ready
- ⚙️ Advanced configuration
- 🖥️ Server deployment friendly

</td>
</tr>
<tr>
<td>

### 🎯 **Smart Frame Selection**
- 📹 Full video processing
- 🎬 Custom frame ranges
- 🔍 Automatic frame matching
- 📐 Precise correspondence

</td>
<td>

### 🐝 **Animal-Specific Support**
- 🐝 Pre-configured bee skeletons
- 🦎 Customizable keypoint models
- 🔗 Automatic skeleton connections
- 📏 Multi-animal support

</td>
</tr>
</table>

---

## 🚀 Quick Start

### 1️⃣ **Installation**

```bash
# Clone the repository
git clone https://github.com/yourusername/cvat-deeplabcut-pipeline.git
cd cvat-deeplabcut-pipeline

# Install dependencies
pip install opencv-python pandas numpy pyyaml tkinter

# Install DeepLabCut (optional but recommended)
pip install deeplabcut
```

> 💡 **Need DeepLabCut?** Follow the comprehensive installation guide at [deeplabcut.github.io](https://deeplabcut.github.io/DeepLabCut/docs/installation.html) and [Official Examples](https://github.com/DeepLabCut/DeepLabCut/tree/main/examples)


### 2️⃣ **Launch GUI Interface**

```bash
python cvat_dlc_gui.py
```
*Beautiful, intuitive interface for seamless conversion*

### 3️⃣ **Or Use Command Line**

```bash
# Basic conversion
python cvat_to_deeplabcut_pipeline.py annotations.xml video.mp4 output_project

# With custom settings
python cvat_to_deeplabcut_pipeline.py annotations.xml video.mp4 output_project \
    --project "MyBeeProject" --scorer "researcher1" --range 100 500
```

## 🔧 Installation & Setup

### Prerequisites

<table>
<tr>
<td width="30%"><strong>🐍 Python</strong></td>
<td>3.8+ (3.10+ recommended)</td>
</tr>
<tr>
<td><strong>📦 Core Dependencies</strong></td>
<td><code>opencv-python pandas numpy pyyaml</code></td>
</tr>
<tr>
<td><strong>🎨 GUI Dependencies</strong></td>
<td><code>tkinter</code> (usually included)</td>
</tr>
<tr>
<td><strong>🤖 DeepLabCut</strong></td>
<td>Optional for H5 generation</td>
</tr>
</table>

### Step-by-Step Installation

<details>
<summary><strong>🪟 Windows Users</strong></summary>

```powershell
# Install Python from python.org
# Clone repository
git clone https://github.com/yourusername/cvat-deeplabcut-pipeline.git
cd cvat-deeplabcut-pipeline

# Install requirements
pip install opencv-python pandas numpy pyyaml

# Optional: Install DeepLabCut
pip install deeplabcut
```

</details>

<details>
<summary><strong>🐧 Linux/Ubuntu Users</strong></summary>

```bash
# Update system
sudo apt update && sudo apt install python3-pip python3-tk

# Clone repository
git clone https://github.com/yourusername/cvat-deeplabcut-pipeline.git
cd cvat-deeplabcut-pipeline

# Install requirements
pip3 install opencv-python pandas numpy pyyaml

# Optional: Install DeepLabCut with GPU support
pip3 install deeplabcut
```

</details>

<details>
<summary><strong>🍎 macOS Users</strong></summary>

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Clone repository
git clone https://github.com/yourusername/cvat-deeplabcut-pipeline.git
cd cvat-deeplabcut-pipeline

# Install requirements
pip3 install opencv-python pandas numpy pyyaml

# Optional: Install DeepLabCut
pip3 install deeplabcut
```

</details>

---

## 💻 Usage

### 🎨 GUI Interface (Recommended)

The GUI provides the most user-friendly experience:

```bash
python cvat_dlc_gui.py
```

**Features:**
- 📁 **File Browser**: Easy file selection with drag-and-drop
- ⚙️ **Project Settings**: Configure project name and scorer
- 🎬 **Frame Selection**: Choose full video or custom range
- 📊 **Progress Tracking**: Real-time conversion progress
- 📝 **Live Logging**: See exactly what's happening

![GUI Interface Demo](docs/images/gui_demo.gif)

### ⌨️ Command Line Interface

Perfect for automation and batch processing:

```bash
# Basic usage
python cvat_to_deeplabcut_pipeline.py [xml_file] [video_file] [output_dir]

# Advanced usage with options
python cvat_to_deeplabcut_pipeline.py annotations.xml video.mp4 my_project \
    --project "BeeTracking2024" \
    --scorer "lab_researcher" \
    --range 50 300 \
    --bodyparts head,thorax,abdomen
```

**CLI Arguments:**
| Argument | Description | Default |
|----------|-------------|---------|
| `xml_file` | CVAT XML annotation file | Required |
| `video_file` | Input video file | Required |
| `output_dir` | Output directory | Required |
| `--project` | Project name | "BeePoseEstimation" |
| `--scorer` | Scorer name | "manual" |
| `--range` | Frame range (start end) | Full video |

---

## 📊 Output Structure

The pipeline generates a complete DeepLabCut project structure:

```
output_project/
├── 📁 labeled-data/
│   └── video_name/
│       ├── 📊 CollectedData_scorer.csv     # Annotation data (CSV)
│       ├── 🗃️ CollectedData_scorer.h5      # Annotation data (H5)
│       └── 🖼️ frame_*.png                 # Extracted frames
├── 🎬 videos/
│   └── original_video.mp4                 # Original video
├── ⚙️ config.yaml                         # DeepLabCut configuration
└── 📋 dataset_summary.txt                 # Conversion summary
```

### 📋 Generated Files Explained

<details>
<summary><strong>📊 CollectedData_scorer.csv</strong></summary>

Standard DeepLabCut annotation format with hierarchical columns:
```csv
scorer,manual,manual,manual,...
bodyparts,head,head,thorax,...
coords,x,y,x,y,...
labeled-data/video/frame_0000.png,245.5,123.2,345.1,234.5,...
```

</details>

<details>
<summary><strong>⚙️ config.yaml</strong></summary>

Complete DeepLabCut project configuration:
```yaml
Task: BeeTracking
scorer: manual
date: Dec5
bodyparts: [head, thorax, abdomen, ...]
skeleton: [[head, thorax], [thorax, abdomen], ...]
project_path: /path/to/project
video_sets: {...}
```

</details>

---

## 🐝 Bee Pose Configuration

The pipeline comes pre-configured with bee-specific skeleton models:

### 👑 Queen Bee Model
```yaml
bodyparts: [head, neck, tail, L1, L2, L3, R1, R2, R3]
skeleton:
  - [head, neck]      # Head to body connection
  - [neck, tail]      # Body segment
  - [L1, L2]          # Left antenna segments
  - [L2, L3]
  - [L3, head]        # Antenna to head
  - [R1, R2]          # Right antenna segments
  - [R2, R3]
  - [R3, head]        # Antenna to head
```

### 🐝 Worker Bee Model
```yaml
bodyparts: [head, neck, tail, L1, L2, L3, R1, R2, R3]
skeleton:
  - [head, neck]
  - [neck, tail]
  - [L1, L2]
  - [L2, L3]
  - [L3, head]
  - [R1, R2]
  - [R2, R3]
  - [R3, head]
```

![Bee Skeleton Visualization](docs/images/bee_skeleton.png)

---

## 🔧 Advanced Features

### 🎬 Frame Selection Modes

<table>
<tr>
<td width="50%">

#### 📹 **Full Mode**
- Processes entire video
- Extracts all annotated frames
- Maintains temporal consistency
- Best for comprehensive training

</td>
<td width="50%">

#### 🎯 **Range Mode**
- Custom start/end frames
- Reduces dataset size
- Focuses on specific behaviors
- Faster processing

</td>
</tr>
</table>

### 🔄 Automatic H5 Conversion

The pipeline intelligently handles DeepLabCut's H5 conversion:

1. **🔍 Detection**: Automatically detects when H5 conversion is needed
2. **🤖 Automation**: Handles interactive prompts automatically
3. **🛡️ Fallback**: Multiple conversion methods for reliability
4. **✅ Verification**: Confirms successful conversion

## 🔍 Troubleshooting

### Common Issues & Solutions

<details>
<summary><strong>❌ "Cannot import deeplabcut"</strong></summary>

**Problem**: DeepLabCut not installed or not in PATH

**Solutions**:
```bash
# Install DeepLabCut
pip install deeplabcut

# Or create conda environment
conda create -n dlc python=3.10
conda activate dlc
pip install deeplabcut
```

</details>

<details>
<summary><strong>🎬 "Video file not found"</strong></summary>

**Problem**: Video path incorrect or file permissions

**Solutions**:
- ✅ Check file path is correct
- ✅ Verify file permissions
- ✅ Ensure video format is supported (mp4, avi, mov)
- ✅ Try absolute path instead of relative

</details>

<details>
<summary><strong>📊 "XML parsing errors"</strong></summary>

**Problem**: CVAT XML file is incomplete or corrupted

**Solutions**:
- ✅ Re-export from CVAT
- ✅ Verify all annotations are saved
- ✅ Check XML file size > 0
- ✅ Validate XML structure

</details>

<details>
<summary><strong>🔄 "H5 conversion fails"</strong></summary>

**Problem**: Interactive prompt or permission issues

**Solutions**:
```bash
# Use manual converter
python h5_converter.py path/to/config.yaml scorer_name

# Or manual DeepLabCut conversion
python -c "import deeplabcut; deeplabcut.convertcsv2h5('config.yaml', scorer='manual')"
```

</details>

### 🆘 Getting Help

1. **📖 Check Documentation**: Review this README and `README_CVAT_Pipeline.md`
2. **🔍 Search Issues**: Look for similar problems in GitHub issues
3. **📝 Check Logs**: Review conversion logs for specific errors
4. **🧪 Test Sample**: Try with provided sample data first
5. **📮 Report Bug**: Create detailed issue with logs and system info

---

## 🚀 Next Steps After Conversion

Once your conversion is complete:

### 1️⃣ **Verify Dataset**
```bash
# Check output structure
ls -la output_project/
# Verify frame count
ls output_project/labeled-data/*/frame_*.png | wc -l
```

### 2️⃣ **Start DeepLabCut Training**
```python
import deeplabcut

# Load your project
config_path = 'output_project/config.yaml'

# Create training dataset
deeplabcut.create_training_dataset(config_path)

# Train the network
deeplabcut.train_network(config_path)
```

### 3️⃣ **Evaluate and Refine**
```python
# Evaluate training
deeplabcut.evaluate_network(config_path)

# Analyze new videos
deeplabcut.analyze_videos(config_path, ['new_video.mp4'])
```

---

## 📚 Documentation

- 📖 **[Detailed Pipeline Guide](README_CVAT_Pipeline.md)** - Complete technical documentation
- 🔧 **[DeepLabCut Installation](https://deeplabcut.github.io/DeepLabCut/docs/installation.html)** - Official installation guide
- 🎯 **[CVAT Documentation](https://opencv.github.io/cvat/)** - Learn about annotation workflow
- 🐍 **[API Reference](docs/api.md)** - Programming interface documentation

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

<table>
<tr>
<td>🐛 <strong>Bug Reports</strong></td>
<td>Found an issue? <a href="../../issues">Report it here</a></td>
</tr>
<tr>
<td>💡 <strong>Feature Requests</strong></td>
<td>Have an idea? <a href="../../issues">Suggest it here</a></td>
</tr>
<tr>
<td>🔧 <strong>Code Contributions</strong></td>
<td>Submit pull requests with improvements</td>
</tr>
<tr>
<td>📖 <strong>Documentation</strong></td>
<td>Help improve guides and examples</td>
</tr>
</table>

### Development Setup

```bash
# Fork and clone your fork
git clone https://github.com/yourusername/cvat-deeplabcut-pipeline.git
cd cvat-deeplabcut-pipeline

# Create development branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -e .
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- 🏆 **[DeepLabCut Team](https://github.com/DeepLabCut/DeepLabCut)** - For the amazing pose estimation framework
- 🎯 **[CVAT Team](https://github.com/opencv/cvat)** - For the excellent annotation platform
- 🐝 **Research Community** - For driving innovation in animal behavior analysis
- 💻 **Open Source Contributors** - For making this project possible

---

<div align="center">

### 🌟 Star this repository if it helped your research!

[![GitHub stars](https://img.shields.io/github/stars/yourusername/cvat-deeplabcut-pipeline.svg?style=social&label=Star)](https://github.com/yourusername/cvat-deeplabcut-pipeline)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/cvat-deeplabcut-pipeline.svg?style=social&label=Fork)](https://github.com/yourusername/cvat-deeplabcut-pipeline/fork)

**Made with ❤️ for the research community**

</div>
