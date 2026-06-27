#!/usr/bin/env python3
"""
Test script for permanent file deletion feature
Tests all aspects of the delete functionality
"""

import os
import json
import tempfile
import shutil
from pathlib import Path

def test_delete_functionality():
    """Test the permanent delete feature"""
    print("🧪 Testing Permanent File Deletion Feature\n")
    print("=" * 60)
    
    # Import after adding to path
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    from main import SecureFileVault
    
    # Create a temporary vault for testing
    test_vault_path = os.path.join(tempfile.gettempdir(), 'test_vault_delete')
    
    # Clean up if exists
    if os.path.exists(test_vault_path):
        shutil.rmtree(test_vault_path)
    
    try:
        # Initialize vault
        print("\n✓ Creating test vault...")
        vault = SecureFileVault(test_vault_path)
        
        # Create a test file
        test_file = os.path.join(tempfile.gettempdir(), 'test_document.txt')
        with open(test_file, 'w') as f:
            f.write("This is a test file for deletion")
        
        print("✓ Created test file:", test_file)
        
        # Store the file with encryption
        print("\n✓ Encrypting file...")
        success, file_id = vault.store_file(test_file, 'testpass123', use_camouflage=True)
        
        if not success:
            print("✗ Failed to store file:", file_id)
            return False
        
        print(f"✓ File stored with ID: {file_id}")
        
        # Verify file was stored
        files_before = vault.get_stored_files()
        print(f"✓ Files in vault before deletion: {len(files_before)}")
        
        metadata_file = os.path.join(test_vault_path, 'metadata', f'{file_id}.json')
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            print(f"  - File name: {metadata.get('original_name')}")
            print(f"  - Camouflaged: {metadata.get('camouflaged')}")
            print(f"  - Storage path: {metadata.get('storage_path')}")
        
        # Check encrypted file exists
        storage_path = metadata.get('storage_path')
        if os.path.exists(storage_path):
            file_size = os.path.getsize(storage_path)
            print(f"  - Encrypted file size: {file_size} bytes")
        
        # Check blockchain has the record
        chain = vault.blockchain.get_chain()
        blockchain_record = None
        for record in chain:
            if record.get('file_id') == file_id:
                blockchain_record = record
                break
        
        if blockchain_record:
            print(f"  - Blockchain record found: {blockchain_record['index']}")
        
        # Check camouflage mapping
        if metadata.get('camouflaged') and os.path.exists(os.path.join(test_vault_path, 'camouflage_map.json')):
            with open(os.path.join(test_vault_path, 'camouflage_map.json'), 'r') as f:
                camouflage_map = json.load(f)
            print(f"  - Camouflage entries: {len(camouflage_map)}")
        
        # NOW DELETE THE FILE
        print("\n" + "=" * 60)
        print("🗑️  DELETING FILE...")
        print("=" * 60)
        
        success, message = vault.delete_file(file_id)
        
        if not success:
            print("✗ Deletion failed:", message)
            return False
        
        print("✓ Deletion successful:", message)
        
        # Verify file was deleted
        print("\n✓ Verifying deletion...")
        
        # Check metadata is gone
        if os.path.exists(metadata_file):
            print("✗ Metadata file still exists!")
            return False
        print("  ✓ Metadata file deleted")
        
        # Check encrypted file is gone
        if os.path.exists(storage_path):
            print("✗ Encrypted file still exists!")
            return False
        print("  ✓ Encrypted file deleted")
        
        # Check blockchain record is gone
        chain_after = vault.blockchain.get_chain()
        for record in chain_after:
            if record.get('file_id') == file_id:
                print("✗ Blockchain record still exists!")
                return False
        print("  ✓ Blockchain record removed")
        
        # Check file list
        files_after = vault.get_stored_files()
        print(f"  ✓ Files in vault after deletion: {len(files_after)}")
        
        if len(files_after) != len(files_before) - 1:
            print(f"✗ File count mismatch: {len(files_before)} -> {len(files_after)}")
            return False
        
        # Check camouflage mapping
        if os.path.exists(os.path.join(test_vault_path, 'camouflage_map.json')):
            with open(os.path.join(test_vault_path, 'camouflage_map.json'), 'r') as f:
                camouflage_map_after = json.load(f)
            if len(camouflage_map_after) >= len(camouflage_map):
                print("✗ Camouflage entry not removed!")
                return False
            print("  ✓ Camouflage mapping updated")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
        # Cleanup
        os.remove(test_file)
        shutil.rmtree(test_vault_path)
        
        return True
    
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup
        if os.path.exists(test_vault_path):
            shutil.rmtree(test_vault_path)
        
        return False

if __name__ == '__main__':
    success = test_delete_functionality()
    exit(0 if success else 1)
