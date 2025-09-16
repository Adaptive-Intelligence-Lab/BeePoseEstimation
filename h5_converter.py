#!/usr/bin/env python3
"""
H5 Converter Utility
A utility script to handle DeepLabCut CSV to H5 conversion with automatic 'yes' response
"""

import sys
import os
from pathlib import Path


def convert_csv_to_h5_auto(config_path: str, scorer: str) -> bool:
    """
    Convert CSV to H5 with automatic 'yes' response to DeepLabCut prompts
    
    Args:
        config_path: Path to config.yaml file
        scorer: Scorer name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import deeplabcut
        
        # Method 1: Try to patch the input function
        try:
            # Backup original input function
            original_input = __builtins__['input'] if isinstance(__builtins__, dict) else __builtins__.input
            
            # Define our auto-yes input function
            def auto_yes_input(prompt=''):
                print(f"{prompt}yes")  # Print the prompt and our response
                return 'yes'
            
            # Temporarily replace input function
            if isinstance(__builtins__, dict):
                __builtins__['input'] = auto_yes_input
            else:
                __builtins__.input = auto_yes_input
            
            # Call the conversion function
            deeplabcut.convertcsv2h5(config_path, scorer=scorer)
            
            # Restore original input function
            if isinstance(__builtins__, dict):
                __builtins__['input'] = original_input
            else:
                __builtins__.input = original_input
                
            print("✅ H5 conversion completed successfully")
            return True
            
        except Exception as e1:
            # Restore input function in case of error
            try:
                if isinstance(__builtins__, dict):
                    __builtins__['input'] = original_input
                else:
                    __builtins__.input = original_input
            except:
                pass
            
            # Method 2: Try using environment variables
            try:
                os.environ['PYTHONIOENCODING'] = 'utf-8'
                os.environ['DLC_BATCH_MODE'] = '1'
                
                # Try again with environment variable
                deeplabcut.convertcsv2h5(config_path, scorer=scorer)
                print("✅ H5 conversion completed successfully")
                return True
                
            except Exception as e2:
                print(f"⚠️ Warning: H5 conversion requires manual confirmation")
                print(f"   DeepLabCut is asking: 'Do you want to convert the csv file in folder: ... ?'")
                print(f"   Please answer 'yes' when prompted")
                
                # Try one more time with the original function
                try:
                    deeplabcut.convertcsv2h5(config_path, scorer=scorer)
                    print("✅ H5 conversion completed successfully")
                    return True
                except Exception as e3:
                    print(f"❌ H5 conversion failed: {e3}")
                    return False
                    
    except ImportError:
        print("❌ DeepLabCut is not installed")
        return False
    except Exception as e:
        print(f"❌ H5 conversion failed: {e}")
        return False


def main():
    """Main function for command line usage"""
    if len(sys.argv) != 3:
        print("Usage: python h5_converter.py <config_path> <scorer>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    scorer = sys.argv[2]
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    print(f"🔄 Converting CSV to H5...")
    print(f"   Config: {config_path}")
    print(f"   Scorer: {scorer}")
    
    success = convert_csv_to_h5_auto(config_path, scorer)
    
    if success:
        print("🎉 Conversion completed successfully!")
        sys.exit(0)
    else:
        print("❌ Conversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
