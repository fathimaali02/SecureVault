#!/usr/bin/env python3
"""
Diagnostic test: Perform enrollment + login flow to verify keystroke confidence.
This script simulates user typing and logs detailed metrics.
"""
import os
import sys
import json
import time
import shutil
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add workspace to path
sys.path.insert(0, os.path.dirname(__file__))

from main import SecureFileVault, KeystrokeAnalyzer, BehavioralAuthenticator

def simulate_typing(analyzer, text: str, wpm: int = 60):
    """
    Simulate typing with realistic timing.
    wpm = words per minute (default 60 WPM)
    """
    # Convert WPM to milliseconds per keystroke
    # 60 WPM ≈ 300 chars/min ≈ 5 chars/sec ≈ 200ms per char
    ms_per_char = (60000 / (wpm * 5))
    dwell_time = ms_per_char / 2  # Hold key for half the interval
    flight_time = ms_per_char / 2  # Release and move to next key
    
    print(f"\n[SIMULATE] Typing: '{text}' at {wpm} WPM ({ms_per_char:.0f}ms per char)")
    
    for i, char in enumerate(text):
        # Press
        analyzer.record_keystroke(char, 'press', f'key_{i}')
        time.sleep(dwell_time / 1000.0)
        
        # Release
        analyzer.record_keystroke(char, 'release', f'key_{i}')
        
        # Flight time to next key (except after last key)
        if i < len(text) - 1:
            time.sleep(flight_time / 1000.0)
    
    print(f"[SIMULATE] Typing simulation complete")

def test_keystroke_flow():
    """Run enrollment + login test"""
    
    # Clean up any previous test vault
    test_vault_path = "secure_vault_test_keystroke"
    if os.path.exists(test_vault_path):
        print(f"\n[TEST] Removing old test vault: {test_vault_path}")
        shutil.rmtree(test_vault_path)
    
    # Initialize fresh vault
    print(f"\n[TEST] Initializing test vault: {test_vault_path}")
    vault = SecureFileVault(test_vault_path)
    
    # === ENROLLMENT PHASE ===
    print("\n" + "="*80)
    print("ENROLLMENT PHASE: Collecting 3 keystroke samples")
    print("="*80)
    
    master_password = "TestPassword123"
    enrollment_samples = []
    
    for sample_num in range(1, 4):
        print(f"\n[ENROLLMENT] Sample {sample_num}/3")
        vault.keystroke_analyzer.start_recording()
        
        # Simulate typing with slight variation between samples
        wpm = 60 + (sample_num - 1) * 5  # Vary speed: 60, 65, 70 WPM
        simulate_typing(vault.keystroke_analyzer, master_password, wpm=wpm)
        
        # Collect metrics
        metrics = vault.keystroke_analyzer.get_typing_metrics()
        enrollment_samples.append(metrics)
        
        print(f"[ENROLLMENT] Metrics collected:")
        print(f"  - Dwell Time: {metrics.get('average_dwell_time', 0):.4f}s")
        print(f"  - Flight Time: {metrics.get('average_flight_time', 0):.4f}s")
        print(f"  - Typing Speed: {metrics.get('typing_speed', 0):.4f} chars/sec")
        print(f"  - Keystroke Count: {metrics.get('keystroke_count', 0)}")
        
        vault.keystroke_analyzer.reset()
    
    # === SAVE MASTER PASSWORD & PROFILE ===
    print(f"\n[TEST] Saving master password...")
    vault.set_master_password(master_password)
    
    print(f"[TEST] Enrolling biometric profile with {len(enrollment_samples)} samples...")
    enrolled = vault.authenticator.enroll_user('master', enrollment_samples)
    if enrolled:
        profile = vault.authenticator.profiles.get('master', {})
        print(f"[TEST] Profile enrolled successfully!")
        print(f"  - Mean: {profile.get('mean', [])}")
        print(f"  - Std: {profile.get('std', [])}")
    else:
        print(f"[TEST] ERROR: Failed to enroll!")
        return False
    
    # === LOGIN PHASE (IDENTICAL TYPING) ===
    print("\n" + "="*80)
    print("LOGIN PHASE 1: Identical typing (same speed as first enrollment sample)")
    print("="*80)
    
    vault.keystroke_analyzer.start_recording()
    simulate_typing(vault.keystroke_analyzer, master_password, wpm=60)
    
    login_metrics = vault.keystroke_analyzer.get_typing_metrics()
    print(f"\n[LOGIN] Login Metrics:")
    print(f"  - Dwell Time: {login_metrics.get('average_dwell_time', 0):.4f}s")
    print(f"  - Flight Time: {login_metrics.get('average_flight_time', 0):.4f}s")
    print(f"  - Typing Speed: {login_metrics.get('typing_speed', 0):.4f} chars/sec")
    print(f"  - Keystroke Count: {login_metrics.get('keystroke_count', 0)}")
    
    # Verify password
    pwd_ok = vault.verify_master_password(master_password)
    print(f"\n[LOGIN] Master password verified: {pwd_ok}")
    
    # Authenticate keystroke
    keystroke_ok, confidence = vault.authenticator.authenticate('master', login_metrics)
    print(f"[LOGIN] Keystroke authentication: OK={keystroke_ok}, Confidence={confidence:.4f}")
    
    if keystroke_ok and pwd_ok:
        print(f"\n[TEST] LOGIN SUCCESSFUL (confidence > threshold)")
    else:
        print(f"\n[TEST] LOGIN FAILED")
        print(f"  - Password OK: {pwd_ok}")
        print(f"  - Keystroke OK: {keystroke_ok} (confidence={confidence:.4f})")
        print(f"  - Threshold: {vault.keystroke_analyzer.required_keystrokes}")
    
    # === LOGIN PHASE (DIFFERENT TYPING SPEED) ===
    print("\n" + "="*80)
    print("LOGIN PHASE 2: Different typing speed (75 WPM - faster)")
    print("="*80)
    
    vault.keystroke_analyzer.reset()
    vault.keystroke_analyzer.start_recording()
    simulate_typing(vault.keystroke_analyzer, master_password, wpm=75)
    
    login_metrics_fast = vault.keystroke_analyzer.get_typing_metrics()
    print(f"\n[LOGIN-FAST] Metrics:")
    print(f"  - Dwell Time: {login_metrics_fast.get('average_dwell_time', 0):.4f}s")
    print(f"  - Flight Time: {login_metrics_fast.get('average_flight_time', 0):.4f}s")
    print(f"  - Typing Speed: {login_metrics_fast.get('typing_speed', 0):.4f} chars/sec")
    
    keystroke_ok_fast, confidence_fast = vault.authenticator.authenticate('master', login_metrics_fast)
    print(f"[LOGIN-FAST] Keystroke authentication: OK={keystroke_ok_fast}, Confidence={confidence_fast:.4f}")
    
    # === SUMMARY ===
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Enrollment samples: {len(enrollment_samples)}")
    print(f"Login (identical speed): confidence={confidence:.4f}, OK={keystroke_ok}")
    print(f"Login (faster speed): confidence={confidence_fast:.4f}, OK={keystroke_ok_fast}")
    print(f"\nThreshold: {vault.keystroke_analyzer.required_keystrokes}")
    print(f"✓ Test vault created at: {test_vault_path}")
    
    return keystroke_ok and pwd_ok

if __name__ == '__main__':
    success = test_keystroke_flow()
    sys.exit(0 if success else 1)
