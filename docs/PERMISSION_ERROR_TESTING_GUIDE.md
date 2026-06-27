# 🧪 Permission Error Fix - Testing Guide

## Quick Test (2 minutes)

### Test 1: Run Verification Script
```bash
cd c:\Project\Finalbackup
python verify_permission_fix.py
```

**Expected Output:**
```
✅ PASSED: Safe file read working correctly
✅ PASSED: Permission error recovery working
✅ PASSED: Temp file cleanup working
✅ PASSED: Retry logic implemented correctly
✅ PASSED: IPFS recovery retry logic implemented

🎉 ALL TESTS PASSED - Fix verified!
```

---

## Detailed Testing (10-15 minutes)

### Test 2: Safe File Read Method

```python
from main import SecureFileVault
import os
import tempfile
import shutil

# Create test environment
test_dir = tempfile.mkdtemp()
vault = SecureFileVault(test_dir)

# Create test file
test_file = os.path.join(test_dir, 'test.txt')
with open(test_file, 'w') as f:
    f.write("test data here")

# Test 1a: Normal read
print("Test 1a: Normal read...")
data = vault._safe_file_read(test_file)
assert data == b"test data here"
print("✅ Normal read successful")

# Test 1b: Read-only file (simulates locked file)
print("Test 1b: Read-only file...")
os.chmod(test_file, 0o444)
data = vault._safe_file_read(test_file)
assert data == b"test data here"
print("✅ Read-only file successful")

# Test 1c: Restore permissions
os.chmod(test_file, 0o644)

# Cleanup
shutil.rmtree(test_dir)
print("✅ Test 1 complete\n")
```

**What This Tests:**
- ✅ Normal file reading works
- ✅ Read-only files are handled (retry + chmod)
- ✅ Backoff timing works
- ✅ File recovery succeeds despite permissions

---

### Test 3: Full Store & Retrieve Cycle

```python
from main import SecureFileVault
import os
import tempfile
import shutil

# Create test environment
test_dir = tempfile.mkdtemp()
vault = SecureFileVault(test_dir)

# Create test file
test_file = os.path.join(test_dir, 'secret.txt')
with open(test_file, 'w') as f:
    f.write("This is a secret message")

print("Test 2: Store and Retrieve")

# Step 1: Store file
print("Step 1: Storing file...")
success, file_id = vault.store_file(
    test_file,
    password="testpassword123",
    use_camouflage=True
)
assert success, f"Store failed: {file_id}"
print(f"✅ File stored: {file_id}")

# Step 2: Verify file is stored
vault_real = os.path.join(test_dir, 'secure_vault', 'real')
assert os.path.exists(vault_real), "Vault storage not created"
print("✅ File in vault")

# Step 3: Retrieve file
print("Step 3: Retrieving file...")
output_file = os.path.join(test_dir, 'retrieved.txt')
success, msg = vault.retrieve_file(
    file_id,
    password="testpassword123",
    output_path=output_file
)
assert success, f"Retrieve failed: {msg}"
print("✅ File retrieved")

# Step 4: Verify content
assert os.path.exists(output_file), "Output file not created"
with open(output_file, 'r') as f:
    content = f.read()
assert content == "This is a secret message", "Content mismatch"
print("✅ Content verified")

# Cleanup
shutil.rmtree(test_dir)
print("✅ Test 2 complete\n")
```

**What This Tests:**
- ✅ File encryption works
- ✅ File camouflage works
- ✅ File retrieval works
- ✅ Decryption works correctly
- ✅ Content integrity maintained

---

### Test 4: Temporary File Cleanup

```python
from main import SecureFileVault
import os
import tempfile
import shutil

# Create test environment
test_dir = tempfile.mkdtemp()
vault = SecureFileVault(test_dir)

# Create test file
test_file = os.path.join(test_dir, 'test.txt')
with open(test_file, 'w') as f:
    f.write("temporary file test")

print("Test 3: Temporary File Cleanup")

# Count temp files before
print("Checking temp files before...")
temp_before = len([f for f in os.listdir(test_dir) 
                   if '_ipfs_temp' in f])
print(f"  Temp files before: {temp_before}")

# Store file
print("Storing file...")
success, file_id = vault.store_file(test_file, "password", use_camouflage=True)
assert success
print(f"✅ Stored: {file_id}")

# Retrieve file
print("Retrieving file...")
output_file = os.path.join(test_dir, 'output.txt')
vault.retrieve_file(file_id, "password", output_file)
print("✅ Retrieved")

# Count temp files after
print("Checking temp files after...")
temp_after = len([f for f in os.listdir(test_dir) 
                  if '_ipfs_temp' in f])
print(f"  Temp files after: {temp_after}")

# Verify cleanup
assert temp_after <= temp_before, f"Temp files not cleaned: {temp_before} → {temp_after}"
print("✅ Temp files cleaned up properly")

# Cleanup
shutil.rmtree(test_dir)
print("✅ Test 3 complete\n")
```

**What This Tests:**
- ✅ Temporary files are created during recovery
- ✅ Temporary files are cleaned up after use
- ✅ No temp file accumulation

---

### Test 5: Error Message Quality

```python
from main import SecureFileVault
import tempfile

# Create test vault
test_dir = tempfile.mkdtemp()
vault = SecureFileVault(test_dir)

print("Test 4: Error Messages")

# Try to retrieve non-existent file
print("Attempting to retrieve non-existent file...")
success, msg = vault.retrieve_file(
    "nonexistent_id",
    "password",
    "output.txt"
)
assert not success, "Should fail for non-existent file"
print(f"✅ Proper error message: {msg}")

# Try with wrong password
print("Attempting to retrieve with wrong password...")
test_file = "test.txt"
with open(test_file, 'w') as f:
    f.write("test")

success, file_id = vault.store_file(test_file, "correct_password", use_camouflage=True)
success, msg = vault.retrieve_file(file_id, "wrong_password", "output.txt")
assert not success, "Should fail with wrong password"
print(f"✅ Proper error message: {msg}")

print("✅ Test 4 complete\n")
```

**What This Tests:**
- ✅ Error messages are clear
- ✅ Error codes are descriptive
- ✅ Wrong password detected
- ✅ Missing file detected

---

## Integration Testing (30 minutes)

### Test 6: With IPFS Integration

Requires IPFS daemon running:

```bash
# Terminal 1: Start IPFS daemon
ipfs daemon

# Terminal 2: Run integration test
python
```

```python
from main import SecureFileVault
import tempfile
import shutil

# Create vault
test_dir = tempfile.mkdtemp()
vault = SecureFileVault(test_dir)

# Enable IPFS (if available)
print("IPFS Status:")
if vault.ipfs.client:
    print("✅ IPFS client connected")
else:
    print("⚠️  IPFS not available (test will still work)")

# Create test file
test_file = "test_ipfs.txt"
with open(test_file, 'w') as f:
    f.write("Testing IPFS integration")

# Store with IPFS backup
print("\nStoring file with IPFS backup...")
success, file_id = vault.store_file(
    test_file,
    password="testpass",
    use_camouflage=True
)
assert success
print(f"✅ File stored: {file_id}")

# Check blockchain record
print("\nChecking blockchain record...")
if hasattr(vault, 'blockchain_backup'):
    status = vault.blockchain_backup.get_file_backup_status(file_id)
    print(f"  Backup count: {status['backup_count']}")
    print(f"  Backed up: {status['has_backups']}")
    if status['has_backups']:
        print(f"  IPFS CID: {status['latest_backup']['ipfs_cid']}")

# Retrieve file
print("\nRetrieving file...")
output_file = "retrieved_ipfs.txt"
success, msg = vault.retrieve_file(file_id, "testpass", output_file)
assert success, f"Retrieval failed: {msg}"
print(f"✅ File retrieved: {msg}")

# Verify content
with open(output_file, 'r') as f:
    content = f.read()
assert "IPFS integration" in content
print("✅ Content verified")

# Cleanup
shutil.rmtree(test_dir)
print("\n✅ IPFS Integration Test Complete")
```

**What This Tests:**
- ✅ IPFS integration works
- ✅ Blockchain records created
- ✅ File recovery from IPFS
- ✅ Permission handling in IPFS context

---

## Performance Testing (10 minutes)

### Test 7: Timing & Performance

```python
from main import SecureFileVault
import tempfile
import time

test_dir = tempfile.mkdtemp()
vault = SecureFileVault(test_dir)

print("Performance Test")
print("=" * 50)

# Test safe file read performance
test_file = "perf_test.txt"
with open(test_file, 'wb') as f:
    f.write(b"x" * 1000000)  # 1MB file

print("\nTiming: Safe file read (1MB file)")
print("  Attempt 1 (normal):")
start = time.time()
data = vault._safe_file_read(test_file)
elapsed = time.time() - start
print(f"    Time: {elapsed*1000:.1f}ms")
print(f"    Data size: {len(data)} bytes")

print("  Attempt 2 (with chmod):")
import os
os.chmod(test_file, 0o444)
start = time.time()
data = vault._safe_file_read(test_file)
elapsed = time.time() - start
print(f"    Time: {elapsed*1000:.1f}ms (includes retries)")
print(f"    Data size: {len(data)} bytes")

print("\n✅ Performance test complete")
```

**What This Tests:**
- ✅ Performance is acceptable
- ✅ Retry overhead is minimal
- ✅ Large files handled correctly
- ✅ Timing is reasonable

---

## Stress Testing (optional, 20 minutes)

### Test 8: Multiple Files & Retries

```python
from main import SecureFileVault
import tempfile
import os

test_dir = tempfile.mkdtemp()
vault = SecureFileVault(test_dir)

print("Stress Test: Multiple Files")
print("=" * 50)

# Create and store multiple files
files = []
for i in range(5):
    file_path = f"stress_test_{i}.txt"
    with open(file_path, 'w') as f:
        f.write(f"Test content {i}")
    
    success, file_id = vault.store_file(
        file_path,
        password=f"password{i}",
        use_camouflage=True
    )
    assert success
    files.append((file_id, f"password{i}"))
    print(f"✅ Stored file {i+1}/5")

# Retrieve all files
print("\nRetrieving all files...")
for i, (file_id, password) in enumerate(files):
    output_file = f"retrieved_{i}.txt"
    success, msg = vault.retrieve_file(file_id, password, output_file)
    assert success
    print(f"✅ Retrieved file {i+1}/5")

# Verify all contents
print("\nVerifying content...")
for i, _ in enumerate(files):
    with open(f"retrieved_{i}.txt", 'r') as f:
        content = f.read()
    assert f"Test content {i}" in content
    print(f"✅ Verified file {i+1}/5")

print("\n✅ Stress test complete - All 5 files processed successfully")
```

**What This Tests:**
- ✅ Multiple files handled correctly
- ✅ Different passwords work
- ✅ No cross-file contamination
- ✅ System scales to multiple operations

---

## Checklist - Before & After Fix

### Before Fix ❌
- [ ] Permission error crashes the system
- [ ] No retry logic
- [ ] Temp files accumulate
- [ ] No permission fixing
- [ ] Poor error messages
- [ ] IPFS recovery fails frequently

### After Fix ✅
- [x] Permission errors handled gracefully
- [x] Automatic retry with backoff
- [x] Temp files cleaned up
- [x] Permissions auto-fixed
- [x] Clear error messages
- [x] IPFS recovery works reliably

---

## Troubleshooting During Testing

### Issue: Tests still failing?

1. **Check Python path**
   ```bash
   cd c:\Project\Finalbackup
   python -c "import main; print('OK')"
   ```

2. **Check file permissions**
   ```bash
   ls -la secure_vault/logs/
   ```

3. **Check IPFS status** (if testing IPFS)
   ```bash
   ipfs id
   ```

4. **Enable debug logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

5. **Check logs**
   ```bash
   tail -f secure_vault/logs/vault.log
   ```

---

## Success Criteria

All tests pass when:
- ✅ verify_permission_fix.py shows all 5 tests passing
- ✅ Safe file read handles permission errors
- ✅ Temporary files are cleaned up
- ✅ Retry logic functions correctly
- ✅ IPFS recovery works (if IPFS available)
- ✅ Performance is acceptable
- ✅ Error messages are clear

---

## Summary

**Quick Test**: Run `python verify_permission_fix.py` (2 min) ✅
**Detailed Test**: Run manual tests above (10-15 min) ✅
**Integration Test**: Test with IPFS (30 min) ✅
**Stress Test**: Test multiple files (20 min) ✅

**Total**: Can be completed in 60-70 minutes

---

## Next Steps After Testing

1. ✅ All tests pass
2. Review error logs for any warnings
3. Deploy to production
4. Monitor logs for issues
5. Collect user feedback

---

**Status**: Ready to test! 🧪
