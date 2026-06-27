#!/usr/bin/env python3
"""
Quick Setup & Test Script for SecureVault Pro
Validates keystroke analyzer and encryption before running the full app.
"""

import sys
import os
import time

# Test 1: Keystroke Analyzer
def test_keystroke_analyzer():
    """Test keystroke recording and metric computation"""
    print("\n" + "="*60)
    print("TEST 1: Keystroke Analyzer")
    print("="*60)
    
    # Import here to avoid full dependency checks
    sys.path.insert(0, os.path.dirname(__file__))
    from main import KeystrokeAnalyzer
    
    ka = KeystrokeAnalyzer()
    ka.start_recording()
    
    # Simulate typing "password" with realistic timings
    events = [
        ('p', 'press'),   (0.08, None),  ('p', 'release'),
        ('a', 'press'),   (0.12, None),  ('a', 'release'),
        ('s', 'press'),   (0.09, None),  ('s', 'release'),
        ('s', 'press'),   (0.10, None),  ('s', 'release'),
        ('w', 'press'),   (0.11, None),  ('w', 'release'),
        ('o', 'press'),   (0.07, None),  ('o', 'release'),
        ('r', 'press'),   (0.09, None),  ('r', 'release'),
        ('d', 'press'),   (0.08, None),  ('d', 'release'),
    ]
    
    current_time = time.time()
    for item, event_type in events:
        if isinstance(item, float):
            time.sleep(item)
        else:
            ka.record_keystroke(item, event_type, item)
    
    metrics = ka.get_typing_metrics()
    
    print(f"✓ Password recorded: '{ka.current_password}'")
    print(f"✓ Total keystrokes: {metrics['keystroke_count']}")
    print(f"✓ Total time: {metrics['total_time']:.2f}s")
    print(f"✓ Average dwell time: {metrics['average_dwell_time']:.3f}s")
    print(f"✓ Average flight time: {metrics['average_flight_time']:.3f}s")
    print(f"✓ Typing speed: {metrics['typing_speed']:.2f} chars/sec")
    print(f"✓ Rhythm consistency: {metrics['rhythm_consistency']:.3f}")
    
    if metrics['keystroke_count'] >= 8:
        print("\n✅ TEST PASSED: Keystroke analyzer working correctly!")
        return True
    else:
        print("\n❌ TEST FAILED: Not enough keystrokes recorded")
        return False


# Test 2: Encryption
def test_encryption():
    """Test AES-256 encryption/decryption"""
    print("\n" + "="*60)
    print("TEST 2: AES-256 Encryption")
    print("="*60)
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from main import EncryptionManager
        
        # Test data
        plaintext = b"This is a secret message for testing encryption"
        password = "SuperSecurePassword123!"
        
        # Encrypt
        encrypted, salt = EncryptionManager.encrypt(plaintext, password)
        print(f"✓ Encrypted {len(plaintext)} bytes")
        print(f"✓ Ciphertext size: {len(encrypted)} bytes")
        print(f"✓ Salt: {salt.hex()[:32]}...")
        
        # Decrypt
        decrypted = EncryptionManager.decrypt(encrypted, salt, password)
        
        if decrypted == plaintext:
            print(f"✓ Decrypted successfully")
            print(f"\n✅ TEST PASSED: Encryption working correctly!")
            return True
        else:
            print(f"\n❌ TEST FAILED: Decryption mismatch")
            return False
    
    except ImportError as e:
        print(f"⚠️  SKIPPED: cryptography not installed ({e})")
        return None
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False


# Test 3: Dependencies
def test_dependencies():
    """Check all required dependencies"""
    print("\n" + "="*60)
    print("TEST 3: Dependencies Check")
    print("="*60)
    
    dependencies = {
        'cryptography': 'Encryption',
        'PIL': 'Image/Steganography',
        'sklearn': 'ML Authentication',
        'numpy': 'Numerical Computing',
        'tkinter': 'GUI Framework',
    }
    
    results = {}
    for module, purpose in dependencies.items():
        try:
            if module == 'PIL':
                from PIL import Image
            elif module == 'sklearn':
                from sklearn.preprocessing import StandardScaler
            elif module == 'numpy':
                import numpy
            elif module == 'tkinter':
                import tkinter
            else:
                __import__(module)
            
            print(f"✓ {module:15} - {purpose}")
            results[module] = True
        except ImportError:
            print(f"⚠️  {module:15} - {purpose} (optional)")
            results[module] = False
    
    if results.get('cryptography') and results.get('tkinter'):
        print("\n✅ All critical dependencies available!")
        return True
    else:
        print("\n❌ Missing critical dependencies (cryptography, tkinter)")
        return False


# Test 4: File System
def test_filesystem():
    """Check vault directory structure"""
    print("\n" + "="*60)
    print("TEST 4: File System Check")
    print("="*60)
    
    vault_path = "secure_vault"
    
    try:
        os.makedirs(vault_path, exist_ok=True)
        os.makedirs(os.path.join(vault_path, 'real'), exist_ok=True)
        os.makedirs(os.path.join(vault_path, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(vault_path, 'metadata'), exist_ok=True)
        os.makedirs(os.path.join(vault_path, 'camouflaged'), exist_ok=True)
        
        print(f"✓ Created vault structure in '{vault_path}'")
        
        # Check write permissions
        test_file = os.path.join(vault_path, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        print(f"✓ Write permissions verified")
        print("\n✅ File system ready!")
        return True
    
    except Exception as e:
        print(f"❌ File system error: {e}")
        return False


# Main test runner
def main():
    """Run all tests"""
    print("\n" + "🔒 SecureVault Pro - Setup & Test Suite")
    print("="*60)
    
    results = {}
    
    # Run all tests
    results['filesystem'] = test_filesystem()
    results['dependencies'] = test_dependencies()
    results['encryption'] = test_encryption()
    results['keystroke'] = test_keystroke_analyzer()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)
    
    print(f"✅ Passed:  {passed}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"❌ Failed:  {failed}")
    
    if failed == 0:
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED! Ready to launch SecureVault Pro")
        print("="*60)
        print("\nNext step: python main.py")
        return 0
    else:
        print("\n" + "="*60)
        print("⚠️  Some tests failed. Install dependencies and try again:")
        print("="*60)
        print("\npip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
