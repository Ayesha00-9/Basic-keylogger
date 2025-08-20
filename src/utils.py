import json
import os
from cryptography.fernet import Fernet
from datetime import datetime
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_config():
    """Load configuration from environment variables"""
    try:
        # Try to load from .env file first
        log_directory = os.getenv('LOG_DIRECTORY', 'logs')
        log_extension = os.getenv('LOG_EXTENSION', '.klg')
        encryption_key = os.getenv('ENCRYPTION_KEY', 'default-key-change-in-production0000')
        
        # Ensure the encryption key is properly formatted
        if len(encryption_key) < 32:
            encryption_key = encryption_key.ljust(32, '0')[:32]
        
        # Encode the key to base64 for Fernet
        encryption_key = base64.urlsafe_b64encode(encryption_key.encode()[:32].ljust(32, b'0')).decode()
        
        check_interval = float(os.getenv('CHECK_INTERVAL', '1.0'))
        
        return {
            "log_directory": log_directory,
            "log_extension": log_extension,
            "encryption_key": encryption_key,
            "check_interval": check_interval
        }
    except Exception as e:
        print(f"Error loading config from environment: {e}")
        # Fallback to default config
        default_key = base64.urlsafe_b64encode(b"default-key-change-in-production0000").decode()
        return {
            "log_directory": "logs",
            "log_extension": ".klg",
            "encryption_key": default_key,
            "check_interval": 1.0
        }

def ensure_log_directory():
    """Create log directory if it doesn't exist"""
    config = load_config()
    if not os.path.exists(config['log_directory']):
        os.makedirs(config['log_directory'])
    return config['log_directory']

def encrypt_data(data, key):
    """Encrypt data using Fernet symmetric encryption"""
    try:
        f = Fernet(key)
        return f.encrypt(data.encode())
    except Exception as e:
        print(f"Encryption error: {e}")
        return data.encode()

def decrypt_data(encrypted_data, key):
    """Decrypt data using Fernet symmetric encryption"""
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return f"[Unable to decrypt: {str(encrypted_data)[:50]}...]"

def get_log_filename():
    """Generate a timestamped log filename"""
    log_dir = ensure_log_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config = load_config()
    return os.path.join(log_dir, f"keylog_{timestamp}{config['log_extension']}")

def get_app_settings():
    """Get application settings from environment"""
    return {
        "app_name": os.getenv('APP_NAME', 'Local Keylogger'),
        "app_version": os.getenv('APP_VERSION', '1.0.0'),
        "app_description": os.getenv('APP_DESCRIPTION', 'Educational keylogger for resume enhancement'),
        "enable_encryption": os.getenv('ENABLE_ENCRYPTION', 'true').lower() == 'true',
        "max_log_size_mb": float(os.getenv('MAX_LOG_SIZE_MB', '10')),
        "auto_cleanup_days": int(os.getenv('AUTO_CLEANUP_DAYS', '30')),
        "ui_theme": os.getenv('UI_THEME', 'light'),
        "ui_width": int(os.getenv('UI_WIDTH', '500')),
        "ui_height": int(os.getenv('UI_HEIGHT', '400')),
        "ui_refresh_rate": int(os.getenv('UI_REFRESH_RATE', '30'))
    }