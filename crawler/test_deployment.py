#!/usr/bin/env python3
"""
Test script to verify deployment environment
"""
import os
import sys
import json

def test_environment():
    """Test basic environment setup"""
    print("=== Environment Test ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    # Test if we can access the shared directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shared_dir = os.path.join(project_root, "shared")
    print(f"Project root: {project_root}")
    print(f"Shared directory: {shared_dir}")
    print(f"Shared directory exists: {os.path.exists(shared_dir)}")
    
    # Test if we can create a test file
    test_file = os.path.join(shared_dir, "test_deployment.json")
    try:
        os.makedirs(shared_dir, exist_ok=True)
        with open(test_file, "w") as f:
            json.dump({"test": "success", "timestamp": "2024-01-01"}, f)
        print(f"Successfully created test file: {test_file}")
        
        # Clean up
        os.remove(test_file)
        print("Test file cleaned up successfully")
        
    except Exception as e:
        print(f"Error creating test file: {e}")
    
    print("=== Environment Test Complete ===")

if __name__ == "__main__":
    test_environment() 