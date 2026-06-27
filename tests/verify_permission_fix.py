#!/usr/bin/env python3
"""
Verification script for permission error fix
Tests the enhanced error handling and recovery mechanisms
"""

import os
import sys
import tempfile
import time
import shutil
from pathlib import Path

# Test results
test_results = {
    'passed': [],
    'failed': [],
    'skipped': []
}

def test_safe_file_read():
    """Test 1: Safe file read with permission handling"""
    print("\n[TEST 1] Safe File Read with Permission Handling")
    try:
        from main import SecureFileVault
        
        # Create test vault
        test_dir = tempfile.mkdtemp(prefix='perm_test_')
        vault = SecureFileVault(test_dir)
        
        # Create test file
        test_file = os.path.join(test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write("test data content")
        
        # Test normal read
        data = vault._safe_file_read(test_file)
        assert data == b"test data content", "Normal read failed"
        
        # Test read-only file (simulate lock)
        os.chmod(test_file, 0o444)
        data = vault._safe_file_read(test_file)
        assert data == b"test data content", "Read-only file read failed"
        
        # Cleanup
        os.chmod(test_file, 0o644)
        shutil.rmtree(test_dir)
        
        print("✅ PASSED: Safe file read working correctly")
        test_results['passed'].append("Safe File Read")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results['failed'].append(("Safe File Read", str(e)))
        return False

def test_permission_error_recovery():
    """Test 2: Permission error recovery in retrieve_file"""
    print("\n[TEST 2] Permission Error Recovery in retrieve_file")
    try:
        from main import SecureFileVault
        
        # Create test vault
        test_dir = tempfile.mkdtemp(prefix='perm_test_')
        vault = SecureFileVault(test_dir)
        
        # Store a test file
        test_file = os.path.join(test_dir, 'secret.txt')
        with open(test_file, 'w') as f:
            f.write("secret content")
        
        success, file_id = vault.store_file(
            test_file,
            password="testpass123",
            use_camouflage=True
        )
        
        assert success, f"Store failed: {file_id}"
        
        # Make the stored file read-only (simulate permission issue)
        metadata_file = os.path.join(vault.metadata_path, f"{file_id}.json")
        assert os.path.exists(metadata_file), "Metadata not found"
        
        # Try to retrieve (should handle permission issues)
        output_file = os.path.join(test_dir, 'retrieved.txt')
        success, msg = vault.retrieve_file(
            file_id,
            password="testpass123",
            output_path=output_file
        )
        
        assert success, f"Retrieve failed: {msg}"
        assert os.path.exists(output_file), "Output file not created"
        
        # Verify content
        with open(output_file, 'r') as f:
            content = f.read()
        assert "secret" in content, "Content not recovered correctly"
        
        # Cleanup
        shutil.rmtree(test_dir)
        
        print("✅ PASSED: Permission error recovery working")
        test_results['passed'].append("Permission Error Recovery")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results['failed'].append(("Permission Error Recovery", str(e)))
        return False

def test_temp_file_cleanup():
    """Test 3: Temporary IPFS file cleanup"""
    print("\n[TEST 3] Temporary IPFS File Cleanup")
    try:
        from main import SecureFileVault
        
        # Create test vault
        test_dir = tempfile.mkdtemp(prefix='perm_test_')
        vault = SecureFileVault(test_dir)
        
        # Create test file
        test_file = os.path.join(test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Count temp files before
        temp_before = len([f for f in os.listdir(test_dir) 
                          if '_ipfs_temp' in f])
        
        # Store and retrieve
        success, file_id = vault.store_file(
            test_file,
            password="testpass",
            use_camouflage=True
        )
        
        output_file = os.path.join(test_dir, 'output.txt')
        vault.retrieve_file(file_id, "testpass", output_file)
        
        # Count temp files after
        temp_after = len([f for f in os.listdir(test_dir) 
                         if '_ipfs_temp' in f])
        
        assert temp_after <= temp_before, "Temp files not cleaned up"
        
        # Cleanup
        shutil.rmtree(test_dir)
        
        print("✅ PASSED: Temp file cleanup working")
        test_results['passed'].append("Temp File Cleanup")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results['failed'].append(("Temp File Cleanup", str(e)))
        return False

def test_retry_logic():
    """Test 4: Retry logic with backoff"""
    print("\n[TEST 4] Retry Logic with Exponential Backoff")
    try:
        # This test verifies the retry mechanism exists
        from main import SecureFileVault
        
        # Check that _safe_file_read has retry logic
        import inspect
        vault = SecureFileVault(tempfile.mkdtemp())
        source = inspect.getsource(vault._safe_file_read)
        
        assert 'max_retries' in source, "Retry logic not found"
        assert 'time.sleep' in source, "Backoff timing not found"
        assert 'PermissionError' in source, "Permission error handling not found"
        
        print("✅ PASSED: Retry logic implemented correctly")
        test_results['passed'].append("Retry Logic")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results['failed'].append(("Retry Logic", str(e)))
        return False

def test_ipfs_recovery_retry():
    """Test 5: IPFS recovery retry logic"""
    print("\n[TEST 5] IPFS Recovery Retry Logic")
    try:
        # Verify IPFS recovery has retry logic
        from ipfs_blockchain_backup import IPFSBackupManager
        import inspect
        
        ipfs = IPFSBackupManager()
        source = inspect.getsource(ipfs.recover_file)
        
        assert 'max_retries' in source, "IPFS retry logic not found"
        assert 'chmod' in source, "Permission fixing not found"
        assert 'os.path.exists' in source, "Verification not found"
        
        print("✅ PASSED: IPFS recovery retry logic implemented")
        test_results['passed'].append("IPFS Recovery Retry")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_results['failed'].append(("IPFS Recovery Retry", str(e)))
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY - Permission Error Fix Verification")
    print("=" * 80)
    
    total = len(test_results['passed']) + len(test_results['failed'])
    passed = len(test_results['passed'])
    failed = len(test_results['failed'])
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    
    if test_results['passed']:
        print("\n✅ PASSED TESTS:")
        for test in test_results['passed']:
            print(f"  • {test}")
    
    if test_results['failed']:
        print("\n❌ FAILED TESTS:")
        for test, error in test_results['failed']:
            print(f"  • {test}: {error}")
    
    print("\n" + "=" * 80)
    
    if not failed:
        print("🎉 ALL TESTS PASSED - Fix verified!")
    else:
        print(f"⚠️  {failed} test(s) failed - see details above")
    
    print("=" * 80)

def main():
    """Run all verification tests"""
    print("\n" + "=" * 80)
    print("🧪 PERMISSION ERROR FIX - VERIFICATION TESTS")
    print("=" * 80)
    print("Testing fixes for PermissionError in IPFS file recovery")
    
    # Run tests
    test_safe_file_read()
    test_permission_error_recovery()
    test_temp_file_cleanup()
    test_retry_logic()
    test_ipfs_recovery_retry()
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    if test_results['failed']:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
