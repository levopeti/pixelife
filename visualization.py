"""
Pygame-based visualization system
Provides interactive viewing with always-visible statistics panel
Can toggle between fast mode (no rendering) and visual mode
"""

import pygame
import sys
from resources import ResourceType
import config

class Visualization:
    """Pygame visualization with fast mode toggle"""
    
    def __init__(self, world, statistics):
        pygame.init()
        
        self.world = world
        self.statistics = statistics
        
        # Window setup
        self.screen_width = 1400
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Artificial Life Simulation")
        
        # Panel dimensions (always visible on the right)
        self.panel_width = 350
        self.panel_x = self.screen_width - self.panel_width
        self.world_view_width = self.screen_width - self.panel_width
        
        # Camera/view settings
        self.zoom = config.INITIAL_ZOOM
        self.camera_x = 0
        self.camera_y = 0
        
        # UI settings
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        self.tiny_font = pygame.font.Font(None, 16)
        
        # Control settings
        self.paused = False
        self.simulation_speed = 1  # 1-9 in visual mode
        self.fast_mode = False  # Toggle between fast and visual mode
        
        # When in fast mode, track updates for occasional rendering
        self.fast_mode_render_interval = 100  # Render every N ticks in fast mode
        self.last_fast_render_tick = 0
        
        self.clock = pygame.time.Clock()
    
    def handle_events(self):
        """Handle pygame events (keyboard, mouse)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Pause/unpause (only in visual mode)
                if event.key == pygame.K_SPACE:
                    if not self.fast_mode:
                        self.paused = not self.paused
                
                # Toggle fast mode with F key
                if event.key == pygame.K_f:
                    self.fast_mode = not self.fast_mode
                    print(f"{'FAST' if self.fast_mode else 'VISUAL'} mode activated")
                
                # Speed control (1-9) - only in visual mode
                if not self.fast_mode and pygame.K_1 <= event.key <= pygame.K_9:
                    self.simulation_speed = event.key - pygame.K_0
                
                # Camera movement (only in visual mode)
                if not self.fast_mode:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.camera_y -= config.PAN_SPEED / self.zoom
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.camera_y += config.PAN_SPEED / self.zoom
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.camera_x -= config.PAN_SPEED / self.zoom
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.camera_x += config.PAN_SPEED / self.zoom
                
                # Save with S key
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    return 'save'
                
                # Load with L key
                if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    return 'load'
            
            if event.type == pygame.MOUSEWHEEL and not self.fast_mode:
                # Zoom in/out (only in visual mode)
                if event.y > 0:
                    self.zoom = min(self.zoom + config.ZOOM_SPEED, config.MAX_ZOOM)
                else:
                    self.zoom = max(self.zoom - config.ZOOM_SPEED, config.MIN_ZOOM)
        
        return True
    
    def should_render(self):
        """Determine if we should render this frame"""
        if not self.fast_mode:
            return True
        
        # In fast mode, render occasionally to show we're still running
        if self.statistics.ticks - self.last_fast_render_tick >= self.fast_mode_render_interval:
            self.last_fast_render_tick = self.statistics.ticks
            return True
        
        return False
    
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_x - self.camera_x) * config.CELL_SIZE * self.zoom
        screen_y = (world_y - self.camera_y) * config.CELL_SIZE * self.zoom
        return int(screen_x), int(screen_y)
    
    def render(self):
        """Render the world and panel to the screen"""
        # Clear screen
        self.screen.fill((10, 10, 10))
        
        if not self.fast_mode:
            # Render world view (only in visual mode)
            self._render_world_view()
        else:
            # In fast mode, show a simple indicator
            self._render_fast_mode_indicator()
        
        # Always render the statistics panel
        self._render_panel()
        
        pygame.display.flip()
    
    def _render_world_view(self):
        """Render the world grid"""
        cell_size_zoomed = config.CELL_SIZE * self.zoom
        
        start_x = max(0, int(self.camera_x))
        end_x = min(self.world.width, int(self.camera_x + self.world_view_width / cell_size_zoomed) + 1)
        start_y = max(0, int(self.camera_y))
        end_y = min(self.world.height, int(self.camera_y + self.screen_height / cell_size_zoomed) + 1)
        
        # Render world grid
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x, screen_y = self.world_to_screen(x, y)
                
                # Skip if off screen or in panel area
                if (screen_x < -cell_size_zoomed or screen_x > self.world_view_width or
                    screen_y < -cell_size_zoomed or screen_y > self.screen_height):
                    continue
                
                cell_type = self.world.get_cell_type(x, y)
                color = self._get_cell_color(x, y, cell_type)
                
                rect = pygame.Rect(screen_x, screen_y, 
                                  max(1, int(cell_size_zoomed)), 
                                  max(1, int(cell_size_zoomed)))
                pygame.draw.rect(self.screen, color, rect)
                
                # Draw creature with its genetic color
                if cell_type == ResourceType.CREATURE:
                    creature = self.world.get_creature_at(x, y)
                    if creature:
                        pygame.draw.rect(self.screen, creature.color, rect)
    
    def _render_fast_mode_indicator(self):
        """Show indicator that fast mode is active"""
        # Create a dark background
        fast_surface = pygame.Surface((self.world_view_width, self.screen_height))
        fast_surface.fill((5, 5, 5))
        self.screen.blit(fast_surface, (0, 0))
        
        # Show big text
        text = self.font.render("FAST MODE", True, (100, 200, 100))
        text_rect = text.get_rect(center=(self.world_view_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(text, text_rect)
        
        subtext = self.small_font.render("Press F to return to visual mode", True, (150, 150, 150))
        subtext_rect = subtext.get_rect(center=(self.world_view_width // 2, self.screen_height // 2))
        self.screen.blit(subtext, subtext_rect)
        
        # Show current tick
        tick_text = self.small_font.render(f"Tick: {self.statistics.ticks}", True, (200, 200, 200))
        tick_rect = tick_text.get_rect(center=(self.world_view_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(tick_text, tick_rect)
    
    def _get_cell_color(self, x, y, cell_type):
        """Get color for a cell based on its type"""
        if cell_type == ResourceType.EMPTY:
            return config.COLOR_EMPTY
        elif cell_type == ResourceType.WALL:
            return config.COLOR_WALL
        elif cell_type == ResourceType.FOOD:
            return config.COLOR_FOOD
        elif cell_type == ResourceType.PLANT:
            resource = self.world.get_resource_at(x, y)
            if resource:
                growth_factor = getattr(resource, 'growth_stage', 0) / 10.0
                green = int(100 + growth_factor * 155)
                return (30, green, 30)
            return config.COLOR_PLANT
        elif cell_type == ResourceType.CREATURE:
            return config.COLOR_CREATURE
        else:
            return config.COLOR_EMPTY
    
    def _render_panel(self):
        """Render the always-visible statistics panel"""
        # Panel background
        panel_surface = pygame.Surface((self.panel_width, self.screen_height))
        panel_surface.fill((25, 25, 30))
        self.screen.blit(panel_surface, (self.panel_x, 0))
        
        # Draw border
        pygame.draw.line(self.screen, (60, 60, 70), 
                        (self.panel_x, 0), (self.panel_x, self.screen_height), 2)
        
        y_offset = 20
        x_offset = self.panel_x + 15
        
        # Title
        title = self.font.render("Simulation Stats", True, (200, 220, 255))
        self.screen.blit(title, (x_offset, y_offset))
        y_offset += 40
        
        # Mode indicator
        mode_text = "FAST MODE" if self.fast_mode else "VISUAL MODE"
        mode_color = (100, 255, 100) if self.fast_mode else (100, 150, 255)
        mode = self.small_font.render(mode_text, True, mode_color)
        self.screen.blit(mode, (x_offset, y_offset))
        y_offset += 30
        
        # Statistics
        stats_lines = [
            ("Time", f"{self.statistics.get_elapsed_time():.0f}s"),
            ("Ticks", f"{self.statistics.ticks}"),
            ("TPS", f"{self.statistics.ticks_per_second:.1f}"),
            ("", ""),
            ("Creatures", f"{self.statistics.creature_count}"),
            ("Peak Pop", f"{self.statistics.peak_population}"),
            ("Births", f"{self.statistics.total_births}"),
            ("Deaths", f"{self.statistics.total_deaths}"),
            ("", ""),
            ("Avg Gen", f"{self.statistics.average_generation:.1f}"),
            ("Max Gen", f"{self.statistics.max_generation}"),
        ]
        
        for label, value in stats_lines:
            if label == "":
                y_offset += 10
            else:
                label_text = self.small_font.render(label + ":", True, (150, 150, 150))
                value_text = self.small_font.render(value, True, (220, 220, 220))
                self.screen.blit(label_text, (x_offset, y_offset))
                self.screen.blit(value_text, (x_offset + 120, y_offset))
                y_offset += 25
        
        # Average traits section
        if self.statistics.average_traits:
            y_offset += 10
            traits_title = self.small_font.render("Average Traits:", True, (200, 220, 255))
            self.screen.blit(traits_title, (x_offset, y_offset))
            y_offset += 25
            
            for trait, value in list(self.statistics.average_traits.items())[:5]:
                trait_text = self.tiny_font.render(f"{trait}: {value:.2f}", True, (180, 180, 180))
                self.screen.blit(trait_text, (x_offset + 10, y_offset))
                y_offset += 20
        
        # Visual mode controls
        if not self.fast_mode:
            y_offset += 20
            zoom_text = self.small_font.render(f"Zoom: {self.zoom:.2f}x", True, (150, 150, 150))
            self.screen.blit(zoom_text, (x_offset, y_offset))
            y_offset += 25
            
            speed_text = self.small_font.render(f"Speed: {self.simulation_speed}x", True, (150, 150, 150))
            self.screen.blit(speed_text, (x_offset, y_offset))
            y_offset += 25
            
            if self.paused:
                pause_text = self.font.render("PAUSED", True, (255, 200, 100))
                self.screen.blit(pause_text, (x_offset, y_offset))
                y_offset += 30
        
        # Controls help at bottom
        help_y = self.screen_height - 280
        pygame.draw.line(self.screen, (60, 60, 70),
                        (self.panel_x + 10, help_y - 10),
                        (self.screen_width - 10, help_y - 10), 1)
        
        controls_title = self.small_font.render("Controls:", True, (200, 220, 255))
        self.screen.blit(controls_title, (x_offset, help_y))
        help_y += 30
        
        controls = [
            "F - Toggle Fast/Visual",
            "Space - Pause (visual)",
            "WASD/Arrows - Pan",
            "Mouse Wheel - Zoom",
            "1-9 - Speed (visual)",
            "",
            "Ctrl+S - Save",
            "Ctrl+L - Load",
            "ESC - Quit"
        ]
        
        for control in controls:
            if control == "":
                help_y += 10
            else:
                text = self.tiny_font.render(control, True, (150, 150, 150))
                self.screen.blit(text, (x_offset, help_y))
                help_y += 22
    
    def get_target_fps(self):
        """Get target FPS based on mode"""
        if self.fast_mode:
            return 30  # Just keep window responsive in fast mode
        else:
            return 60  # Smooth rendering in visual mode
    
    def get_ticks_per_frame(self):
        """Get how many simulation ticks to run per frame"""
        if self.fast_mode:
            # In fast mode, run many ticks per frame
            return config.FAST_MODE_TPS // 30  # Divide by FPS
        else:
            # In visual mode, respect speed setting
            return self.simulation_speed
    
    def tick(self):
        """Tick the visualization clock"""
        self.clock.tick(self.get_target_fps())

