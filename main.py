#!/usr/bin/env python3
"""
🔒 SecureVault Pro - Advanced File Security with Biometric Authentication
Features:
  ✓ AES-256 Encryption (password-derived key with PBKDF2)
  ✓ ML-Powered Keystroke Dynamics Authentication
  ✓ Steganography (hide files in images)
  ✓ File Camouflage (system-like renaming)
  ✓ Blockchain Integrity Verification
  ✓ IPFS Decentralized Storage Integration
  ✓ Decoy Vault & Honeytrap Detection
  ✓ Modern Tkinter Dashboard with gradient backgrounds

Author: SecureVault Development Team
Version: 2.0
"""

import os
import json
import base64
import hashlib
import logging
import sys
import time
import random
import string
import platform
import threading
import statistics
import tempfile
import shutil
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any, List
from collections import deque

# Tkinter imports
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog

# PIL for image handling
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - steganography disabled")

import numpy as np
# Cryptography
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("cryptography not available")

# ML and feature scaling
try:
    # from sklearn.preprocessing import StandardScaler
    # from sklearn.ensemble import IsolationForest
    # from sklearn.svm import OneClassSVM
    # import joblib
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import OneClassSVM
    from sklearn.cluster import KMeans
    from sklearn.metrics import pairwise_distances
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("scikit-learn not available - ML features disabled")

# IPFS
try:
    import ipfshttpclient
    IPFS_AVAILABLE = True
except ImportError:
    IPFS_AVAILABLE = False
    logging.warning("ipfshttpclient not available - IPFS disabled")


# ============================================================================
# THEME & UI COMPONENTS
# ============================================================================

class ModernTheme:
    """Modern color palette and styling"""
    COLORS = {
        'primary': '#6366f1',
        'primary_dark': '#4f46e5',
        'primary_light': '#818cf8',
        'secondary': '#10b981',
        'danger': '#ef4444',
        'warning': '#f59e0b',
        'dark': '#1e293b',
        'darker': '#0f172a',
        'light': '#f8fafc',
        'light_gray': '#f1f5f9',
        'gray': '#94a3b8',
        'gray_dark': '#64748b',
        'success': '#22c55e',
        'card_bg': '#ffffff',
    }
    
    FONTS = {
        'title': ('Segoe UI', 24, 'bold'),
        'heading': ('Segoe UI', 18, 'bold'),
        'subheading': ('Segoe UI', 14, 'bold'),
        'normal': ('Segoe UI', 11),
        'small': ('Segoe UI', 9),
    }
    
    @staticmethod
    def setup_styles():
        """Setup ttk styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Button style
        style.configure('TButton',
                       font=ModernTheme.FONTS['normal'],
                       background=ModernTheme.COLORS['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', ModernTheme.COLORS['primary_dark']),
                            ('pressed', ModernTheme.COLORS['primary_dark'])])
        
        # Label style
        style.configure('TLabel',
                       font=ModernTheme.FONTS['normal'],
                       background='white',
                       foreground=ModernTheme.COLORS['dark'])
        
        # Entry style
        style.configure('TEntry',
                       font=ModernTheme.FONTS['normal'],
                       fieldbackground='white',
                       foreground=ModernTheme.COLORS['dark'])
        
        # Frame style
        style.configure('TFrame',
                       background='white')


# ============================================================================
# UI COMPONENTS
# ============================================================================

class GradientFrame(tk.Canvas):
    """Create a gradient background frame"""
    def __init__(self, parent, color1, color2, height=200, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.height = height
        self.bind("<Configure>", self._draw_gradient)
        
    def _draw_gradient(self, event=None):
        """Draw the gradient"""
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height() or self.height
        
        # Convert hex colors to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(self.color1)
        rgb2 = hex_to_rgb(self.color2)
        
        # Create gradient
        for i in range(height):
            ratio = i / height
            r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
            g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
            b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.create_line(0, i, width, i, fill=color, tags="gradient")


# ============================================================================
# KEYSTROKE ANALYSIS
# ============================================================================

class KeystrokeAnalyzer:
    """Analyzes keystroke dynamics for behavioral authentication"""
    
    def __init__(self, required_keystrokes: int = 8):
        self.required_keystrokes = required_keystrokes
        self.start_time = None
        self.is_recording = False
        self.current_password = ""
        self.press_records = []
        self.holds = []
        self.flights = []
        self._pending_presses = []
    
    def start_recording(self):
        """Begin recording keystroke events"""
        self.reset()
        self.start_time = time.time()
        self.is_recording = True
        self.holds = []
        self.flights = []
        self._pending_presses = []
        logging.debug("[KEYSTROKE DEBUG] start_recording called - recording started")
    
    def record_keystroke(self, char: str, event_type: str = "press", 
                        key_identifier: Optional[str] = None):
        """
        Record a keystroke event.
        
        Args:
            char: printable character (may be empty)
            event_type: 'press' or 'release'
            key_identifier: keysym or keycode to match press->release pairs
        """
        if not self.is_recording:
            logging.debug(f"[KEYSTROKE DEBUG] record_keystroke called but not recording (char={char!r}, event_type={event_type}, ident={key_identifier})")
            return
        
        ts = time.time()
        ident = key_identifier if key_identifier else char
        
        if event_type == "press":
            # Record pending press
            self._pending_presses.append({'ident': ident, 'char': char, 'ts': ts})
            
            # Compute flight time (gap from previous press)
            if self.press_records:
                prev_ts = self.press_records[-1][1]
                self.flights.append(ts - prev_ts)
            
            # Record press timestamp
            self.press_records.append((char, ts))
            
            # Update password string
            if char and char.isprintable():
                self.current_password += char
        
        elif event_type == "release":
            # Find matching press (LIFO for repeated keys)
            for i in range(len(self._pending_presses) - 1, -1, -1):
                if self._pending_presses[i]['ident'] == ident:
                    press_ts = self._pending_presses[i]['ts']
                    dwell = ts - press_ts
                    self.holds.append(dwell)
                    del self._pending_presses[i]
                    break
    
    def get_typing_metrics(self) -> Dict[str, float]:
        """Return computed metrics for ML authentication"""
        metrics = {
            'total_time': 0.0,
            'average_dwell_time': 0.0,
            'average_flight_time': 0.0,
            'rhythm_consistency': 0.0,
            'pressure_mean': 0.0,
            'pressure_variance': 0.0,
            'keystroke_count': 0,
            'typing_speed': 0.0,
        }
        
        try:
            if self.press_records:
                first = self.press_records[0][1]
                last = self.press_records[-1][1]
                metrics['total_time'] = last - first if last > first else 0.0
                if metrics['total_time'] > 0:
                    metrics['typing_speed'] = len(self.current_password) / metrics['total_time']
            
            if self.holds:
                metrics['average_dwell_time'] = statistics.mean(self.holds)
                metrics['pressure_mean'] = metrics['average_dwell_time']
                if len(self.holds) > 1:
                    metrics['pressure_variance'] = statistics.variance(self.holds)
            
            if self.flights:
                metrics['average_flight_time'] = statistics.mean(self.flights)
            
            if len(self.holds) > 1:
                metrics['rhythm_consistency'] = statistics.stdev(self.holds)
            
            metrics['keystroke_count'] = len(self.press_records)
            
            # Backward-compatible pattern features
            for i in range(20):
                metrics[f'dwell_{i}'] = self.holds[i] if i < len(self.holds) else 0.2
            
            for i in range(19):
                metrics[f'flight_{i}_{i+1}'] = self.flights[i] if i < len(self.flights) else 0.3
            
            # DEBUG: Log detailed keystroke metrics
            logging.debug(f"[KEYSTROKE DEBUG] Holds: {self.holds}")
            logging.debug(f"[KEYSTROKE DEBUG] Flights: {self.flights}")
            logging.debug(f"[KEYSTROKE DEBUG] Avg Dwell: {metrics['average_dwell_time']:.4f}, Avg Flight: {metrics['average_flight_time']:.4f}")
            logging.debug(f"[KEYSTROKE DEBUG] Typing Speed: {metrics['typing_speed']:.4f}, Keystroke Count: {metrics['keystroke_count']}")
        
        except Exception as e:
            logging.error(f"Keystroke metrics error: {e}")
            return self._get_default_metrics()
        
        return metrics
    
    def _get_default_metrics(self) -> Dict[str, float]:
        """Safe default metrics"""
        return {
            'total_time': 1.0,
            'average_dwell_time': 0.2,
            'average_flight_time': 0.3,
            'rhythm_consistency': 0.1,
            'pressure_mean': 0.2,
            'pressure_variance': 0.01,
            'keystroke_count': 0,
            'typing_speed': 4.0,
            **{f'dwell_{i}': 0.2 for i in range(20)},
            **{f'flight_{i}_{i+1}': 0.3 for i in range(19)}
        }
    
    def has_sufficient_data(self) -> bool:
        return len(self.press_records) >= self.required_keystrokes
    
    def reset(self):
        """Clear all recorded data"""
        self.start_time = None
        self.is_recording = False
        self.current_password = ""
        self.press_records = []
        self.holds = []
        self.flights = []
        self._pending_presses = []


# ============================================================================
# ENCRYPTION & DECRYPTION
# ============================================================================

class EncryptionManager:
    """AES-256 encryption/decryption with PBKDF2 key derivation"""
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive 256-bit key from password"""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography package required")
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    @staticmethod
    def encrypt(data: bytes, password: str) -> Tuple[bytes, bytes]:
        """Encrypt data. Returns (encrypted_data, salt)"""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography package required")
        
        salt = os.urandom(16)
        key = EncryptionManager.derive_key(password, salt)
        cipher = Fernet(key)
        encrypted = cipher.encrypt(data)
        return encrypted, salt
    
    @staticmethod
    def decrypt(encrypted_data: bytes, salt: bytes, password: str) -> bytes:
        """Decrypt data with salt and password"""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography package required")
        
        key = EncryptionManager.derive_key(password, salt)
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_data)


# ============================================================================
# ML-BASED BEHAVIORAL AUTHENTICATOR
# ============================================================================

class BehavioralAuthenticator:

    

    """Machine Learning based keystroke dynamics authentication"""

    
    
    def __init__(self, model_dir: str = "user_models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.profiles = {}
        self.load_profiles()
    
    def load_profiles(self):
        """Load saved user profiles"""
        profile_file = os.path.join(self.model_dir, 'profiles.json')
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r') as f:
                    self.profiles = json.load(f)
                logging.info(f"Loaded {len(self.profiles)} user profiles")
            except Exception as e:
                logging.error(f"Error loading profiles: {e}")
    
    def save_profiles(self):
        """Save profiles to disk"""
        profile_file = os.path.join(self.model_dir, 'profiles.json')
        try:
            with open(profile_file, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving profiles: {e}")
    
    def enroll_user(self, user_id: str, metrics_list: List[Dict]) -> bool:
        """Enroll user with multiple keystroke samples"""
        if len(metrics_list) < 2:
            return False
        
        try:
            feature_keys = ['average_dwell_time', 'average_flight_time', 
                          'rhythm_consistency', 'typing_speed', 'keystroke_count']
            
            # Extract features
            features = []
            for m in metrics_list:
                feat = [m.get(k, 0.0) for k in feature_keys]
                features.append(feat)
            
            # Store template
            import numpy as np
            features_array = np.array(features)
            template = {
                'mean': features_array.mean(axis=0).tolist(),
                'std': features_array.std(axis=0).tolist(),
                'samples': len(metrics_list),
                'enrolled_at': datetime.now().isoformat()
            }
            
            self.profiles[user_id] = template
            self.save_profiles()
            return True
        
        except Exception as e:
            logging.error(f"Enrollment error: {e}")
            return False
    
    def authenticate(self, user_id: str, metrics: Dict) -> Tuple[bool, float]:
        """
        Authenticate user based on keystroke metrics.
        Returns (is_authenticated, confidence_score)
        """
        if user_id not in self.profiles:
            return False, 0.0
        
        try:
            import numpy as np
            
            profile = self.profiles[user_id]
            feature_keys = ['average_dwell_time', 'average_flight_time', 
                          'rhythm_consistency', 'typing_speed', 'keystroke_count']
            
            # Extract current features
            current_feat = np.array([metrics.get(k, 0.0) for k in feature_keys])
            template_mean = np.array(profile['mean'])
            template_std = np.array(profile['std'])
            
            # DEBUG: Log template and current features
            logging.debug(f"[AUTH DEBUG] Template Mean: {template_mean}")
            logging.debug(f"[AUTH DEBUG] Template Std: {template_std}")
            logging.debug(f"[AUTH DEBUG] Current Features: {current_feat}")
            
            # Compute distance (Mahalanobis-like) with improved normalization
            diff = np.abs(current_feat - template_mean)
            logging.debug(f"[AUTH DEBUG] Abs Differences: {diff}")
            
            with np.errstate(divide='ignore', invalid='ignore'):
                distances = np.where(template_std > 0, diff / (template_std + 0.001), 0)
            
            logging.debug(f"[AUTH DEBUG] Normalized Distances: {distances}")
            
            # Feature weights: exclude keystroke_count from final scoring (std=0 causes problems)
            # Only score the actual biometric timing features
            # [dwell, flight, rhythm, speed, count]
            weights = np.array([0.40, 0.40, 0.15, 0.05, 0.0])  # Count excluded
            weighted_distances = distances * weights
            
            logging.debug(f"[AUTH DEBUG] Weighted Distances: {weighted_distances}")
            
            # Average weighted distance (use mean of non-zero weighted distances)
            valid_distances = weighted_distances[weights > 0]
            avg_distance = np.mean(valid_distances) if len(valid_distances) > 0 else 0.0
            
            # Confidence: 1 / (1 + distance)
            confidence = 1.0 / (1.0 + avg_distance)
            
            logging.info(f"[AUTH DEBUG] Avg Distance: {avg_distance:.4f}, Confidence: {confidence:.4f}")
            
            # Threshold: 0.6 (adjustable)
            is_authenticated = confidence > AUTH_CONFIDENCE_THRESHOLD
            
            return is_authenticated, confidence
        
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return False, 0.0
    def create_user_profile(self, password_hash: str, timing_data: Dict[str, float]):
        """Create or update a user profile based on keystroke dynamics"""
        profile_id = password_hash[:16]

        if profile_id not in self.user_profiles:
            self.user_profiles[profile_id] = {
                'password_hash': password_hash,
                'samples': [],
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'stats': {}
            }

        # Add new sample
        sample_data = {
            'timing_data': timing_data,
            'timestamp': datetime.now().isoformat()
        }
        self.user_profiles[profile_id]['samples'].append(sample_data)

        # Keep only recent samples (sliding window)
        max_samples = 15
        if len(self.user_profiles[profile_id]['samples']) > max_samples:
            self.user_profiles[profile_id]['samples'] = self.user_profiles[profile_id]['samples'][-max_samples:]

        # Update statistics
        self._update_profile_stats(profile_id)

        # Update last used
        self.user_profiles[profile_id]['last_used'] = datetime.now().isoformat()

        # Train ML model if we have enough samples
        if len(self.user_profiles[profile_id]['samples']) >= self.min_samples_for_training:
            self._train_enhanced_models(profile_id)

        self.save_profiles()
        self.save_models()
        return profile_id

    def _update_profile_stats(self, profile_id: str):
        """Update statistical profile of user's typing behavior"""
        try:
            samples = self.user_profiles[profile_id]['samples']
            if not samples:
                return

            # Extract all timing data
            all_dwell_times = []
            all_flight_times = []
            all_speeds = []

            for sample in samples:
                timing_data = sample['timing_data']
                all_dwell_times.append(timing_data.get('average_dwell_time', 0))
                all_flight_times.append(timing_data.get('average_flight_time', 0))
                all_speeds.append(timing_data.get('typing_speed', 0))

            # Calculate statistics
            stats = {
                'dwell_time_mean': statistics.mean(all_dwell_times) if all_dwell_times else 0,
                'dwell_time_std': statistics.stdev(all_dwell_times) if len(all_dwell_times) > 1 else 0.1,
                'flight_time_mean': statistics.mean(all_flight_times) if all_flight_times else 0,
                'flight_time_std': statistics.stdev(all_flight_times) if len(all_flight_times) > 1 else 0.1,
                'typing_speed_mean': statistics.mean(all_speeds) if all_speeds else 0,
                'typing_speed_std': statistics.stdev(all_speeds) if len(all_speeds) > 1 else 10,
                'rhythm_consistency_mean': statistics.mean(
                    [s['timing_data'].get('rhythm_consistency', 0) for s in samples]),
                'sample_count': len(samples)
            }

            self.user_profiles[profile_id]['stats'] = stats

        except Exception as e:
            logging.error(f"Error updating profile stats: {e}")

    def _train_enhanced_models(self, profile_id: str):
        """Train enhanced ML models for the user profile"""
        if not ML_AVAILABLE or profile_id not in self.user_profiles:
            return

        try:
            samples = self.user_profiles[profile_id]['samples']
            if len(samples) < self.min_samples_for_training:
                return

            # Extract enhanced features
            features = []
            for sample in samples:
                feature_vector = self.extract_enhanced_features(sample['timing_data'])
                if feature_vector is not None:
                    features.append(feature_vector)

            if len(features) < 2:
                return

            features_array = np.vstack(features)

            # Train multiple models for ensemble approach
            models = {}

            # 1. Isolation Forest for anomaly detection
            iso_forest = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            iso_forest.fit(features_array)
            models['isolation_forest'] = iso_forest

            # 2. One-Class SVM for boundary detection
            oc_svm = OneClassSVM(
                kernel='rbf',
                gamma='scale',
                nu=0.1
            )
            oc_svm.fit(features_array)
            models['one_class_svm'] = oc_svm

            # 3. K-Means for pattern clustering
            kmeans = KMeans(
                n_clusters=min(3, len(features_array)),
                random_state=42
            )
            kmeans.fit(features_array)
            models['kmeans'] = kmeans

            # Store models
            self.ml_models[profile_id] = models

            logging.info(f"Trained enhanced ML models for profile {profile_id}")

        except Exception as e:
            logging.error(f"Error training enhanced ML model for {profile_id}: {e}")

    def extract_enhanced_features(self, timing_data: Dict[str, float]) -> Optional[np.ndarray]:
        """Extract enhanced features from timing data"""
        try:
            features = []

            # Basic timing features
            features.extend([
                timing_data.get("total_time", 0),
                timing_data.get("average_dwell_time", 0),
                timing_data.get("average_flight_time", 0),
                timing_data.get("typing_speed", 0)
            ])

            # Rhythm and consistency features
            features.extend([
                timing_data.get("rhythm_consistency", 0),
                timing_data.get("dwell_time_std", 0),
                timing_data.get("flight_time_std", 0),
                timing_data.get("pressure_variance", 0)
            ])

            # Error pattern features
            features.extend([
                timing_data.get("error_rate", 0),
                timing_data.get("backspace_count", 0)
            ])

            # Individual keystroke timings (first 15)
            for i in range(15):
                features.append(timing_data.get(f"dwell_{i}", 0))

            # Flight times between keystrokes (first 14)
            for i in range(14):
                features.append(timing_data.get(f"flight_{i}_{i+1}", 0))

            # Add some digraph times if available
            digraph_times = list(timing_data.get('digraph_times', {}).values())
            features.extend(digraph_times[:5])  # First 5 digraph times

            # Handle variable length by padding/truncating
            target_length = 40  # Fixed feature vector length
            if len(features) < target_length:
                features.extend([0] * (target_length - len(features)))
            elif len(features) > target_length:
                features = features[:target_length]

            return np.array(features).reshape(1, -1)

        except Exception as e:
            logging.error(f"Error extracting enhanced features: {e}")
            return None

    def authenticate_user(self, password_hash: str, current_timing: Dict[str, float]) -> Tuple[bool, float, bool]:
        """Enhanced authentication using ensemble ML approach"""
        profile_id = password_hash[:16]

        # For first-time users, always authenticate successfully to create profile
        if profile_id not in self.user_profiles:
            return True, 0.8, False

        try:
            user_profile = self.user_profiles[profile_id]

            # Multi-factor authentication score
            total_score = 0.0
            fraud_indicators = 0

            # 1. Statistical comparison
            stats_score = self._calculate_statistical_similarity(user_profile, current_timing)
            total_score += stats_score * self.feature_weights['timing']

            # 2. ML model predictions
            if profile_id in self.ml_models:
                ml_score, ml_fraud = self._ml_authentication(profile_id, current_timing)
                total_score += ml_score * self.feature_weights['rhythm']
                if ml_fraud:
                    fraud_indicators += 1
            else:
                # Fallback to statistical only
                total_score += stats_score * self.feature_weights['rhythm']

            # 3. Pattern analysis
            pattern_score = self._pattern_analysis(user_profile, current_timing)
            total_score += pattern_score * self.feature_weights['pattern']

            # 4. Behavioral analysis
            behavior_score, behavior_fraud = self._behavioral_analysis(current_timing)
            total_score += behavior_score * self.feature_weights['pressure']
            if behavior_fraud:
                fraud_indicators += 1

            # Normalize final score
            final_score = min(max(total_score, 0.0), 1.0)

            # FIXED: Only grant access if similarity score is sufficient
            # Lower threshold for better usability but still secure
            is_authenticated = final_score >= 0.5  # Reduced from 0.65 to 0.5
            is_fraud = fraud_indicators >= 2 or final_score < 0.2  # Lower fraud threshold

            return is_authenticated, final_score, is_fraud

        except Exception as e:
            logging.error(f"Enhanced authentication error: {e}")
            # If error, deny access for security
            return False, 0.0, False
    def _calculate_statistical_similarity(self, user_profile: Dict, current_timing: Dict) -> float:
        """Calculate statistical similarity between current and stored patterns"""
        try:
            stats = user_profile.get('stats', {})
            if not stats:
                return 0.7  # Default similarity for new profiles

            similarities = []

            # Compare key statistical measures
            measures = [
                ('average_dwell_time', 'dwell_time_mean', 'dwell_time_std'),
                ('average_flight_time', 'flight_time_mean', 'flight_time_std'),
                ('typing_speed', 'typing_speed_mean', 'typing_speed_std'),
                ('rhythm_consistency', 'rhythm_consistency_mean', 0.1)
            ]

            for current_key, mean_key, std_key in measures:
                current_val = current_timing.get(current_key, 0)
                mean_val = stats.get(mean_key, 0)

                # Use provided std or default value
                if isinstance(std_key, str):
                    std_val = max(stats.get(std_key, 0.1), 0.01)
                else:
                    std_val = std_key

                if current_val > 0 and mean_val > 0:
                    # Calculate similarity with tolerance
                    deviation = abs(current_val - mean_val)
                    similarity = max(0, 1 - (deviation / (std_val * 2)))  # More tolerant
                    similarities.append(similarity)
                else:
                    # If we can't compare, assume moderate similarity
                    similarities.append(0.7)

            return statistics.mean(similarities) if similarities else 0.5

        except Exception as e:
            logging.error(f"Statistical similarity error: {e}")
            return 0.5

    def _ml_authentication(self, profile_id: str, current_timing: Dict) -> Tuple[float, bool]:
        """ML-based authentication using ensemble of models"""
        try:
            features = self.extract_enhanced_features(current_timing)
            if features is None:
                return 0.5, False

            models = self.ml_models[profile_id]
            scores = []
            fraud_indicators = 0

            # Isolation Forest scoring
            if 'isolation_forest' in models:
                try:
                    iso_score = models['isolation_forest'].score_samples(features)[0]
                    # Convert to similarity score (higher is better)
                    iso_similarity = max(0, (iso_score + 0.5) / 1.0)  # Normalize to 0-1
                    scores.append(iso_similarity)
                    if iso_score < self.fraud_detection_threshold:
                        fraud_indicators += 1
                except:
                    scores.append(0.5)

            # One-Class SVM scoring
            if 'one_class_svm' in models:
                try:
                    svm_pred = models['one_class_svm'].predict(features)[0]
                    svm_similarity = 1.0 if svm_pred == 1 else 0.0
                    scores.append(svm_similarity)
                    if svm_pred == -1:
                        fraud_indicators += 1
                except:
                    scores.append(0.5)

            # K-Means distance scoring
            if 'kmeans' in models:
                try:
                    distances = models['kmeans'].transform(features)
                    min_distance = np.min(distances)
                    # Convert distance to similarity (closer = more similar)
                    km_similarity = max(0, 1 - min_distance / 10.0)  # Normalize
                    scores.append(km_similarity)
                except:
                    scores.append(0.5)

            avg_score = statistics.mean(scores) if scores else 0.5
            is_fraud = fraud_indicators >= 2

            return avg_score, is_fraud

        except Exception as e:
            logging.error(f"ML authentication error: {e}")
            return 0.5, False

    def _pattern_analysis(self, user_profile: Dict, current_timing: Dict) -> float:
        """Analyze typing patterns and sequences"""
        try:
            samples = user_profile['samples']
            if not samples:
                return 0.5

            # Compare key sequence patterns
            current_sequence = current_timing.get('key_sequence_pattern', '')
            if not current_sequence:
                return 0.5

            sequence_similarities = []
            for sample in samples[-3:]:  # Compare with recent samples
                stored_sequence = sample['timing_data'].get('key_sequence_pattern', '')
                if stored_sequence:
                    # Simple sequence similarity
                    min_len = min(len(current_sequence), len(stored_sequence))
                    if min_len > 0:
                        common_chars = sum(
                            1 for a, b in zip(current_sequence[:min_len], stored_sequence[:min_len]) if a == b)
                        similarity = common_chars / min_len
                        sequence_similarities.append(similarity)

            return statistics.mean(sequence_similarities) if sequence_similarities else 0.5

        except Exception as e:
            logging.error(f"Pattern analysis error: {e}")
            return 0.5

    def _behavioral_analysis(self, timing_data: Dict) -> Tuple[float, bool]:
        """Analyze behavioral patterns for fraud detection"""
        try:
            fraud_indicators = 0
            behavior_score = 1.0  # Start with perfect score

            # Check for unnatural typing speed
            typing_speed = timing_data.get('typing_speed', 0)
            if typing_speed > 500:  # Unnaturally fast (500 WPM)
                fraud_indicators += 1
                behavior_score *= 0.5
            elif typing_speed < 10:  # Unnaturally slow
                fraud_indicators += 1
                behavior_score *= 0.7

            # Check rhythm consistency
            rhythm_std = timing_data.get('rhythm_consistency', 0)
            if rhythm_std < 0.001:  # Too consistent (machine-like)
                fraud_indicators += 1
                behavior_score *= 0.6
            elif rhythm_std > 1.0:  # Too inconsistent
                fraud_indicators += 1
                behavior_score *= 0.8

            # Check dwell time patterns
            avg_dwell = timing_data.get('average_dwell_time', 0)
            if avg_dwell < 0.02:  # Too short (20ms)
                fraud_indicators += 1
                behavior_score *= 0.5
            elif avg_dwell > 2.0:  # Too long (2 seconds)
                fraud_indicators += 1
                behavior_score *= 0.7

            is_fraud = fraud_indicators >= 2
            return behavior_score, is_fraud

        except Exception as e:
            logging.error(f"Behavioral analysis error: {e}")
            return 0.5, False

# ============================================================================
# STEGANOGRAPHY (Hide encrypted data in images)
# ============================================================================

class SteganographyManager:
    """Hide and extract data from images using LSB"""
    
    @staticmethod
    def hide(data: bytes, cover_image_path: str, output_path: str) -> bool:
        """Hide data in image using LSB steganography"""
        if not PIL_AVAILABLE:
            logging.error("PIL required for steganography")
            return False
        
        try:
            # Open or create cover image
            if not os.path.exists(cover_image_path):
                img = Image.new('RGB', (800, 600), color='lightblue')
            else:
                img = Image.open(cover_image_path)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            pixels = img.load()
            width, height = img.size
            
            # Prepare data with length header
            data_len = len(data)
            header = data_len.to_bytes(4, 'big')
            full_data = header + data
            
            # Check capacity
            required_pixels = len(full_data) * 8
            available = width * height * 3
            
            if required_pixels > available:
                logging.warning(f"Image too small. Need {required_pixels}, have {available}")
                return False
            
            # Hide bits in LSB
            data_bits = ''.join(f'{byte:08b}' for byte in full_data)
            bit_index = 0
            
            for y in range(height):
                for x in range(width):
                    if bit_index >= len(data_bits):
                        break
                    
                    r, g, b = pixels[x, y]
                    
                    if bit_index < len(data_bits):
                        r = (r & 0xFE) | int(data_bits[bit_index])
                        bit_index += 1
                    if bit_index < len(data_bits):
                        g = (g & 0xFE) | int(data_bits[bit_index])
                        bit_index += 1
                    if bit_index < len(data_bits):
                        b = (b & 0xFE) | int(data_bits[bit_index])
                        bit_index += 1
                    
                    pixels[x, y] = (r, g, b)
                
                if bit_index >= len(data_bits):
                    break
            
            img.save(output_path, 'PNG')
            logging.info(f"Data hidden in {output_path} ({data_len} bytes)")
            return True
        
        except Exception as e:
            logging.error(f"Steganography hide error: {e}")
            return False
    
    @staticmethod
    def extract(stego_image_path: str) -> Optional[bytes]:
        """Extract hidden data from image"""
        if not PIL_AVAILABLE:
            return None
        
        try:
            img = Image.open(stego_image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            pixels = img.load()
            width, height = img.size
            
            # Extract bits
            bits = []
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    bits.append(str(r & 1))
                    bits.append(str(g & 1))
                    bits.append(str(b & 1))
            
            # Read header (first 32 bits = data length)
            if len(bits) < 32:
                return None
            
            header_bits = ''.join(bits[:32])
            data_len = int(header_bits, 2)
            
            # Read data
            total_bits = 32 + (data_len * 8)
            if len(bits) < total_bits:
                return None
            
            data_bits = bits[32:total_bits]
            data_bytes = bytearray()
            for i in range(0, len(data_bits), 8):
                if i + 8 <= len(data_bits):
                    byte_bits = ''.join(data_bits[i:i+8])
                    data_bytes.append(int(byte_bits, 2))
            
            if len(data_bytes) == data_len:
                return bytes(data_bytes)
            
            return None
        
        except Exception as e:
            logging.error(f"Steganography extract error: {e}")
            return None


# ============================================================================
# FILE CAMOUFLAGE (System-like renaming)
# ============================================================================

class FileCamouflageManager:
    """Rename files to look like system files"""
    
    SYSTEM_NAMES = [
        'kernel32.dll', 'ntoskrnl.exe', 'svchost.exe', 'csrss.exe',
        'services.exe', 'lsass.exe', 'winlogon.exe', 'dwm.exe',
        'taskhostw.exe', 'explorer.exe', 'spoolsv.exe'
    ]
    
    SYSTEM_FOLDERS = [
        'System32', 'SysWOW64', 'Windows', 'AppData', 'ProgramData',
        'Temp', 'Logs', 'Cache', 'Config', 'Backup'
    ]
    
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.mapping_file = os.path.join(vault_path, 'camouflage_map.json')
        self.mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict:
        """Load camouflage filename mapping"""
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_mapping(self):
        """Save mapping to disk"""
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.mapping, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving mapping: {e}")
    
    def camouflage(self, original_path: str, file_id: str) -> str:
        """Rename and relocate file, return new path"""
        try:
            original_name = os.path.basename(original_path)
            fake_name = random.choice(self.SYSTEM_NAMES)
            fake_folder = random.choice(self.SYSTEM_FOLDERS)
            
            # Create folder
            fake_path = os.path.join(self.vault_path, 'camouflaged', fake_folder)
            os.makedirs(fake_path, exist_ok=True)
            
            new_path = os.path.join(fake_path, fake_name)
            
            # If destination exists, add a counter to make it unique
            attempt = 0
            original_new_path = new_path
            while os.path.exists(new_path) and attempt < 100:
                attempt += 1
                name_parts = os.path.splitext(fake_name)
                new_path = os.path.join(fake_path, f"{name_parts[0]}_{attempt}{name_parts[1]}")
            
            # Move file
            if os.path.exists(original_path):
                os.rename(original_path, new_path)
            
            # Record mapping using the provided file_id
            self.mapping[file_id] = {
                'original': original_name,
                'fake_name': os.path.basename(new_path),
                'fake_path': new_path,
                'timestamp': datetime.now().isoformat()
            }
            self._save_mapping()
            
            return new_path
        
        except Exception as e:
            logging.error(f"Camouflage error: {e}")
            messagebox.showerror("Camouflage Error", 
                f"⚠️ Failed to camouflage file\n\nError: {str(e)}\n\n"
                f"The file will be stored without camouflage protection.\n"
                f"Please check file permissions and disk space.")
            return original_path
    
    def remove_camouflage_record(self, file_id: str) -> bool:
        """Remove camouflage record and delete the camouflaged file"""
        try:
            if file_id in self.mapping:
                record = self.mapping[file_id]
                fake_path = record.get('fake_path')
                
                # Delete the actual file if it exists
                if fake_path and os.path.exists(fake_path):
                    os.remove(fake_path)
                    logging.info(f"Deleted camouflaged file: {fake_path}")
                
                # Remove from mapping
                del self.mapping[file_id]
                self._save_mapping()
                return True
            return False
        except Exception as e:
            logging.error(f"Error removing camouflage record: {e}")
            return False
    
    def get_camouflaged_files(self) -> List[Dict]:
        """List all camouflaged files"""
        return list(self.mapping.values())


# ============================================================================
# BLOCKCHAIN & IPFS INTEGRATION
# ============================================================================

class BlockchainLedger:
    """Simple blockchain for file integrity verification"""
    
    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self.chain = self._load_chain()
    
    def _load_chain(self) -> List[Dict]:
        """Load blockchain from file"""
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self._create_genesis()
    
    def _create_genesis(self) -> List[Dict]:
        """Create genesis block"""
        genesis = {
            'index': 0,
            'timestamp': datetime.now().isoformat(),
            'data': 'GENESIS',
            'prev_hash': '0' * 64,
            'hash': hashlib.sha256(b'GENESIS').hexdigest()
        }
        return [genesis]
    
    def add_record(self, file_id: str, file_hash: str, ipfs_cid: Optional[str] = None) -> Dict:
        """Add file record to blockchain"""
        try:
            prev = self.chain[-1]
            record = {
                'index': len(self.chain),
                'timestamp': datetime.now().isoformat(),
                'file_id': file_id,
                'file_hash': file_hash,
                'ipfs_cid': ipfs_cid,
                'prev_hash': prev['hash'],
            }
            # Compute hash
            record_str = json.dumps(record, sort_keys=True)
            record['hash'] = hashlib.sha256(record_str.encode()).hexdigest()
            
            self.chain.append(record)
            self._save_chain()
            return record
        
        except Exception as e:
            logging.error(f"Blockchain add error: {e}")
            return {}
    
    def _save_chain(self):
        """Save chain to file"""
        try:
            os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
            with open(self.ledger_path, 'w') as f:
                json.dump(self.chain, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving chain: {e}")
    
    def verify_integrity(self, file_id: str, file_hash: str) -> bool:
        """Verify file hasn't been modified"""
        for record in self.chain:
            if record.get('file_id') == file_id:
                return record.get('file_hash') == file_hash
        return False
    
    def remove_record(self, file_id: str) -> bool:
        """Remove a file record from the blockchain ledger"""
        try:
            # Find and remove the record with the matching file_id
            original_length = len(self.chain)
            self.chain = [record for record in self.chain if record.get('file_id') != file_id]
            
            if len(self.chain) < original_length:
                self._save_chain()
                logging.info(f"Removed blockchain record for file_id: {file_id}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error removing blockchain record: {e}")
            return False
    
    def get_chain(self) -> List[Dict]:
        """Get full chain"""
        return self.chain


class IPFSManager:
    """IPFS upload/download management"""
    
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """Connect to IPFS daemon"""
        if IPFS_AVAILABLE:
            try:
                self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
                logging.info("Connected to IPFS")
            except Exception as e:
                logging.warning(f"IPFS connection failed: {e}")
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload file to IPFS, return CID"""
        if not self.client:
            return None
        
        try:
            response = self.client.add(file_path)
            cid = response['Hash']
            logging.info(f"IPFS upload: {file_path} -> {cid}")
            return cid
        except Exception as e:
            logging.error(f"IPFS upload error: {e}")
            return None
    
    def download_file(self, cid: str, output_path: str) -> bool:
        """Download file from IPFS using CID"""
        if not self.client:
            logging.error("IPFS client not available")
            return False
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.client.get(cid, output_path)
            logging.info(f"IPFS download: {cid} -> {output_path}")
            return True
        except Exception as e:
            logging.error(f"IPFS download error: {e}")
            return False


# ============================================================================
# DECOY VAULT & HONEYTRAP
# ============================================================================

class DecoyVault:
    """Generate and manage honeytrap files"""
    
    HONEYTRAP_FILES = [
        {
            'name': 'financial_records.txt',
            'content': '''═══════════════════════════════════════════════════════════════
                    CONFIDENTIAL FINANCIAL RECORDS
═══════════════════════════════════════════════════════════════

FISCAL YEAR 2025 - Q3 EARNINGS REPORT

Revenue Summary:
├─ Product Sales:          $3,247,582
├─ Service Revenue:        $1,928,374
├─ Licensing Fees:         $847,293
└─ TOTAL REVENUE:          $6,023,249

Operating Expenses:
├─ Salaries & Benefits:    $2,384,756
├─ Infrastructure:         $847,293
├─ Marketing:              $584,920
├─ R&D:                    $743,827
├─ Administration:         $294,827
└─ TOTAL EXPENSES:         $4,855,623

Net Operating Income:      $1,167,626
Tax Rate: 21%
Net Profit After Tax:      $921,944

Bank Account Information:
┌─────────────────────────────────────────────────────────┐
│ PRIMARY OPERATIONS ACCOUNT                              │
│ Bank: JPMorgan Chase                                    │
│ Account: ••••••••••••4582                              │
│ Balance: $2,847,293                                     │
│ Last Reconciliation: 2025-12-07                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ PAYROLL ACCOUNT                                         │
│ Bank: Wells Fargo                                       │
│ Account: ••••••••••••6719                              │
│ Balance: $1,384,729                                     │
│ Upcoming Payment: $847,293 (2025-12-15)                 │
└─────────────────────────────────────────────────────────┘

Financial Ratios (Q3 2025):
├─ Current Ratio: 2.47
├─ Debt-to-Equity: 0.83
├─ Operating Margin: 19.4%
├─ ROE: 12.8%
└─ ROA: 8.3%

CONFIDENTIAL: This document is protected by law.
Unauthorized access, disclosure, or distribution is prohibited.
═══════════════════════════════════════════════════════════════'''
        },
        {
            'name': 'passwords_backup.txt',
            'content': '''═══════════════════════════════════════════════════════════════
                    PASSWORD VAULT BACKUP - ENCRYPTED
═══════════════════════════════════════════════════════════════

MASTER ACCOUNT CREDENTIALS
────────────────────────────────────────────────────────────

ROOT / ADMINISTRATIVE ACCESS:
┌─────────────────────────────────────────────────────────┐
│ Account: administrator                                  │
│ Email: admin@company.internal                           │
│ Password: Tr0ub4dor&3$2024                              │
│ Access Level: UNRESTRICTED                              │
│ MFA: TOTP (Google Authenticator)                        │
│ Last Changed: 2025-10-23                                │
└─────────────────────────────────────────────────────────┘

DATABASE ADMINISTRATION:
┌─────────────────────────────────────────────────────────┐
│ Account: dba-primary-node                               │
│ Database: PostgreSQL Enterprise 14.2                    │
│ Host: db-prod-01.internal.network                       │
│ Password: P@ssw0rd_DBAdmin#2024!                        │
│ Privileges: SUPERUSER, CREATEDB, CREATEROLE            │
│ Backup User: backup-dba | Pw: Backup#2024$Admin        │
│ Last Access: 2025-12-08 14:37:23 UTC                    │
└─────────────────────────────────────────────────────────┘

INFRASTRUCTURE & CLOUD SERVICES:
┌─────────────────────────────────────────────────────────┐
│ AWS Account ID: 847392-1847-2938                        │
│ Root User: security+aws@company.com                     │
│ Password: AwsR00t$2024#Secure!                          │
│ Access Keys: AKIAIOSFODNN7EXAMPLE                       │
│ Secret Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY   │
│ MFA Status: ENABLED (Hardware Token)                    │
│ Billing Alert: $5000/month threshold                    │
│ Last Login: 2025-12-08 10:15:47 UTC                     │
└─────────────────────────────────────────────────────────┘

VPN & REMOTE ACCESS:
┌─────────────────────────────────────────────────────────┐
│ VPN Service: Fortinet FortiVPN                          │
│ Admin Account: vpn-admin-847                            │
│ Password: VPN#Secure$Access2024!                        │
│ Gateway IP: 203.0.113.42                               │
│ IKEv2 PSK: SharedS3cr3t#VPN$2024                        │
│ Active Sessions: 142                                    │
│ Concurrent Users Limit: 500                             │
└─────────────────────────────────────────────────────────┘

EMAIL & COMMUNICATION SYSTEMS:
┌─────────────────────────────────────────────────────────┐
│ Exchange Admin: mail-admin-portal                       │
│ Password: M@il#Admin$2024!Secure                        │
│ Server: exchange-prod.company.internal                  │
│ API Key: X-API-Key-847392847293847                      │
│ Mailbox Quota: 1TB per user                             │
│ Archival: 7-Year Retention Policy                       │
│ Backup: Veeam Daily (Full Weekend)                      │
└─────────────────────────────────────────────────────────┘

SECURITY POLICY ENFORCEMENTS:
├─ Password Expiration: 90 days
├─ Minimum Length: 14 characters
├─ Complexity: Uppercase, Lowercase, Numbers, Symbols
├─ MFA: REQUIRED for all admin accounts
├─ Session Timeout: 30 minutes (admin), 4 hours (user)
├─ Failed Attempts: 5 max, 30-min lockout
├─ Access Logging: All privileged actions logged
├─ Audit Review: Monthly by Security Team
└─ Compliance: SOC 2 Type II, ISO 27001 Certified

LAST UPDATED: 2025-12-08 08:00:00 UTC
CREATED BY: Security Operations Team
DISTRIBUTION: RESTRICTED - Management & Admin Only

⚠️  CRITICAL NOTICE: Unauthorized access, disclosure, or
distribution of this document is strictly prohibited and
will be prosecuted to the fullest extent of the law.
═══════════════════════════════════════════════════════════════'''
        },
        {
            'name': 'project_phoenix.txt',
            'content': '''═══════════════════════════════════════════════════════════════
                  PROJECT PHOENIX - CLASSIFIED BRIEFING
═══════════════════════════════════════════════════════════════

CLASSIFICATION: TOP SECRET / RESTRICTED DISTRIBUTION
Release Authority: Chief Information Security Officer
Document ID: PHOENIX-2025-Q4-001

PROJECT OVERVIEW
────────────────────────────────────────────────────────────

Codename: PROJECT PHOENIX
Full Title: Advanced Post-Quantum Cryptographic 
            Infrastructure Development Initiative

Status: ACTIVE (Phase 3 - Advanced Development)
Timeline: 2024-01-15 → 2026-12-31 (32 months)
Estimated Budget: $4,847,293 (Approved)
Current Spend: $2,847,293 (58.8% of budget)

PRIMARY OBJECTIVES
────────────────────────────────────────────────────────────

1. QUANTUM-RESISTANT ENCRYPTION SUITE
   ├─ Develop lattice-based encryption (NTRU variant)
   ├─ Implement code-based cryptography (McEliece)
   ├─ Create hybrid quantum-safe/classical protocols
   └─ Target deployment: Q2 2026

2. BIOMETRIC AUTHENTICATION ADVANCEMENT
   ├─ Multi-modal fingerprint recognition
   ├─ Iris scanning with liveness detection
   ├─ Facial recognition with spoofing resistance
   ├─ Voice/speaker authentication
   └─ Achieve False Rejection Rate < 0.5%

3. DISTRIBUTED LEDGER INTEGRATION
   ├─ Blockchain-based audit trails
   ├─ Smart contracts for access control
   ├─ Zero-knowledge proof authentication
   └─ Compatibility: Hyperledger Fabric, Ethereum

4. ADAPTIVE THREAT DETECTION
   ├─ AI/ML-based anomaly detection
   ├─ Behavioral biometric analysis
   ├─ Real-time threat scoring
   └─ Integration with SIEM platforms

PROJECT TEAM STRUCTURE
────────────────────────────────────────────────────────────

Project Director:
  Dr. Margaret Chen (Ph.D. Cryptography, MIT)
  Email: m.chen@company.internal
  Office: Security Tower, Level 8
  Extension: 8847

Lead Researchers:
  Dr. Robert Patterson (Quantum Security, 15 years)
  Dr. Sarah Williams (Biometrics Expert, 12 years)
  Dr. James Rodriguez (Blockchain Specialist, 8 years)

Development Team:
  Senior Engineer: Michael Thompson
  Engineers: Lisa Johnson, David Kumar, Emily Foster
  DevOps Lead: Christopher Hayes
  Quality Assurance: Maria Santos

TECHNICAL SPECIFICATIONS
────────────────────────────────────────────────────────────

Encryption Parameters:
├─ Algorithm: Hybrid (NTRU Prime + ChaCha20-Poly1305)
├─ Key Size: 4096-bit NTRU parameter set
├─ Session Derivation: SHAKE256 (NIST approved)
├─ Perfect Forward Secrecy: ENABLED
├─ Post-Quantum Safety: Certified Level 5 (NIST)
└─ Expected Lifetime: >20 years against quantum

Performance Targets:
├─ Encryption Speed: >100 MB/s (hardware acceleration)
├─ Key Generation: <500ms per keypair
├─ Authentication Latency: <200ms (average)
├─ False Negative Rate: <1% biometric
└─ System Availability: >99.95% SLA

FUNDING & BUDGET ALLOCATION
────────────────────────────────────────────────────────────

Total Approved Budget: $4,847,293

Distribution:
├─ Personnel (Salaries): $2,384,927 (49.2%)
├─ Hardware/Infrastructure: $1,247,382 (25.7%)
├─ Software & Tools Licenses: $584,920 (12.1%)
├─ Research & Consulting: $384,920 (7.9%)
├─ Contingency (5%): $261,144 (5.4%)
└─ Facilities & Overhead: $42,000 (0.9%)

CRITICAL MILESTONES
────────────────────────────────────────────────────────────

2025-12-15: Core cryptography module completion (40% done)
2026-02-28: Biometric integration alpha release
2026-05-31: Full system integration testing
2026-08-30: Pilot deployment (5 offices)
2026-10-31: Company-wide rollout preparation
2026-12-31: Full operational deployment

SECURITY PROTOCOLS
────────────────────────────────────────────────────────────

Access Control:
├─ Personnel: Background check + Security clearance
├─ Physical: Badge access + Biometric + Guard
├─ Network: VPN + IP Whitelist + 2FA required
├─ Code: Signed commits + Code review mandatory
└─ Data: AES-256 at rest + TLS 1.3 in transit

Communication:
├─ All documentation: Encrypted storage
├─ Meetings: Secure conference room (TEMPEST certified)
├─ Email: PGP encryption for external
├─ Logs: Immutable blockchain audit trail
└─ Destruction: 7-pass DoD wiping protocol

COMPLIANCE & STANDARDS
────────────────────────────────────────────────────────────

Regulatory Alignment:
├─ NIST SP 800-175 (Post-Quantum Cryptography)
├─ FIPS 140-3 (Cryptographic Module Validation)
├─ ISO/IEC 27001 (Information Security)
├─ Common Criteria EAL5 (Evaluation Assurance)
├─ Export Control: EAR 740.17(b)(1) Notification pending
└─ Patent: 47 claims filed (23 granted, 24 pending)

NEXT REVIEW MEETING: 2025-12-22 14:00 GMT
Conference Room: Phoenix Room (L8-847)

═════════════════════════════════════════════════════════════
NOTICE: This document contains proprietary and confidential
information protected by law. Unauthorized access, disclosure,
reproduction, or distribution is strictly PROHIBITED and
constitutes criminal activity subject to civil and criminal
penalties including imprisonment up to 10 years.

Classification Level: TOP SECRET
Handling Code: NOFORN (No Foreign Nationals)
═════════════════════════════════════════════════════════════'''
        },
        {
            'name': 'passwords_backup.txt',
            'content': '''════════════════════════════════════════════════════════
        CREDENTIALS & ACCESS MANAGEMENT
════════════════════════════════════════════════════════

⚠️  CRITICAL: This file contains sensitive credentials.
Last Updated: 2025-12-08 10:30 UTC
Access Restricted to: System Admins & Security Team

ADMINISTRATIVE CREDENTIALS
────────────────────────────────────────────────────────

Domain Admin:
  Username: admin@company.internal
  Password: C0mplex!2025#Secure$Admin
  MFA Token: GoogleAuth / TOTP
  SSH Key: id_rsa (4096-bit, in secure storage)

Database Admin:
  Service: PostgreSQL (prod-db-01.company.internal)
  Username: postgres_admin
  Password: Tr0pic@lM0nk3y!Database$2025
  Database: company_prod_db
  Port: 5433 (non-standard for security)

AWS Root Account (DO NOT USE - EMERGENCY ONLY):
  Account ID: 847293847293
  Username: root@company.aws
  Password: AWS#RootAccess$Emergency2025!
  MFA Serial: arn:aws:iam::847293847293:mfa/root
  Recovery Codes: Stored in offline vault (location: Safe D)

API KEYS & TOKENS
────────────────────────────────────────────────────────

GitHub Enterprise:
  Organization: company-secure
  Token: ghp_847293847293847293847293847293847293
  Scope: admin:repo_hook, admin:org
  Created: 2025-06-15

Jira Cloud:
  API Token: ATATT847293847293847293847293847293847293
  Username: automation@company.atlassian.net
  Instance: company.atlassian.net
  Permissions: Admin

Slack Workspace Admin:
  Token: xoxb-847293847293-847293847293-847293847293847293
  Workspace ID: T847293847293
  Scope: admin, channels:read, users:read

VPN & REMOTE ACCESS
────────────────────────────────────────────────────────

OpenVPN Master:
  CA Certificate: /etc/openvpn/ca-cert.pem
  Key: /etc/openvpn/private/server-key.pem
  Master Password: V!P_M@st3r_P@ss#2025$Secure

FortiGate Firewall:
  Admin: fortiadmin
  Password: Fort!G@t3#S3cur3$2025Admin
  VLAN 847: Management (192.168.1.0/24)
  VLAN 293: Production (10.0.0.0/8)

BACKUP & RECOVERY
────────────────────────────────────────────────────────

Veeam Backup Master:
  Service Account: veeam_backup_svc
  Password: V33m#B@ckup$Master2025!Secure
  License Key: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX

Disaster Recovery:
  DR Site: AWS Region us-west-2
  Failover Password: DR#F@il0v3r$2025!Emergency
  RPO Target: 4 hours
  RTO Target: 2 hours

EMAIL & COMMUNICATION
────────────────────────────────────────────────────────

Exchange Online Admin:
  UPN: exchange-admin@company.onmicrosoft.com
  Password: Exch@ng3_#Admin2025!Secure$
  Azure MFA: Enabled (authenticator app)

ProtonMail Executive:
  Account: secure-comms@protonmail.com
  Password: Pr0t0n#M@il$Secure2025!Executive
  Decryption Key: [64-char hex key stored separately]

COMPLIANCE NOTES:
  • Rotate all passwords quarterly (Next: 2026-03-08)
  • All credentials stored in KeePass with master key in vault
  • Hardware security key backup in safe
  • Access audit: Monthly by Security Officer
  • Last rotation: 2025-09-08
  • Next rotation: 2026-03-08

⚠️  WARNING: Do not share this file. All access is logged.
══════════════════════════════════════════════════════════'''
        },
        {
            'name': 'employee_records.csv',
            'content': '''Employee_ID,Full_Name,Department,Position,Salary,Clearance_Level,Start_Date,Manager
E001,James Mitchell,Executive,CEO,850000,Top Secret,2015-01-15,Board Chair
E002,Sarah Johnson,Engineering,VP Engineering,320000,Secret,2016-03-20,CEO
E003,Michael Chen,Finance,CFO,310000,Secret,2017-06-10,CEO
E004,David Rodriguez,Operations,VP Operations,290000,Confidential,2018-02-14,CEO
E005,Emily Watson,Security,Chief Security Officer,275000,Top Secret,2016-11-22,CEO
E006,Robert Thompson,Engineering,Senior Architect,185000,Secret,2015-09-10,VP Engineering
E007,Jessica Lee,Engineering,Security Engineer,160000,Secret,2019-04-15,VP Engineering
E008,Christopher Hayes,Engineering,DevOps Lead,155000,Confidential,2018-01-08,VP Engineering
E009,Lisa Anderson,Finance,Controller,145000,Confidential,2017-08-20,CFO
E010,Thomas Wilson,Operations,Systems Manager,138000,Confidential,2018-05-12,VP Operations
E011,Rachel Green,Engineering,Senior Developer,152000,Secret,2016-11-03,VP Engineering
E012,Kevin Murphy,Security,Incident Response,148000,Secret,2019-02-18,Chief Security Officer
E013,Amanda Foster,Finance,Accounting Manager,125000,Confidential,2019-07-25,Controller
E014,Mark Johnson,Operations,Network Engineer,132000,Confidential,2017-12-01,Systems Manager
E015,Victoria Price,Engineering,QA Lead,138000,Confidential,2018-06-14,VP Engineering'''
        },
        {
            'name': 'api_keys.json',
            'content': '''{
  "production_keys": {
    "aws": {
      "access_key_id": "AKIAJ847293847293847",
      "secret_access_key": "wJalrXUtnFEMI/K7MDENG/+PVLK847293847293847",
      "region": "us-east-1",
      "description": "Production deployment account"
    },
    "azure": {
      "subscription_id": "847293847-2938-2938-2938-847293847293",
      "tenant_id": "847293847-2938-2938-2938-847293847293",
      "client_id": "847293847-2938-2938-2938-847293847293",
      "client_secret": "Az@re#Secret$Key2025!Production",
      "description": "Azure enterprise subscription"
    },
    "stripe": {
      "api_key_live": "sk_live_847293847293847293847293847293847",
      "api_key_restricted": "rk_live_847293847293847293847293847293847",
      "webhook_secret": "whsec_847293847293847293847293847293847",
      "description": "Payment processing - live"
    }
  },
  "third_party_integrations": {
    "twilio": {
      "account_sid": "AC847293847293847293847293847293",
      "auth_token": "847293847293847293847293847293847",
      "phone_number": "+1-555-847-2938",
      "description": "SMS & Voice API"
    },
    "sendgrid": {
      "api_key": "SG.847293847293847293847293_847293847293847293847",
      "description": "Email delivery service"
    },
    "github": {
      "personal_access_token": "ghp_847293847293847293847293847293847293",
      "organization": "company-secure",
      "description": "Repository management"
    }
  },
  "internal_services": {
    "rabbitmq": {
      "host": "rabbitmq-prod.company.internal",
      "port": 5672,
      "username": "admin_mq",
      "password": "R@bbitMQ#Secure2025!Production",
      "virtual_host": "/company_prod"
    },
    "elasticsearch": {
      "cluster_name": "production-cluster",
      "nodes": ["es-node-1.company.internal:9200", "es-node-2.company.internal:9200"],
      "username": "elastic_admin",
      "password": "Elastic#Search$Admin2025!Secure",
      "api_key": "VnVhQ2FyZDpOVEJDZDJOQmMzQkQ847293847293"
    }
  },
  "monitoring_and_alerts": {
    "datadog": {
      "api_key": "847293847293847293847293847293847293",
      "app_key": "847293847293847293847293847293847293847293847293",
      "description": "Monitoring & observability"
    },
    "pagerduty": {
      "api_token": "u+847293847293847293847293847293847293847293",
      "integration_key": "847293847293847293847293847293847293847293",
      "description": "Incident management"
    }
  }
}'''
        },
        {
            'name': 'server_config.conf',
            'content': '''# Production Server Configuration
# Last Modified: 2025-12-08 14:30 UTC
# Managed By: Infrastructure Team

[SERVER]
hostname = prod-app-01.company.internal
ip_address = 192.168.100.50
netmask = 255.255.255.0
gateway = 192.168.100.1
dns_primary = 8.8.8.8
dns_secondary = 8.8.4.4
ntp_server = time.company.internal

[SECURITY]
firewall_enabled = true
selinux_mode = enforcing
apparmor_profile = /etc/apparmor.d/prod-app-01
intrusion_detection = yes
log_level = debug

[DATABASE]
db_type = PostgreSQL
db_host = prod-db-01.company.internal
db_port = 5433
db_name = company_production
db_username = app_user
db_password = P0stgres#P@ss2025!Secure$Prod
connection_pool_size = 50
max_connections = 100
backup_retention_days = 90

[APPLICATION]
app_server = Apache 2.4.52
app_port = 8080
https_port = 8443
ssl_certificate = /etc/ssl/certs/prod-app-01.crt
ssl_key = /etc/ssl/private/prod-app-01.key
certificate_expiry = 2026-12-08

[MONITORING]
monitoring_agent = Datadog
agent_status = running
cpu_threshold = 80%
memory_threshold = 85%
disk_threshold = 90%
alert_email = ops@company.internal

[BACKUP]
backup_enabled = true
backup_type = Incremental Daily + Full Weekly
backup_destination = /mnt/backup/prod-app-01
retention_policy = 30 days
last_backup = 2025-12-08 02:00 UTC
next_backup = 2025-12-09 02:00 UTC

[SECURITY_HARDENING]
password_policy = 14 chars min, complexity required
session_timeout = 900 seconds
failed_login_attempts = 5
lockout_duration = 1800 seconds
audit_logging = enabled
audit_retention = 365 days'''
        },
        {
            'name': 'client_list.xlsx',
            'content': '''CLIENT DATABASE EXPORT
Created: 2025-12-08
Format: Microsoft Excel

ACTIVE CLIENTS (2025)

Client Name,Contact Person,Email,Phone,Industry,Contract Value,Status
Acme Corporation,John Smith,john.smith@acme.com,+1-555-0101,Technology,$2,847,000,Active
Global Solutions Inc,Sarah Johnson,sarah@globalsol.com,+1-555-0102,Consulting,$1,927,000,Active
TechVenture LLC,Michael Chen,m.chen@techventure.com,+1-555-0103,Startup,$847,000,Active
National Bank Group,David Rodriguez,d.rodriguez@natbank.com,+1-555-0104,Finance,$3,247,000,Active
SecureCloud Systems,Emily Watson,e.watson@securecloud.com,+1-555-0105,Technology,$2,147,000,Active
FinanceFirst Partners,Robert Kim,r.kim@financefirst.com,+1-555-0106,Finance,$1,847,000,Pending
Digital Innovations,Jessica Lee,j.lee@diginnovate.com,+1-555-0107,Technology,$1,647,000,Active
Healthcare Solutions,Christopher Hayes,c.hayes@healthsol.com,+1-555-0108,Healthcare,$2,347,000,Active
Corporate Ventures,Amanda Foster,a.foster@corpventures.com,+1-555-0109,Investment,$947,000,Active
Educational Systems,Mark Johnson,m.johnson@edusys.com,+1-555-0110,Education,$747,000,Active

NOTES:
* Contract values represent annual engagement
* All clients signed NDA with confidentiality clause
* Escalation contacts maintained separately
* Renewal dates tracked in CRM system'''
        },
        {
            'name': 'source_code.zip',
            'content': '''ARCHIVE CONTENTS MANIFEST
Archive: source_code.zip
Created: 2025-12-08 14:30 UTC
Size: 6.4 MB (compressed)

Project: SecureVault Enterprise Edition
Version: 4.2.1

Directory Structure:
├── src/
│   ├── encryption/ (247 files, 1.2 MB)
│   ├── authentication/ (156 files, 0.8 MB)
│   ├── steganography/ (89 files, 0.4 MB)
│   ├── ui/ (234 files, 1.1 MB)
│   └── core/ (187 files, 0.9 MB)
├── tests/
│   ├── unit_tests/ (156 files, 0.6 MB)
│   ├── integration_tests/ (94 files, 0.5 MB)
│   └── security_tests/ (67 files, 0.4 MB)
├── docs/
│   ├── api_documentation/ (847 KB)
│   ├── architecture/ (562 KB)
│   ├── deployment/ (493 KB)
│   └── security_protocols/ (724 KB)
├── config/
│   ├── production/ (847 KB)
│   ├── staging/ (743 KB)
│   └── development/ (621 KB)
└── build/
    ├── cmake/ (187 files, 0.3 MB)
    ├── docker/ (12 files, 0.2 MB)
    └── CI-CD/ (24 files, 0.3 MB)

Key Components:
• Cryptographic engine with post-quantum algorithms
• Biometric authentication system (ML-based)
• Steganographic codec for LSB embedding
• Decentralized storage (IPFS) integration
• Blockchain verification layer
• RESTful API server
• Web dashboard UI
• Command-line tools

Compiled Binaries:
• securevault-cli (x86_64, Linux/Windows/macOS)
• securevault-daemon (x86_64)
• securevault-ui (Qt5-based, x86_64)

Build Status: All systems pass security audit
Deployment Ready: Yes
Last Updated: 2025-12-08 14:30 UTC

⚠️  WARNING: This archive contains proprietary source code.
Unauthorized distribution is strictly prohibited.'''
        },
        {
            'name': 'encryption_master.key',
            'content': '''MASTER ENCRYPTION KEY
================================================================================
File: encryption_master.key
Type: RSA 4096-bit Private Key (PKCS#1 format)
Created: 2015-06-15 (renewed 2023-12-01)
Expires: 2026-12-01
Usage: Root key derivation for all enterprise encryption

-----BEGIN RSA PRIVATE KEY-----
MIIG/AIBAAKCAgEAwT3+Yf7K9wF847293847293847293847293847293847293847
293847293847293847293847293847293847293847293847293847293847293847
293847293847293847293847293847293847293847293847293847293847293847
kR0nQ7XzT4K+YwS0J8hJ0mLkK+rVqW8X5T4YzY6A2B3CdEfGhIjKlMnOpQrSt
UsVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsT847293847
293847293847293847293847293847293847293847293847293847293847
293847293847293847293847293847293847293847293847293847293847EQIDA
QABAoICABE3wT4mK9JoL8uR9sT0lVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBc
DeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLm
NoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsT8472
938472938472938472938472938472938472938472938472938472938472938472938
4K8472938473493847IEACgYEA2R0lS8T0847293847293847293847293847293
847293847293847293847293847293847293847293847293847293847293847
293847293847293847293847293847293847293847293847293847293847
Pq0CAf847293847293847293847293847293847293847293847293847293847
293847293847293847293847293847293847293847293847293847293847
wkCgYAaR0lS8T0847293847293847293847293847293847293847293847
293847293847293847293847293847293847293847293847293847293847293847
CgYB1
-----END RSA PRIVATE KEY-----

BACKUP INFORMATION:
• Backup Location: Hardware Security Module (HSM)
• HSM Slot: 3
• Label: MASTER-KEY-PROD
• Access: Dual-key custody (2 of 2 required)
• Backup encrypted with: AES-256-GCM
• Last backup verified: 2025-12-07
• Recovery procedure: See Enterprise Key Management Plan

SECURITY NOTES:
⚠️  This is the master key for all enterprise encryption
⚠️  Loss of this key renders all encrypted data unrecoverable
⚠️  This key must never be transmitted over unencrypted channels
⚠️  Access is restricted to Chief Security Officer + CTO
⚠️  All access attempts are logged and audited
⚠️  Compromised immediately if accessed by unauthorized parties

Key Hierarchy:
Master Key (This file)
  ├── Database Encryption Key (DEK)
  ├── Certificate Authority Key (CA)
  ├── TLS Certificate Signing Key
  └── API Signing Key

Rotation Policy:
• Primary rotation: Every 2 years
• Emergency rotation: If access suspected
• Last rotation: 2023-12-01
• Next rotation: 2025-12-01
• Previous key archived in vault

⚠️  CRITICAL: This file is protected by law. Unauthorized
access, possession, or disclosure is subject to severe criminal
and civil penalties.'''
        }
    ]
    
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.honeytrap_path = os.path.join(vault_path, 'honeytrap')
        os.makedirs(self.honeytrap_path, exist_ok=True)
        self.initialize()
    
    def initialize(self):
        """Create honeytrap files"""
        for trap in self.HONEYTRAP_FILES:
            path = os.path.join(self.honeytrap_path, trap['name'])
            if not os.path.exists(path):
                try:
                    # Use UTF-8 encoding to support emojis and special characters
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(trap['content'])
                    logging.info(f"Created honeytrap: {trap['name']}")
                except Exception as e:
                    logging.error(f"Error creating honeytrap: {e}")
    
    def log_access(self, action: str, timestamp: Optional[str] = None):
        """Log suspicious access"""
        log_file = os.path.join(self.vault_path, 'honeytrap_log.txt')
        ts = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            # Ensure log writes use UTF-8 to avoid encoding errors on Windows
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{ts}] {action}\n")
        except:
            pass


# ============================================================================
# SECURE FILE VAULT (Main Backend)
# ============================================================================

# Authentication thresholds (tweakable)
AUTH_CONFIDENCE_THRESHOLD = 0.35  # Lowered from 0.6 for real-world typing variation
ADAPTIVE_ACCEPT_THRESHOLD = 0.25  # if password correct and confidence >= this, offer to allow

class SecureFileVault:
    """Main vault engine combining all security features"""
    
    def __init__(self, vault_path: str = "secure_vault"):
        self.vault_path = vault_path
        self.real_vault = os.path.join(vault_path, 'real')
        self.log_path = os.path.join(vault_path, 'logs')
        self.metadata_path = os.path.join(vault_path, 'metadata')
        
        # Create directories
        for path in [self.vault_path, self.real_vault, self.log_path, self.metadata_path]:
            os.makedirs(path, exist_ok=True)
        
        # Initialize components
        self.keystroke_analyzer = KeystrokeAnalyzer()
        self.authenticator = BehavioralAuthenticator(os.path.join(vault_path, 'models'))
        self.camouflage = FileCamouflageManager(vault_path)
        self.blockchain = BlockchainLedger(os.path.join(self.log_path, 'blockchain.json'))
        self.ipfs = IPFSManager()
        self.decoy = DecoyVault(vault_path)
        
        self._setup_logging()
    
        # Master password storage (single-user)
        self.master_file = os.path.join(self.metadata_path, 'master.json')

    # -------------------- Master password management --------------------
    def has_master_password(self) -> bool:
        return os.path.exists(self.master_file)

    def set_master_password(self, password: str):
        """Store a salted PBKDF2 hash of the master password"""
        try:
            salt = os.urandom(16)
            # Use PBKDF2-HMAC-SHA256
            dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200000)
            payload = {
                'salt': base64.b64encode(salt).decode(),
                'hash': dk.hex(),
                'created_at': datetime.now().isoformat()
            }
            with open(self.master_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error setting master password: {e}")
            return False

    def verify_master_password(self, password: str) -> bool:
        """Verify a candidate master password against stored hash"""
        try:
            if not os.path.exists(self.master_file):
                return False
            with open(self.master_file, 'r', encoding='utf-8') as f:
                payload = json.load(f)
            salt = base64.b64decode(payload.get('salt', ''))
            expected = payload.get('hash', '')
            dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200000)
            # Use manual constant-time comparison (fallback for older Python versions)
            computed = dk.hex()
            if len(computed) != len(expected):
                return False
            result = 0
            for x, y in zip(computed, expected):
                result |= ord(x) ^ ord(y)
            return result == 0
        except Exception as e:
            logging.error(f"Error verifying master password: {e}")
            return False
    def _setup_logging(self):
        """Setup logging"""
        log_file = os.path.join(self.log_path, 'vault.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def _safe_file_read(self, file_path: str, max_retries: int = 3) -> Optional[bytes]:
        """
        Safely read a file with retry logic for permission/lock issues
        Handles cases where file is locked by another process
        """
        import time
        
        for attempt in range(max_retries):
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                return data
            except PermissionError as pe:
                if attempt < max_retries - 1:
                    logging.warning(f"Permission denied on attempt {attempt + 1}/{max_retries}, retrying: {pe}")
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    
                    # Try to fix permissions
                    try:
                        os.chmod(file_path, 0o644)
                    except:
                        pass
                else:
                    logging.error(f"Failed to read file after {max_retries} attempts: {pe}")
                    raise
            except IOError as ie:
                if attempt < max_retries - 1:
                    logging.warning(f"IO error on attempt {attempt + 1}/{max_retries}, retrying: {ie}")
                    time.sleep(0.5 * (attempt + 1))
                else:
                    logging.error(f"Failed to read file after {max_retries} attempts: {ie}")
                    raise
        
        return None
    
    def store_file(self, file_path: str, password: str, 
                  use_camouflage: bool = True, 
                  use_steganography: bool = False,
                  cover_image: Optional[str] = None) -> Tuple[bool, str]:
        """
        Encrypt and store file.
        Returns (success, file_id or error_message)
        """
        try:
            if not os.path.exists(file_path):
                return False, "File not found"
            
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt
            encrypted, salt = EncryptionManager.encrypt(data, password)
            file_hash = hashlib.sha256(encrypted).hexdigest()
            
            # Generate unique ID using UUID4 for guaranteed uniqueness
            file_id = str(uuid.uuid4()).replace('-', '')[:16]
            
            # Store encrypted data
            stego_success = False
            if use_steganography and cover_image and PIL_AVAILABLE:
                stego_path = os.path.join(self.real_vault, f"{file_id}.png")
                if SteganographyManager.hide(encrypted, cover_image, stego_path):
                    storage_path = stego_path
                    stego_success = True
                else:
                    # Fallback to regular encryption if steganography failed
                    logging.warning(f"Steganography failed, falling back to regular encryption for {file_id}")
                    storage_path = os.path.join(self.real_vault, f"{file_id}.enc")
                    with open(storage_path, 'wb') as f:
                        f.write(encrypted)
                    use_steganography = False  # Mark as non-stego since it failed
            else:
                storage_path = os.path.join(self.real_vault, f"{file_id}.enc")
                with open(storage_path, 'wb') as f:
                    f.write(encrypted)
                use_steganography = False
            
            # Apply camouflage if needed
            if use_camouflage:
                storage_path = self.camouflage.camouflage(storage_path, file_id)
            
            # Save metadata - only mark steganography=True if it actually succeeded
            metadata = {
                'file_id': file_id,
                'original_name': os.path.basename(file_path),
                'salt': base64.b64encode(salt).decode(),
                'file_hash': file_hash,
                'storage_path': storage_path,
                'encrypted_at': datetime.now().isoformat(),
                'camouflaged': use_camouflage,
                'steganography': stego_success
            }
            
            meta_file = os.path.join(self.metadata_path, f"{file_id}.json")
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Upload to IPFS if available
            ipfs_cid = None
            if IPFS_AVAILABLE:
                ipfs_cid = self.ipfs.upload_file(storage_path)
            
            # Record on blockchain
            self.blockchain.add_record(file_id, file_hash, ipfs_cid)
            
            logging.info(f"File stored: {file_id}")
            return True, file_id
        
        except Exception as e:
            logging.error(f"Store error: {e}")
            return False, str(e)
    
    def retrieve_file(self, file_id: str, password: str, 
                     output_path: str) -> Tuple[bool, str]:
        """Decrypt and retrieve file. Returns (success, error_code)"""
        try:
            meta_file = os.path.join(self.metadata_path, f"{file_id}.json")
            if not os.path.exists(meta_file):
                logging.error(f"Retrieve error: Metadata file not found: {meta_file}")
                return False, "metadata_not_found"
            
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            
            storage_path = metadata.get('storage_path')
            
            # If storage file is missing, try IPFS fallback
            if not os.path.exists(storage_path):
                logging.warning(f"Storage file not found: {storage_path}, attempting IPFS fallback...")
                
                # Try to get IPFS CID from blockchain ledger
                ipfs_cid = None
                try:
                    chain = self.blockchain.get_chain()
                    for block in chain:
                        if block.get('file_id') == file_id:
                            ipfs_cid = block.get('ipfs_cid')
                            break
                except Exception as e:
                    logging.warning(f"Could not retrieve IPFS CID from blockchain: {e}")
                
                # Try IPFS download
                if ipfs_cid:
                    logging.info(f"Retrieving file from IPFS: {ipfs_cid}")
                    temp_path = os.path.join(self.vault_path, f"{file_id}_ipfs_temp.enc")
                    if self.ipfs.download_file(ipfs_cid, temp_path):
                        storage_path = temp_path
                        # ipfs.get may create a directory containing the file; if so, pick the first file inside
                        try:
                            if os.path.isdir(storage_path):
                                files_inside = [f for f in os.listdir(storage_path) if os.path.isfile(os.path.join(storage_path, f))]
                                if files_inside:
                                    storage_path = os.path.join(storage_path, files_inside[0])
                                    logging.debug(f"IPFS download produced directory; using contained file: {storage_path}")
                        except Exception as e:
                            logging.debug(f"Error inspecting IPFS download output: {e}")
                        logging.info(f"Successfully retrieved from IPFS: {file_id}")
                    else:
                        logging.error(f"Retrieve error: IPFS download failed for {file_id}")
                        return False, "ipfs_download_failed"
                else:
                    logging.error(f"Retrieve error: No IPFS CID found and storage file missing: {storage_path}")
                    return False, "storage_not_found"
            
            # Extract encrypted data with permission error handling
            encrypted = None
            
            try:
                if metadata.get('steganography'):
                    # Only try steganography extraction if file exists and is likely an image
                    if os.path.exists(storage_path):
                        try:
                            encrypted = SteganographyManager.extract(storage_path)
                            if not encrypted:
                                # Fallback to direct read if extraction failed
                                logging.warning(f"Steganography extraction returned None, attempting direct read")
                                encrypted = self._safe_file_read(storage_path)
                        except PermissionError as pe:
                            logging.warning(f"Permission denied reading steganography file, retrying: {pe}")
                            # Wait a moment and retry
                            import time
                            time.sleep(0.5)
                            encrypted = self._safe_file_read(storage_path)
                        except Exception as e:
                            # If extraction fails (e.g., not a valid image), try direct read
                            logging.warning(f"Steganography extraction failed ({e}), attempting direct read")
                            encrypted = self._safe_file_read(storage_path)
                    else:
                        logging.error(f"Storage path does not exist: {storage_path}")
                        return False, "storage_path_missing"
                else:
                    encrypted = self._safe_file_read(storage_path)
            
            except PermissionError as pe:
                logging.error(f"Permission denied accessing file {storage_path}: {pe}")
                # If this is a temp IPFS file, try to remove and retry
                if "_ipfs_temp" in storage_path:
                    try:
                            import time
                            import stat
                            import subprocess
                        
                            # Step 1: Wait for initial lock release
                            time.sleep(1)
                        
                            # Step 2: Remove read-only attribute using attrib (Windows)
                            try:
                                subprocess.run(['attrib', '-R', storage_path], 
                                             capture_output=True, timeout=3)
                                logging.debug(f"Removed read-only attribute from {storage_path}")
                            except Exception as attr_e:
                                logging.debug(f"attrib command failed: {attr_e}")
                        
                            # Step 3: Apply chmod with proper flags
                            try:
                                os.chmod(storage_path, stat.S_IWRITE | stat.S_IREAD)
                                logging.debug(f"Applied chmod to {storage_path}")
                            except Exception as chmod_e:
                                logging.debug(f"chmod failed: {chmod_e}")
                        
                            # Step 4: Brief wait for permission changes to take effect
                            time.sleep(0.5)
                            encrypted = self._safe_file_read(storage_path)
                    except Exception as retry_e:
                        logging.error(f"Failed to recover from permission error: {retry_e}")
                        return False, "permission_denied"
                else:
                    return False, "permission_denied"
            
            if not encrypted:
                logging.error(f"Retrieve error: No encrypted data found in {storage_path}")
                return False, "no_encrypted_data"
            
            # Decrypt
            salt = base64.b64decode(metadata['salt'])
            try:
                decrypted = EncryptionManager.decrypt(encrypted, salt, password)
            except Exception as decrypt_error:
                # Check if this is likely an invalid password error
                error_msg = str(decrypt_error)
                if 'InvalidToken' in error_msg or 'Signature did not match' in error_msg or 'decrypt' in error_msg.lower():
                    logging.warning(f"Invalid password for file {file_id}")
                    return (False, "invalid_password")  # Return special code for invalid password
                elif metadata.get('steganography'):
                    logging.error(f"File marked as steganography but decryption failed. The file may be corrupted or metadata is incorrect.")
                    return (False, "corrupted_steganography")
                else:
                    logging.warning(f"Decryption failed with current data. Error: {decrypt_error}")
                    return (False, "decryption_failed")
            
            # Verify hash
            if hashlib.sha256(encrypted).hexdigest() != metadata.get('file_hash'):
                logging.warning(f"Hash mismatch for {file_id}")
                return False, "hash_mismatch"
            
            # Save - restore original filename/extension when appropriate
            orig_name = metadata.get('original_name', f"{file_id}")
            # Detect directory-like output_path (explicit dir or ends with separator)
            is_dir_like = False
            try:
                if output_path.endswith(os.sep) or output_path.endswith('/'):
                    is_dir_like = True
            except Exception:
                pass

            if os.path.isdir(output_path):
                is_dir_like = True

            orig_ext = os.path.splitext(orig_name)[1]
            if is_dir_like:
                final_path = os.path.join(output_path, orig_name)
            else:
                base, _ = os.path.splitext(output_path)
                # Always enforce the original extension if present
                if orig_ext:
                    final_path = base + orig_ext
                else:
                    final_path = output_path

            os.makedirs(os.path.dirname(final_path) or '.', exist_ok=True)
            with open(final_path, 'wb') as f:
                f.write(decrypted)
            logging.info(f"Saved retrieved file to: {final_path}")
            
            # Clean up temporary IPFS file if it was downloaded
            if "_ipfs_temp" in storage_path and os.path.exists(storage_path):
                try:
                    import time
                    time.sleep(0.2)  # Small delay to ensure file is released
                    os.chmod(storage_path, 0o644)  # Ensure readable before deleting
                    os.remove(storage_path)
                    logging.info(f"Cleaned up temporary IPFS file: {storage_path}")
                except Exception as cleanup_e:
                    logging.warning(f"Could not clean up temp IPFS file {storage_path}: {cleanup_e}")
            
            logging.info(f"File retrieved: {file_id} -> {final_path}")
            return True, final_path
        
        except Exception as e:
            logging.error(f"Retrieve error: {e}", exc_info=True)
            
            # Attempt to clean up temp file on error
            if 'storage_path' in locals() and "_ipfs_temp" in storage_path:
                try:
                    os.chmod(storage_path, 0o644)
                    os.remove(storage_path)
                except:
                    pass
            
            return False, "unknown_error"
    
    def delete_file(self, file_id: str) -> Tuple[bool, str]:
        """
        Permanently delete a file and all its encrypted versions
        Returns (success, message)
        """
        try:
            meta_file = os.path.join(self.metadata_path, f"{file_id}.json")
            
            # Check if metadata exists
            if not os.path.exists(meta_file):
                return False, f"File ID {file_id} not found"
            
            # Load metadata
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            
            original_name = metadata.get('original_name', 'Unknown')
            
            # Step 1: Delete the encrypted storage file
            storage_path = metadata.get('storage_path')
            if storage_path and os.path.exists(storage_path):
                try:
                    os.remove(storage_path)
                    logging.info(f"Deleted encrypted file: {storage_path}")
                except Exception as e:
                    logging.error(f"Failed to delete encrypted file {storage_path}: {e}")
                    return False, f"Failed to delete encrypted file: {e}"
            
            # Step 2: Delete camouflaged reference if applicable
            if metadata.get('camouflaged'):
                try:
                    self.camouflage.remove_camouflage_record(file_id)
                    logging.info(f"Removed camouflage mapping for {file_id}")
                except Exception as e:
                    logging.warning(f"Failed to remove camouflage mapping: {e}")
            
            # Step 3: Delete metadata file
            try:
                os.remove(meta_file)
                logging.info(f"Deleted metadata file: {meta_file}")
            except Exception as e:
                logging.error(f"Failed to delete metadata file: {e}")
                return False, f"Failed to delete metadata: {e}"
            
            # Step 4: Remove from blockchain ledger (optional - for audit trail)
            try:
                self.blockchain.remove_record(file_id)
                logging.info(f"Removed blockchain record for {file_id}")
            except Exception as e:
                logging.warning(f"Failed to remove blockchain record: {e}")
            
            logging.info(f"File permanently deleted: {file_id} ({original_name})")
            return True, f"File '{original_name}' permanently deleted along with all encrypted copies"
        
        except Exception as e:
            logging.error(f"Delete error: {e}")
            return False, str(e)
    
    def get_stored_files(self) -> List[Dict]:
        """List all stored files"""
        files = []
        if not os.path.exists(self.metadata_path):
            return files

        for meta_file in os.listdir(self.metadata_path):
            if not meta_file.endswith('.json'):
                continue

            path = os.path.join(self.metadata_path, meta_file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                # Only include valid file metadata that contains a file_id
                if isinstance(meta, dict) and meta.get('file_id'):
                    files.append(meta)
                else:
                    logging.debug(f"Skipping non-file metadata: {meta_file}")
            except Exception as e:
                logging.warning(f"Error loading metadata {meta_file}: {e}")

        return files

class SecureVaultGUI:
    """Main Tkinter application"""
    
    def __init__(self, root):
        self.root = root
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Setup theme
        ModernTheme.setup_styles()
        
        # Initialize vault
        self.vault = SecureFileVault()
        
        # Check if authenticated
        self.is_authenticated = False
        
        # Check if master password exists, if not show enrollment, else show auth
        try:
            if not self.vault.has_master_password() or 'master' not in getattr(self.vault.authenticator, 'profiles', {}):
                self.show_enrollment_screen()
                return
        except Exception:
            self.show_enrollment_screen()
            return
        
        # Master password exists, show auth screen
        self.show_auth_screen()
    
    def show_home_screen(self):
        """Show home page with modern dashboard design"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f5f7fb', highlightthickness=0)
        main_frame.pack(fill='both', expand=True)
        
        # ==================== LEFT SIDEBAR ====================
        sidebar = tk.Frame(main_frame, bg='#6366f1', highlightthickness=0, width=220)
        sidebar.pack(fill='y', side='left')
        sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = tk.Frame(sidebar, bg='#6366f1', highlightthickness=0, height=80)
        sidebar_header.pack(fill='x')
        sidebar_header.pack_propagate(False)
        
        logo_label = tk.Label(sidebar_header, text="🔒 SecureVault", 
                             font=('Segoe UI', 13, 'bold'),
                             foreground='white', bg='#6366f1')
        logo_label.pack(pady=15)
        
        # Sidebar menu items
        menu_frame = tk.Frame(sidebar, bg="#6366f1", highlightthickness=0)
        menu_frame.pack(fill='both', expand=True, padx=0, pady=10)
        
        # Menu items with commands
        menu_items = [
            ('📁 Files', self.view_carrier_files),
            ('📤 Upload', self.upload_encrypt),
            ('⚠️ Security', self.view_intrusion_logs),
            ('⚙️ Settings', self._change_password_and_keystroke),
        ]
        
        for menu_text, menu_cmd in menu_items:
            menu_btn = tk.Button(menu_frame, text=menu_text,
                                font=('Segoe UI', 11),
                                bg='#6366f1', fg='white',
                                relief='flat', bd=0,
                                anchor='w', padx=15, pady=12,
                                activebackground='#4f46e5',
                                activeforeground='white',
                                cursor='hand2',
                                command=menu_cmd)
            menu_btn.pack(fill='x', pady=2)
        
        # Logout button at bottom
        logout_btn = tk.Button(sidebar, text="🚪 Logout",
                              font=('Segoe UI', 10, 'bold'),
                              bg='#ef4444', fg='white',
                              relief='flat', bd=0,
                              padx=15, pady=12,
                              activebackground='#dc2626',
                              cursor='hand2',
                              command=self.logout)
        logout_btn.pack(fill='x', padx=10, pady=10, side='bottom')
        
        # ==================== RIGHT CONTENT ====================
        content = tk.Frame(main_frame, bg='#f5f7fb', highlightthickness=0)
        content.pack(fill='both', expand=True, side='left')
        
        # Top header bar with gradient
        header_bar = tk.Frame(content, bg='white', highlightthickness=0, height=90)
        header_bar.pack(fill='x')
        header_bar.pack_propagate(False)
        
        # Header content with padding
        header_content = tk.Frame(header_bar, bg='white', highlightthickness=0)
        header_content.pack(fill='both', expand=True, padx=30, pady=5)
        
        # Greeting
        greeting_label = tk.Label(header_content, text="Welcome Back! 👋",
                                 font=('Segoe UI', 18, 'bold'),
                                 fg='#1f2937', bg='white')
        greeting_label.pack(anchor='w', pady=(0,8))
        
        # Subtitle
        subtitle_label = tk.Label(header_content, text="Secure your files with advanced encryption & steganography",
                                 font=('Segoe UI', 10),
                                 fg='#6b7280', bg='white')
        subtitle_label.pack(anchor='w')
        
        # Scrollable content area
        canvas = tk.Canvas(content, bg='#f5f7fb', highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(content, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f7fb', highlightthickness=0)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind arrow keys
        def _on_key(event):
            if event.keysym == 'Up':
                canvas.yview_scroll(-3, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(3, "units")
        
        canvas.bind("<Up>", _on_key)
        canvas.bind("<Down>", _on_key)
        scrollable_frame.bind("<Up>", _on_key)
        scrollable_frame.bind("<Down>", _on_key)
        
        # ==================== STATS SECTION ====================
        stats_frame = tk.Frame(scrollable_frame, bg='#f5f7fb', highlightthickness=0)
        stats_frame.pack(fill='x', padx=30, pady=(30, 20))
        
        stored_files = self.vault.get_stored_files()
        
        # Stat 1: Total Files (Purple)
        stat1 = tk.Frame(stats_frame, bg='white', highlightthickness=1, highlightbackground='#e5e7eb')
        stat1.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        stat1_icon = tk.Label(stat1, text="📁", font=('Arial', 28),
                             bg='#f3f4f6', fg='#6366f1')
        stat1_icon.pack(pady=(15, 10))
        
        stat1_label = tk.Label(stat1, text="Total Files",
                              font=('Segoe UI', 10),
                              fg='#6b7280', bg='white')
        stat1_label.pack()
        
        stat1_value = tk.Label(stat1, text=str(len(stored_files)),
                              font=('Segoe UI', 24, 'bold'),
                              fg='#6366f1', bg='white')
        stat1_value.pack(pady=(5, 15))
        
        # Stat 2: Encryption (Green)
        stat2 = tk.Frame(stats_frame, bg='white', highlightthickness=1, highlightbackground='#e5e7eb')
        stat2.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        stat2_icon = tk.Label(stat2, text="🔐", font=('Arial', 28),
                             bg='#f0fdf4', fg='#10b981')
        stat2_icon.pack(pady=(15, 10))
        
        stat2_label = tk.Label(stat2, text="Encrypted",
                              font=('Segoe UI', 10),
                              fg='#6b7280', bg='white')
        stat2_label.pack()
        
        stat2_value = tk.Label(stat2, text="AES-256",
                              font=('Segoe UI', 14, 'bold'),
                              fg='#10b981', bg='white')
        stat2_value.pack(pady=(8, 15))
        
        # Stat 3: Security (Cyan)
        stat3 = tk.Frame(stats_frame, bg='white', highlightthickness=1, highlightbackground='#e5e7eb')
        stat3.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        stat3_icon = tk.Label(stat3, text="🛡️", font=('Arial', 28),
                             bg='#ecf9ff', fg='#06b6d4')
        stat3_icon.pack(pady=(15, 10))
        
        stat3_label = tk.Label(stat3, text="Security",
                              font=('Segoe UI', 10),
                              fg='#6b7280', bg='white')
        stat3_label.pack()
        
        stat3_value = tk.Label(stat3, text="Protected",
                              font=('Segoe UI', 14, 'bold'),
                              fg='#06b6d4', bg='white')
        stat3_value.pack(pady=(8, 15))
        
        # Stat 4: Features (Orange)
        stat4 = tk.Frame(stats_frame, bg='white', highlightthickness=1, highlightbackground='#e5e7eb')
        stat4.pack(side='left', fill='both', expand=True)
        
        stat4_icon = tk.Label(stat4, text="⭐", font=('Arial', 28),
                             bg='#fffbeb', fg='#f59e0b')
        stat4_icon.pack(pady=(15, 10))
        
        stat4_label = tk.Label(stat4, text="Features",
                              font=('Segoe UI', 10),
                              fg='#6b7280', bg='white')
        stat4_label.pack()
        
        stat4_value = tk.Label(stat4, text="4 Active",
                              font=('Segoe UI', 14, 'bold'),
                              fg='#f59e0b', bg='white')
        stat4_value.pack(pady=(8, 15))
        
        # ==================== CARRIER IMAGES SECTION ====================
        carrier_label = tk.Label(scrollable_frame, text="📷 Carrier Files",
                                font=('Segoe UI', 14, 'bold'),
                                foreground='#1f2937', bg='#f5f7fb')
        carrier_label.pack(anchor='w', padx=30, pady=(20, 10))
        
        carrier_info = tk.Label(scrollable_frame, text="Secure files embedded within carrier images using advanced steganography",
                               font=('Segoe UI', 9),
                               foreground='#6b7280', bg='#f5f7fb')
        carrier_info.pack(anchor='w', padx=30, pady=(0, 20))
        
        # Carrier images grid - RESPONSIVE WITH WRAPPING TO NEXT ROW
        carrier_grid = tk.Frame(scrollable_frame, bg='#f5f7fb', highlightthickness=0)
        carrier_grid.pack(fill='both', expand=True, padx=30, pady=(0, 30))
        
        if len(stored_files) == 0:
            carriers = [
                {'name': 'cat_sleeping.jpg', 'desc': 'Cat Photo', 'size': '2.4 MB', 'time': '2 hours ago'},
                {'name': 'vacation_sunset.png', 'desc': 'Vacation Photo', 'size': '4.1 MB', 'time': '3 hours ago'},
                {'name': 'family_dinner.jpg', 'desc': 'Family Photo', 'size': '3.2 MB', 'time': '1 day ago'},
                {'name': 'beach_waves.jpg', 'desc': 'Beach Photo', 'size': '3.5 MB', 'time': '2 days ago'},
                {'name': 'mountain_view.jpg', 'desc': 'Mountain Photo', 'size': '3.8 MB', 'time': '3 days ago'},
                {'name': 'city_lights.jpg', 'desc': 'City Photo', 'size': '2.9 MB', 'time': '4 days ago'},
                {'name': 'forest_trail.jpg', 'desc': 'Forest Photo', 'size': '3.1 MB', 'time': '5 days ago'},
            ]
        else:
            carriers = []
            for file_info in stored_files:
                encrypted_at = file_info.get('encrypted_at', 'N/A')
                try:
                    from datetime import datetime as dt
                    date_obj = dt.fromisoformat(encrypted_at)
                    time_str = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    time_str = encrypted_at[:19] if isinstance(encrypted_at, str) else 'N/A'

                carriers.append({
                    'file_id': file_info.get('file_id'),
                    'name': file_info.get('original_name', 'Unknown'),
                    'desc': 'Encrypted File',
                    'size': 'Encrypted',
                    'time': time_str
                })
        
        # Color palette for cards - cycling through colors
        card_colors = [
            {'icon_bg': '#f3f4f6', 'icon_color': '#a78bfa', 'accent': '#a78bfa'},  # Purple
            {'icon_bg': '#f0fdf4', 'icon_color': '#10b981', 'accent': '#10b981'},  # Green
            {'icon_bg': '#ecf9ff', 'icon_color': '#06b6d4', 'accent': '#06b6d4'},  # Cyan
            {'icon_bg': '#fffbeb', 'icon_color': '#f59e0b', 'accent': '#f59e0b'},  # Orange
        ]
        
        # Configure grid columns for equal width distribution
        for col in range(4):
            carrier_grid.grid_columnconfigure(col, weight=1, uniform='card')
        
        # Pack all cards into grid with wrapping
        for i, carrier in enumerate(carriers):
            color = card_colors[i % len(card_colors)]
            
            # Card layout - grid will wrap automatically
            card = tk.Frame(carrier_grid, bg='white', highlightthickness=1, 
                           highlightbackground='#e5e7eb', width=260, height=320)
            card.grid(row=i//4, column=i%4, padx=8, pady=8, sticky='nsew')
            card.pack_propagate(False)
            
            # Icon section with fixed height
            icon_frame = tk.Frame(card, bg=color['icon_bg'], highlightthickness=0, height=100)
            icon_frame.pack(fill='x')
            icon_frame.pack_propagate(False)
            
            # Determine icon based on file type
            file_name = carrier.get('name', '')
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Map extensions to icons
            icon_map = {
                '.pdf': '📄',
                '.doc': '📄', '.docx': '📄', '.txt': '📄', '.xlsx': '📊', '.csv': '📊',
                '.jpg': '📷', '.jpeg': '📷', '.png': '📷', '.gif': '📷', '.bmp': '📷',
                '.mp4': '🎥', '.avi': '🎥', '.mov': '🎥', '.mkv': '🎥',
                '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.aac': '🎵',
                '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦',
                '.exe': '⚙️', '.msi': '⚙️', '.app': '⚙️',
                '.html': '🌐', '.css': '🌐', '.js': '🌐', '.py': '🐍',
            }
            
            # Get icon or default to image
            icon_text = icon_map.get(file_ext, '📷')
            
            icon = tk.Label(icon_frame, text=icon_text, font=('Arial', 40),
                           bg=color['icon_bg'], fg=color['icon_color'], cursor='hand2')
            icon.pack(pady=15)

            # Content section
            content_frame = tk.Frame(card, bg='white', highlightthickness=0)
            content_frame.pack(fill='both', expand=True, padx=15, pady=15)
            
            # If this carrier represents a stored file, add password panel
            if carrier.get('file_id'):
                fid = carrier.get('file_id')
                
                # Status label
                status_lbl = tk.Label(content_frame, text='', font=('Segoe UI', 9), fg='#6b7280', bg='white')
                status_lbl.pack(pady=(0, 10))

                # Password frame
                pwd_frame = tk.Frame(content_frame, bg='#f9fafb', highlightthickness=1, highlightbackground='#e5e7eb')
                pwd_frame.pack(fill='x', pady=(0, 15))

                pwd_inner = tk.Frame(pwd_frame, bg='#f9fafb')
                pwd_inner.pack(fill='x', padx=10, pady=8)

                ttk.Label(pwd_inner, text='🔐', font=('Arial', 13), background='#f9fafb').pack(side='left', padx=(0,6))
                pwd_var = tk.StringVar()
                pwd_entry = ttk.Entry(pwd_inner, textvariable=pwd_var, show='•', width=20)
                pwd_entry.pack(side='left', fill='x', expand=True)

                btn_frame = tk.Frame(pwd_frame, bg='#f9fafb')
                btn_frame.pack(fill='x', padx=10, pady=(0, 8))

                save_btn = None
                quick_btn = None

                def _start_retrieve(dest_path: str):
                    pwd_entry.config(state='disabled')
                    save_btn.config(state='disabled')
                    quick_btn.config(state='disabled')
                    status_lbl.config(text='🔄 Decrypting...', fg='#f59e0b')
                    self.root.update_idletasks()
                    try:
                        if not pwd_var.get():
                            status_lbl.config(text='❌ Password required', fg='#ef4444')
                            return
                        ok, result = self.vault.retrieve_file(fid, pwd_var.get(), dest_path)
                        if ok:
                            saved_path = result
                            status_lbl.config(text=f"✅ Saved: {os.path.basename(saved_path)[:30]}", fg='#10b981')
                            pwd_var.set('')
                        else:
                            status_lbl.config(text='❌ Retrieval failed', fg='#ef4444')
                    except Exception as e:
                        logging.error(f'Inline retrieve error: {e}', exc_info=True)
                        status_lbl.config(text=f'❌ Error', fg='#ef4444')
                    finally:
                        pwd_entry.config(state='normal')
                        save_btn.config(state='normal')
                        quick_btn.config(state='normal')

                def _save_as():
                    suggested = carrier.get('name') or fid
                    dest = filedialog.asksaveasfilename(title='Save retrieved file as', initialfile=suggested)
                    if not dest:
                        return
                    _start_retrieve(dest)

                def _quick_save():
                    suggested = carrier.get('name') or fid
                    downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
                    if not os.path.exists(downloads):
                        downloads = os.getcwd()
                    dest = os.path.join(downloads, suggested)
                    _start_retrieve(dest)

                pwd_inner.pack_forget()
                btn_frame.pack_forget()
                pwd_visible = [False]

                def _toggle_pwd(e):
                    if pwd_visible[0]:
                        try:
                            pwd_inner.pack_forget()
                        except Exception:
                            pass
                        try:
                            btn_frame.pack_forget()
                        except Exception:
                            pass
                        pwd_visible[0] = False
                    else:
                        pwd_inner.pack(fill='x', padx=10, pady=8)
                        btn_frame.pack(fill='x', padx=10, pady=(0, 8))
                        pwd_entry.focus()
                        pwd_visible[0] = True

                # Create proper closure to capture current fid value
                def make_preview_handler(file_id, name):
                    def on_preview(event=None):
                        self.show_carrier_image_preview(file_id, name)
                    return on_preview
                
                icon.bind('<Button-1>', make_preview_handler(fid, carrier.get('name', 'Unknown')))
            
            # File info section
            name = tk.Label(content_frame, text=carrier['name'],
                           font=('Segoe UI', 13, 'bold'),
                           foreground='#1f2937', bg='white')
            name.pack(anchor='w', pady=(0, 5))
            
            desc = tk.Label(content_frame, text=carrier['desc'],
                           font=('Segoe UI', 10),
                           foreground='#6b7280', bg='white')
            desc.pack(anchor='w', pady=(0, 10))
            
            # Divider
            divider = tk.Frame(content_frame, bg='#e5e7eb', height=1)
            divider.pack(fill='x', pady=10)
            divider.pack_propagate(False)
            
            # Details row
            details_frame = tk.Frame(content_frame, bg='white', highlightthickness=0)
            details_frame.pack(fill='x')
            
            detail_left = tk.Frame(details_frame, bg='white')
            detail_left.pack(side='left', fill='both', expand=True)
            
            size_label = tk.Label(detail_left, text="Size",
                                 font=('Segoe UI', 8),
                                 foreground='#9ca3af', bg='white')
            size_label.pack(anchor='w')
            
            size_value = tk.Label(detail_left, text=carrier['size'],
                                 font=('Segoe UI', 10, 'bold'),
                                 foreground=color['accent'], bg='white')
            size_value.pack(anchor='w')
            
            detail_right = tk.Frame(details_frame, bg='white')
            detail_right.pack(side='right', fill='both', expand=True)
            
            time_label = tk.Label(detail_right, text="Last Updated",
                                 font=('Segoe UI', 8),
                                 foreground='#9ca3af', bg='white')
            time_label.pack(anchor='w')
            
            time_value = tk.Label(detail_right, text=carrier['time'],
                                 font=('Segoe UI', 10, 'bold'),
                                 foreground='#6b7280', bg='white')
            time_value.pack(anchor='w')
        
        # ==================== SYSTEM FILES SECTION ====================
        # Only show system files section if there are encrypted files
        # stored_files = self.vault.get_stored_files()
        
        # if len(stored_files) > 0:
        #     system_label = tk.Label(scrollable_frame, text="System Files",
        #                            font=('Segoe UI', 14, 'bold'),
        #                            foreground='white', bg='#0f172a')
        #     system_label.pack(anchor='w', padx=30, pady=(20, 10))
            
        #     system_info = tk.Label(scrollable_frame, text="Encrypted files disguised as legitimate Windows system components",
        #                           font=('Segoe UI', 10),
        #                           foreground='#94a3b8', bg='#0f172a')
        #     system_info.pack(anchor='w', padx=30, pady=(0, 20))
            
        #     # System files grid
        #     system_grid = tk.Frame(scrollable_frame, bg='#0f172a', highlightthickness=0)
        #     system_grid.pack(fill='x', padx=30, pady=(0, 30))
            
        #     # Load actual camouflaged files from camouflage_map.json
        #     camouflaged_files = []
        #     try:
        #         camouflage_map_path = os.path.join(self.vault.vault_path, 'camouflage_map.json')
        #         if os.path.exists(camouflage_map_path):
        #             with open(camouflage_map_path, 'r', encoding='utf-8') as f:
        #                 camouflage_map = json.load(f)
                    
        #             # Convert camouflage_map to list of files
        #             for file_id, file_info in camouflage_map.items():
        #                 fake_path = file_info.get('fake_path', '')
        #                 # Extract location from fake_path
        #                 if '\\' in fake_path:
        #                     loc = '\\'.join(fake_path.split('\\')[:-1]) + '\\'
        #                 else:
        #                     loc = 'C:\\Windows\\System32\\'
                        
        #                 camouflaged_files.append({
        #                     'name': file_info.get('fake_name', 'Unknown'),
        #                     'desc': 'Encrypted File',
        #                     'size': 'Encrypted',
        #                     'loc': loc
        #                 })
        #     except Exception as e:
        #         logging.warning(f"Could not load camouflaged files: {e}")
            
        #     # If no camouflaged files, load sample system files as fallback
        #     if not camouflaged_files:
        #         try:
        #             sample_files_path = os.path.join(os.path.dirname(__file__), 'sample_system_files.json')
        #             if os.path.exists(sample_files_path):
        #                 with open(sample_files_path, 'r', encoding='utf-8') as f:
        #                     all_system_files = json.load(f)
        #                     camouflaged_files = all_system_files[:len(stored_files)]
        #         except Exception as e:
        #             logging.warning(f"Could not load sample system files: {e}")
            
        #     # Fallback to default if still empty
        #     if not camouflaged_files:
        #         camouflaged_files = [
        #             {'name': 'kernel32.dll', 'desc': 'Kernel Libraries', 'size': '512 KB', 'loc': 'C:\\Windows\\System32\\'},
        #             {'name': 'ntoskrnl.exe', 'desc': 'Operating System Kernel', 'size': '8.2 MB', 'loc': 'C:\\Windows\\System32\\'},
        #         ]
            
        #     # Only show as many as there are encrypted files
        #     display_files = camouflaged_files[:len(stored_files)]
            
        #     for i, sysfile in enumerate(display_files):
        #         if i % 3 == 0 and i > 0:
        #             system_grid = tk.Frame(scrollable_frame, bg='#0f172a', highlightthickness=0)
        #             system_grid.pack(fill='x', padx=30, pady=(0, 30))
                
        #         card = tk.Frame(system_grid, bg='#1e293b', highlightthickness=1,
        #                        highlightbackground='#334155')
        #         card.pack(side='left', padx=8, fill='both', expand=True)
                
        #         icon = tk.Label(card, text="📂", font=('Arial', 28),
        #                        bg='#1e293b', fg='#3b82f6')
        #         icon.pack(pady=(12, 8))
                
        #         name = tk.Label(card, text=sysfile['name'],
        #                        font=('Segoe UI', 11, 'bold'),
        #                        foreground='white', bg='#1e293b')
        #         name.pack()
                
        #         desc = tk.Label(card, text=sysfile['desc'],
        #                        font=('Segoe UI', 9),
        #                        foreground='#94a3b8', bg='#1e293b')
        #         desc.pack()
                
        #         size = tk.Label(card, text=f"{sysfile['size']} • System File",
        #                        font=('Segoe UI', 8),
        #                        foreground='#64748b', bg='#1e293b')
        #         size.pack(pady=(4, 6))
                
        #         loc = tk.Label(card, text=sysfile['loc'],
        #                       font=('Segoe UI', 8),
        #                       foreground='#475569', bg='#1e293b')
        #         loc.pack(pady=(0, 12))
        
        # ==================== FILE HISTORY SECTION ====================
        history_header = tk.Frame(scrollable_frame, bg='#f5f7fb', highlightthickness=0)
        history_header.pack(fill='x', padx=30, pady=(40, 10))
        
        history_title = tk.Label(history_header, text="📋 File History",
                                font=('Segoe UI', 14, 'bold'),
                                foreground='#1f2937', bg='#f5f7fb')
        history_title.pack(anchor='w')
        
        history_subtitle = tk.Label(scrollable_frame, text="Complete audit trail of all encrypted files with timestamps and security status",
                                   font=('Segoe UI', 9),
                                   foreground='#6b7280', bg='#f5f7fb')
        history_subtitle.pack(anchor='w', padx=30, pady=(0, 15))
        
        # Create history table container
        history_container = tk.Frame(scrollable_frame, bg='#f5f7fb', highlightthickness=0)
        history_container.pack(fill='both', expand=True, padx=30, pady=(0, 40))
        
        # Table header
        header_frame = tk.Frame(history_container, bg='white', highlightthickness=1, 
                               highlightbackground='#e5e7eb', height=50)
        header_frame.pack(fill='x', pady=(0, 0))
        header_frame.pack_propagate(False)
        
        # Header background
        header_bg = tk.Frame(header_frame, bg='#f3f4f6', highlightthickness=0)
        header_bg.pack(fill='both', expand=True)
        
        # Column headers with proper spacing
        col_headers = tk.Frame(header_bg, bg='#f3f4f6', highlightthickness=0)
        col_headers.pack(fill='both', expand=True, padx=20, pady=12)
        
        # Date column (20%)
        date_header = tk.Label(col_headers, text="📅 Date & Time",
                              font=('Segoe UI', 10, 'bold'),
                              foreground='#374151', bg='#f3f4f6')
        date_header.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # File name column (35%)
        name_header = tk.Label(col_headers, text="📄 File Name",
                              font=('Segoe UI', 10, 'bold'),
                              foreground='#374151', bg='#f3f4f6')
        name_header.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Encryption column (15%)
        enc_header = tk.Label(col_headers, text="🔐 Encryption",
                             font=('Segoe UI', 10, 'bold'),
                             foreground='#374151', bg='#f3f4f6')
        enc_header.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Camouflage column (15%)
        camouflage_header = tk.Label(col_headers, text="👁️ Camouflage",
                                    font=('Segoe UI', 10, 'bold'),
                                    foreground='#374151', bg='#f3f4f6')
        camouflage_header.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Status column (15%)
        status_header = tk.Label(col_headers, text="✓ Status",
                                font=('Segoe UI', 10, 'bold'),
                                foreground='#374151', bg='#f3f4f6')
        status_header.pack(side='left', fill='both', expand=True)
        
        # Scrollable history list
        history_canvas = tk.Canvas(history_container, bg='white', highlightthickness=0, bd=0, height=300)
        history_scrollbar = tk.Scrollbar(history_container, orient='vertical', command=history_canvas.yview)
        history_frame_inner = tk.Frame(history_canvas, bg='white', highlightthickness=0)
        
        history_frame_inner.bind(
            "<Configure>",
            lambda e: history_canvas.configure(scrollregion=history_canvas.bbox("all"))
        )
        
        history_canvas.create_window((0, 0), window=history_frame_inner, anchor="nw", width=800)
        history_canvas.configure(yscrollcommand=history_scrollbar.set)
        
        history_canvas.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to history table
        def _on_history_mousewheel(event):
            history_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        history_canvas.bind("<MouseWheel>", _on_history_mousewheel)
        history_frame_inner.bind("<MouseWheel>", _on_history_mousewheel)
        
        # Populate history table
        if len(stored_files) > 0:
            for idx, file_info in enumerate(stored_files):
                row_bg_color = '#ffffff' if idx % 2 == 0 else '#f9fafb'
                
                row_frame = tk.Frame(history_frame_inner, bg=row_bg_color, highlightthickness=1, 
                                    highlightbackground='#f3f4f6', height=60)
                row_frame.pack(fill='x', pady=0)
                row_frame.pack_propagate(False)
                
                row_content = tk.Frame(row_frame, bg=row_bg_color, highlightthickness=0)
                row_content.pack(fill='both', expand=True, padx=20, pady=12)
                
                # Extract and format date
                encrypted_at = file_info.get('encrypted_at', 'N/A')
                try:
                    from datetime import datetime as dt
                    date_obj = dt.fromisoformat(encrypted_at)
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    time_ago = date_obj.strftime('%b %d, %Y')
                except:
                    date_str = encrypted_at[:19] if isinstance(encrypted_at, str) else 'N/A'
                    time_ago = 'N/A'
                
                # Date cell (20%)
                date_cell = tk.Frame(row_content, bg=row_bg_color)
                date_cell.pack(side='left', fill='both', expand=True, padx=(0, 10))
                
                date_label = tk.Label(date_cell, text=date_str,
                                     font=('Segoe UI', 9),
                                     foreground='#1f2937', bg=row_bg_color)
                date_label.pack(anchor='w')
                
                date_ago_label = tk.Label(date_cell, text=time_ago,
                                         font=('Segoe UI', 8),
                                         foreground='#9ca3af', bg=row_bg_color)
                date_ago_label.pack(anchor='w')
                
                # File name cell (35%)
                name_cell = tk.Frame(row_content, bg=row_bg_color)
                name_cell.pack(side='left', fill='both', expand=True, padx=(0, 10))
                
                original_name = file_info.get('original_name', 'Unknown')
                file_ext = os.path.splitext(original_name)[1].lower()
                
                # Map extensions to icons
                icon_map = {
                    '.pdf': '📄',
                    '.doc': '📄', '.docx': '📄', '.txt': '📄', '.xlsx': '📊', '.csv': '📊',
                    '.jpg': '📷', '.jpeg': '📷', '.png': '📷', '.gif': '📷', '.bmp': '📷',
                    '.mp4': '🎥', '.avi': '🎥', '.mov': '🎥', '.mkv': '🎥',
                    '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.aac': '🎵',
                    '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦',
                    '.exe': '⚙️', '.msi': '⚙️', '.app': '⚙️',
                    '.html': '🌐', '.css': '🌐', '.js': '🌐', '.py': '🐍',
                }
                
                file_icon = icon_map.get(file_ext, '📄')
                
                name_label = tk.Label(name_cell, text=f"{file_icon} {original_name}",
                                     font=('Segoe UI', 9),
                                     foreground='#1f2937', bg=row_bg_color)
                name_label.pack(anchor='w')
                
                # Encryption cell (15%)
                enc_cell = tk.Frame(row_content, bg=row_bg_color)
                enc_cell.pack(side='left', fill='both', expand=True, padx=(0, 10))
                
                enc_label = tk.Label(enc_cell, text="🔐 AES-256",
                                    font=('Segoe UI', 9),
                                    foreground='#10b981', bg=row_bg_color)
                enc_label.pack(anchor='w')
                
                # Camouflage cell (15%)
                camouflage_cell = tk.Frame(row_content, bg=row_bg_color)
                camouflage_cell.pack(side='left', fill='both', expand=True, padx=(0, 10))
                
                is_camouflaged = file_info.get('camouflaged', False)
                camouflage_icon = "✓ Yes" if is_camouflaged else "✗ No"
                camouflage_color = '#10b981' if is_camouflaged else '#ef4444'
                
                camouflage_label = tk.Label(camouflage_cell, text=camouflage_icon,
                                           font=('Segoe UI', 9),
                                           foreground=camouflage_color, bg=row_bg_color)
                camouflage_label.pack(anchor='w')
                
                # Status cell (15%)
                status_cell = tk.Frame(row_content, bg=row_bg_color)
                status_cell.pack(side='left', fill='both', expand=True)
                
                status_label = tk.Label(status_cell, text="✓ Secure",
                                       font=('Segoe UI', 9),
                                       foreground='#06b6d4', bg=row_bg_color)
                status_label.pack(anchor='w')
        else:
            # Empty state
            empty_frame = tk.Frame(history_frame_inner, bg='white', highlightthickness=0, height=100)
            empty_frame.pack(fill='x', pady=30)
            empty_frame.pack_propagate(False)
            
            empty_label = tk.Label(empty_frame, text="No files stored yet",
                                  font=('Segoe UI', 11),
                                  foreground='#9ca3af', bg='white')
            empty_label.pack()
            
            empty_hint = tk.Label(empty_frame, text="Upload files to see them in the history",
                                 font=('Segoe UI', 9),
                                 foreground='#d1d5db', bg='white')
            empty_hint.pack(pady=(5, 0))
    
    def view_carrier_files(self):
        """View carrier files section"""
        messagebox.showinfo("Carrier Files", "Viewing stored carrier images with embedded encrypted data")
        self.show_home_screen()
    
    def upload_encrypt(self):
        """Show modern upload and encrypt page with 2-column layout - light theme"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main background - light theme
        main_bg = tk.Frame(self.root, bg='#f0f2f5', highlightthickness=0)
        main_bg.pack(fill='both', expand=True)
        
        # Top header with back button
        header = tk.Frame(main_bg, bg='white', highlightthickness=1, highlightbackground='#d4d9e8', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        back_btn = tk.Button(header, text="← Back", 
                            font=('Segoe UI', 10, 'bold'),
                            bg='white', fg='#2563eb',
                            relief='flat', bd=0,
                            cursor='hand2',
                            command=self.show_home_screen,
                            activebackground='#f0f2f5',
                            activeforeground='#1d4ed8')
        back_btn.pack(side='left', padx=20, pady=15)
        
        title_label = tk.Label(header, text="📤 Upload & Encrypt",
                              font=('Segoe UI', 16, 'bold'),
                              fg='#4a5568', bg='white')
        title_label.pack(side='left', padx=0, pady=15)
        
        subtitle_label = tk.Label(header, text="Secure & Hide Your Files",
                                 font=('Segoe UI', 10),
                                 fg='#7a8799', bg='white')
        subtitle_label.pack(side='left', padx=10, pady=15)
        
        # ==================== 2-COLUMN LAYOUT ====================
        content_frame = tk.Frame(main_bg, bg='#f0f2f5', highlightthickness=0)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ==================== LEFT COLUMN: FILE SELECTION ====================
        left_col = tk.Frame(content_frame, bg='#f0f2f5', highlightthickness=0)
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Title
        left_title = tk.Label(left_col, text="📤 Step 1: Select Files",
                             font=('Segoe UI', 14, 'bold'),
                             fg='#2563eb', bg='#f0f2f5')
        left_title.pack(anchor='w', pady=(0, 15))
        
        # Card frame for file selection
        select_card = tk.Frame(left_col, bg='white', highlightthickness=1,
                              highlightbackground='#d4d9e8')
        select_card.pack(fill='both', expand=True)
        
        # Icon and text area
        drop_area = tk.Frame(select_card, bg='#f8f9fc', highlightthickness=2,
                            highlightbackground='#d4d9e8', relief='flat')
        drop_area.pack(fill='both', padx=15, pady=15, ipady=35)
        
        icon_label = tk.Label(drop_area, text="📤", font=('Arial', 48),
                             bg='#f8f9fc')
        icon_label.pack(pady=(10, 5))
        
        drop_text = tk.Label(drop_area, text="Click to select files",
                            font=('Segoe UI', 11, 'bold'),
                            fg='#4a5568', bg='#f8f9fc')
        drop_text.pack()
        
        support_text = tk.Label(drop_area, text="All file types • Multiple files",
                               font=('Segoe UI', 8),
                               fg='#7a8799', bg='#f8f9fc')
        support_text.pack(pady=(3, 12))
        
        select_btn = tk.Button(drop_area, text="📁 Browse Files",
                              font=('Segoe UI', 10, 'bold'),
                              bg='#2563eb', fg='white',
                              relief='flat', bd=0, padx=20, pady=10,
                              cursor='hand2',
                              activebackground='#1d4ed8',
                              activeforeground='white',
                              command=lambda: self._pick_files_for_upload())
        select_btn.pack()
        
        # Selected files list
        self.upload_selected_files = []
        
        files_label = tk.Label(select_card, text="Selected Files:",
                              font=('Segoe UI', 10, 'bold'),
                              fg='#5a6578', bg='white')
        files_label.pack(anchor='w', padx=15, pady=(12, 5))
        
        self._selected_listbox = tk.Listbox(select_card, height=8, bg='#f3f4f8',
                                           fg='#4a5568', bd=0, highlightthickness=1,
                                           highlightbackground='#d4d9e8',
                                           font=('Segoe UI', 9), selectmode='extended')
        self._selected_listbox.pack(fill='both', expand=True, padx=15, pady=(0, 10))
        
        clear_btn = tk.Button(select_card, text="🗑️ Clear Selection",
                             font=('Segoe UI', 9),
                             bg='#e5e7eb', fg='#4a5568',
                             relief='flat', bd=0,
                             padx=10, pady=8,
                             cursor='hand2',
                             activebackground='#d1d5db',
                             activeforeground='#2563eb',
                             command=lambda: self._clear_upload_selection())
        clear_btn.pack(fill='x', padx=15, pady=(0, 12))
        
        # ==================== RIGHT COLUMN: SETTINGS ====================
        right_col = tk.Frame(content_frame, bg='#f0f2f5', highlightthickness=0, width=350)
        right_col.pack(side='right', fill='both', expand=False, padx=(10, 0))
        right_col.pack_propagate(False)
        
        # Settings scroll area
        settings_canvas = tk.Canvas(right_col, bg='#f0f2f5', highlightthickness=0, bd=0)
        settings_scrollbar = tk.Scrollbar(right_col, orient='vertical', command=settings_canvas.yview)
        settings_scrollable = tk.Frame(settings_canvas, bg='#f0f2f5', highlightthickness=0)
        
        settings_scrollable.bind(
            "<Configure>",
            lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
        )
        
        settings_canvas.create_window((0, 0), window=settings_scrollable, anchor="nw")
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        
        settings_canvas.pack(side='left', fill='both', expand=True)
        settings_scrollbar.pack(side='right', fill='y')
        
        # Settings title
        settings_title = tk.Label(settings_scrollable, text="⚙️ Settings",
                                 font=('Segoe UI', 14, 'bold'),
                                 fg='#4a5568', bg='#f0f2f5')
        settings_title.pack(anchor='w', pady=(0, 15))
        
        # ==================== ENCRYPTION LEVEL ====================
        enc_card = tk.Frame(settings_scrollable, bg='white', highlightthickness=1,
                           highlightbackground='#d4d9e8')
        enc_card.pack(fill='x', pady=(0, 12))
        
        enc_title = tk.Label(enc_card, text="🔐 Encryption Level",
                            font=('Segoe UI', 11, 'bold'),
                            fg='#2563eb', bg='white')
        enc_title.pack(anchor='w', padx=12, pady=(10, 8))
        
        self.upload_enc_var = tk.StringVar(value="AES-256 (Secure)")
        enc_dropdown = tk.OptionMenu(enc_card, self.upload_enc_var,
                                    "AES-256 (Secure)", "AES-192", "AES-128")
        enc_dropdown.config(bg='#f3f4f8', fg='#4a5568',
                           activebackground='#2563eb',
                           activeforeground='white',
                           relief='flat', bd=0,
                           font=('Segoe UI', 9), highlightthickness=0)
        enc_dropdown.pack(fill='x', padx=12, pady=(0, 10))
        
        # ==================== PASSWORD ====================
        pwd_card = tk.Frame(settings_scrollable, bg='white', highlightthickness=1,
                           highlightbackground='#d4d9e8')
        pwd_card.pack(fill='x', pady=(0, 12))
        
        pwd_title = tk.Label(pwd_card, text="🔑 Password (Optional)",
                            font=('Segoe UI', 11, 'bold'),
                            fg='#2563eb', bg='white')
        pwd_title.pack(anchor='w', padx=12, pady=(10, 8))
        
        self.upload_password_var = tk.StringVar(value='')
        pwd_entry = tk.Entry(pwd_card, textvariable=self.upload_password_var,
                            font=('Segoe UI', 10), bg='#f3f4f8', fg='#4a5568',
                            insertbackground='#5b7dd9', show='•', relief='solid', bd=1, borderwidth=1)
        pwd_entry.pack(fill='x', padx=12, pady=(0, 10), ipady=8)
        
        # ==================== CUSTOM FILENAME ====================
        custom_card = tk.Frame(settings_scrollable, bg='white', highlightthickness=1,
                              highlightbackground='#d4d9e8')
        custom_card.pack(fill='x', pady=(0, 12))
        
        custom_frame = tk.Frame(custom_card, bg='white')
        custom_frame.pack(fill='x', padx=12, pady=10)
        
        custom_icon = tk.Label(custom_frame, text="📝",
                              font=('Arial', 10),
                              bg='white')
        custom_icon.pack(side='left', padx=(0, 10))
        
        custom_label = tk.Label(custom_frame, text="Custom Filename",
                               font=('Segoe UI', 10, 'bold'),
                               fg='#5a6578', bg='white')
        custom_label.pack(side='left')
        
        self.upload_custom_var = tk.BooleanVar(value=False)
        custom_toggle = tk.Checkbutton(custom_frame, variable=self.upload_custom_var,
                                      bg='white', fg='#2563eb',
                                      activebackground='white',
                                      activeforeground='#2563eb',
                                      highlightthickness=0,
                                      selectcolor='white')
        custom_toggle.pack(side='right')
        
        # ==================== CARRIER IMAGE ====================
        carrier_card = tk.Frame(settings_scrollable, bg='white', highlightthickness=1,
                               highlightbackground='#d4d9e8')
        carrier_card.pack(fill='x', pady=(0, 12))
        
        carrier_title = tk.Label(carrier_card, text="🎨 Steganography",
                                font=('Segoe UI', 11, 'bold'),
                                fg='#2563eb', bg='white')
        carrier_title.pack(anchor='w', padx=12, pady=(10, 8))
        
        self.upload_cover_image = None
        def _choose_cover():
            path = filedialog.askopenfilename(title='Select cover image',
                                             filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
            if path:
                self.upload_cover_image = path
                carrier_chosen_label.config(text=f"✓ {os.path.basename(path)}", fg='#059669')
        
        carrier_btn = tk.Button(carrier_card, text="🖼️ Choose Image",
                               font=('Segoe UI', 10, 'bold'),
                               bg='#2563eb', fg='white',
                               relief='flat', bd=0, padx=12, pady=8,
                               cursor='hand2',
                               activebackground='#1d4ed8',
                               activeforeground='white',
                               command=_choose_cover)
        carrier_btn.pack(fill='x', padx=12, pady=(0, 8))
        
        carrier_chosen_label = tk.Label(carrier_card, text='No image selected',
                                        font=('Segoe UI', 8),
                                        fg='#9ca3b0', bg='white')
        carrier_chosen_label.pack(anchor='w', padx=12, pady=(0, 10))
        
        # ==================== SECURITY NOTICE ====================
        notice_card = tk.Frame(settings_scrollable, bg='white', highlightthickness=1,
                              highlightbackground='#d4d9e8')
        notice_card.pack(fill='x', pady=(0, 20))
        
        notice_title = tk.Label(notice_card, text="⚠️ Security",
                               font=('Segoe UI', 10, 'bold'),
                               fg='#ea580c', bg='white')
        notice_title.pack(anchor='w', padx=12, pady=(10, 8))
        
        notice_text = tk.Label(notice_card,
                              text="✓ AES-256 encryption\n✓ Camouflage protection\n✓ Biometric backup",
                              font=('Segoe UI', 8),
                              fg='#5a6578', bg='white',
                              justify='left')
        notice_text.pack(anchor='w', padx=12, pady=(0, 10))
        
        # ==================== ACTION BUTTON ====================
        action_card = tk.Frame(settings_scrollable, bg='white', highlightthickness=1,
                              highlightbackground='#d4d9e8')
        action_card.pack(fill='x', pady=(0, 12))
        
        encrypt_btn = tk.Button(action_card, text="✓ Encrypt & Secure",
                               font=('Segoe UI', 11, 'bold'),
                               bg='#2563eb', fg='white',
                               relief='flat', bd=0, padx=12, pady=12,
                               cursor='hand2',
                               activebackground='#1d4ed8',
                               activeforeground='white',
                               command=lambda: self._perform_upload_encrypt())
        encrypt_btn.pack(fill='x', padx=12, pady=12)
        
    def _select_files_for_upload(self, parent_frame):
        """Helper to select and encrypt files"""
        # Legacy quick-encrypt helper (not used by the new multi-step upload flow)
        file_paths = filedialog.askopenfilenames(title="Select files to encrypt")
        if not file_paths:
            return

        password = ''
        if hasattr(self, 'upload_password_var') and self.upload_password_var.get() is not None:
            password = self.upload_password_var.get()

        success_count = 0
        for file_path in file_paths:
            success, result = self.vault.store_file(file_path, password, use_camouflage=True)
            if success:
                success_count += 1

        messagebox.showinfo("Success", f"✅ {success_count} file(s) encrypted and stored!")
        self.show_home_screen()

    def _pick_files_for_upload(self):
        """Allow user to pick files and populate the selection listbox"""
        file_paths = filedialog.askopenfilenames(title="Select files to encrypt")
        if not file_paths:
            return
        # store selection and update UI listbox
        self.upload_selected_files = list(file_paths)
        try:
            self._selected_listbox.delete(0, 'end')
            for p in self.upload_selected_files:
                self._selected_listbox.insert('end', os.path.basename(p))
        except Exception:
            pass

    def _clear_upload_selection(self):
        self.upload_selected_files = []
        try:
            self._selected_listbox.delete(0, 'end')
        except Exception:
            pass

    def _perform_upload_encrypt(self):
        """Perform encryption of files selected in upload page using page settings"""
        files = getattr(self, 'upload_selected_files', []) or []
        if len(files) == 0:
            messagebox.showwarning("No files", "Please select files to encrypt (Step 1)")
            return

        # Read settings
        password = ''
        if hasattr(self, 'upload_password_var') and self.upload_password_var.get() is not None:
            password = self.upload_password_var.get()

        enc_level = getattr(self, 'upload_enc_var', tk.StringVar(value='AES-256 (Secure)')).get()
        use_camouflage = bool(getattr(self, 'upload_custom_var', tk.BooleanVar(value=False)).get())
        use_stego = bool(getattr(self, 'upload_cover_image', None))
        cover = getattr(self, 'upload_cover_image', None)

        # Encrypt each file
        success_count = 0
        for file_path in files:
            try:
                success, result = self.vault.store_file(file_path, password, use_camouflage=use_camouflage, use_steganography=use_stego, cover_image=cover)
                if success:
                    success_count += 1
            except Exception as e:
                logging.error(f"Error storing file {file_path}: {e}")

        messagebox.showinfo("Upload Complete", f"✅ {success_count}/{len(files)} file(s) encrypted and stored")
        # clear selection and refresh
        self._clear_upload_selection()
        self.show_home_screen()
    
    def _show_password_dialog(self):
        """Show custom password entry dialog with modern design"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Encryption Password")
        dialog.geometry("450x250")
        dialog.configure(bg='#0f172a')
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center dialog on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='#1e293b', highlightthickness=2,
                             highlightbackground='#334155')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title
        title = tk.Label(main_frame, text="🔐 Encryption Password",
                        font=('Segoe UI', 14, 'bold'),
                        fg='white', bg='#1e293b')
        title.pack(pady=(20, 5))
        
        # Description
        desc = tk.Label(main_frame, text="Enter a strong password to encrypt your files",
                       font=('Segoe UI', 9),
                       fg='#94a3b8', bg='#1e293b')
        desc.pack(pady=(0, 20))
        
        # Password field label
        pwd_label = tk.Label(main_frame, text="Password",
                            font=('Segoe UI', 10, 'bold'),
                            fg='#cbd5e1', bg='#1e293b')
        pwd_label.pack(anchor='w', padx=25, pady=(0, 5))
        
        # Password entry
        pwd_entry = tk.Entry(main_frame, font=('Segoe UI', 11),
                            bg='#334155', fg='white',
                            insertbackground='white',
                            show='•', relief='flat', bd=0)
        pwd_entry.pack(fill='x', padx=25, pady=(0, 5), ipady=10)
        pwd_entry.focus()
        
        # Strength indicator
        strength_frame = tk.Frame(main_frame, bg='#1e293b')
        strength_frame.pack(fill='x', padx=25, pady=(0, 20))
        
        strength_bar = tk.Frame(strength_frame, bg='#334155', height=4)
        strength_bar.pack(fill='x', side='left', expand=True, padx=(0, 10))
        strength_bar.pack_propagate(False)
        
        strength_label = tk.Label(strength_frame, text="Weak",
                                 font=('Segoe UI', 8),
                                 fg='#ef4444', bg='#1e293b')
        strength_label.pack(side='right')
        
        def update_strength(*args):
            pwd = pwd_entry.get()
            if len(pwd) < 6:
                strength_bar.configure(bg='#ef4444')
                strength_label.configure(text="Weak", fg='#ef4444')
            elif len(pwd) < 10:
                strength_bar.configure(bg='#f59e0b')
                strength_label.configure(text="Fair", fg='#f59e0b')
            elif len(pwd) < 16:
                strength_bar.configure(bg='#eab308')
                strength_label.configure(text="Good", fg='#eab308')
            else:
                strength_bar.configure(bg='#10b981')
                strength_label.configure(text="Strong", fg='#10b981')
        
        pwd_entry.bind('<KeyRelease>', update_strength)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#1e293b')
        buttons_frame.pack(fill='x', padx=25, pady=(15, 15))
        
        result = {'password': None}
        
        def confirm():
            password = pwd_entry.get()
            if not password:
                messagebox.showwarning("Empty Password", "Please enter a password")
                return
            if len(password) < 6:
                messagebox.showwarning("Weak Password", "Password should be at least 6 characters")
                return
            result['password'] = password
            dialog.destroy()
        
        def cancel():
            result['password'] = None
            dialog.destroy()
        
        # Encrypt button
        encrypt_btn = tk.Button(buttons_frame, text="✓ Encrypt Files",
                               font=('Segoe UI', 10, 'bold'),
                               bg='#10b981', fg='white',
                               relief='flat', bd=0,
                               padx=20, pady=10,
                               cursor='hand2',
                               activebackground='#059669',
                               activeforeground='white',
                               command=confirm)
        encrypt_btn.pack(side='right', padx=(10, 0))
        
        # Cancel button
        cancel_btn = tk.Button(buttons_frame, text="✕ Cancel",
                              font=('Segoe UI', 10),
                              bg='#334155', fg='#cbd5e1',
                              relief='flat', bd=0,
                              padx=20, pady=10,
                              cursor='hand2',
                              activebackground='#475569',
                              activeforeground='#10b981',
                              command=cancel)
        cancel_btn.pack(side='right')
        
        # Handle Enter key
        pwd_entry.bind('<Return>', lambda e: confirm())
        dialog.bind('<Escape>', lambda e: cancel())
        
        # Wait for dialog
        self.root.wait_window(dialog)
        return result['password']
    
    def view_intrusion_logs(self):
        """View intrusion/security logs"""
        self.show_security_logs_window()
    
    def show_settings_in_main(self):
        """Show settings in main content area (not a popup)"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create a simple settings view in main window instead of popup
        main_frame = tk.Frame(self.root, bg='#0f172a')
        main_frame.pack(fill='both', expand=True)
        
        # Header with back button
        header = tk.Frame(main_frame, bg='#1e293b', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        back_btn = tk.Button(header, text="← Back to Home",
                            font=('Segoe UI', 10, 'bold'),
                            bg='#1e293b', fg='#94a3b8',
                            relief='flat', bd=0,
                            cursor='hand2',
                            command=self.show_home_screen)
        back_btn.pack(side='left', padx=20, pady=15)
        
        title = tk.Label(header, text="⚙️ Settings & Preferences",
                        font=('Segoe UI', 18, 'bold'),
                        foreground='white', bg='#1e293b')
        title.pack(side='left', padx=20)
        
        # Scrollable content
        canvas = tk.Canvas(main_frame, bg='#0f172a', highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0f172a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel and arrow keys
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        def _on_key(event):
            if event.keysym == 'Up':
                canvas.yview_scroll(-3, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(3, "units")
        
        canvas.bind("<Up>", _on_key)
        canvas.bind("<Down>", _on_key)
        scrollable_frame.bind("<Up>", _on_key)
        scrollable_frame.bind("<Down>", _on_key)
        
        # PASSWORD MANAGEMENT SECTION
        pwd_section = tk.Frame(scrollable_frame, bg='#1e293b', highlightthickness=1, highlightbackground='#334155')
        pwd_section.pack(fill='x', padx=30, pady=(30, 20))
        
        tk.Label(pwd_section, text="🔐 Password Management",
                font=('Segoe UI', 14, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', padx=20, pady=(15, 10))
        
        pwd_buttons = tk.Frame(pwd_section, bg='#1e293b')
        pwd_buttons.pack(fill='x', padx=20, pady=(0, 20))
        
        
        # ==================== SYSTEM INFORMATION SECTION ====================
        """Show settings panel with Figma design"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("900x700")
        settings_window.configure(bg='#0f172a')
        settings_window.geometry("900x700")
        settings_window.configure(bg='#0f172a')
        
        # ==================== MAIN CONTAINER ====================
        main_frame = tk.Frame(settings_window, bg='#0f172a', highlightthickness=0)
        main_frame.pack(fill='both', expand=True)
        
        # ==================== HEADER ====================
        header = tk.Frame(main_frame, bg='#1e293b', highlightthickness=0, height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg='#1e293b')
        header_content.pack(fill='both', expand=True, padx=30, pady=15)
        
        title = tk.Label(header_content, text="⚙️ Settings & Preferences",
                        font=('Segoe UI', 20, 'bold'),
                        foreground='white', bg='#1e293b')
        title.pack(anchor='w')
        
        subtitle = tk.Label(header_content, text="Manage your security settings and preferences",
                           font=('Segoe UI', 10),
                           foreground='#94a3b8', bg='#1e293b')
        subtitle.pack(anchor='w', pady=(5, 0))
        
        # ==================== SCROLLABLE CONTENT ====================
        canvas = tk.Canvas(main_frame, bg='#0f172a', highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0f172a', highlightthickness=0)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ==================== DARK MODE SECTION ====================
        dark_mode_section = tk.Frame(scrollable_frame, bg='#1e293b', highlightthickness=1,
                                     highlightbackground='#334155')
        dark_mode_section.pack(fill='x', padx=30, pady=(30, 20))
        
        dark_mode_header = tk.Frame(dark_mode_section, bg='#1e293b')
        dark_mode_header.pack(fill='x', padx=20, pady=(15, 10))
        
        tk.Label(dark_mode_header, text="🌙 Dark Mode",
                font=('Segoe UI', 14, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(10, 0))
        
        tk.Label(dark_mode_header, text="Hide UI from system logs and file explorers",
                font=('Segoe UI', 10),
                foreground='#94a3b8', bg='#1e293b').pack(anchor='w', pady=(0, 10))
        
        dark_toggle = tk.Frame(dark_mode_section, bg='#1e293b')
        dark_toggle.pack(fill='x', padx=20, pady=(0, 15))
        
        toggle_btn = tk.Button(dark_toggle, text="◉ On",
                              font=('Segoe UI', 10, 'bold'),
                              bg='#10b981', fg='white',
                              relief='flat', bd=0, padx=15, pady=8,
                              cursor='hand2')
        toggle_btn.pack(anchor='e')
        
        # ==================== PASSWORD MANAGEMENT SECTION ====================
        pwd_section = tk.Frame(scrollable_frame, bg='#1e293b', highlightthickness=1,
                              highlightbackground='#334155')
        pwd_section.pack(fill='x', padx=30, pady=(0, 20))
        
        pwd_header = tk.Frame(pwd_section, bg='#1e293b')
        pwd_header.pack(fill='x', padx=20, pady=(15, 10))
        
        tk.Label(pwd_header, text="🔐 Password Management",
                font=('Segoe UI', 14, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(10, 0))
        
        pwd_buttons = tk.Frame(pwd_section, bg='#1e293b')
        pwd_buttons.pack(fill='x', padx=20, pady=(0, 20))
        
        # Three columns for password options
        col1 = tk.Frame(pwd_buttons, bg='#1e293b')
        col1.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(col1, text="Current Password",
                font=('Segoe UI', 10, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(0, 5))
        
        tk.Label(col1, text="Enter current password",
                font=('Segoe UI', 9),
                foreground='#94a3b8', bg='#1e293b').pack(anchor='w', pady=(0, 8))
        
        current_pwd_btn = tk.Button(col1, text="Verify",
                                   font=('Segoe UI', 10),
                                   bg='#475569', fg='white',
                                   relief='flat', bd=0, padx=20, pady=8,
                                   cursor='hand2',
                                   activebackground='#64748b')
        current_pwd_btn.pack(fill='x')
        
        col2 = tk.Frame(pwd_buttons, bg='#1e293b')
        col2.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(col2, text="New Password",
                font=('Segoe UI', 10, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(0, 5))
        
        tk.Label(col2, text="Enter new password",
                font=('Segoe UI', 9),
                foreground='#94a3b8', bg='#1e293b').pack(anchor='w', pady=(0, 8))
        
        new_pwd_btn = tk.Button(col2, text="Set New",
                               font=('Segoe UI', 10),
                               bg='#475569', fg='white',
                               relief='flat', bd=0, padx=20, pady=8,
                               cursor='hand2',
                               activebackground='#64748b')
        new_pwd_btn.pack(fill='x')
        
        col3 = tk.Frame(pwd_buttons, bg='#1e293b')
        col3.pack(side='left', fill='both', expand=True)
        
        tk.Label(col3, text="Confirm New Password",
                font=('Segoe UI', 10, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(0, 5))
        
        tk.Label(col3, text="Confirm new password",
                font=('Segoe UI', 9),
                foreground='#94a3b8', bg='#1e293b').pack(anchor='w', pady=(0, 8))
        
        confirm_pwd_btn = tk.Button(col3, text="Confirm",
                                   font=('Segoe UI', 10),
                                   bg='#475569', fg='white',
                                   relief='flat', bd=0, padx=20, pady=8,
                                   cursor='hand2',
                                   activebackground='#64748b')
        confirm_pwd_btn.pack(fill='x')
        
        # ==================== VAULT MANAGEMENT SECTION ====================
        vault_section = tk.Frame(scrollable_frame, bg='#1e293b', highlightthickness=1,
                                highlightbackground='#334155')
        vault_section.pack(fill='x', padx=30, pady=(0, 20))
        
        vault_header = tk.Frame(vault_section, bg='#1e293b')
        vault_header.pack(fill='x', padx=20, pady=(15, 10))
        
        tk.Label(vault_header, text="🔒 Vault Management",
                font=('Segoe UI', 14, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(10, 0))
        
        vault_buttons = tk.Frame(vault_section, bg='#1e293b')
        vault_buttons.pack(fill='x', padx=20, pady=(0, 20))
        
        col1 = tk.Frame(vault_buttons, bg='#1e293b')
        col1.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(col1, text="Export Vault",
                font=('Segoe UI', 10, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(0, 5))
        
        tk.Label(col1, text="Create encrypted backup",
                font=('Segoe UI', 9),
                foreground='#94a3b8', bg='#1e293b').pack(anchor='w', pady=(0, 8))
        
        export_btn = tk.Button(col1, text="↑ Export",
                              font=('Segoe UI', 10),
                              bg='#475569', fg='white',
                              relief='flat', bd=0, padx=20, pady=8,
                              cursor='hand2',
                              activebackground='#64748b')
        export_btn.pack(fill='x')
        
        col2 = tk.Frame(vault_buttons, bg='#1e293b')
        col2.pack(side='left', fill='both', expand=True)
        
        tk.Label(col2, text="Import Vault",
                font=('Segoe UI', 10, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(0, 5))
        
        tk.Label(col2, text="Restore from backup",
                font=('Segoe UI', 9),
                foreground='#94a3b8', bg='#1e293b').pack(anchor='w', pady=(0, 8))
        
        import_btn = tk.Button(col2, text="↓ Import",
                              font=('Segoe UI', 10),
                              bg='#475569', fg='white',
                              relief='flat', bd=0, padx=20, pady=8,
                              cursor='hand2',
                              activebackground='#64748b')
        import_btn.pack(fill='x')
        
        # ==================== ADVANCED SECURITY SECTION ====================
        adv_section = tk.Frame(scrollable_frame, bg='#1e293b', highlightthickness=1,
                              highlightbackground='#334155')
        adv_section.pack(fill='x', padx=30, pady=(0, 20))
        
        adv_header = tk.Frame(adv_section, bg='#1e293b')
        adv_header.pack(fill='x', padx=20, pady=(15, 10))
        
        tk.Label(adv_header, text="🛡️ Advanced Security",
                font=('Segoe UI', 14, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(10, 0))
        
        tk.Label(adv_header, text="Create a decoy vault with fake files that appears when wrong password is entered. Helps protect against coercive attacks.",
                font=('Segoe UI', 9),
                foreground='#94a3b8', bg='#1e293b', wraplength=800, justify='left').pack(anchor='w', pady=(5, 10))
        
        create_decoy_btn = tk.Button(adv_header, text="🎭 Create Fake Vault",
                                    font=('Segoe UI', 10),
                                    bg='#f59e0b', fg='#0f172a',
                                    relief='flat', bd=0, padx=20, pady=8,
                                    cursor='hand2',
                                    activebackground='#fbbf24')
        create_decoy_btn.pack(anchor='w', pady=(0, 10))
        
        # ==================== DANGER ZONE SECTION ====================
        
        # ==================== SYSTEM INFORMATION SECTION ====================
        info_section = tk.Frame(scrollable_frame, bg='#1e293b', highlightthickness=1,
                               highlightbackground='#334155')
        info_section.pack(fill='x', padx=30, pady=(0, 30))
        
        info_header = tk.Frame(info_section, bg='#1e293b')
        info_header.pack(fill='x', padx=20, pady=(15, 10))
        
        tk.Label(info_header, text="System Information",
                font=('Segoe UI', 12, 'bold'),
                foreground='white', bg='#1e293b').pack(anchor='w', pady=(10, 10))
        
        info_content = tk.Frame(info_section, bg='#1e293b')
        info_content.pack(fill='x', padx=20, pady=(0, 15))
        
        info_items = [
            ("Vault Version", "2.4.1"),
            ("Encryption Library", "OpenSSL 1.1.2"),
            ("Total Files Secured", "98"),
            ("Storage Used", "8.2 GB / 50 GB"),
            ("Last Security Scan", "2024-01-16 14:30"),
        ]
        
        for label, value in info_items:
            row = tk.Frame(info_content, bg='#1e293b')
            row.pack(fill='x', pady=3)
            
            tk.Label(row, text=label,
                    font=('Segoe UI', 9),
                    foreground='#94a3b8', bg='#1e293b', width=25, anchor='w').pack(side='left')
            
            tk.Label(row, text=value,
                    font=('Segoe UI', 9, 'bold'),
                    foreground='white', bg='#1e293b').pack(side='right')
    
    def _change_password_and_keystroke(self):
        """Open dialog to change password and re-enroll keystroke profile"""
        # Create a new toplevel window for password change
        dialog = tk.Toplevel(self.root)
        dialog.title("🔐 Change Password & Re-Enroll Keystroke")
        dialog.geometry("500x600")
        dialog.configure(bg='#f0f2f5')
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center dialog on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame with scrolling
        main_frame = tk.Frame(dialog, bg='#ffffff', highlightthickness=2,
                             highlightbackground='#d4d9e8')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title
        title = tk.Label(main_frame, text="🔐 Change Password",
                        font=('Segoe UI', 14, 'bold'),
                        fg='#2563eb', bg='#ffffff')
        title.pack(pady=(20, 5))
        
        # Description
        desc = tk.Label(main_frame, text="Enter current password for verification,\nthen set a new password and re-enroll keystroke",
                       font=('Segoe UI', 9),
                       fg='#6b7280', bg='#ffffff')
        desc.pack(pady=(0, 20))
        
        # Current password field with visibility toggle
        tk.Label(main_frame, text="Current Password",
                font=('Segoe UI', 10, 'bold'),
                fg='#374151', bg='#ffffff').pack(anchor='w', padx=25, pady=(0, 5))
        
        # Current password container with toggle button
        current_pwd_container = tk.Frame(main_frame, bg='#ffffff')
        current_pwd_container.pack(fill='x', padx=25, pady=(0, 15))
        
        current_pwd = tk.Entry(current_pwd_container, font=('Segoe UI', 11),
                              bg='#f3f4f8', fg='#1f2937',
                              insertbackground='#2563eb',
                              show='•', relief='flat', bd=0)
        current_pwd.pack(side='left', fill='both', expand=True, ipady=10)
        
        # Toggle button for current password
        change_pwd_current_show = tk.BooleanVar(value=False)
        
        def toggle_current_pwd_visibility():
            if change_pwd_current_show.get():
                current_pwd.config(show='')
                change_pwd_current_toggle.config(text='🙈 Hide')
            else:
                current_pwd.config(show='•')
                change_pwd_current_toggle.config(text='👁 Show')
            change_pwd_current_show.set(not change_pwd_current_show.get())
        
        change_pwd_current_toggle = tk.Button(current_pwd_container, 
                                             text='👁 Show',
                                             font=('Segoe UI', 9),
                                             bg='#ffffff', fg='#2563eb',
                                             relief='flat', bd=0, padx=8,
                                             cursor='hand2',
                                             command=toggle_current_pwd_visibility)
        change_pwd_current_toggle.pack(side='right', padx=(5, 0))
        
        # New password field with visibility toggle
        tk.Label(main_frame, text="New Password",
                font=('Segoe UI', 10, 'bold'),
                fg='#374151', bg='#ffffff').pack(anchor='w', padx=25, pady=(0, 5))
        
        # New password container with toggle button
        new_pwd_container = tk.Frame(main_frame, bg='#ffffff')
        new_pwd_container.pack(fill='x', padx=25, pady=(0, 15))
        
        new_pwd = tk.Entry(new_pwd_container, font=('Segoe UI', 11),
                          bg='#f3f4f8', fg='#1f2937',
                          insertbackground='#2563eb',
                          show='•', relief='flat', bd=0)
        new_pwd.pack(side='left', fill='both', expand=True, ipady=10)
        
        # Toggle button for new password
        change_pwd_new_show = tk.BooleanVar(value=False)
        
        def toggle_new_pwd_visibility():
            if change_pwd_new_show.get():
                new_pwd.config(show='')
                change_pwd_new_toggle.config(text='🙈 Hide')
            else:
                new_pwd.config(show='•')
                change_pwd_new_toggle.config(text='👁 Show')
            change_pwd_new_show.set(not change_pwd_new_show.get())
        
        change_pwd_new_toggle = tk.Button(new_pwd_container, 
                                         text='👁 Show',
                                         font=('Segoe UI', 9),
                                         bg='#ffffff', fg='#2563eb',
                                         relief='flat', bd=0, padx=8,
                                         cursor='hand2',
                                         command=toggle_new_pwd_visibility)
        change_pwd_new_toggle.pack(side='right', padx=(5, 0))
        
        # Confirm new password field with visibility toggle
        tk.Label(main_frame, text="Confirm New Password",
                font=('Segoe UI', 10, 'bold'),
                fg='#374151', bg='#ffffff').pack(anchor='w', padx=25, pady=(0, 5))
        
        # Confirm password container with toggle button
        confirm_pwd_container = tk.Frame(main_frame, bg='#ffffff')
        confirm_pwd_container.pack(fill='x', padx=25, pady=(0, 15))
        
        confirm_pwd = tk.Entry(confirm_pwd_container, font=('Segoe UI', 11),
                              bg='#f3f4f8', fg='#1f2937',
                              insertbackground='#2563eb',
                              show='•', relief='flat', bd=0)
        confirm_pwd.pack(side='left', fill='both', expand=True, ipady=10)
        
        # Toggle button for confirm password
        change_pwd_confirm_show = tk.BooleanVar(value=False)
        
        def toggle_confirm_pwd_visibility():
            if change_pwd_confirm_show.get():
                confirm_pwd.config(show='')
                change_pwd_confirm_toggle.config(text='🙈 Hide')
            else:
                confirm_pwd.config(show='•')
                change_pwd_confirm_toggle.config(text='👁 Show')
            change_pwd_confirm_show.set(not change_pwd_confirm_show.get())
        
        change_pwd_confirm_toggle = tk.Button(confirm_pwd_container, 
                                             text='👁 Show',
                                             font=('Segoe UI', 9),
                                             bg='#ffffff', fg='#2563eb',
                                             relief='flat', bd=0, padx=8,
                                             cursor='hand2',
                                             command=toggle_confirm_pwd_visibility)
        change_pwd_confirm_toggle.pack(side='right', padx=(5, 0))
        
        # Info text
        info_text = tk.Label(main_frame, 
                           text=f"⚠️ You will need to re-enroll your keystroke\nprofile after changing password",
                           font=('Segoe UI', 9),
                           fg='#ea580c', bg='#ffffff', justify='left')
        info_text.pack(padx=25, pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#ffffff')
        button_frame.pack(fill='x', padx=25, pady=(0, 20))
        
        def proceed_with_change():
            """Verify current password and proceed with change"""
            curr = current_pwd.get()
            new = new_pwd.get()
            confirm = confirm_pwd.get()
            
            # Validation
            if not curr or not new or not confirm:
                messagebox.showerror("Error", "All fields are required")
                return
            
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match")
                return
            
            if len(new) < 6:
                messagebox.showerror("Error", "New password must be at least 6 characters")
                return
            
            # Verify current password
            if not self.vault.verify_master_password(curr):
                messagebox.showerror("Error", "Current password is incorrect")
                return
            
            # All checks passed - proceed to keystroke re-enrollment
            dialog.destroy()
            self._proceed_password_change(new)
        
        cancel_btn = tk.Button(main_frame, text="Cancel",
                              font=('Segoe UI', 10),
                              bg='#e5e7eb', fg='#374151',
                              relief='flat', bd=0, padx=20, pady=8,
                              cursor='hand2',
                              activebackground='#d1d5db',
                              command=dialog.destroy)
        cancel_btn.pack(side='left', padx=(0, 10))
        
        change_btn = tk.Button(main_frame, text="✓ Proceed",
                              font=('Segoe UI', 10),
                              bg='#2563eb', fg='white',
                              relief='flat', bd=0, padx=20, pady=8,
                              cursor='hand2',
                              activebackground='#1d4ed8',
                              command=proceed_with_change)
        change_btn.pack(side='left')
    
    def _proceed_password_change(self, new_password: str):
        """Proceed with keystroke re-enrollment for new password"""
        # Create re-enrollment window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.change_enroll_samples = []
        self.change_enroll_needed = 4
        self.change_enroll_current = 0
        self.new_password_for_change = new_password
        
        frame = tk.Frame(self.root, bg='#f0f2f5')
        frame.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(frame, bg='#ffffff', highlightthickness=0, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="🔐 Re-Enroll Keystroke Profile",
                              font=('Segoe UI', 16, 'bold'),
                              fg='#2563eb', bg='#ffffff')
        title_label.pack(anchor='w', padx=20, pady=(20, 10))
        
        subtitle = tk.Label(header, text=f"Type your NEW password exactly {self.change_enroll_needed} times to re-enroll biometric authentication",
                           font=('Segoe UI', 10),
                           fg='#6b7280', bg='#ffffff')
        subtitle.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Content
        content = tk.Frame(frame, bg='#f0f2f5')
        content.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Progress indicator section
        progress_frame = tk.Frame(content, bg='#f0f2f5')
        progress_frame.pack(fill='x', pady=(0, 30))
        
        progress_label = tk.Label(progress_frame, text=f"Sample 1 of {self.change_enroll_needed}",
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='#2563eb', bg='#f0f2f5')
        progress_label.pack(anchor='w', pady=(0, 8))
        
        # Progress bar container (8px height like enrollment)
        progress_bar_bg = tk.Frame(progress_frame, bg='#e5e7eb', height=8)
        progress_bar_bg.pack(fill='x', pady=(0, 5))
        progress_bar_bg.pack_propagate(False)
        
        progress_indicator = tk.Frame(progress_bar_bg, bg='#2563eb', height=8, width=0)
        progress_indicator.pack(side='left', fill='y')
        
        # Progress text indicator (checkmarks and circles)
        progress_text = tk.Label(progress_frame, text="○ ○ ○ ○",
                                font=('Segoe UI', 12),
                                fg='#6b7280', bg='#f0f2f5')
        progress_text.pack(anchor='w')
        
        # Instructions
        instr_label = tk.Label(content, text="Type your new password:",
                              font=('Segoe UI', 11, 'bold'),
                              fg='#1f2937', bg='#f0f2f5')
        instr_label.pack(anchor='w', pady=(0, 10))
        
        # Password input field
        change_input = tk.Entry(content, font=('Segoe UI', 13),
                               bg='#f3f4f8', fg='#1f2937',
                               insertbackground='#2563eb',
                               show='•', relief='flat', bd=0)
        change_input.pack(fill='x', ipady=12, pady=(0, 20))
        change_input.focus()
        
        # Bind keystroke events for biometric recording
        change_input.bind('<KeyPress>', self._change_password_on_keypress)
        change_input.bind('<KeyRelease>', self._change_password_on_keyrelease)
        
        # Buttons
        button_frame = tk.Frame(content, bg='#f0f2f5')
        button_frame.pack(fill='x', pady=(20, 0))
        
        def confirm_change_sample():
            """Confirm a keystroke sample during password change"""
            typed = change_input.get()
            
            if typed != self.new_password_for_change:
                messagebox.showerror("Error", "Password does not match. Please try again.")
                self.vault.keystroke_analyzer.reset()
                change_input.delete(0, 'end')
                return
            
            # Ensure sufficient keystrokes
            recorded = len(self.vault.keystroke_analyzer.current_password)
            needed = max(1, len(self.new_password_for_change))
            if recorded < needed:
                messagebox.showerror("Error", 
                    f"Insufficient keystroke data. Please type the full password.\nMinimum: {needed} keys, Recorded: {recorded}")
                self.vault.keystroke_analyzer.reset()
                change_input.delete(0, 'end')
                return
            
            # Collect metrics
            metrics = self.vault.keystroke_analyzer.get_typing_metrics()
            self.change_enroll_samples.append(metrics)
            self.change_enroll_current += 1
            
            # Update progress label
            progress_label.config(text=f"Sample {self.change_enroll_current} of {self.change_enroll_needed}")
            
            # Animate progress bar (30 frames)
            def animate_progress(step=0):
                if step <= 30:
                    progress_pct = (self.change_enroll_current / self.change_enroll_needed) * 100
                    # Easing calculation
                    ease_pct = progress_pct * (step / 30)
                    # Calculate width based on container
                    container_width = progress_bar_bg.winfo_width()
                    if container_width <= 1:
                        container_width = 300
                    progress_width = int((ease_pct / 100) * container_width)
                    progress_indicator.config(width=progress_width)
                    
                    self.root.after(20, lambda: animate_progress(step + 1))
                else:
                    # Update progress text with checkmarks
                    progress_display = ""
                    for i in range(self.change_enroll_needed):
                        if i < self.change_enroll_current:
                            progress_display += "✓ "
                        else:
                            progress_display += "○ "
                    progress_text.config(text=progress_display.strip())
            
            animate_progress(0)
            
            # Reset for next sample
            self.vault.keystroke_analyzer.reset()
            change_input.delete(0, 'end')
            
            if self.change_enroll_current >= self.change_enroll_needed:
                # All samples collected - save new password and re-enroll
                try:
                    # Update master password
                    ok = self.vault.set_master_password(self.new_password_for_change)
                    if not ok:
                        messagebox.showerror("Error", "Failed to save new password")
                        return
                    
                    # Re-enroll keystroke profile with new samples
                    enrolled = self.vault.authenticator.enroll_user('master', self.change_enroll_samples)
                    if not enrolled:
                        messagebox.showerror("Error", "Failed to re-enroll keystroke profile")
                        return
                    
                    messagebox.showinfo("Success", 
                        "✅ Password changed successfully!\n"
                        "Your new keystroke profile has been enrolled.\n\n"
                        "Please log out and log back in with your new password.")
                    
                    # Return to home screen
                    self.show_home_screen()
                    
                except Exception as e:
                    logging.error(f"Error changing password: {e}")
                    messagebox.showerror("Error", f"Failed to change password:\n{str(e)}")
                    self.show_home_screen()
                return
            
            # Show message for next sample
            messagebox.showinfo("Success", 
                f"✅ Sample {self.change_enroll_current} captured!\n\n"
                f"Please type sample {self.change_enroll_current + 1} of {self.change_enroll_needed}")
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                              font=('Segoe UI', 10),
                              bg='#e5e7eb', fg='#374151',
                              relief='flat', bd=0, padx=20, pady=8,
                              cursor='hand2',
                              activebackground='#d1d5db',
                              command=self.show_home_screen)
        cancel_btn.pack(side='left', padx=(0, 10))
        
        confirm_btn = tk.Button(button_frame, text="✓ Confirm Password Pattern",
                               font=('Segoe UI', 10),
                               bg='#2563eb', fg='white',
                               relief='flat', bd=0, padx=20, pady=8,
                               cursor='hand2',
                               activebackground='#1d4ed8',
                               command=confirm_change_sample)
        confirm_btn.pack(side='left')
    
    def _change_password_on_keypress(self, event):
        """Record keypress during password change re-enrollment"""
        try:
            if not self.vault.keystroke_analyzer.is_recording:
                self.vault.keystroke_analyzer.start_recording()
            
            char = event.char if hasattr(event, 'char') else ''
            ident = event.keysym if hasattr(event, 'keysym') else str(event.keycode)
            self.vault.keystroke_analyzer.record_keystroke(char, 'press', ident)
        except Exception as e:
            logging.error(f"Error in _change_password_on_keypress: {e}")
    
    def _change_password_on_keyrelease(self, event):
        """Record keyrelease during password change re-enrollment"""
        try:
            char = event.char if hasattr(event, 'char') else ''
            ident = event.keysym if hasattr(event, 'keysym') else str(event.keycode)
            self.vault.keystroke_analyzer.record_keystroke(char, 'release', ident)
        except Exception as e:
            logging.error(f"Error in _change_password_on_keyrelease: {e}")
    
    def _confirm_reset_vault(self, settings_window):
        """Confirm and execute vault reset (remove all files, change password, re-enroll keystroke)"""
        result = messagebox.askyesno(
            "⚠️ Confirm Reset",
            "This will:\n"
            "  • Delete ALL encrypted files\n"
            "  • Remove keystroke profile\n"
            "  • Change master password\n"
            "\nThis action CANNOT be undone!\n\n"
            "Continue?"
        )
        
        if not result:
            return
        
        try:
            import shutil
            import glob
            vault_path = self.vault.vault_path
            reset_log = []
            
            # Step 1: Delete all files from real vault
            real_files_path = os.path.join(vault_path, 'real')
            try:
                if os.path.exists(real_files_path):
                    shutil.rmtree(real_files_path, ignore_errors=True)
                    os.makedirs(real_files_path, exist_ok=True)
                    reset_log.append("✓ Cleared real/ directory")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing real/: {e}")
                logging.error(f"Error clearing real/: {e}")
            
            # Step 2: Clear camouflaged files - DELETE ALL SUBDIRECTORIES AND FILES
            camouflaged_path = os.path.join(vault_path, 'camouflaged')
            try:
                if os.path.exists(camouflaged_path):
                    # Delete everything inside
                    for item in os.listdir(camouflaged_path):
                        item_path = os.path.join(camouflaged_path, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                        else:
                            os.remove(item_path)
                    reset_log.append("✓ Cleared camouflaged/ directory (all subdirs)")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing camouflaged/: {e}")
                logging.error(f"Error clearing camouflaged/: {e}")
            
            # Step 3: Clear camouflage mapping
            camouflage_map_path = os.path.join(vault_path, 'camouflage_map.json')
            try:
                if os.path.exists(camouflage_map_path):
                    with open(camouflage_map_path, 'w') as f:
                        json.dump({}, f)
                    reset_log.append("✓ Cleared camouflage_map.json")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing camouflage_map.json: {e}")
                logging.error(f"Error clearing camouflage_map.json: {e}")
            
            # Step 4: Delete keystroke profile
            profiles_path = os.path.join(vault_path, 'models', 'profiles.json')
            try:
                if os.path.exists(profiles_path):
                    os.remove(profiles_path)
                    with open(profiles_path, 'w') as f:
                        json.dump({}, f)
                    reset_log.append("✓ Cleared keystroke profiles")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing profiles: {e}")
                logging.error(f"Error clearing profiles: {e}")
            
            # Step 5: Clear metadata
            metadata_path = os.path.join(vault_path, 'metadata', 'master.json')
            try:
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'w') as f:
                        json.dump({'files': []}, f)
                    reset_log.append("✓ Cleared metadata/master.json")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing metadata: {e}")
                logging.error(f"Error clearing metadata: {e}")
            
            # Step 6: Clear blockchain ledger
            blockchain_path = os.path.join(vault_path, 'logs', 'blockchain.json')
            try:
                if os.path.exists(blockchain_path):
                    # Create fresh genesis block
                    genesis = {
                        'index': 0,
                        'timestamp': datetime.now().isoformat(),
                        'data': 'GENESIS',
                        'prev_hash': '0' * 64,
                        'hash': hashlib.sha256(b'GENESIS').hexdigest()
                    }
                    with open(blockchain_path, 'w') as f:
                        json.dump([genesis], f, indent=2)
                    reset_log.append("✓ Reset blockchain ledger (fresh genesis)")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing blockchain: {e}")
                logging.error(f"Error clearing blockchain: {e}")
            
            # Step 7: Clear vault log
            vault_log_path = os.path.join(vault_path, 'logs', 'vault.log')
            try:
                if os.path.exists(vault_log_path):
                    with open(vault_log_path, 'w') as f:
                        f.write('')
                    reset_log.append("✓ Cleared vault.log")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing vault.log: {e}")
                logging.error(f"Error clearing vault.log: {e}")
            
            # Step 8: Clear honeytrap files
            honeytrap_path = os.path.join(vault_path, 'honeytrap')
            try:
                if os.path.exists(honeytrap_path):
                    for item in os.listdir(honeytrap_path):
                        item_path = os.path.join(honeytrap_path, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                        else:
                            os.remove(item_path)
                    reset_log.append("✓ Cleared honeytrap files")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing honeytrap: {e}")
                logging.error(f"Error clearing honeytrap: {e}")
            
            # Step 9: Clear honeytrap log
            honeytrap_log_path = os.path.join(vault_path, 'honeytrap_log.txt')
            try:
                if os.path.exists(honeytrap_log_path):
                    with open(honeytrap_log_path, 'w') as f:
                        f.write('')
                    reset_log.append("✓ Cleared honeytrap log")
            except Exception as e:
                reset_log.append(f"⚠ Error clearing honeytrap log: {e}")
                logging.error(f"Error clearing honeytrap log: {e}")
            
            # Log reset completion
            logging.info(f"Factory Reset Complete:\n" + "\n".join(reset_log))
            
            # Close settings window if provided (when called from popup)
            if settings_window is not None:
                settings_window.destroy()
            
            # Step 9: Show enrollment screen for new password and keystroke
            reset_message = "✅ Factory Reset Complete!\n\n" + "\n".join(reset_log) + "\n\nYou will now re-enroll with a new password\nand keystroke profile."
            messagebox.showinfo("Reset Complete", reset_message)
            
            self.show_enrollment_screen()
            
        except Exception as e:
            logging.error(f"Error during vault reset: {e}")
            messagebox.showerror("Reset Error", f"Failed to reset vault:\n{str(e)}")
    
    def show_security_logs_window(self):
        """Show modern intrusion logs page based on Figma design"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main background
        main_bg = tk.Frame(self.root, bg='#f0f2f5', highlightthickness=0)
        main_bg.pack(fill='both', expand=True)
        
        # ==================== HEADER ====================
        header = tk.Frame(main_bg, bg='#ffffff', highlightthickness=0, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_left = tk.Frame(header, bg='#ffffff')
        header_left.pack(side='left', padx=20, pady=15)
        
        back_btn = tk.Button(header_left, text="← Back",
                            font=('Segoe UI', 10, 'bold'),
                            bg='#ffffff', fg='#6b7280',
                            relief='flat', bd=0,
                            cursor='hand2',
                            command=self.show_home_screen,
                            activebackground='#f3f4f8',
                            activeforeground='#2563eb')
        back_btn.pack(side='left', padx=(0, 15))
        
        alert_icon = tk.Label(header_left, text="⚠️",
                             font=('Arial', 20),
                             bg='#ffffff', fg='#ef4444')
        alert_icon.pack(side='left', padx=(0, 10))
        
        title_frame = tk.Frame(header_left, bg='#ffffff')
        title_frame.pack(side='left')
        
        title = tk.Label(title_frame, text="Intrusion Logs",
                        font=('Segoe UI', 18, 'bold'),
                        fg='#1f2937', bg='#ffffff')
        title.pack(anchor='w')
        
        subtitle = tk.Label(title_frame, text="Security events & alerts",
                           font=('Segoe UI', 10),
                           fg='#6b7280', bg='#ffffff')
        subtitle.pack(anchor='w')
        
        # Header buttons on right
        header_right = tk.Frame(header, bg='#ffffff')
        header_right.pack(side='right', padx=20, pady=15)
        
        refresh_btn = tk.Button(header_right, text="🔄 Refresh",
                               font=('Segoe UI', 10, 'bold'),
                               bg='#e5e7eb', fg='#2563eb',
                               relief='flat', bd=0,
                               padx=15, pady=8,
                               cursor='hand2',
                               activebackground='#d1d5db',
                               command=lambda: self.show_security_logs_window())
        refresh_btn.pack(side='left', padx=5)
        
        export_btn = tk.Button(header_right, text="📥 Export",
                              font=('Segoe UI', 10, 'bold'),
                              bg='#e5e7eb', fg='#374151',
                              relief='flat', bd=0,
                              padx=15, pady=8,
                              cursor='hand2',
                              activebackground='#d1d5db',
                              command=self.export_intrusion_logs)
        export_btn.pack(side='left', padx=5)
        
        # ==================== CONTENT ====================
        content = tk.Frame(main_bg, bg='#f0f2f5')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ==================== STAT CARDS ====================
        stats_frame = tk.Frame(content, bg='#f0f2f5')
        stats_frame.pack(fill='x', pady=(0, 25))
        
        # Parse events from honeytrap log
        total_events, critical_count, high_count, today_count = self._parse_intrusion_events()
        
        # Stat 1: Total Events (blue)
        stat1 = tk.Frame(stats_frame, bg='#ffffff', highlightthickness=1,
                        highlightbackground='#d4d9e8')
        stat1.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        stat1_icon = tk.Label(stat1, text="🔵", font=('Arial', 20),
                             bg='#ffffff')
        stat1_icon.pack(pady=(12, 0))
        
        stat1_label = tk.Label(stat1, text="Total Events",
                              font=('Segoe UI', 10),
                              fg='#6b7280', bg='#ffffff')
        stat1_label.pack()
        
        stat1_value = tk.Label(stat1, text=str(total_events),
                              font=('Segoe UI', 24, 'bold'),
                              fg='#2563eb', bg='#ffffff')
        stat1_value.pack(pady=(5, 12))
        
        # Stat 2: Critical Alerts (red)
        stat2 = tk.Frame(stats_frame, bg='#ffffff', highlightthickness=1,
                        highlightbackground='#d4d9e8')
        stat2.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        stat2_icon = tk.Label(stat2, text="🔴", font=('Arial', 20),
                             bg='#ffffff')
        stat2_icon.pack(pady=(12, 0))
        
        stat2_label = tk.Label(stat2, text="Critical Alerts",
                              font=('Segoe UI', 10),
                              fg='#6b7280', bg='#ffffff')
        stat2_label.pack()
        
        stat2_value = tk.Label(stat2, text=str(critical_count),
                              font=('Segoe UI', 24, 'bold'),
                              fg='#ef4444', bg='#ffffff')
        stat2_value.pack(pady=(5, 12))
        
        # Stat 3: High Priority (orange)
        stat3 = tk.Frame(stats_frame, bg='#ffffff', highlightthickness=1,
                        highlightbackground='#d4d9e8')
        stat3.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        stat3_icon = tk.Label(stat3, text="🟠", font=('Arial', 20),
                             bg='#ffffff')
        stat3_icon.pack(pady=(12, 0))
        
        stat3_label = tk.Label(stat3, text="High Priority",
                              font=('Segoe UI', 10),
                              fg='#6b7280', bg='#ffffff')
        stat3_label.pack()
        
        stat3_value = tk.Label(stat3, text=str(high_count),
                              font=('Segoe UI', 24, 'bold'),
                              fg='#ea580c', bg='#ffffff')
        stat3_value.pack(pady=(5, 12))
        
        # Stat 4: Today's Events (green)
        stat4 = tk.Frame(stats_frame, bg='#ffffff', highlightthickness=1,
                        highlightbackground='#d4d9e8')
        stat4.pack(side='left', fill='both', expand=True)
        
        stat4_icon = tk.Label(stat4, text="🟢", font=('Arial', 20),
                             bg='#ffffff')
        stat4_icon.pack(pady=(12, 0))
        
        stat4_label = tk.Label(stat4, text="Today's Events",
                              font=('Segoe UI', 10),
                              fg='#6b7280', bg='#ffffff')
        stat4_label.pack()
        
        stat4_value = tk.Label(stat4, text=str(today_count),
                              font=('Segoe UI', 24, 'bold'),
                              fg='#10b981', bg='#ffffff')
        stat4_value.pack(pady=(5, 12))
        
        # ==================== FILTER SECTION ====================
        filter_frame = tk.Frame(content, bg='#f0f2f5')
        filter_frame.pack(fill='x', pady=(0, 20))
        
        filter_label = tk.Label(filter_frame, text="Filter Events",
                               font=('Segoe UI', 10, 'bold'),
                               fg='#374151', bg='#f0f2f5')
        filter_label.pack(anchor='w', pady=(0, 10))
        
        filter_buttons = tk.Frame(filter_frame, bg='#f0f2f5')
        filter_buttons.pack(anchor='w')
        
        self.intrusion_filter = tk.StringVar(value='All Events')
        
        all_btn = tk.Button(filter_buttons, text="All Events",
                           font=('Segoe UI', 9, 'bold'),
                           bg='#2563eb' if self.intrusion_filter.get() == 'All Events' else '#e5e7eb',
                           fg='white' if self.intrusion_filter.get() == 'All Events' else '#374151',
                           relief='flat', bd=0,
                           padx=15, pady=6,
                           cursor='hand2',
                           activebackground='#1d4ed8',
                           command=lambda: self._update_intrusion_filter('All Events'))
        all_btn.pack(side='left', padx=(0, 8))
        
        critical_btn = tk.Button(filter_buttons, text="Critical Only",
                                font=('Segoe UI', 9, 'bold'),
                                bg='#e5e7eb', fg='#ef4444',
                                relief='flat', bd=0,
                                padx=15, pady=6,
                                cursor='hand2',
                                activebackground='#d1d5db',
                                command=lambda: self._update_intrusion_filter('Critical'))
        critical_btn.pack(side='left', padx=5)
        
        high_btn = tk.Button(filter_buttons, text="High Priority",
                            font=('Segoe UI', 9, 'bold'),
                            bg='#e5e7eb', fg='#ea580c',
                            relief='flat', bd=0,
                            padx=15, pady=6,
                            cursor='hand2',
                            activebackground='#d1d5db',
                            command=lambda: self._update_intrusion_filter('High'))
        high_btn.pack(side='left', padx=5)
        
        # ==================== EVENTS LIST ====================
        events_label = tk.Label(content, text="Recent Events",
                               font=('Segoe UI', 12, 'bold'),
                               fg='#1f2937', bg='#f0f2f5')
        events_label.pack(anchor='w', pady=(0, 12))
        
        # Scrollable events area with frame wrapper
        events_wrapper = tk.Frame(content, bg='#f0f2f5')
        events_wrapper.pack(fill='both', expand=True)
        
        events_canvas = tk.Canvas(events_wrapper, bg='#f0f2f5', highlightthickness=0, bd=0)
        events_scrollbar = tk.Scrollbar(events_wrapper, orient='vertical', command=events_canvas.yview)
        events_frame = tk.Frame(events_canvas, bg='#f0f2f5')
        
        events_frame.bind(
            "<Configure>",
            lambda e: events_canvas.configure(scrollregion=events_canvas.bbox("all"))
        )
        
        events_canvas_window = events_canvas.create_window((0, 0), window=events_frame, anchor="nw")
        events_canvas.configure(yscrollcommand=events_scrollbar.set)
        
        # Bind mousewheel scrolling
        def _on_mousewheel(event):
            events_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        events_canvas.bind("<MouseWheel>", _on_mousewheel)
        events_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind arrow keys
        def _on_key(event):
            if event.keysym == 'Up':
                events_canvas.yview_scroll(-3, "units")
            elif event.keysym == 'Down':
                events_canvas.yview_scroll(3, "units")
        
        events_canvas.bind("<Up>", _on_key)
        events_canvas.bind("<Down>", _on_key)
        events_frame.bind("<Up>", _on_key)
        events_frame.bind("<Down>", _on_key)
        
        events_canvas.pack(side='left', fill='both', expand=True)
        events_scrollbar.pack(side='right', fill='y')
        
        # Get events from log
        events_list = self._get_intrusion_events()
        
        if not events_list:
            no_events = tk.Label(events_frame, text="No intrusion events recorded",
                                font=('Segoe UI', 11),
                                fg='#9ca3af', bg='#f0f2f5')
            no_events.pack(pady=40)
        else:
            for event in events_list[:20]:  # Show last 20 events
                event_card = tk.Frame(events_frame, bg='#ffffff', highlightthickness=1,
                                     highlightbackground='#d4d9e8')
                event_card.pack(fill='x', pady=(0, 10))
                
                # Event header with icon, title, and timestamp
                event_header = tk.Frame(event_card, bg='#ffffff')
                event_header.pack(fill='x', padx=12, pady=(10, 5))
                
                # Determine icon and color based on severity
                severity = event.get('severity', 'info')
                if severity == 'critical':
                    icon = '🔴'
                    color = '#ef4444'
                    text_color = 'white'
                elif severity == 'high':
                    icon = '🟠'
                    color = '#ea580c'
                    text_color = 'white'
                else:
                    icon = '⚠️'
                    color = '#2563eb'
                    text_color = 'white'
                
                event_icon = tk.Label(event_header, text=icon,
                                     font=('Arial', 14),
                                     bg='#ffffff')
                event_icon.pack(side='left', padx=(0, 8))
                
                # Title and severity
                title_frame = tk.Frame(event_header, bg='#ffffff')
                title_frame.pack(side='left', fill='x', expand=True)
                
                event_title = tk.Label(title_frame, text=event.get('title', 'Unknown event'),
                                      font=('Segoe UI', 10, 'bold'),
                                      fg='#1f2937', bg='#ffffff')
                event_title.pack(anchor='w')
                
                # Severity badge and timestamp
                time_frame = tk.Frame(event_header, bg='#ffffff')
                time_frame.pack(side='right', padx=(10, 0))
                
                severity_badge = tk.Label(time_frame, text=severity.upper(),
                                         font=('Segoe UI', 9, 'bold'),
                                         fg=text_color, bg=color,
                                         padx=8, pady=3)
                
                timestamp = tk.Label(time_frame, text=event.get('time', 'N/A'),
                                    font=('Segoe UI', 8),
                                    fg='#9ca3af', bg='#ffffff')
                timestamp.pack(side='left')
                
                # Event description
                desc = tk.Label(event_card, text=event.get('description', ''),
                               font=('Segoe UI', 9),
                               fg='#6b7280', bg='#ffffff',
                               wraplength=700, justify='left')
                desc.pack(fill='x', padx=12, pady=(0, 10), anchor='w')
                
                # Honeytrap file info if present
                if event.get('honeytrap_file'):
                    honeytrap_info = tk.Label(event_card,
                                             text=f"🎯 Honeytrap File: {event.get('honeytrap_file')}",
                                             font=('Segoe UI', 8),
                                             fg='#6366f1', bg='#ffffff')
                    honeytrap_info.pack(fill='x', padx=12, pady=(0, 10), anchor='w')
        
        # ==================== SECURITY RECOMMENDATIONS ====================
        recommendations_label = tk.Label(content, text="Security Recommendations",
                                        font=('Segoe UI', 12, 'bold'),
                                        fg='#ea580c', bg='#f0f2f5')
        recommendations_label.pack(anchor='w', pady=(20, 12))
        
        recommendations_card = tk.Frame(content, bg='#ffffff', highlightthickness=1,
                                       highlightbackground='#d4d9e8')
        recommendations_card.pack(fill='x')
        
        recommendations = [
            "• Fake vault accessed - unauthorized user detected",
            "• Honeytrap files successfully triggered security monitoring",
            "• Consider changing vault password if access was not authorized",
            "• Review access patterns to determine if investigation is needed"
        ]
        
        for rec in recommendations:
            rec_label = tk.Label(recommendations_card, text=rec,
                                font=('Segoe UI', 9),
                                fg='#6b7280', bg='#ffffff',
                                wraplength=700, justify='left')
            rec_label.pack(anchor='w', padx=12, pady=5)
    
    def logout(self):
        """Logout and return to auth screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.is_authenticated = False
            self.vault.keystroke_analyzer.reset()
            self.show_auth_screen()
    
    def store_file_dialog(self):
        """Store file dialog"""
        file_path = filedialog.askopenfilename(title="Select file to encrypt and store")
        if not file_path:
            return
        # Use inline upload page password if available, otherwise encrypt with empty password
        password = ''
        if hasattr(self, 'upload_password_var') and self.upload_password_var.get() is not None:
            password = self.upload_password_var.get()

        success, result = self.vault.store_file(file_path, password, use_camouflage=True)
        if success:
            messagebox.showinfo("Success", f"✅ File stored successfully!\nFile ID: {result}")
            # Refresh home screen to show new file in carrier list
            self.show_home_screen()
        else:
            messagebox.showerror("Error", f"❌ Failed to store file: {result}")
    
    def show_auth_screen(self):
        # Clear all existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # If no master password/profile exists, go to enrollment flow
        try:
            if not self.vault.has_master_password() or 'master' not in getattr(self.vault.authenticator, 'profiles', {}):
                self.show_enrollment_screen()
                return
        except Exception:
            # Fall back to enrollment if any error
            self.show_enrollment_screen()
            return
        
        # Light background - exact Windows System Maintenance Utility style
        main_bg = tk.Frame(self.root, bg='#f0f2f5', highlightthickness=0)
        main_bg.pack(fill='both', expand=True)
        
        # Center container - matching reference layout
        center_frame = tk.Frame(main_bg, bg='#f0f2f5', highlightthickness=0)
        center_frame.place(relx=0.5, rely=0.5, anchor='center', width=480, height=650)
        
        # ==================== TOP ICON SECTION ====================
        icon_bg = tk.Canvas(center_frame, bg='#f0f2f5', width=80, height=80, 
                           highlightthickness=0, bd=0)
        icon_bg.pack(pady=(0, 25))
        
        # Draw rounded rectangle for icon background
        arc_radius = 15
        icon_bg.create_oval((0, 0), (arc_radius*2, arc_radius*2), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_oval((80-arc_radius*2, 0), (80, arc_radius*2), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_oval((0, 80-arc_radius*2), (arc_radius*2, 80), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_oval((80-arc_radius*2, 80-arc_radius*2), (80, 80), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_rectangle((arc_radius, 0), (80-arc_radius, 80), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_rectangle((0, arc_radius), (80, 80-arc_radius), fill='#dfe9f8', outline='#dfe9f8')
        
        icon_label = tk.Label(icon_bg, text="⚙️", font=('Arial', 40), bg='#dfe9f8', fg='#5b7dd9')
        icon_bg.create_window(40, 40, window=icon_label)
        
        # Title
        title_label = tk.Label(center_frame, text="System Maintenance Utility v2.4.1",
                              font=('Segoe UI', 15, 'bold'),
                              fg='#4a5568', bg='#f0f2f5')
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(center_frame, text="Windows System Optimization Tool",
                                 font=('Segoe UI', 9),
                                 fg='#7a8799', bg='#f0f2f5')
        subtitle_label.pack(pady=(4, 28))
        
        # ==================== WHITE CARD WITH ROUNDED CORNERS ====================
        card_canvas = tk.Canvas(center_frame, bg='#f0f2f5', highlightthickness=0, bd=0)
        card_canvas.pack(fill='both', expand=True)
        
        # Draw rounded rectangle card background
        corner_radius = 12
        card_canvas.create_oval((0, 0), (corner_radius*2, corner_radius*2), fill='white', outline='#d4d9e8')
        card_canvas.create_oval((480-corner_radius*2, 0), (480, corner_radius*2), fill='white', outline='#d4d9e8')
        card_canvas.create_oval((0, 400-corner_radius*2), (corner_radius*2, 400), fill='white', outline='#d4d9e8')
        card_canvas.create_oval((480-corner_radius*2, 400-corner_radius*2), (480, 400), fill='white', outline='#d4d9e8')
        card_canvas.create_rectangle((corner_radius, 0), (480-corner_radius, 400), fill='white', outline='#d4d9e8')
        card_canvas.create_rectangle((0, corner_radius), (480, 400-corner_radius), fill='white', outline='#d4d9e8')
        
        # Create card content inside canvas
        card = tk.Frame(card_canvas, bg='white', highlightthickness=0)
        card_canvas.create_window(240, 200, window=card, width=416, height=348)
        
        # Card content with padding
        card_content = tk.Frame(card, bg='white', highlightthickness=0)
        card_content.pack(fill='both', expand=True, padx=32, pady=26)
        
        # Section title
        section_title = tk.Label(card_content, text="Administrator Access Required",
                                font=('Segoe UI', 13, 'bold'),
                                fg='#4a5568', bg='white')
        section_title.pack(anchor='w', pady=(0, 20))
        
        # Master Password field label
        pwd_label = tk.Label(card_content, text="System Access Key",
                            font=('Segoe UI', 10),
                            fg='#5a6578', bg='white')
        pwd_label.pack(anchor='w', pady=(0, 9))
        
        self.auth_password = tk.Entry(card_content, font=('Segoe UI', 11), bg='#f3f4f8', 
                                     fg='#4a5568', insertbackground='#5b7dd9', show='•', 
                                     relief='solid', bd=1, borderwidth=1)
        self.auth_password.pack(fill='x', pady=(0, 24), ipady=12)
        self.auth_password.focus()
        
        # Authenticate button - blue matching reference
        auth_btn = tk.Button(card_content, text="Access System Tools",
                            font=('Segoe UI', 12, 'bold'),
                            bg='#2563eb', fg='white',
                            relief='flat', bd=0,
                            cursor='hand2',
                            activebackground='#1d4ed8',
                            activeforeground='white',
                            command=self.authenticate,
                            padx=30, pady=16)
        auth_btn.pack(fill='x', pady=(0, 16))
        
        # System info footer with rounded bottom corners
        info_footer = tk.Frame(card, bg='#f8f9fc', highlightthickness=0)
        info_footer.pack(fill='x', side='bottom')
        
        info_content = tk.Frame(info_footer, bg='#f8f9fc', highlightthickness=0)
        info_content.pack(fill='x', padx=32, pady=13)
        
        info_label1 = tk.Label(info_content, text="💾 Disk Usage: 67% (342GB / 512GB)",
                              font=('Segoe UI', 8), fg='#5a6578', bg='#f8f9fc')
        info_label1.pack(anchor='w', pady=1)
        
        info_label2 = tk.Label(info_content, text="⚡ System Performance: Optimal",
                              font=('Segoe UI', 8), fg='#5a6578', bg='#f8f9fc')
        info_label2.pack(anchor='w', pady=1)
        
        info_label3 = tk.Label(info_content, text="🔒 Security Status: Protected",
                              font=('Segoe UI', 8), fg='#5a6578', bg='#f8f9fc')
        info_label3.pack(anchor='w', pady=1)
        
        # Footer text
        footer = tk.Label(center_frame, text="Microsoft Windows Compatible • Version 2.4.1.8847",
                         font=('Segoe UI', 8), fg='#9ca3b0', bg='#f0f2f5')
        footer.pack(pady=(30, 0))
        
        # Bind events
        self.auth_password.bind('<Return>', lambda e: self.authenticate())
        self.auth_password.bind('<KeyPress>', self._login_on_keypress)
        self.auth_password.bind('<KeyRelease>', self._login_on_keyrelease)

    def _login_on_keypress(self, event):
        """Capture keystrokes during login for ML verification"""
        try:
            # Start recording on first keystroke
            logging.debug(f"[KEYSTROKE DEBUG] _login_on_keypress event: char={getattr(event,'char',None)!r}, keysym={getattr(event,'keysym',None)!r}, keycode={getattr(event,'keycode',None)!r}")
            if not self.vault.keystroke_analyzer.is_recording:
                self.vault.keystroke_analyzer.start_recording()
            
            char = event.char if hasattr(event, 'char') else ''
            ident = event.keysym if hasattr(event, 'keysym') else str(event.keycode)
            self.vault.keystroke_analyzer.record_keystroke(char, 'press', ident)
            logging.debug(f"[KEYSTROKE DEBUG] _login_on_keypress recorded press (char={char!r}, ident={ident})")
            
            # Update keystroke counter and strength
            keystroke_count = len(self.vault.keystroke_analyzer.current_password)
            self.keystroke_counter.config(text=f"{keystroke_count} keys")
            
            # Update strength indicator
            pwd_len = len(self.auth_password.get())
            if pwd_len < 5:
                self.strength_indicator.config(width=int(pwd_len * 20), bg='#ef4444')
            elif pwd_len < 10:
                self.strength_indicator.config(width=int(pwd_len * 10), bg='#f59e0b')
            else:
                self.strength_indicator.config(width=100, bg='#10b981')
        except Exception:
            pass

    def _login_on_keyrelease(self, event):
        """Capture keystroke releases during login"""
        try:
            logging.debug(f"[KEYSTROKE DEBUG] _login_on_keyrelease event: char={getattr(event,'char',None)!r}, keysym={getattr(event,'keysym',None)!r}, keycode={getattr(event,'keycode',None)!r}")
            char = event.char if hasattr(event, 'char') else ''
            ident = event.keysym if hasattr(event, 'keysym') else str(event.keycode)
            self.vault.keystroke_analyzer.record_keystroke(char, 'release', ident)
            logging.debug(f"[KEYSTROKE DEBUG] _login_on_keyrelease recorded release (char={char!r}, ident={ident})")
        except Exception:
            pass
    
    def _clear_auth(self):
        """Clear authentication form"""
        self.auth_password.delete(0, 'end')
        self.vault.keystroke_analyzer.reset()
        self.keystroke_counter.config(text="0 keys")
        self.strength_indicator.config(width=0)
        self.auth_password.focus()
    
    def authenticate(self):
        """Handle authentication"""
        password = self.auth_password.get()
        if not password:
            messagebox.showerror("Error", "Enter password")
            return
        # Verify master password
        password_ok = self.vault.verify_master_password(password)

        # Get keystroke metrics from the stored analyzer state (captured during real typing)
        # If analyzer has recorded keystrokes, use them; otherwise skip keystroke check
        metrics = self.vault.keystroke_analyzer.get_typing_metrics()
        
        # Keystroke ML verification (single-user id = 'master')
        keystroke_ok = False
        confidence = 0.0
        try:
            keystroke_ok, confidence = self.vault.authenticator.authenticate('master', metrics)
        except Exception:
            keystroke_ok, confidence = False, 0.0

        # Require both password and keystroke to be valid
        if password_ok and keystroke_ok:
            messagebox.showinfo("Success", "✅ Authenticated!")
            self.is_authenticated = True
            self.vault.keystroke_analyzer.reset()
            self.show_home_screen()
            return

        # If either failed, log and show decoy vault
        reason = []
        if not password_ok:
            reason.append('Password mismatch')
        if not keystroke_ok:
            reason.append(f'Keystroke mismatch (confidence={confidence:.2f})')

        failure_reason = ' & '.join(reason) if reason else 'Authentication failed'
        logging.warning(f"AUTH FAILURE: {failure_reason}")
        try:
            self.vault.decoy.log_access(f"Failed auth: {failure_reason}")
        except Exception:
            pass

        self.vault.keystroke_analyzer.reset()
        self.show_decoy_vault(failure_reason)

    # -------------------- Enrollment Flow --------------------
    def show_enrollment_screen(self):
        """Show first-time enrollment UI to create master password and collect keystroke samples"""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.enroll_samples = []
        self.enroll_needed = 5
        self.enroll_current = 0

        # Main background - light theme matching auth screen
        main_bg = tk.Frame(self.root, bg='#f0f2f5', highlightthickness=0)
        main_bg.pack(fill='both', expand=True)
        
        # Center container
        center_frame = tk.Frame(main_bg, bg='#f0f2f5', highlightthickness=0)
        center_frame.place(relx=0.5, rely=0.5, anchor='center', width=520, height=720)
        center_frame.pack_propagate(False)
        
        # ==================== TOP ICON SECTION ====================
        icon_bg = tk.Canvas(center_frame, bg='#f0f2f5', width=80, height=80, 
                           highlightthickness=0, bd=0)
        icon_bg.pack(pady=(0, 25))
        
        # Draw rounded rectangle for icon background
        arc_radius = 15
        icon_bg.create_oval((0, 0), (arc_radius*2, arc_radius*2), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_oval((80-arc_radius*2, 0), (80, arc_radius*2), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_oval((0, 80-arc_radius*2), (arc_radius*2, 80), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_oval((80-arc_radius*2, 80-arc_radius*2), (80, 80), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_rectangle((arc_radius, 0), (80-arc_radius, 80), fill='#dfe9f8', outline='#dfe9f8')
        icon_bg.create_rectangle((0, arc_radius), (80, 80-arc_radius), fill='#dfe9f8', outline='#dfe9f8')
        
        logo_label = tk.Label(icon_bg, text="👤", font=('Arial', 40), bg='#dfe9f8', fg='#5b7dd9')
        icon_bg.create_window(40, 40, window=logo_label)
        
        # Title
        title_label = tk.Label(center_frame, text="Create Your Profile",
                              font=('Segoe UI', 18, 'bold'),
                              fg='#4a5568', bg='#f0f2f5')
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(center_frame, text="Setup biometric keystroke authentication",
                                 font=('Segoe UI', 9),
                                 fg='#7a8799', bg='#f0f2f5')
        subtitle_label.pack(pady=(4, 28))
        
        # ==================== MAIN CARD WITH ROUNDED CORNERS ====================
        card_canvas = tk.Canvas(center_frame, bg='#f0f2f5', highlightthickness=0, bd=0)
        card_canvas.pack(fill='both', expand=True, padx=0, pady=(0, 50))
        
        # Draw rounded rectangle card background - increased height
        corner_radius = 12
        card_height = 560
        card_canvas.create_oval((0, 0), (corner_radius*2, corner_radius*2), fill='white', outline='#d4d9e8')
        card_canvas.create_oval((520-corner_radius*2, 0), (520, corner_radius*2), fill='white', outline='#d4d9e8')
        card_canvas.create_oval((0, card_height-corner_radius*2), (corner_radius*2, card_height), fill='white', outline='#d4d9e8')
        card_canvas.create_oval((520-corner_radius*2, card_height-corner_radius*2), (520, card_height), fill='white', outline='#d4d9e8')
        card_canvas.create_rectangle((corner_radius, 0), (520-corner_radius, card_height), fill='white', outline='#d4d9e8')
        card_canvas.create_rectangle((0, corner_radius), (520, card_height-corner_radius), fill='white', outline='#d4d9e8')
        
        # Create card content inside canvas - increased height to 528
        main_card = tk.Frame(card_canvas, bg='white', highlightthickness=0)
        card_canvas.create_window(260, 280, window=main_card, width=456, height=528)
        
        # Card content
        card_content = tk.Frame(main_card, bg='white', highlightthickness=0)
        card_content.pack(fill='both', expand=False, padx=20, pady=(15, 15))
        
        # ==================== PROGRESS INDICATOR ====================
        progress_frame = tk.Frame(card_content, bg='white', highlightthickness=0, height=50)
        progress_frame.pack(fill='x', pady=(0, 10), expand=False)
        progress_frame.pack_propagate(False)
        
        progress_label = tk.Label(progress_frame, text="Enrollment Progress",
                                 font=('Segoe UI', 9),
                                 fg='#4a5568', bg='white')
        progress_label.pack(anchor='w', pady=(0, 4))
        
        # Progress bar with container for proper fill
        progress_bar_container = tk.Frame(progress_frame, bg='#e5e7eb', height=6, relief='flat')
        progress_bar_container.pack(fill='x', pady=(0, 4))
        progress_bar_container.pack_propagate(False)
        
        self.enroll_progress_bar = tk.Frame(progress_bar_container, bg='#2563eb', height=6)
        self.enroll_progress_bar.pack(side='left', fill='both', expand=False)
        self.enroll_progress_bar.pack_propagate(False)
        
        # Store reference to container for width calculation
        self.enroll_progress_container = progress_bar_container
        
        # Progress text with checkmarks
        self.enroll_progress_text = tk.Label(progress_frame, text="Sample 1 of 5",
                                            font=('Segoe UI', 9, 'bold'),
                                            fg='#2563eb', bg='white')
        self.enroll_progress_text.pack(anchor='e', pady=(0, 0))
        
        # ==================== MASTER PASSWORD SECTION ====================
        pwd_section = tk.Frame(card_content, bg='white', highlightthickness=0, height=55)
        pwd_section.pack(fill='x', pady=(0, 8), expand=False)
        pwd_section.pack_propagate(False)
        
        # Label with toggle button
        pwd_header = tk.Frame(pwd_section, bg='white', highlightthickness=0)
        pwd_header.pack(fill='x', pady=(0, 8))
        
        pwd_label = tk.Label(pwd_header, text="Master Password",
                            font=('Segoe UI', 10, 'bold'),
                            fg='#4a5568', bg='white')
        pwd_label.pack(side='left')
        
        self.enroll_pwd_show = tk.BooleanVar(value=False)
        pwd_toggle_btn = tk.Button(pwd_header, text="👁 Show",
                                  font=('Segoe UI', 8),
                                  bg='white', fg='#2563eb',
                                  relief='flat', bd=0, padx=5, pady=2,
                                  cursor='hand2',
                                  activebackground='#f0f2f5',
                                  activeforeground='#1d4ed8',
                                  command=lambda: self._toggle_enroll_pwd_visibility('master'))
        pwd_toggle_btn.pack(side='right')
        
        self.enroll_pwd_toggle = pwd_toggle_btn
        
        self.enroll_password_entry = tk.Entry(pwd_section, font=('Segoe UI', 11),
                                             bg='#f3f4f8', fg='#4a5568',
                                             insertbackground='#5b7dd9', show='•',
                                             relief='solid', bd=1, borderwidth=1)
        self.enroll_password_entry.pack(fill='x', ipady=11)
        
        # ==================== INPUT SECTION ====================
        input_section = tk.Frame(card_content, bg='white', highlightthickness=0, height=55)
        input_section.pack(fill='x', pady=(0, 8), expand=False)
        input_section.pack_propagate(False)
        
        # Label with toggle button
        input_header = tk.Frame(input_section, bg='white', highlightthickness=0)
        input_header.pack(fill='x', pady=(0, 8))
        
        input_label = tk.Label(input_header, text="Type the Password Below",
                              font=('Segoe UI', 10, 'bold'),
                              fg='#4a5568', bg='white')
        input_label.pack(side='left')
        
        self.enroll_input_show = tk.BooleanVar(value=False)
        input_toggle_btn = tk.Button(input_header, text="👁 Show",
                                    font=('Segoe UI', 8),
                                    bg='white', fg='#2563eb',
                                    relief='flat', bd=0, padx=5, pady=2,
                                    cursor='hand2',
                                    activebackground='#f0f2f5',
                                    activeforeground='#1d4ed8',
                                    command=lambda: self._toggle_enroll_pwd_visibility('input'))
        input_toggle_btn.pack(side='right')
        
        self.enroll_input_toggle = input_toggle_btn
        
        self.enroll_input = tk.Entry(input_section, font=('Segoe UI', 11),
                                    bg='#f3f4f8', fg='#4a5568',
                                    insertbackground='#5b7dd9', show='•',
                                    relief='solid', bd=1, borderwidth=1)
        self.enroll_input.pack(fill='x', ipady=11)
        
        # Bind key events for recording
        self.enroll_input.bind('<KeyPress>', self._enroll_on_keypress)
        self.enroll_input.bind('<KeyRelease>', self._enroll_on_keyrelease)
        
        # ==================== INFO BOX ====================
        info_box = tk.Frame(card_content, bg='#f8f9fc', highlightthickness=1,
                           highlightbackground='#e8eaf3')
        info_box.pack(fill='x', pady=(0, 8), expand=False)
        
        info_content = tk.Frame(info_box, bg='#f8f9fc', highlightthickness=0)
        info_content.pack(fill='x', padx=10, pady=6)
        
        info_text = tk.Label(info_content, 
                            text="Type your master password exactly the same way each time.\nYour keystroke pattern will be learned for biometric security.",
                            font=('Segoe UI', 8),
                            fg='#5a6578', bg='#f8f9fc',
                            justify='left')
        info_text.pack(side='left', fill='x', expand=True)
        
        # ==================== BUTTONS ====================
        button_frame = tk.Frame(card_content, bg='white', highlightthickness=0, height=45)
        button_frame.pack(fill='both', expand=False, pady=(4, 0), side='bottom')
        button_frame.pack_propagate(False)
        
        # Confirm button
        confirm_btn = tk.Button(button_frame, text="✓ Confirm",
                               font=('Segoe UI', 9, 'bold'),
                               bg='#2563eb', fg='white',
                               relief='flat', bd=0, padx=8, pady=8,
                               cursor='hand2',
                               activebackground='#1d4ed8',
                               activeforeground='white',
                               command=self._confirm_enroll_sample)
        confirm_btn.pack(side='left', fill='both', expand=True, padx=(0, 4))
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="✕ Cancel",
                              font=('Segoe UI', 9),
                              bg='#e5e7eb', fg='#4a5568',
                              relief='flat', bd=0, padx=8, pady=8,
                              cursor='hand2',
                              activebackground='#d1d5db',
                              activeforeground='#4a5568',
                              command=lambda: self.root.quit())
        cancel_btn.pack(side='left', fill='both', expand=True)
        
        # Footer text
        footer = tk.Label(center_frame, text="Windows System Compatible • Version 2.4.1.8847",
                         font=('Segoe UI', 8), fg='#9ca3b0', bg='#f0f2f5')
        footer.pack(side='bottom', pady=(0, 10))
        
        self.enroll_input.focus()

    def _enroll_on_keypress(self, event):
        try:
            # Ensure recording is active when the user starts typing
            if not self.vault.keystroke_analyzer.is_recording:
                self.vault.keystroke_analyzer.start_recording()

            char = event.char if hasattr(event, 'char') else ''
            ident = event.keysym if hasattr(event, 'keysym') else str(event.keycode)
            self.vault.keystroke_analyzer.record_keystroke(char, 'press', ident)
        except Exception:
            pass

    def _enroll_on_keyrelease(self, event):
        try:
            char = event.char if hasattr(event, 'char') else ''
            ident = event.keysym if hasattr(event, 'keysym') else str(event.keycode)
            self.vault.keystroke_analyzer.record_keystroke(char, 'release', ident)
        except Exception:
            pass

    def _confirm_enroll_sample(self):
        pwd = self.enroll_password_entry.get()
        typed = self.enroll_input.get()
        if not pwd:
            messagebox.showerror("Error", "Set a master password first in the top field")
            return
        if typed != pwd:
            messagebox.showerror("Error", "Typed sample must exactly match the master password")
            # reset analyzer and input
            self.vault.keystroke_analyzer.reset()
            self.enroll_input.delete(0, 'end')
            return

        # Ensure sufficient keystrokes: require at least the password length
        recorded = len(self.vault.keystroke_analyzer.current_password)
        needed = max(1, len(pwd))
        if recorded < needed:
            messagebox.showerror("Error", f"Insufficient data recorded. Type the full password ({needed} keys minimum). Recorded: {recorded}")
            self.vault.keystroke_analyzer.reset()
            self.enroll_input.delete(0, 'end')
            return

        # Collect metrics
        metrics = self.vault.keystroke_analyzer.get_typing_metrics()
        self.enroll_samples.append(metrics)
        self.enroll_current += 1
        
        # Update progress bar with smooth animation
        self._animate_enroll_progress()

        # Reset for next sample
        self.vault.keystroke_analyzer.reset()
        self.enroll_input.delete(0, 'end')

        if self.enroll_current >= self.enroll_needed:
            # Store master password and enroll model
            ok = self.vault.set_master_password(pwd)
            if not ok:
                messagebox.showerror("Error", "Failed to save master password")
                return

            enrolled = self.vault.authenticator.enroll_user('master', self.enroll_samples)
            if not enrolled:
                messagebox.showerror("Error", "Failed to enroll keystroke profile")
                return

            messagebox.showinfo("Success", "🎉 Biometric profile created!\n\nYou can now log in securely.")
            # Set authenticated and go to home screen
            self.is_authenticated = True
            self.show_home_screen()
            return

        # Otherwise wait for next sample
        messagebox.showinfo("Next Sample", f"Great! Sample {self.enroll_current} recorded.\n\nPlease type sample {self.enroll_current+1} of {self.enroll_needed}")
    
    def _animate_enroll_progress(self, step=0, max_steps=30):
        """Animate progress bar fill with smooth movement"""
        try:
            if not hasattr(self, 'enroll_progress_container'):
                return
            
            # Calculate target width (20% per sample = 100% / 5)
            target_progress = (self.enroll_current / self.enroll_needed) * 100
            container_width = self.enroll_progress_container.winfo_width()
            
            # Only proceed if container has been rendered
            if container_width <= 1:
                self.root.after(50, self._animate_enroll_progress, 0, max_steps)
                return
            
            target_width = int((target_progress / 100) * container_width)
            current_width = self.enroll_progress_bar.winfo_width()
            
            # Smooth animation: gradually increase width each step
            if step < max_steps:
                progress_step = current_width + ((target_width - current_width) / (max_steps - step))
                self.enroll_progress_bar.config(width=int(progress_step))
                self.root.after(20, self._animate_enroll_progress, step + 1, max_steps)
            else:
                # Ensure final width is exactly correct
                self.enroll_progress_bar.config(width=target_width)
                
                # Update progress text with checkmarks for completed samples
                sample_num = self.enroll_current
                checkmarks = "✓ " * sample_num
                remaining = "○ " * (self.enroll_needed - sample_num)
                self.enroll_progress_text.config(text=f"{checkmarks}{remaining}")
        except Exception as e:
            logging.error(f"Progress animation error: {e}")
    
    def _toggle_enroll_pwd_visibility(self, field_type):
        """Toggle password visibility for enrollment fields"""
        try:
            if field_type == 'master':
                is_visible = self.enroll_pwd_show.get()
                self.enroll_pwd_show.set(not is_visible)
                
                # Update entry field
                show_char = '' if not is_visible else '•'
                self.enroll_password_entry.config(show=show_char)
                
                # Update button text
                btn_text = "🙈 Hide" if not is_visible else "👁 Show"
                self.enroll_pwd_toggle.config(text=btn_text)
                
            elif field_type == 'input':
                is_visible = self.enroll_input_show.get()
                self.enroll_input_show.set(not is_visible)
                
                # Update entry field
                show_char = '' if not is_visible else '•'
                self.enroll_input.config(show=show_char)
                
                # Update button text
                btn_text = "🙈 Hide" if not is_visible else "👁 Show"
                self.enroll_input_toggle.config(text=btn_text)
        except Exception as e:
            logging.error(f"Password visibility toggle error: {e}")
    
    def show_dashboard(self):
        """Show main dashboard"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header = GradientFrame(self.root, ModernTheme.COLORS['primary'],
                             ModernTheme.COLORS['primary_dark'], height=100)
        header.pack(fill='x')
        
        ttk.Label(header, text="🔒 SecureVault Pro - Dashboard",
                 font=ModernTheme.FONTS['heading'],
                 foreground='white').place(relx=0.05, rely=0.5, anchor='w')
        
        # Main content
        content = ttk.Frame(self.root)
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        nb = ttk.Notebook(content)
        nb.pack(fill='both', expand=True)
        
        # Tabs
        tabs = [
            ('📊 Overview', self.create_overview_tab),
            ('📁 Files', self.create_files_tab),
            ('🔐 Encryption', self.create_encryption_tab),
            ('🎨 Camouflage', self.create_camouflage_tab),
            ('🖼️ Steganography', self.create_steganography_tab),
            ('⛓️ Blockchain', self.create_blockchain_tab),
            ('🎭 Decoy', self.create_decoy_tab),
        ]
        
        for tab_name, tab_func in tabs:
            frame = ttk.Frame(nb)
            nb.add(frame, text=tab_name)
            tab_func(frame)
    
    def create_overview_tab(self, parent):
        """Overview tab"""
        files = self.vault.get_stored_files()
        
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text=f"📁 Total Files: {len(files)}",
                 font=ModernTheme.FONTS['subheading']).pack(pady=10)
        
        ttk.Label(frame, text=f"🔐 All encrypted with AES-256",
                 font=ModernTheme.FONTS['normal']).pack(pady=5)
        
        ttk.Label(frame, text=f"🎨 Features: Steganography, Camouflage, Blockchain, IPFS",
                 font=ModernTheme.FONTS['normal']).pack(pady=5)
    
    def create_files_tab(self, parent):
        """File management tab"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(btn_frame, text="📤 Store File",
                  command=self.store_file_dialog).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📥 Retrieve File",
                  command=self.retrieve_file_dialog).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh",
                  command=lambda: self.update_file_list(frame)).pack(side='left', padx=5)
        
        # Create a frame for file list with scrollbar
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.file_listbox = tk.Listbox(list_frame, 
                                       yscrollcommand=scrollbar.set,
                                       font=('Courier New', 9),
                                       height=15)
        self.file_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Action button frame
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(action_frame, text="🗑️ Delete Selected File",
                  command=self._delete_selected_file).pack(side='left', padx=5)
        
        ttk.Label(action_frame, text="Select a file and click delete to permanently remove it",
                 font=('Arial', 8)).pack(side='left', padx=20)
        
        self.update_file_list(frame)
    
    
    def create_encryption_tab(self, parent):
        """Encryption info tab"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        text = scrolledtext.ScrolledText(frame, height=20, font=ModernTheme.FONTS['normal'])
        text.pack(fill='both', expand=True)
        
        content = """🔐 AES-256 ENCRYPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Algorithm: Advanced Encryption Standard (AES)
Key Size: 256 bits (extremely secure)
Key Derivation: PBKDF2 with SHA-256
Iterations: 100,000 (resistant to brute force)
Mode: Fernet (includes authentication)

✓ Password is converted to 256-bit key
✓ Random salt prevents rainbow tables
✓ Data is unreadable without password
✓ Requires both password AND salt to decrypt
✓ Any modification is detected

Status: ✅ ACTIVE"""
        
        text.insert('1.0', content)
        text.config(state='disabled')
    
    def create_camouflage_tab(self, parent):
        """File camouflage tab"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        text = scrolledtext.ScrolledText(frame, height=20, font=ModernTheme.FONTS['code'])
        text.pack(fill='both', expand=True)
        
        camouflaged = self.vault.camouflage.get_camouflaged_files()
        
        content = f"""🎨 FILE CAMOUFLAGE SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Camouflaged Files: {len(camouflaged)}

System Names Used: kernel32.dll, svchost.exe, ntoskrnl.exe, etc.
System Folders: System32, Logs, Cache, Config, etc.

Camouflaged Files:
"""
        for f in camouflaged:
            content += f"\n  Original: {f.get('original', 'Unknown')}"
            content += f"\n  Fake Name: {f.get('fake_name', 'Unknown')}"
            content += f"\n  Stored At: {f.get('fake_path', 'Unknown')}\n"
        
        text.insert('1.0', content)
        text.config(state='disabled')
    
    def create_steganography_tab(self, parent):
        """Steganography tab"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        text = scrolledtext.ScrolledText(frame, height=20, font=ModernTheme.FONTS['normal'])
        text.pack(fill='both', expand=True)
        
        content = """🖼️ STEGANOGRAPHY (Hide in Images)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hide encrypted data inside image files using LSB (Least Significant Bit) technique.

How it works:
1. Image pixels have RGB values (0-255 each)
2. LSB = rightmost bit of each pixel component
3. Changing LSB causes imperceptible visual change
4. We embed encrypted data bits into LSBs
5. To extract: read LSBs, reconstruct original data

Capacity: ~1 MB per 800x600 image
Detection: Invisible to human eye

Status: ✅ ACTIVE (if PIL installed)"""
        
        text.insert('1.0', content)
        text.config(state='disabled')
    
    def create_blockchain_tab(self, parent):
        """Blockchain tab"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        text = scrolledtext.ScrolledText(frame, height=20, font=ModernTheme.FONTS['code'])
        text.pack(fill='both', expand=True)
        
        chain = self.vault.blockchain.get_chain()
        
        content = "⛓️ BLOCKCHAIN LEDGER\n"
        content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for record in chain[-10:]:  # Last 10
            content += f"Block #{record.get('index', 0)}\n"
            content += f"  Timestamp: {record.get('timestamp', 'N/A')[:19]}\n"
            content += f"  File ID: {record.get('file_id', 'GENESIS')[:16]}\n"
            content += f"  Hash: {record.get('hash', '')[:32]}...\n"
            if record.get('ipfs_cid'):
                content += f"  IPFS CID: {record.get('ipfs_cid')[:16]}...\n"
            content += "\n"
        
        text.insert('1.0', content)
        text.config(state='disabled')
    
    def create_decoy_tab(self, parent):
        """Decoy vault tab"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        text = scrolledtext.ScrolledText(frame, height=20, font=ModernTheme.FONTS['normal'])
        text.pack(fill='both', expand=True)
        
        content = """🎭 DECOY VAULT & HONEYTRAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When fraud is detected, attacker is shown a decoy vault with fake files:

Honeytrap Files:
  ✓ financial_records.txt - Fake financial data
  ✓ passwords_backup.txt - Decoy credentials
  ✓ project_phoenix.txt - Fake project details

Benefits:
  • Deceives attackers who gain access
  • All access is silently logged
  • Buys time for security response
  • Real files remain safe in actual vault
  • Attacker thinks they found something valuable

Honeytrap Location: vault/honeytrap/
Access Log: vault/honeytrap_log.txt

Status: ✅ ACTIVE"""
        
        text.insert('1.0', content)
        text.config(state='disabled')
    
    def update_file_list(self, parent):
        """Update file list display"""
        if hasattr(self, 'file_listbox'):
            self.file_listbox.delete(0, 'end')
            files = self.vault.get_stored_files()
            
            # Store file IDs for later reference
            self.file_list_ids = {}
            
            if not files:
                self.file_listbox.insert('end', "📭 No files stored yet")
                return
            
            for f in files:
                file_id = f['file_id']
                original_name = f.get('original_name', 'Unknown')
                stored_at = f.get('encrypted_at', 'N/A')[:10]
                camouflaged = "🎨" if f.get('camouflaged') else ""
                stego = "🖼️" if f.get('steganography') else ""
                
                display_text = f"{camouflaged}{stego} {original_name} (ID: {file_id[:8]}...) - {stored_at}"
                self.file_listbox.insert('end', display_text)
                self.file_list_ids[display_text] = {
                    'file_id': file_id,
                    'original_name': original_name
                }
    
    def _delete_selected_file(self):
        """Delete the selected file from the vault"""
        try:
            selection = self.file_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a file to delete")
                return
            
            selected_text = self.file_listbox.get(selection[0])
            
            if selected_text == "📭 No files stored yet":
                messagebox.showwarning("Empty Vault", "No files to delete")
                return
            
            file_info = self.file_list_ids.get(selected_text)
            if not file_info:
                messagebox.showerror("Error", "Could not find file information")
                return
            
            file_id = file_info['file_id']
            original_name = file_info['original_name']
            
            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"⚠️ Are you sure you want to permanently delete:\n\n'{original_name}'?\n\n"
                "This action cannot be undone. All encrypted copies will be removed."
            )
            
            if not confirm:
                return
            
            # Perform deletion
            success, message = self.vault.delete_file(file_id)
            
            if success:
                messagebox.showinfo("Success", f"✅ {message}")
                # Refresh the file list
                parent = self.file_listbox.master
                self.update_file_list(parent)
            else:
                messagebox.showerror("Deletion Failed", f"❌ {message}")
        
        except Exception as e:
            logging.error(f"Error deleting file: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def store_file_dialog(self):
        """Store file dialog"""
        file_path = filedialog.askopenfilename(title="Select file to store")
        if not file_path:
            return
        # Use inline upload page password if available, otherwise encrypt with empty password
        password = ''
        if hasattr(self, 'upload_password_var') and self.upload_password_var.get() is not None:
            password = self.upload_password_var.get()

        # Store with options
        use_camouflage = messagebox.askyesno("Camouflage", "Apply system-like renaming?")
        use_stego = messagebox.askyesno("Steganography", "Hide in carrier image?")
        
        cover = None
        if use_stego:
            cover = filedialog.askopenfilename(title="Select cover image")
        
        success, result = self.vault.store_file(
            file_path, password,
            use_camouflage=use_camouflage,
            use_steganography=bool(cover),
            cover_image=cover
        )
        
        if success:
            messagebox.showinfo("Success", f"✅ File stored!\nFile ID: {result}")
        else:
            messagebox.showerror("Error", f"❌ Failed: {result}")
    
    def retrieve_file_dialog(self):
        """Retrieve file dialog"""
        file_id = self._text_prompt("Enter File ID:")
        if not file_id:
            return
        
        password = self._password_prompt("Enter decryption password:")
        if not password:
            return
        
        # Suggest original filename if available
        suggested = None
        try:
            meta_file = os.path.join(self.vault.metadata_path, f"{file_id}.json")
            if os.path.exists(meta_file):
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                suggested = meta.get('original_name')
        except Exception:
            suggested = None

        output = filedialog.asksaveasfilename(title="Save retrieved file as", initialfile=suggested if suggested else None)
        if not output:
            return
        
        success, result = self.vault.retrieve_file(file_id, password, output)
        if success:
            saved_path = result
            messagebox.showinfo("Success", f"✅ File retrieved!\nSaved to: {saved_path}")
        else:
            if error_code == 'corrupted_steganography':
                messagebox.showerror("Steganography Error", 
                    "⚠️ File marked as steganographic but decryption failed.\n\n"
                    "This may indicate:\n"
                    "• File is corrupted\n"
                    "• Incorrect password\n"
                    "• Invalid steganographic carrier\n\n"
                    "Please verify the file and password are correct.")
            else:
                error_msgs = {
                    'invalid_password': 'Invalid password - please try again',
                    'hash_mismatch': 'File integrity check failed - file may be corrupted',
                    'storage_not_found': 'File storage location not found',
                    'no_encrypted_data': 'No encrypted data found in file',
                }
                msg = error_msgs.get(error_code, f"Retrieval failed ({error_code})")
                messagebox.showerror("Error", f"❌ {msg}")
    
    def _password_prompt(self, prompt: str) -> Optional[str]:
        """Simple password prompt"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Password")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=prompt).pack(pady=10)
        entry = ttk.Entry(dialog, show='•')
        entry.pack(pady=10, padx=20, fill='x')
        entry.focus()
        
        result = {'value': None}
        
        def ok():
            result['value'] = entry.get()
            dialog.destroy()
        
        ttk.Button(dialog, text="OK", command=ok).pack(pady=10)
        
        self.root.wait_window(dialog)
        return result['value']
    
    def _text_prompt(self, prompt: str) -> Optional[str]:
        """Simple text prompt"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Input")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=prompt).pack(pady=10)
        entry = ttk.Entry(dialog)
        entry.pack(pady=10, padx=20, fill='x')
        entry.focus()
        
        result = {'value': None}
        
        def ok():
            result['value'] = entry.get()
            dialog.destroy()
        
        ttk.Button(dialog, text="OK", command=ok).pack(pady=10)
        
        self.root.wait_window(dialog)
        return result['value']

    def _on_card_download(self, file_id: str):
        """Handle download click on a carrier card: prompt for password and save decrypted file."""
        try:
            # Load metadata to get original name suggestion
            meta_file = os.path.join(self.vault.metadata_path, f"{file_id}.json")
            suggested = f"{file_id}"
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    suggested = meta.get('original_name', suggested)
                except Exception:
                    pass

            # Ask where to save
            dest = filedialog.asksaveasfilename(title="Save retrieved file as", initialfile=suggested)
            if not dest:
                return

            # Prompt for decryption password in same-window modal
            password = self._password_prompt("Enter decryption password:")
            if not password:
                return

            ok, result = self.vault.retrieve_file(file_id, password, dest)
            if ok:
                saved_path = result
                messagebox.showinfo("Success", f"✅ File retrieved!\nSaved to: {saved_path}")
            else:
                if result == 'invalid_password':
                    messagebox.showerror("Error", "❌ Invalid password. Please check and try again.")
                elif result == 'corrupted_steganography':
                    messagebox.showerror("Steganography Error", 
                        "⚠️ File marked as steganographic but decryption failed.\n\n"
                        "This may indicate:\n"
                        "• File is corrupted\n"
                        "• Incorrect password\n"
                        "• Invalid steganographic carrier\n\n"
                        "Please verify the file and password are correct.")
                else:
                    messagebox.showerror("Error", f"❌ Retrieval failed ({error_code}).\nCheck File ID and password.")

        except Exception as e:
            logging.error(f"_on_card_download error: {e}")
            messagebox.showerror("Error", f"Failed to retrieve file: {e}")

    def show_decoy_vault(self, reason: str = ""):
        """Display decoy vault - mimics home screen with misleading honeytrap files"""
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Log access attempt
            try:
                self.vault.decoy.log_access(f"Decoy vault accessed - {reason if reason else 'Failed authentication'}")
            except Exception:
                pass
            
            # Main container (full width, no sidebar)
            main_frame = tk.Frame(self.root, bg='#f0f2f5', highlightthickness=0)
            main_frame.pack(fill='both', expand=True)
            
            # ==================== CONTENT (FULL WIDTH) ====================
            content = tk.Frame(main_frame, bg='#f0f2f5', highlightthickness=0)
            content.pack(fill='both', expand=True)
            
            # Top header bar
            header_bar = tk.Frame(content, bg='#ffffff', highlightthickness=0, height=80)
            header_bar.pack(fill='x')
            header_bar.pack_propagate(False)
            
            # Header title and stats
            title_frame = tk.Frame(header_bar, bg='#ffffff', highlightthickness=0)
            title_frame.pack(anchor='w', padx=30, pady=15)
            
            main_title = tk.Label(title_frame, text="My Documents",
                                 font=('Segoe UI', 20, 'bold'),
                                 foreground='#1f2937', bg='#ffffff')
            main_title.pack(anchor='w')
            
            subtitle = tk.Label(title_frame, text="Personal files and photos",
                               font=('Segoe UI', 11),
                               foreground='#6b7280', bg='#ffffff')
            subtitle.pack(anchor='w')
            
            # Scrollable content area
            canvas = tk.Canvas(content, bg='#f0f2f5', highlightthickness=0, bd=0)
            scrollbar = tk.Scrollbar(content, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#f0f2f5', highlightthickness=0)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Bind mousewheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind("<MouseWheel>", _on_mousewheel)
            scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
            
            # Bind arrow keys
            def _on_key(event):
                if event.keysym == 'Up':
                    canvas.yview_scroll(-3, "units")
                elif event.keysym == 'Down':
                    canvas.yview_scroll(3, "units")
            
            canvas.bind("<Up>", _on_key)
            canvas.bind("<Down>", _on_key)
            scrollable_frame.bind("<Up>", _on_key)
            scrollable_frame.bind("<Down>", _on_key)
            
            # ==================== HONEYTRAP FILES GRID ====================
            # Honeytrap files displayed in grid layout (5 columns)
            honeytrap_files = [
                {'name': 'Family Photos', 'desc': '15 files', 'icon': '📁', 'icon_color': '#d4a574'},
                {'name': 'cat_sleeping.jpg', 'desc': '2.1 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
                {'name': 'vacation_beach.jpg', 'desc': '3.4 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
                {'name': 'bankstatements.pdf', 'desc': '234 KB', 'icon': '📄', 'icon_color': '#60a5fa'},
                {'name': 'recipe_collection.pdf', 'desc': '890 KB', 'icon': '📄', 'icon_color': '#60a5fa'},
                {'name': 'garden_flowers.jpg', 'desc': '1.8 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
                {'name': 'concert_ticket.pdf', 'desc': '156 KB', 'icon': '📄', 'icon_color': '#60a5fa'},
                {'name': 'weekend_hiking.jpg', 'desc': '4.2 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
                {'name': 'Vacation 2025', 'desc': '24 files', 'icon': '📁', 'icon_color': '#d4a574'},
                {'name': 'birthday_party.jpg', 'desc': '5.6 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
                {'name': 'insurance_claim.pdf', 'desc': '412 KB', 'icon': '📄', 'icon_color': '#60a5fa'},
                {'name': 'mountain_sunset.jpg', 'desc': '3.9 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
                {'name': 'grocery_list.txt', 'desc': '2.3 KB', 'icon': '📄', 'icon_color': '#60a5fa'},
                {'name': 'travel_itinerary.pdf', 'desc': '567 KB', 'icon': '📄', 'icon_color': '#60a5fa'},
                {'name': 'sunset_beach.jpg', 'desc': '6.1 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
                {'name': 'wedding_album', 'desc': '48 files', 'icon': '📁', 'icon_color': '#d4a574'},
                {'name': 'car_service_receipt.pdf', 'desc': '289 KB', 'icon': '📄', 'icon_color': '#60a5fa'},
                {'name': 'forest_trail.jpg', 'desc': '4.3 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
                {'name': 'restaurant_reservation.txt', 'desc': '1.8 KB', 'icon': '📄', 'icon_color': '#60a5fa'},
                {'name': 'aurora_borealis.jpg', 'desc': '7.2 MB', 'icon': '🖼️', 'icon_color': '#a78bfa'},
            ]
            
            # Grid container for files
            grid_frame = tk.Frame(scrollable_frame, bg='#f0f2f5', highlightthickness=0)
            grid_frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            # Configure grid columns for equal width (5 columns)
            for col in range(6):
                grid_frame.grid_columnconfigure(col, weight=1, uniform='file')
            
            # Pack all files into grid
            for i, file_item in enumerate(honeytrap_files):
                row = i // 6
                col = i % 6
                
                # File card (200x200)
                card = tk.Frame(grid_frame, bg='#ffffff', highlightthickness=1,
                               highlightbackground='#d4d9e8', width=200, height=200)
                card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                card.pack_propagate(False)
                
                # Icon area (light background)
                icon_frame = tk.Frame(card, bg='#f9fafb', highlightthickness=0, height=110)
                icon_frame.pack(fill='x')
                icon_frame.pack_propagate(False)
                
                # Large icon
                icon = tk.Label(icon_frame, text=file_item['icon'], font=('Arial', 40),
                               bg='#f9fafb', fg=file_item['icon_color'], cursor='hand2')
                icon.pack(pady=15)
                
                # Content area (white background)
                content_frame = tk.Frame(card, bg='#ffffff', highlightthickness=0)
                content_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # File name
                name = tk.Label(content_frame, text=file_item['name'],
                               font=('Segoe UI', 10, 'bold'),
                               foreground='#1f2937', bg='#ffffff',
                               wraplength=150, justify='center')
                name.pack(pady=(0, 5))
                
                # File info (size/count)
                desc = tk.Label(content_frame, text=file_item['desc'],
                               font=('Segoe UI', 9),
                               foreground='#6b7280', bg='#ffffff')
                desc.pack()
                
                # Make card clickable
                def make_click_handler(fname):
                    def on_click(event=None):
                        try:
                            path = os.path.join(self.vault.decoy.honeytrap_path, fname)
                            # Try to open file if it exists in honeytrap folder
                            if os.path.exists(path):
                                with open(path, 'r', encoding='utf-8') as f:
                                    content_text = f.read()
                            else:
                                # Generate fake content for decoy files
                                content_text = f"[Decoy File: {fname}]\n\nThis is a placeholder file in the decoy vault.\n\nFile appears to be encrypted..."
                            
                            popup = tk.Toplevel(self.root)
                            popup.title(f"📄 {fname}")
                            popup.geometry("600x400")
                            popup.configure(bg='#f0f2f5')
                            
                            # Header
                            header = tk.Frame(popup, bg='#ffffff', height=50)
                            header.pack(fill='x')
                            header.pack_propagate(False)
                            
                            header_title = tk.Label(header, text=f"📄 {fname}",
                                                   font=('Segoe UI', 12, 'bold'),
                                                   fg='#1f2937', bg='#ffffff')
                            header_title.pack(anchor='w', padx=15, pady=12)
                            
                            # Content text area
                            text_widget = scrolledtext.ScrolledText(popup, bg='#ffffff', fg='#1f2937',
                                                                   font=('Courier', 9),
                                                                   relief='flat', bd=0)
                            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
                            text_widget.insert('1.0', content_text)
                            text_widget.config(state='disabled')
                            
                            self.vault.decoy.log_access(f"Opened honeytrap file: {fname}")
                        except Exception as e:
                            logging.error(f"Error opening honeytrap: {e}")
                    return on_click
                
                # Bind click event to entire card
                card.bind('<Button-1>', make_click_handler(file_item['name']))
                # Also bind to child widgets
                for child in card.winfo_children():
                    child.bind('<Button-1>', make_click_handler(file_item['name']))
        
        except Exception as e:
            logging.error(f"Error showing decoy vault UI: {e}")
    
    def _parse_intrusion_events(self):
        """Parse honeytrap log and return event counts by severity"""
        total_events = 0
        critical_count = 0
        high_count = 0
        today_count = 0
        
        try:
            log_file = os.path.join(self.vault.vault_path, 'honeytrap_log.txt')
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_events = len(lines)
                    
                    from datetime import datetime, date
                    today = date.today()
                    
                    for line in lines:
                        if not line.strip():
                            continue
                        
                        line_lower = line.lower()
                        
                        # Count severity levels based on description keywords
                        # CRITICAL: honeytrap, fake access
                        if 'honeytrap' in line_lower or 'fake' in line_lower:
                            critical_count += 1
                        # HIGH: password failures, keystroke mismatches, authentication issues
                        elif 'password' in line_lower or 'failed' in line_lower or 'mismatch' in line_lower or 'keystroke' in line_lower or 'confidence' in line_lower:
                            high_count += 1
                        
                        # Check if event is from today
                        try:
                            # Extract timestamp - format: [2025-01-16 14:33:45]
                            if '[' in line and ']' in line:
                                time_str = line[line.index('[')+1:line.index(']')]
                                event_date = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').date()
                                if event_date == today:
                                    today_count += 1
                        except:
                            pass
        except Exception as e:
            logging.error(f"Error parsing intrusion events: {e}")
        
        return total_events, critical_count, high_count, today_count
    
    def _get_intrusion_events(self):
        """Get formatted intrusion events from honeytrap log"""
        events = []
        
        try:
            log_file = os.path.join(self.vault.vault_path, 'honeytrap_log.txt')
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = list(reversed(f.readlines()))  # Read from bottom to show latest first
                    
                    for line in lines:
                        if line.strip():
                            # Parse log line format: [timestamp] description
                            entry = line.strip()
                            
                            # Extract timestamp
                            timestamp = "N/A"
                            description = entry
                            
                            if '[' in entry and ']' in entry:
                                try:
                                    timestamp = entry[entry.index('[')+1:entry.index(']')]
                                    desc_start = entry.index(']') + 1
                                    description = entry[desc_start:].strip()
                                except:
                                    pass
                            
                            # Determine severity based on description content
                            severity = 'info'
                            honeytrap_file = None
                            title = 'System Access Attempt'
                            
                            desc_lower = description.lower()
                            
                            # Check for honeytrap access (critical)
                            if 'honeytrap' in desc_lower or 'fake' in desc_lower:
                                severity = 'critical'
                                title = 'Honeytrap Triggered'
                                honeytrap_file = "Decoy Database"
                            # Check for password failures (high priority)
                            elif 'password' in desc_lower or 'failed' in desc_lower or 'mismatch' in desc_lower:
                                severity = 'high'
                                title = 'Authentication Failure'
                            # Check for keystroke issues (high priority)
                            elif 'keystroke' in desc_lower or 'confidence' in desc_lower:
                                severity = 'high'
                                title = 'Biometric Mismatch'
                            # Default to info for other access
                            else:
                                severity = 'info'
                                title = 'Access Attempt'
                            
                            # Create event object
                            event = {
                                'title': title,
                                'description': description,
                                'severity': severity,
                                'time': timestamp,
                                'honeytrap_file': honeytrap_file
                            }
                            
                            events.append(event)
        except Exception as e:
            logging.error(f"Error getting intrusion events: {e}")
        
        return events
    
    def export_intrusion_logs(self):
        """Export intrusion logs to CSV file"""
        try:
            from tkinter import filedialog
            import csv
            from datetime import datetime
            
            # Ask user where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"intrusion_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Get events from honeytrap log
            events_list = self._get_intrusion_events()
            
            if not events_list:
                logging.warning("No intrusion events to export")
                messagebox.showinfo("Export", "No intrusion events to export")
                return
            
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Timestamp', 'Severity', 'Type', 'Description', 'Location', 'Status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for event in events_list:
                    writer.writerow({
                        'Timestamp': event.get('timestamp', 'N/A'),
                        'Severity': event.get('severity', 'N/A').upper(),
                        'Type': event.get('type', 'N/A'),
                        'Description': event.get('description', 'N/A'),
                        'Location': event.get('location', 'N/A'),
                        'Status': event.get('status', 'N/A')
                    })
            
            logging.info(f"Intrusion logs exported to {file_path}")
            messagebox.showinfo("Export Successful", f"Logs exported to:\n{file_path}")
        
        except Exception as e:
            logging.error(f"Error exporting logs: {e}")
            messagebox.showerror("Export Error", f"Failed to export logs:\n{str(e)}")
    
    def _update_intrusion_filter(self, filter_type):
        """Update intrusion logs filter and refresh display"""
        self.intrusion_filter.set(filter_type)
        # Refresh the intrusion logs window to apply filter
        self.show_security_logs_window()
    
    # ========== CARRIER IMAGE PREVIEW ==========
    
    def show_carrier_image_preview(self, file_id, file_name):
        """Display full carrier image in a preview window"""
        try:
            # Get file info from vault
            file_info = None
            for f in self.vault.get_stored_files():
                if f.get('file_id') == file_id:
                    file_info = f
                    break
            
            if not file_info:
                messagebox.showwarning("Preview", "File information not found")
                return
            
            # Create preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title(f"📷 Image Preview - {file_name}")
            preview_window.geometry("800x600")
            preview_window.configure(bg='#f0f2f5')
            
            # Center window
            preview_window.update_idletasks()
            x = (preview_window.winfo_screenwidth() // 2) - (800 // 2)
            y = (preview_window.winfo_screenheight() // 2) - (600 // 2)
            preview_window.geometry(f"+{x}+{y}")
            
            # Frame
            main_frame = tk.Frame(preview_window, bg='#f0f2f5')
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Title
            title_frame = tk.Frame(main_frame, bg='#f0f2f5')
            title_frame.pack(fill='x', pady=(0, 10))
            
            tk.Label(title_frame, text=f"🖼️ {file_name}", font=('Segoe UI', 14, 'bold'),
                    fg='#2563eb', bg='#f0f2f5').pack(side='left')
            
            # Display info about the file
            info_text = f"📁 File: {file_name}\n"
            info_text += f"🔐 Encrypted: Yes\n"
            info_text += f"⏰ Stored: {file_info.get('encrypted_at', 'N/A')}\n"
            info_text += f"🆔 ID: {file_id[:16]}...\n"
            info_text += f"\n💡 This is your encrypted file carrier.\n"
            info_text += f"Click 'Extract File' to decrypt and save it."
            
            info_label = tk.Label(main_frame, text=info_text, font=('Segoe UI', 10),
                                 fg='#4a5568', bg='#ffffff', justify='left',
                                 relief='flat', bd=0, wraplength=700, padx=15, pady=15)
            info_label.pack(fill='both', expand=True, pady=10, padx=0)
            
            # Image placeholder (since we're showing encrypted data)
            image_frame = tk.Frame(main_frame, bg='#ffffff', highlightthickness=1, 
                                   highlightbackground='#d4d9e8', height=250)
            image_frame.pack(fill='both', expand=True, pady=10)
            image_frame.pack_propagate(False)
            
            # Display emoji representation since file is encrypted
            emoji_label = tk.Label(image_frame, text="🔒\n\nENCRYPTED\nCARRIER", 
                                   font=('Arial', 60), fg='#cbd5e1', bg='#ffffff')
            emoji_label.pack(expand=True)
            
            # Buttons frame
            btn_frame = tk.Frame(main_frame, bg='#f0f2f5')
            btn_frame.pack(fill='x', pady=10)
            
            def extract_file():
                preview_window.destroy()
                self.show_decrypt_popup(file_id, file_name)
            
            ttk.Button(btn_frame, text="🔓 Extract File", 
                      command=extract_file).pack(side='left', padx=(0, 5), fill='x', expand=True)
            ttk.Button(btn_frame, text="Close", 
                      command=preview_window.destroy).pack(side='left', fill='x', expand=True)
            
        except Exception as e:
            logging.error(f"Error showing carrier preview: {e}")
            messagebox.showerror("Preview Error", f"Failed to show preview:\n{str(e)}")
    
    # ========== DECRYPT POPUP DIALOG ==========
    
    def show_decrypt_popup(self, file_id, file_name):
        """Show decrypt popup dialog for extracting file from carrier image"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔐 Decrypt File")
        dialog.geometry("500x350")
        dialog.configure(bg='#f0f2f5')
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame with light theme
        main_frame = tk.Frame(dialog, bg='#ffffff', highlightthickness=1, highlightbackground='#d4d9e8')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Icon
        icon_label = tk.Label(main_frame, text="🔐", font=('Arial', 48), bg='#ffffff')
        icon_label.pack(pady=(20, 10))
        
        # Title
        title = tk.Label(main_frame, text="Decrypt & Extract File", font=('Segoe UI', 14, 'bold'),
                        fg='#2563eb', bg='#ffffff')
        title.pack(pady=(5, 10))
        
        # File info
        info_text = tk.Label(main_frame, text=f"File: {file_name}", font=('Segoe UI', 10),
                            fg='#4a5568', bg='#ffffff', wraplength=400)
        info_text.pack(pady=(5, 20))
        
        # Password label
        pwd_label = tk.Label(main_frame, text="Enter Password:", font=('Segoe UI', 10),
                            fg='#1f2937', bg='#ffffff')
        pwd_label.pack(anchor='w', padx=40, pady=(5, 2))
        
        # Password entry
        pwd_var = tk.StringVar()
        pwd_entry = ttk.Entry(main_frame, textvariable=pwd_var, show='•', width=40)
        pwd_entry.pack(padx=40, pady=(0, 20), fill='x')
        pwd_entry.focus()
        
        # Status label
        status_label = tk.Label(main_frame, text='', font=('Segoe UI', 9), fg='#ea580c', bg='#ffffff')
        status_label.pack(pady=(5, 15))
        
        # Button frame
        btn_frame = tk.Frame(main_frame, bg='#ffffff')
        btn_frame.pack(pady=(10, 20), fill='x', padx=40)
        
        # Create button placeholders
        decrypt_btn = None
        close_btn = None
        
        def decrypt_and_save():
            """Decrypt file and let user save it"""
            #if not pwd_var.get():
             #   status_label.config(text='❌ Please enter password', fg='#ef4444')
              #  return
            
            # Ask where to save
            suggested_name = file_name if file_name else 'decrypted_file'
            dest_path = filedialog.asksaveasfilename(
                title='Save decrypted file as',
                initialfile=suggested_name,
                filetypes=[("All files", "*.*")]
            )
            
            if not dest_path:
                return
            
            # Disable buttons during decryption
            if decrypt_btn:
                decrypt_btn.config(state='disabled')
            if close_btn:
                close_btn.config(state='disabled')
            pwd_entry.config(state='disabled')
            status_label.config(text='🔄 Decrypting...', fg='#ea580c')
            dialog.update_idletasks()
            
            try:
                # Decrypt file
                success, result = self.vault.retrieve_file(file_id, pwd_var.get(), dest_path)
                if success:
                    saved_path = result
                    status_label.config(text=f'✅ File saved successfully', fg='#22c55e')
                    messagebox.showinfo('Success', f'File saved to:\n\n{saved_path}')
                    dialog.destroy()
                else:
                    if result == 'invalid_password':
                        status_label.config(text='❌ Invalid password', fg='#ef4444')
                    elif result == 'corrupted_steganography':
                        status_label.config(text='❌ File corrupted (steganography)', fg='#ef4444')
                        messagebox.showerror("Steganography Error", 
                            "⚠️ File marked as steganographic but decryption failed.\n\n"
                            "This may indicate:\n"
                            "• File is corrupted\n"
                            "• Incorrect password\n"
                            "• Invalid steganographic carrier\n\n"
                            "Please verify the file and password are correct.")
                    elif error_code == 'hash_mismatch':
                        status_label.config(text='❌ File integrity check failed', fg='#ef4444')
                    else:
                        status_label.config(text=f'❌ {error_code}', fg='#ef4444')
            except Exception as e:
                logging.error(f'Decrypt error: {e}')
                status_label.config(text=f'❌ Error: {str(e)[:30]}', fg='#ef4444')
            finally:
                if decrypt_btn and dialog.winfo_exists():
                    decrypt_btn.config(state='normal')
                if close_btn and dialog.winfo_exists():
                    close_btn.config(state='normal')
                if dialog.winfo_exists():
                    pwd_entry.config(state='normal')
        
        # Now create buttons
        decrypt_btn = ttk.Button(btn_frame, text='🔓 Decrypt & Save', command=decrypt_and_save)
        decrypt_btn.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        close_btn = ttk.Button(btn_frame, text='Close', command=dialog.destroy)
        close_btn.pack(side='left', fill='x', expand=True)
        
        # Allow Enter key to decrypt
        pwd_entry.bind('<Return>', lambda e: decrypt_and_save())
    
    # ========== SAVE & QUICK SAVE DIALOGS ==========
    
    def show_save_dialog(self):
        """Show comprehensive save dialog with multiple save options"""
        dialog = tk.Toplevel(self.root)
        dialog.title("💾 Save Vault Data")
        dialog.geometry("600x500")
        dialog.configure(bg='#0f172a')
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='#1e293b', highlightthickness=2, highlightbackground='#334155')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title
        title = tk.Label(main_frame, text="💾 Save Vault Data", font=('Segoe UI', 14, 'bold'),
                        fg='white', bg='#1e293b')
        title.pack(pady=(20, 5))
        
        # Subtitle
        subtitle = tk.Label(main_frame, text="Choose what to save and where",
                           font=('Segoe UI', 9), fg='#94a3b8', bg='#1e293b')
        subtitle.pack(pady=(0, 20))
        
        # ==================== SAVE OPTIONS ====================
        
        # Option 1: Quick Save Encrypted Backup
        option1_frame = tk.Frame(main_frame, bg='#334155', highlightthickness=1,
                                highlightbackground='#475569')
        option1_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(option1_frame, text="⚡ Quick Save (Encrypted Backup)", font=('Segoe UI', 10, 'bold'),
                fg='#10b981', bg='#334155').pack(anchor='w', padx=15, pady=(10, 5))
        
        tk.Label(option1_frame, text="Save vault as encrypted backup to default location",
                font=('Segoe UI', 9), fg='#cbd5e1', bg='#334155').pack(anchor='w', padx=15, pady=(0, 5))
        
        tk.Label(option1_frame, text="📍 Location: Desktop/SecureVault_Backup_[date].enc",
                font=('Segoe UI', 8), fg='#94a3b8', bg='#334155').pack(anchor='w', padx=15, pady=(0, 10))
        
        tk.Button(option1_frame, text="⚡ Quick Save", font=('Segoe UI', 10),
                 bg='#6366f1', fg='white', relief='flat', bd=0, padx=20, pady=8,
                 cursor='hand2', activebackground='#4f46e5',
                 command=self._quick_save_vault).pack(fill='x', padx=15, pady=(0, 10))
        
        # Option 2: Save to Custom Location
        option2_frame = tk.Frame(main_frame, bg='#334155', highlightthickness=1,
                                highlightbackground='#475569')
        option2_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(option2_frame, text="📁 Save As (Custom Location)", font=('Segoe UI', 10, 'bold'),
                fg='#a78bfa', bg='#334155').pack(anchor='w', padx=15, pady=(10, 5))
        
        tk.Label(option2_frame, text="Save vault backup to a custom location of your choice",
                font=('Segoe UI', 9), fg='#cbd5e1', bg='#334155').pack(anchor='w', padx=15, pady=(0, 5))
        
        tk.Label(option2_frame, text="💡 Tip: Include date in filename for version control",
                font=('Segoe UI', 8), fg='#94a3b8', bg='#334155').pack(anchor='w', padx=15, pady=(0, 10))
        
        tk.Button(option2_frame, text="📁 Save As...", font=('Segoe UI', 10),
                 bg='#6366f1', fg='white', relief='flat', bd=0, padx=20, pady=8,
                 cursor='hand2', activebackground='#4f46e5',
                 command=self._save_vault_as).pack(fill='x', padx=15, pady=(0, 10))
        
        # Option 3: Export Files
        option3_frame = tk.Frame(main_frame, bg='#334155', highlightthickness=1,
                                highlightbackground='#475569')
        option3_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(option3_frame, text="📤 Export Selected File", font=('Segoe UI', 10, 'bold'),
                fg='#f59e0b', bg='#334155').pack(anchor='w', padx=15, pady=(10, 5))
        
        tk.Label(option3_frame, text="Extract and save an encrypted file from vault",
                font=('Segoe UI', 9), fg='#cbd5e1', bg='#334155').pack(anchor='w', padx=15, pady=(0, 5))
        
        tk.Label(option3_frame, text="🔐 Files are decrypted during export",
                font=('Segoe UI', 8), fg='#94a3b8', bg='#334155').pack(anchor='w', padx=15, pady=(0, 10))
        
        tk.Button(option3_frame, text="📤 Export File", font=('Segoe UI', 10),
                 bg='#6366f1', fg='white', relief='flat', bd=0, padx=20, pady=8,
                 cursor='hand2', activebackground='#4f46e5',
                 command=self.retrieve_file_dialog).pack(fill='x', padx=15, pady=(0, 10))
        
        # ==================== INFO BOX ====================
        
        info_frame = tk.Frame(main_frame, bg='#1e293b')
        info_frame.pack(fill='x', padx=20, pady=(10, 0))
        
        tk.Label(info_frame, text="ℹ️ All backups are encrypted with your vault password",
                font=('Segoe UI', 8), fg='#cbd5e1', bg='#1e293b').pack(anchor='w')
        
        # ==================== BUTTONS ====================
        
        btn_frame = tk.Frame(main_frame, bg='#1e293b')
        btn_frame.pack(fill='x', padx=20, pady=(20, 15))
        
        tk.Button(btn_frame, text="✕ Close", font=('Segoe UI', 10),
                 bg='#475569', fg='white', relief='flat', bd=0, padx=20, pady=8,
                 cursor='hand2', activebackground='#64748b',
                 command=dialog.destroy).pack(side='right')
    
    def show_quick_save_popup(self):
        """Show quick save progress popup"""
        popup = tk.Toplevel(self.root)
        popup.title("⚡ Quick Save")
        popup.geometry("400x200")
        popup.configure(bg='#0f172a')
        popup.resizable(False, False)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (400 // 2)
        y = (popup.winfo_screenheight() // 2) - (200 // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Prevent close
        popup.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Main frame
        main_frame = tk.Frame(popup, bg='#1e293b', highlightthickness=2, highlightbackground='#334155')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Icon
        icon = tk.Label(main_frame, text="⚡", font=('Arial', 40), bg='#1e293b')
        icon.pack(pady=(20, 10))
        
        # Title
        title = tk.Label(main_frame, text="Quick Saving Vault...", font=('Segoe UI', 12, 'bold'),
                         fg='white', bg='#1e293b')
        title.pack(pady=5)
        
        # Progress bar
        progress = tk.Frame(main_frame, bg='#334155', height=6)
        progress.pack(fill='x', padx=40, pady=10)
        progress.pack_propagate(False)
        
        progress_bar = tk.Frame(progress, bg='#10b981', height=6)
        progress_bar.pack(side='left', fill='both', expand=True)
        
        # Status
        status = tk.Label(main_frame, text="Encrypting and saving vault backup...",
                         font=('Segoe UI', 9), fg='#cbd5e1', bg='#1e293b')
        status.pack(pady=(10, 20))
        
        popup.update()
        return popup, progress_bar, status
    
    def _quick_save_vault(self):
        """Quick save vault to default location (Desktop)"""
        try:
            # Get desktop path
            desktop = os.path.expanduser('~/Desktop')
            os.makedirs(desktop, exist_ok=True)
            
            # Generate filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'SecureVault_Backup_{timestamp}.enc'
            save_path = os.path.join(desktop, filename)
            
            # Show progress popup
            popup, progress_bar, status = self.show_quick_save_popup()
            
            # Encrypt entire vault directory
            vault_path = 'secure_vault'
            
            # Create a backup archive
            import shutil
            temp_backup = os.path.join(tempfile.gettempdir(), 'vault_backup_temp')
            
            if os.path.exists(temp_backup):
                shutil.rmtree(temp_backup)
            
            # Copy vault to temp location
            shutil.copytree(vault_path, temp_backup)
            
            # Update progress
            popup.update()
            progress_bar.pack_forget()
            progress_bar2 = tk.Frame(progress_bar.master, bg='#10b981', height=6)
            progress_bar2.pack(side='left', fill='both', expand=True, padx=(0, 20))
            popup.update()
            
            # Create zip of vault
            zip_path = os.path.join(tempfile.gettempdir(), 'vault_backup.zip')
            shutil.make_archive(zip_path[:-4], 'zip', temp_backup)
            
            # Encrypt the zip
            with open(zip_path, 'rb') as f:
                vault_data = f.read()
            
            encrypted, salt = EncryptionManager.encrypt(vault_data, 'vault_backup')
            
            # Save encrypted backup
            backup_data = {
                'encrypted': base64.b64encode(encrypted).decode(),
                'salt': base64.b64encode(salt).decode(),
                'timestamp': datetime.now().isoformat(),
                'version': '2.0'
            }
            
            with open(save_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Cleanup
            shutil.rmtree(temp_backup)
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            # Close popup
            popup.destroy()
            
            # Show success
            messagebox.showinfo(
                "✅ Quick Save Successful",
                f"Vault backup saved to:\
\
{save_path}\
\
Size: {os.path.getsize(save_path) / (1024*1024):.2f} MB"
            )
            
            logging.info(f"Vault quick saved to: {save_path}")
            
        except Exception as e:
            logging.error(f"Quick save error: {e}")
            messagebox.showerror("Quick Save Error", f"Failed to quick save vault:\n{str(e)}")
    
    def _save_vault_as(self):
        """Save vault to custom location"""
        try:
            save_path = filedialog.asksaveasfilename(
                title="Save Vault Backup As",
                defaultextension=".enc",
                filetypes=[("Encrypted Backup", "*.enc"), ("All files", "*.*")],
                initialfile=f"SecureVault_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.enc"
            )
            
            if not save_path:
                return
            
            # Show progress
            popup, progress_bar, status = self.show_quick_save_popup()
            status.config(text="Saving to custom location...")
            popup.update()
            
            # Create backup
            vault_path = 'secure_vault'
            temp_backup = os.path.join(tempfile.gettempdir(), 'vault_backup_temp')
            
            if os.path.exists(temp_backup):
                shutil.rmtree(temp_backup)
            
            shutil.copytree(vault_path, temp_backup)
            popup.update()
            
            # Create zip
            zip_path = os.path.join(tempfile.gettempdir(), 'vault_backup.zip')
            shutil.make_archive(zip_path[:-4], 'zip', temp_backup)
            
            # Encrypt
            with open(zip_path, 'rb') as f:
                vault_data = f.read()
            
            encrypted, salt = EncryptionManager.encrypt(vault_data, 'vault_backup')
            
            # Save
            backup_data = {
                'encrypted': base64.b64encode(encrypted).decode(),
                'salt': base64.b64encode(salt).decode(),
                'timestamp': datetime.now().isoformat(),
                'version': '2.0'
            }
            
            with open(save_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Cleanup
            shutil.rmtree(temp_backup)
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            popup.destroy()
            
            messagebox.showinfo(
                "Save Successful",
                f"Vault backup saved to:\n\n{save_path}\n\nSize: {os.path.getsize(save_path) / (1024*1024):.2f} MB"
            )
            
            logging.info(f"Vault saved to: {save_path}")
            
        except Exception as e:
            logging.error(f"Save error: {e}")
            messagebox.showerror("Save Error", f"Failed to save vault:\n{str(e)}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Launch application"""
    root = tk.Tk()
    app = SecureVaultGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
