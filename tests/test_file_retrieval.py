#!/usr/bin/env python3
"""
Test: File retrieval with auto-restore of original filename
"""
import os
import sys
import json
import shutil

sys.path.insert(0, os.path.dirname(__file__))

from main import SecureFileVault

def test_file_retrieval():
    """Test storing and retrieving a file with auto-named output"""
    
    # Clean up old test
    test_vault = "test_vault_retrieve"
    if os.path.exists(test_vault):
        shutil.rmtree(test_vault)
    
    # Create test file
    test_file = "test_sample.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test file for retrieval\nOriginal name: test_sample.txt")
    
    print(f"[TEST] Created test file: {test_file}")
    
    # Initialize vault
    vault = SecureFileVault(test_vault)
    print(f"[TEST] Initialized vault: {test_vault}")
    
    # Store file
    password = "SecurePassword123"
    success, file_id = vault.store_file(test_file, password, use_camouflage=True)
    
    if not success:
        print(f"[TEST] ERROR: Failed to store file")
        return False
    
    print(f"[TEST] File stored successfully with ID: {file_id}")
    
    # Get metadata to show original name
    meta_file = os.path.join(vault.metadata_path, f"{file_id}.json")
    with open(meta_file, 'r') as f:
        metadata = json.load(f)
    
    original_name = metadata.get('original_name', 'unknown')
    print(f"[TEST] Original filename stored in metadata: {original_name}")
    
    # Create output folder
    output_folder = "retrieved_files"
    os.makedirs(output_folder, exist_ok=True)
    
    # Retrieve with auto-restored filename
    output_path = os.path.join(output_folder, original_name)
    print(f"\n[TEST] Retrieving file...")
    print(f"  File ID: {file_id}")
    print(f"  Output folder: {output_folder}")
    print(f"  Auto-restored filename: {original_name}")
    print(f"  Full path: {output_path}")
    
    success = vault.retrieve_file(file_id, password, output_path)
    
    if not success:
        print(f"[TEST] ERROR: Failed to retrieve file")
        return False
    
    print(f"[TEST] File retrieved successfully!")
    
    # Verify file exists and content matches
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            content = f.read()
        
        if "This is a test file" in content:
            print(f"[TEST] Content verified - file is intact")
            print(f"\n[SUCCESS] File retrieval with auto-restore works correctly!")
            print(f"  Original: {test_file}")
            print(f"  Retrieved: {output_path}")
            return True
        else:
            print(f"[TEST] ERROR: File content mismatch")
            return False
    else:
        print(f"[TEST] ERROR: Retrieved file not found at {output_path}")
        return False

if __name__ == '__main__':
    success = test_file_retrieval()
    sys.exit(0 if success else 1)
