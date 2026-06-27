#!/usr/bin/env python3
"""
Test suite for IPFS & Blockchain Backup System
Tests automatic backup, recovery, and integrity verification
"""

import os
import json
import hashlib
import tempfile
import shutil
import logging
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import backup system
from ipfs_blockchain_backup import (
    IPFSBackupManager,
    BlockchainBackupLedger,
    AutomaticBackupRecoverySystem,
    setup_ipfs_backup_system
)


class TestIPFSBlockchainBackup:
    """Test suite for backup system"""
    
    def __init__(self):
        """Initialize test environment"""
        self.test_dir = tempfile.mkdtemp(prefix='backup_test_')
        self.vault_path = os.path.join(self.test_dir, 'secure_vault')
        self.ledger_path = os.path.join(self.vault_path, 'logs/blockchain.json')
        
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        
        self.test_results = {
            'passed': [],
            'failed': [],
            'skipped': []
        }
    
    def cleanup(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.test_dir)
            print(f"✅ Cleaned up test directory: {self.test_dir}")
        except Exception as e:
            logging.warning(f"Cleanup warning: {e}")
    
    def create_test_file(self, content: str = "Test file content") -> str:
        """Create a temporary test file"""
        test_file = os.path.join(self.test_dir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write(content)
        return test_file
    
    def test_ipfs_manager_initialization(self):
        """Test 1: IPFS Manager Initialization"""
        print("\n[TEST 1] IPFS Manager Initialization")
        try:
            ipfs = IPFSBackupManager()
            assert ipfs is not None, "IPFS manager not initialized"
            assert hasattr(ipfs, 'backup_file'), "Missing backup_file method"
            assert hasattr(ipfs, 'recover_file'), "Missing recover_file method"
            print("✅ PASSED: IPFS manager initialized correctly")
            self.test_results['passed'].append("IPFS Manager Initialization")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("IPFS Manager Initialization", str(e)))
            return False
    
    def test_blockchain_ledger_initialization(self):
        """Test 2: Blockchain Ledger Initialization"""
        print("\n[TEST 2] Blockchain Ledger Initialization")
        try:
            blockchain = BlockchainBackupLedger(self.ledger_path)
            assert blockchain is not None, "Blockchain not initialized"
            
            # Check genesis block
            ledger = blockchain.get_backups_ledger()
            assert len(ledger) >= 1, "Genesis block not created"
            assert ledger[0]['type'] == 'GENESIS_BACKUP', "Invalid genesis block"
            
            print("✅ PASSED: Blockchain ledger initialized with genesis block")
            self.test_results['passed'].append("Blockchain Ledger Initialization")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("Blockchain Ledger Initialization", str(e)))
            return False
    
    def test_backup_record_creation(self):
        """Test 3: Backup Record Creation"""
        print("\n[TEST 3] Backup Record Creation")
        try:
            blockchain = BlockchainBackupLedger(self.ledger_path)
            
            # Create a backup record
            record = blockchain.record_backup(
                file_id='test_file_001',
                cid='QmTestCID123',
                file_hash='sha256hash123',
                is_camouflaged=True,
                file_size=1024
            )
            
            assert record, "No record returned"
            assert record['file_id'] == 'test_file_001', "File ID mismatch"
            assert record['ipfs_cid'] == 'QmTestCID123', "CID mismatch"
            assert record['is_camouflaged'] == True, "Camouflage flag mismatch"
            
            print("✅ PASSED: Backup record created successfully")
            self.test_results['passed'].append("Backup Record Creation")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("Backup Record Creation", str(e)))
            return False
    
    def test_file_backup_status(self):
        """Test 4: File Backup Status Tracking"""
        print("\n[TEST 4] File Backup Status Tracking")
        try:
            blockchain = BlockchainBackupLedger(self.ledger_path)
            
            # Add multiple backup records
            file_id = 'test_file_002'
            for i in range(3):
                blockchain.record_backup(
                    file_id=file_id,
                    cid=f'QmCID{i}',
                    file_hash=f'hash{i}',
                    is_camouflaged=True,
                    file_size=1024 * (i + 1)
                )
            
            # Get status
            status = blockchain.get_file_backup_status(file_id)
            
            assert status['has_backups'], "Backups not detected"
            assert status['backup_count'] == 3, f"Expected 3 backups, got {status['backup_count']}"
            assert status['latest_backup']['ipfs_cid'] == 'QmCID2', "Latest backup not correct"
            
            print(f"✅ PASSED: File backup status correctly tracked ({status['backup_count']} backups)")
            self.test_results['passed'].append("File Backup Status Tracking")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("File Backup Status Tracking", str(e)))
            return False
    
    def test_recovery_record_creation(self):
        """Test 5: Recovery Record Creation"""
        print("\n[TEST 5] Recovery Record Creation")
        try:
            blockchain = BlockchainBackupLedger(self.ledger_path)
            
            # First create a backup record
            file_id = 'test_file_003'
            blockchain.record_backup(
                file_id=file_id,
                cid='QmRecoveryCID',
                file_hash='recovery_hash',
                is_camouflaged=True,
                file_size=2048
            )
            
            # Then record recovery
            recovery = blockchain.record_recovery(
                file_id=file_id,
                cid='QmRecoveryCID',
                recovered_at='/path/to/recovered/file'
            )
            
            assert recovery, "No recovery record returned"
            assert recovery['type'] == 'FILE_RECOVERY', "Invalid recovery type"
            
            # Check status now includes recovery
            status = blockchain.get_file_backup_status(file_id)
            assert status['has_recovery_record'], "Recovery record not found in status"
            
            print("✅ PASSED: Recovery record created and tracked")
            self.test_results['passed'].append("Recovery Record Creation")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("Recovery Record Creation", str(e)))
            return False
    
    def test_file_hash_calculation(self):
        """Test 6: File Hash Calculation"""
        print("\n[TEST 6] File Hash Calculation")
        try:
            ipfs = IPFSBackupManager()
            
            # Create test file
            test_file = self.create_test_file("Test content for hashing")
            
            # Calculate hash
            hash1 = ipfs._calculate_hash(test_file)
            hash2 = ipfs._calculate_hash(test_file)
            
            assert hash1 == hash2, "Hash mismatch for same file"
            assert len(hash1) == 64, "Invalid SHA256 hash length"
            
            # Verify it's a valid hash
            import re
            assert re.match(r'^[a-f0-9]{64}$', hash1), "Invalid hash format"
            
            print(f"✅ PASSED: File hash calculated correctly ({hash1[:16]}...)")
            self.test_results['passed'].append("File Hash Calculation")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("File Hash Calculation", str(e)))
            return False
    
    def test_file_health_check(self):
        """Test 7: File Health Check"""
        print("\n[TEST 7] File Health Check")
        try:
            ipfs = IPFSBackupManager()
            
            file_id = 'health_check_test'
            original_hash = 'abcdef123456'
            
            # No backup history yet
            health = ipfs.check_file_health(file_id, original_hash)
            assert not health['healthy'], "File marked healthy without backup"
            assert not health['backed_up'], "File marked as backed up without history"
            
            # Add to backup history
            ipfs.backup_history[file_id] = [{
                'cid': 'QmHealthCheck',
                'timestamp': datetime.now().isoformat(),
                'size': 1024,
                'hash': original_hash,
                'backup_name': 'test.txt'
            }]
            
            # Check health again - should match
            health = ipfs.check_file_health(file_id, original_hash)
            assert health['healthy'], "File not marked healthy despite hash match"
            assert health['hash_match'], "Hash match not detected"
            
            # Check with different hash - corruption detected
            health = ipfs.check_file_health(file_id, 'different_hash')
            assert not health['healthy'], "Corrupted file marked as healthy"
            assert health['needs_recovery'], "Corruption not detected"
            
            print("✅ PASSED: File health check works correctly")
            self.test_results['passed'].append("File Health Check")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("File Health Check", str(e)))
            return False
    
    def test_backup_ledger_persistence(self):
        """Test 8: Blockchain Ledger Persistence"""
        print("\n[TEST 8] Blockchain Ledger Persistence")
        try:
            # Create and save
            blockchain1 = BlockchainBackupLedger(self.ledger_path)
            blockchain1.record_backup(
                file_id='persist_test',
                cid='QmPersist123',
                file_hash='hash_persist',
                is_camouflaged=True,
                file_size=5120
            )
            
            ledger1 = blockchain1.get_backups_ledger()
            assert len(ledger1) >= 2, "Record not saved"
            
            # Reload and verify
            blockchain2 = BlockchainBackupLedger(self.ledger_path)
            ledger2 = blockchain2.get_backups_ledger()
            
            assert len(ledger1) == len(ledger2), "Ledger not persisted correctly"
            assert ledger2[-1]['file_id'] == 'persist_test', "Data corruption after reload"
            
            print("✅ PASSED: Blockchain ledger persists correctly")
            self.test_results['passed'].append("Blockchain Ledger Persistence")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("Blockchain Ledger Persistence", str(e)))
            return False
    
    def test_backup_report_generation(self):
        """Test 9: Backup Report Generation"""
        print("\n[TEST 9] Backup Report Generation")
        try:
            ipfs = IPFSBackupManager()
            blockchain = BlockchainBackupLedger(self.ledger_path)
            recovery = AutomaticBackupRecoverySystem(
                self.vault_path, ipfs, blockchain
            )
            
            # Add some backups
            ipfs.backup_history['file_a'] = [
                {'cid': 'QmA', 'timestamp': '2025-01-12T10:00:00', 'size': 1024, 'backup_name': 'a.txt'}
            ]
            ipfs.backup_history['file_b'] = [
                {'cid': 'QmB', 'timestamp': '2025-01-12T10:05:00', 'size': 2048, 'backup_name': 'b.txt'}
            ]
            
            # Generate report
            report = recovery.generate_backup_report()
            
            assert report, "No report generated"
            assert 'IPFS BACKUPS' in report, "IPFS section missing"
            assert 'BLOCKCHAIN RECORDS' in report, "Blockchain section missing"
            assert 'file_a' in report, "File a not in report"
            assert 'file_b' in report, "File b not in report"
            
            print("✅ PASSED: Backup report generated successfully")
            self.test_results['passed'].append("Backup Report Generation")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("Backup Report Generation", str(e)))
            return False
    
    def test_camouflaged_file_tracking(self):
        """Test 10: Camouflaged File Backup Tracking"""
        print("\n[TEST 10] Camouflaged File Tracking")
        try:
            blockchain = BlockchainBackupLedger(self.ledger_path)
            
            # Simulate multiple camouflaged files
            camouflaged_files = [
                ('file_camo_1', 'kernel32.dll', True),
                ('file_camo_2', 'svchost.exe', True),
                ('file_normal', 'document.txt', False),
            ]
            
            for file_id, name, is_camo in camouflaged_files:
                blockchain.record_backup(
                    file_id=file_id,
                    cid=f'QmCamo{file_id}',
                    file_hash=f'hash_{file_id}',
                    is_camouflaged=is_camo,
                    file_size=4096
                )
            
            # Verify camouflaged files are tracked
            ledger = blockchain.get_backups_ledger()
            camo_records = [r for r in ledger if r.get('is_camouflaged')]
            
            assert len(camo_records) >= 2, "Camouflaged files not tracked"
            
            print(f"✅ PASSED: Camouflaged files tracked ({len(camo_records)} records)")
            self.test_results['passed'].append("Camouflaged File Tracking")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results['failed'].append(("Camouflaged File Tracking", str(e)))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 80)
        print("🧪 IPFS & BLOCKCHAIN BACKUP SYSTEM - TEST SUITE")
        print("=" * 80)
        
        tests = [
            self.test_ipfs_manager_initialization,
            self.test_blockchain_ledger_initialization,
            self.test_backup_record_creation,
            self.test_file_backup_status,
            self.test_recovery_record_creation,
            self.test_file_hash_calculation,
            self.test_file_health_check,
            self.test_backup_ledger_persistence,
            self.test_backup_report_generation,
            self.test_camouflaged_file_tracking,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logging.error(f"Test exception: {e}")
        
        # Summary
        self._print_summary()
    
    def _print_summary(self):
        """Print test summary"""
        total = len(self.test_results['passed']) + len(self.test_results['failed'])
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed:  {len(self.test_results['passed'])}/{total}")
        print(f"❌ Failed:  {len(self.test_results['failed'])}/{total}")
        print(f"⏭️  Skipped: {len(self.test_results['skipped'])}/{total}")
        
        if self.test_results['failed']:
            print("\n❌ FAILED TESTS:")
            for test_name, error in self.test_results['failed']:
                print(f"  • {test_name}: {error}")
        
        print("\n" + "=" * 80)
        
        if not self.test_results['failed']:
            print("✅ ALL TESTS PASSED!")
        else:
            print(f"❌ {len(self.test_results['failed'])} TEST(S) FAILED")
        
        print("=" * 80 + "\n")


def main():
    """Main test runner"""
    tester = TestIPFSBlockchainBackup()
    
    try:
        tester.run_all_tests()
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
