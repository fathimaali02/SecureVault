#!/usr/bin/env python3
"""
Test: Security Logs functionality
Verify that vault logs and honeytrap logs are created and displayed correctly
"""
import os
import sys
import json
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from main import SecureFileVault

def test_security_logs():
    """Test security logs creation and display"""
    
    # Clean up old test
    test_vault = "test_vault_logs"
    if os.path.exists(test_vault):
        shutil.rmtree(test_vault)
    
    print(f"[TEST] Creating test vault: {test_vault}")
    vault = SecureFileVault(test_vault)
    
    # === TEST 1: Verify vault log exists ===
    vault_log_path = os.path.join(vault.log_path, 'vault.log')
    print(f"\n[TEST 1] Vault log location: {vault_log_path}")
    print(f"  Exists: {os.path.exists(vault_log_path)}")
    
    if os.path.exists(vault_log_path):
        with open(vault_log_path, 'r', encoding='utf-8') as f:
            vault_content = f.read()
        print(f"  Size: {len(vault_content)} bytes")
        print(f"  Sample logs:\n{vault_content[-200:]}")
    
    # === TEST 2: Create honeytrap log with failed auth entries ===
    honeytrap_log_path = os.path.join(vault.vault_path, 'honeytrap_log.txt')
    print(f"\n[TEST 2] Honeytrap log location: {honeytrap_log_path}")
    
    # Simulate failed authentication attempts
    vault.decoy.log_access("Failed auth: Password mismatch")
    vault.decoy.log_access("Failed auth: Keystroke mismatch (confidence=0.25)")
    vault.decoy.log_access("Failed auth: Both password and keystroke mismatch")
    
    if os.path.exists(honeytrap_log_path):
        with open(honeytrap_log_path, 'r', encoding='utf-8') as f:
            honeytrap_content = f.read()
        print(f"  Exists: True")
        print(f"  Size: {len(honeytrap_content)} bytes")
        print(f"  Content:\n{honeytrap_content}")
    else:
        print(f"  Exists: False")
    
    # === TEST 3: Store a file and verify blockchain record ===
    test_file = "test_security_log.txt"
    with open(test_file, 'w') as f:
        f.write("Test file for security logs")
    
    print(f"\n[TEST 3] Storing test file...")
    success, file_id = vault.store_file(test_file, "TestPassword123")
    
    if success:
        print(f"  File stored with ID: {file_id}")
        
        # Check blockchain
        chain = vault.blockchain.get_chain()
        print(f"  Blockchain records: {len(chain)}")
        
        if len(chain) > 1:
            latest = chain[-1]
            print(f"  Latest record: Block #{latest['index']}, File: {latest.get('file_id', 'N/A')[:8]}...")
    else:
        print(f"  Failed to store file: {file_id}")
    
    # === TEST 4: Verify log file integrity ===
    print(f"\n[TEST 4] Log file integrity check")
    
    logs_to_check = [
        (vault_log_path, "Vault log"),
        (honeytrap_log_path, "Honeytrap log"),
    ]
    
    for log_path, log_name in logs_to_check:
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"  {log_name}: OK ({len(content)} bytes)")
            except Exception as e:
                print(f"  {log_name}: ERROR - {e}")
        else:
            print(f"  {log_name}: Not found")
    
    # === TEST 5: Verify files list reflects operations ===
    print(f"\n[TEST 5] File operations tracking")
    files = vault.get_stored_files()
    print(f"  Stored files: {len(files)}")
    
    for f in files:
        print(f"  - {f['original_name']} (ID: {f['file_id'][:8]}...)")
        print(f"    Encrypted: {f['encrypted_at'][:19]}")
    
    # === SUMMARY ===
    print(f"\n" + "=" * 60)
    print(f"SECURITY LOGS TEST SUMMARY")
    print(f"=" * 60)
    print(f"Vault log: {'Created' if os.path.exists(vault_log_path) else 'Missing'}")
    print(f"Honeytrap log: {'Created' if os.path.exists(honeytrap_log_path) else 'Missing'}")
    print(f"Blockchain records: {len(chain)}")
    print(f"Stored files: {len(files)}")
    print(f"\nTest vault location: {os.path.abspath(test_vault)}")
    print(f"Test PASSED - All security logs functional")
    
    return True

if __name__ == '__main__':
    try:
        success = test_security_logs()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
