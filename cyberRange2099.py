import pygame
import random
import sys
import math
from pygame import mixer

FULLSCREEN = False

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER RANGE 2099")

def toggle_fullscreen():
    global FULLSCREEN, screen
    FULLSCREEN = not FULLSCREEN
    if FULLSCREEN:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BRIGHT_BLUE = (0, 120, 255)
NEON_GREEN = (0, 255, 128)
DARK_PURPLE = (80, 0, 80)
BRIGHT_RED = (255, 60, 60)
YELLOW = (255, 255, 0)
ORANGE = (255, 160, 0)

SCANLINE_COLOR = (0, 0, 0, 50)

try:
    main_font = pygame.font.Font("pixelfont.ttf", 32)
    small_font = pygame.font.Font("pixelfont.ttf", 20)
except:
    main_font = pygame.font.SysFont("Arial", 32)
    small_font = pygame.font.SysFont("Arial", 20)

try:
    gunshot = mixer.Sound("gunshot.mp3")
    reload_sound = mixer.Sound("reload.mp3")
    #hit_sound = mixer.Sound("hit.mp3")
    
    mixer.music.load("background.mp3")
    mixer.music.set_volume(0.5)
    mixer.music.play(-1)
except:
    empty_sound = pygame.mixer.Sound(buffer=bytes(bytearray(705)))
    gunshot = empty_sound
    reload_sound = empty_sound
    hit_sound = empty_sound

class Target:
    def __init__(self, size=50):
        self.size = size
        self.reset()
        self.create_image()
        
    def create_image(self):
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        target_type = random.choice(["standard", "bonus", "special"])
        
        if target_type == "standard":
            outer_color = CYAN
            inner_color = MAGENTA
            center_color = BRIGHT_RED
        elif target_type == "bonus":
            outer_color = YELLOW
            inner_color = ORANGE
            center_color = BRIGHT_RED
        else:
            outer_color = NEON_GREEN
            inner_color = BRIGHT_BLUE
            center_color = WHITE
        
        pygame.draw.circle(self.image, outer_color, (self.size//2, self.size//2), self.size//2)
        pygame.draw.circle(self.image, BLACK, (self.size//2, self.size//2), self.size//2, 2)
        pygame.draw.circle(self.image, inner_color, (self.size//2, self.size//2), self.size//3)
        pygame.draw.circle(self.image, BLACK, (self.size//2, self.size//2), self.size//3, 2)
        pygame.draw.circle(self.image, center_color, (self.size//2, self.size//2), self.size//6)
        
        line_length = self.size // 4
        pygame.draw.line(self.image, BLACK, 
                        (self.size//2 - line_length, self.size//2), 
                        (self.size//2 + line_length, self.size//2), 
                        2)
        pygame.draw.line(self.image, BLACK, 
                        (self.size//2, self.size//2 - line_length), 
                        (self.size//2, self.size//2 + line_length), 
                        2)
        
        scale_factor = 4
        small_img = pygame.transform.scale(self.image, 
                                          (self.size // scale_factor, self.size // scale_factor))
        self.image = pygame.transform.scale(small_img, (self.size, self.size))
    
    def reset(self):
        margin = 100
        self.x = random.randint(margin, WIDTH - margin)
        self.y = random.randint(margin, HEIGHT - margin)
        self.active = True
        
        self.move_speed = 0.3
        self.direction = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(self.direction) * self.move_speed
        self.dy = math.sin(self.direction) * self.move_speed
        self.time_alive = 0
        
        self.create_image()
        
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.2, 0.2)
    
    def update(self, dt):
        if not self.active:
            return
        
        self.time_alive += dt
        
        self.x += self.dx * dt
        self.y += self.dy * dt
        
        self.rotation += self.rotation_speed * dt / 10
        
        if self.x < 0 or self.x > WIDTH - self.size:
            self.dx *= -1
            if random.random() < 0.3:
                self.dy = -self.dy
        if self.y < 0 or self.y > HEIGHT - self.size:
            self.dy *= -1
            if random.random() < 0.3:
                self.dx = -self.dx
            
        current_speed = math.sqrt(self.dx*self.dx + self.dy*self.dy)
        if current_speed > self.move_speed * 1.5:
            self.dx = (self.dx / current_speed) * self.move_speed * 1.5
            self.dy = (self.dy / current_speed) * self.move_speed * 1.5
        
        if random.random() < 0.005:
            angles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 
                     5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
            self.direction = random.choice(angles)
            self.dx = math.cos(self.direction) * self.move_speed
            self.dy = math.sin(self.direction) * self.move_speed
    
    def draw(self, surface):
        if self.active:
            if self.rotation != 0:
                rotated_image = pygame.transform.rotate(self.image, self.rotation)
                new_rect = rotated_image.get_rect(center=(self.x, self.y))
                surface.blit(rotated_image, new_rect.topleft)
            else:
                surface.blit(self.image, (self.x - self.size//2, self.y - self.size//2))
    
    def hit_test(self, x, y):
        if not self.active:
            return False, 0
        
        dx = x - self.x
        dy = y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.size//2:
            score = max(1, 10 - int(distance / (self.size/10)))
            self.active = False
            return True, score
        return False, 0

class Explosion:
    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.lifetime = 500
        self.time = 0
        self.particles = []
        
        num_particles = 20
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.1, 0.5)
            size = random.randint(2, 8)
            color = random.choice([
                CYAN,
                MAGENTA,
                BRIGHT_BLUE,
                NEON_GREEN,
                YELLOW,
                BRIGHT_RED
            ])
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed * size,
                'dy': math.sin(angle) * speed * size,
                'size': size,
                'color': color,
                'shape': random.choice(['circle', 'square', 'pixel'])
            })
    
    def update(self, dt):
        self.time += dt
        for particle in self.particles:
            particle['x'] += particle['dx'] * dt
            particle['y'] += particle['dy'] * dt
            particle['size'] = max(0, particle['size'] - dt * 0.01)
    
    def draw(self, surface):
        for particle in self.particles:
            if particle['size'] > 0:
                if particle['shape'] == 'circle':
                    pygame.draw.circle(
                        surface, 
                        particle['color'], 
                        (int(particle['x']), int(particle['y'])), 
                        int(particle['size'])
                    )
                elif particle['shape'] == 'square':
                    size = int(particle['size'] * 2)
                    pygame.draw.rect(
                        surface,
                        particle['color'],
                        (int(particle['x'] - size/2), int(particle['y'] - size/2), size, size)
                    )
                else:
                    size = int(particle['size'] * 1.5)
                    pygame.draw.rect(
                        surface,
                        particle['color'],
                        (int(particle['x'] - size/2), int(particle['y'] - size/2), size, size)
                    )
    
    def is_complete(self):
        return self.time >= self.lifetime

class Game:
    def __init__(self):
        self.score = 0
        self.shots_fired = 0
        self.hits = 0
        self.miss_count = 0
        self.max_misses = 5
        
        self.wave = 1
        self.targets_per_wave = 10
        self.targets_cleared = 0
        self.base_speed = 0.3
        self.speed_increase = 0.2
        
        self.targets = [Target() for _ in range(5)]
        self.explosions = []
        self.game_over = False
        self.game_won = False
        self.ammo = 12
        self.max_ammo = 12
        self.reloading = False
        self.reload_time = 0
        self.reload_duration = 1500
        
        self.scanlines = []
        for y in range(0, HEIGHT, 3):
            self.scanlines.append(pygame.Rect(0, y, WIDTH, 1))
            
        self.border_width = 20
        
        self.set_wave_difficulty()
        
        self.dialog_messages = [
            "MISSION: ELIMINATE ALL TARGETS",
            "SYSTEM ONLINE. TARGETING ACTIVE.",
            "SUSPECT DETECTED. TAKE THE SHOT.",
            "WATCH YOUR AMMO COUNT, ROOKIE.",
            "ACCURACY IS KEY. DON'T WASTE SHOTS."
        ]
        self.current_dialog = random.choice(self.dialog_messages)
        self.dialog_timer = 3000
        self.show_dialog = True
        
    def reset(self):
        self.__init__()
        
    def set_wave_difficulty(self):
        current_speed = self.base_speed + (self.wave - 1) * self.speed_increase
        
        for target in self.targets:
            target.move_speed = current_speed
            target.dx = math.cos(target.direction) * target.move_speed
            target.dy = math.sin(target.direction) * target.move_speed
        
        rotation_factor = min(1.0, 0.1 + (self.wave * 0.05))
        
        for target in self.targets:
            target.rotation_speed = random.uniform(-0.2, 0.2) * rotation_factor
        
        wave_dialogs = [
            f"WAVE {self.wave} INITIATED. THREAT LEVEL INCREASED.",
            f"WARNING: ENEMY REINFORCEMENTS DETECTED.",
            f"SYSTEM UPGRADE COMPLETE. PROCEEDING TO WAVE {self.wave}.",
            f"TARGETS ARE MOVING FASTER. STAY FOCUSED."
        ]
        self.current_dialog = random.choice(wave_dialogs)
        self.dialog_timer = 3000
        self.show_dialog = True
        
    def update(self, dt):
        if self.game_over or self.game_won:
            return
        
        if self.show_dialog:
            self.dialog_timer -= dt
            if self.dialog_timer <= 0:
                self.show_dialog = False
        
        if self.reloading:
            self.reload_time += dt
            if self.reload_time >= self.reload_duration:
                self.ammo = self.max_ammo
                self.reloading = False
                self.current_dialog = "RELOAD COMPLETE. WEAPON READY."
                self.dialog_timer = 1500
                self.show_dialog = True
        
        for explosion in list(self.explosions):
            explosion.update(dt)
            if explosion.is_complete():
                self.explosions.remove(explosion)
                
        active_targets = sum(1 for target in self.targets if target.active)
        
        for target in self.targets:
            target.update(dt)
            
            if not target.active and active_targets < len(self.targets):
                target.reset()
                target.move_speed = self.base_speed + (self.wave - 1) * self.speed_increase
                target.dx = math.cos(target.direction) * target.move_speed
                target.dy = math.sin(target.direction) * target.move_speed
                active_targets += 1
                
        if self.targets_cleared >= self.targets_per_wave:
            self.wave += 1
            self.targets_cleared = 0
            
            self.miss_count = max(0, self.miss_count - 2)
            
            self.set_wave_difficulty()

            try:
                pygame.mixer.Sound("wave_complete.mp3").play()
            except:
                pass
                
            if self.wave > 5:
                self.game_won = True
    
    def draw(self, surface):
        self.draw_grid_background(surface)
        
        for target in self.targets:
            target.draw(surface)
            
        for explosion in self.explosions:
            explosion.draw(surface)
            
        self.draw_hud(surface)
        
        for line in self.scanlines:
            pygame.draw.rect(surface, SCANLINE_COLOR, line)
            
        pygame.draw.rect(surface, BLACK, (0, 0, WIDTH, self.border_width))
        pygame.draw.rect(surface, BLACK, (0, HEIGHT - self.border_width, WIDTH, self.border_width))
        pygame.draw.rect(surface, BLACK, (0, 0, self.border_width, HEIGHT))
        pygame.draw.rect(surface, BLACK, (WIDTH - self.border_width, 0, self.border_width, HEIGHT))
        
        corner_size = 30
        pygame.draw.rect(surface, CYAN, (0, 0, corner_size, 5))
        pygame.draw.rect(surface, CYAN, (0, 0, 5, corner_size))
        pygame.draw.rect(surface, CYAN, (WIDTH - corner_size, 0, corner_size, 5))
        pygame.draw.rect(surface, CYAN, (WIDTH - 5, 0, 5, corner_size))
        pygame.draw.rect(surface, CYAN, (0, HEIGHT - 5, corner_size, 5))
        pygame.draw.rect(surface, CYAN, (0, HEIGHT - corner_size, 5, corner_size))
        pygame.draw.rect(surface, CYAN, (WIDTH - corner_size, HEIGHT - 5, corner_size, 5))
        pygame.draw.rect(surface, CYAN, (WIDTH - 5, HEIGHT - corner_size, 5, corner_size))
        
        if self.show_dialog:
            self.draw_dialog_box(surface, self.current_dialog)
            
        if self.game_over:
            self.draw_game_over(surface)
            
        if self.game_won:
            self.draw_victory_screen(surface)
            
    def draw_grid_background(self, surface):
        surface.fill(DARK_PURPLE)
        
        for x in range(0, WIDTH, 50):
            pygame.draw.line(surface, BRIGHT_BLUE, (x, 0), (x, HEIGHT), 1)
            
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(surface, BRIGHT_BLUE, (0, y), (WIDTH, y), 1)
            
        for x in range(0, WIDTH, 100):
            pygame.draw.line(surface, CYAN, (x, 0), (x, HEIGHT), 2)
            
        for y in range(0, HEIGHT, 100):
            pygame.draw.line(surface, CYAN, (0, y), (WIDTH, y), 2)
            
    def draw_hud(self, surface):
        score_panel = pygame.Rect(10, 10, 200, 45)
        pygame.draw.rect(surface, BLACK, score_panel)
        pygame.draw.rect(surface, CYAN, score_panel, 2)
        
        corner_size = 10
        pygame.draw.line(surface, MAGENTA, (10, 10 + corner_size), (10, 10), 2)
        pygame.draw.line(surface, MAGENTA, (10, 10), (10 + corner_size, 10), 2)
        pygame.draw.line(surface, MAGENTA, (210 - corner_size, 55), (210, 55), 2)
        pygame.draw.line(surface, MAGENTA, (210, 55 - corner_size), (210, 55), 2)
        
        score_text = main_font.render(f"SCORE:{self.score}", True, CYAN)
        surface.blit(score_text, (20, 15))
        
        wave_panel = pygame.Rect(WIDTH//2 - 100, 10, 200, 45)
        pygame.draw.rect(surface, BLACK, wave_panel)
        pygame.draw.rect(surface, YELLOW, wave_panel, 2)
        
        wave_text = main_font.render(f"WAVE:{self.wave}", True, YELLOW)
        surface.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, 15))
        
        targets_panel = pygame.Rect(WIDTH//2 - 100, 65, 200, 35)
        pygame.draw.rect(surface, BLACK, targets_panel)
        pygame.draw.rect(surface, NEON_GREEN, targets_panel, 1)
        
        targets_text = small_font.render(f"TARGETS:{self.targets_cleared}/{self.targets_per_wave}", True, NEON_GREEN)
        surface.blit(targets_text, (WIDTH//2 - targets_text.get_width()//2, 70))
        
        misses_panel = pygame.Rect(WIDTH - 210, 10, 200, 45)
        pygame.draw.rect(surface, BLACK, misses_panel)
        pygame.draw.rect(surface, BRIGHT_RED, misses_panel, 2)
        
        stripe_size = 10
        pygame.draw.rect(surface, BRIGHT_RED, (WIDTH - 210, 10, stripe_size, stripe_size))
        pygame.draw.rect(surface, BRIGHT_RED, (WIDTH - stripe_size - 10, 10, stripe_size, stripe_size))
        pygame.draw.rect(surface, BRIGHT_RED, (WIDTH - 210, 55 - stripe_size, stripe_size, stripe_size))
        pygame.draw.rect(surface, BRIGHT_RED, (WIDTH - stripe_size - 10, 55 - stripe_size, stripe_size, stripe_size))
        
        misses_text = main_font.render(f"MISS:{self.miss_count}/{self.max_misses}", True, BRIGHT_RED)
        surface.blit(misses_text, (WIDTH - misses_text.get_width() - 20, 15))
        
        ammo_panel = pygame.Rect(10, HEIGHT - 60, 200, 50)
        pygame.draw.rect(surface, BLACK, ammo_panel)
        pygame.draw.rect(surface, CYAN, ammo_panel, 2)
        
        for i in range(self.max_ammo):
            ammo_rect = pygame.Rect(20 + i*15, HEIGHT - 50, 10, 30)
            if i < self.ammo:
                pygame.draw.rect(surface, NEON_GREEN, ammo_rect)
            else:
                pygame.draw.rect(surface, DARK_PURPLE, ammo_rect)
            pygame.draw.rect(surface, BLACK, ammo_rect, 1)
            
        accuracy = 0 if self.shots_fired == 0 else (self.hits / self.shots_fired) * 100
        
        accuracy_panel = pygame.Rect(WIDTH - 210, HEIGHT - 60, 200, 50)
        pygame.draw.rect(surface, BLACK, accuracy_panel)
        pygame.draw.rect(surface, YELLOW, accuracy_panel, 2)
        
        accuracy_text = small_font.render(f"ACCURACY:{accuracy:.1f}%", True, YELLOW)
        surface.blit(accuracy_text, (WIDTH - accuracy_text.get_width() - 20, HEIGHT - 45))
        
        if self.reloading:
            if pygame.time.get_ticks() % 500 < 250:
                reload_panel = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)
                pygame.draw.rect(surface, BLACK, reload_panel)
                pygame.draw.rect(surface, BRIGHT_RED, reload_panel, 2)
                
                time_fraction = (self.reload_time / self.reload_duration)
                dots = "." * (1 + int(time_fraction * 5))
                reload_text = small_font.render(f"RELOADING{dots}", True, BRIGHT_RED)
                surface.blit(reload_text, (WIDTH//2 - reload_text.get_width()//2, HEIGHT - 45))
    
    def draw_dialog_box(self, surface, text):
        dialog_height = 80
        dialog_rect = pygame.Rect(40, HEIGHT - dialog_height - 80, WIDTH - 80, dialog_height)
        
        dialog_bg = pygame.Surface((dialog_rect.width, dialog_rect.height), pygame.SRCALPHA)
        dialog_bg.fill((0, 0, 0, 200))
        surface.blit(dialog_bg, dialog_rect)
        
        pygame.draw.rect(surface, CYAN, dialog_rect, 2)
        
        corner_size = 15
        pygame.draw.line(surface, MAGENTA, 
                         (dialog_rect.left, dialog_rect.top + corner_size), 
                         (dialog_rect.left, dialog_rect.top), 
                         2)
        pygame.draw.line(surface, MAGENTA, 
                         (dialog_rect.left, dialog_rect.top), 
                         (dialog_rect.left + corner_size, dialog_rect.top), 
                         2)
        pygame.draw.line(surface, MAGENTA, 
                         (dialog_rect.right - corner_size, dialog_rect.top), 
                         (dialog_rect.right, dialog_rect.top), 
                         2)
        pygame.draw.line(surface, MAGENTA, 
                         (dialog_rect.right, dialog_rect.top), 
                         (dialog_rect.right, dialog_rect.top + corner_size), 
                         2)
        pygame.draw.line(surface, MAGENTA, 
                         (dialog_rect.left, dialog_rect.bottom - corner_size), 
                         (dialog_rect.left, dialog_rect.bottom), 
                         2)
        pygame.draw.line(surface, MAGENTA, 
                         (dialog_rect.left, dialog_rect.bottom), 
                         (dialog_rect.left + corner_size, dialog_rect.bottom), 
                         2)
        pygame.draw.line(surface, MAGENTA, 
                         (dialog_rect.right - corner_size, dialog_rect.bottom), 
                         (dialog_rect.right, dialog_rect.bottom), 
                         2)
        pygame.draw.line(surface, MAGENTA, 
                         (dialog_rect.right, dialog_rect.bottom), 
                         (dialog_rect.right, dialog_rect.bottom - corner_size), 
                         2)
        
        name_tag = pygame.Rect(dialog_rect.left, dialog_rect.top - 30, 120, 30)
        pygame.draw.rect(surface, BLACK, name_tag)
        pygame.draw.rect(surface, YELLOW, name_tag, 2)
        
        name_text = small_font.render("SYSTEM", True, YELLOW)
        surface.blit(name_text, (name_tag.left + 10, name_tag.top + 5))
        
        chars_to_show = len(text) * (1 - (self.dialog_timer / 3000))
        display_text = text[:int(chars_to_show)]
        
        dialog_text = small_font.render(display_text, True, WHITE)
        surface.blit(dialog_text, (dialog_rect.left + 20, dialog_rect.top + 20))
        
        if chars_to_show >= len(text) and pygame.time.get_ticks() % 1000 < 500:
            indicator = small_font.render(">>>", True, CYAN)
            surface.blit(indicator, (dialog_rect.right - 60, dialog_rect.bottom - 30))
            
    def draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        for _ in range(10):
            glitch_height = random.randint(2, 10)
            glitch_y = random.randint(0, HEIGHT - glitch_height)
            glitch_width = random.randint(50, WIDTH)
            glitch_x = random.randint(0, WIDTH - glitch_width)
            
            glitch_color = random.choice([CYAN, MAGENTA, BRIGHT_RED])
            glitch_rect = pygame.Rect(glitch_x, glitch_y, glitch_width, glitch_height)
            pygame.draw.rect(surface, glitch_color, glitch_rect)
        
        game_over_text = main_font.render("SYSTEM FAILURE", True, BRIGHT_RED)
        for offset in range(5, 0, -1):
            surface.blit(game_over_text, 
                        (WIDTH//2 - game_over_text.get_width()//2 + random.randint(-2, 2), 
                         HEIGHT//2 - 70 + offset))
         
        surface.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 70))
        
        error_text = main_font.render("ERROR CODE: #FF-512", True, YELLOW)
        surface.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2 - 20))
        
        final_score = main_font.render(f"FINAL SCORE: {self.score}", True, CYAN)
        surface.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 + 30))
        
        wave_text = small_font.render(f"SECURITY LEVEL REACHED: {self.wave}", True, NEON_GREEN)
        surface.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, HEIGHT//2 + 70))
        
        if pygame.time.get_ticks() % 1000 < 500:
            restart_text = small_font.render("PRESS R TO REBOOT SYSTEM", True, WHITE)
            surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 120))
     
    def draw_victory_screen(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 200))
        surface.blit(overlay, (0, 0))
        
        for _ in range(30):
            drop_x = random.randint(0, WIDTH)
            drop_y = random.randint(0, HEIGHT)
            drop_length = random.randint(5, 30)
            drop_char = random.choice(["0", "1", "7", "F", "A", "X"])
            
            drop_color = random.choice([CYAN, NEON_GREEN, BRIGHT_BLUE])
            drop_text = small_font.render(drop_char, True, drop_color)
            
            for i in range(drop_length):
                char_y = (drop_y + i * 15) % HEIGHT
                alpha = 255 - (i * 255 // drop_length)
                drop_text.set_alpha(alpha)
                surface.blit(drop_text, (drop_x, char_y))
        
        box_width, box_height = 400, 300
        box_rect = pygame.Rect(WIDTH//2 - box_width//2, HEIGHT//2 - box_height//2, 
                              box_width, box_height)
        
        pygame.draw.rect(surface, BLACK, box_rect)
        pygame.draw.rect(surface, NEON_GREEN, box_rect, 3)
        
        for i in range(0, box_width, 20):
            if i % 40 == 0:
                pygame.draw.rect(surface, BRIGHT_BLUE, 
                               (box_rect.left + i, box_rect.top - 5, 10, 5))
            if (i + 20) % 40 == 0:
                pygame.draw.rect(surface, BRIGHT_BLUE, 
                               (box_rect.left + i, box_rect.bottom, 10, 5))
        
        victory_text = main_font.render("MISSION COMPLETE", True, NEON_GREEN)
        surface.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 - 100))
        
        success_text = small_font.render("ALL TARGETS ELIMINATED", True, WHITE)
        surface.blit(success_text, (WIDTH//2 - success_text.get_width()//2, HEIGHT//2 - 50))
        
        score_text = main_font.render(f"FINAL SCORE: {self.score}", True, YELLOW)
        surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        
        accuracy = 0 if self.shots_fired == 0 else (self.hits / self.shots_fired) * 100
        accuracy_text = small_font.render(f"ACCURACY RATING: {accuracy:.1f}%", True, CYAN)
        surface.blit(accuracy_text, (WIDTH//2 - accuracy_text.get_width()//2, HEIGHT//2 + 50))
        
        if pygame.time.get_ticks() % 1000 < 500:
            restart_text = small_font.render("PRESS R TO PLAY AGAIN", True, WHITE)
            surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
            
    def shoot(self, x, y):
        if self.game_over or self.reloading or self.game_won:
            return False
            
        if self.ammo <= 0:
            self.reload()
            self.current_dialog = "NO AMMO! RELOADING..."
            self.dialog_timer = 1500
            self.show_dialog = True
            return False
            
        self.ammo -= 1
        self.shots_fired += 1
        
        try:
            gunshot.play()
        except:
            pass
            
        hit = False
        for target in self.targets:
            is_hit, points = target.hit_test(x, y)
            if is_hit:
                self.explosions.append(Explosion(target.x, target.y, target.size))
                
                wave_bonus = 1.0 + (self.wave - 1) * 0.2
                final_points = int(points * wave_bonus)
                
                self.score += final_points
                self.hits += 1
                self.targets_cleared += 1
                
                hit_messages = [
                    "TARGET ELIMINATED!",
                    "CLEAN SHOT!",
                    f"+{final_points} POINTS",
                    "TARGET DOWN!",
                    "CONFIRMED HIT!"
                ]
                
                if random.random() < 0.3:
                    self.current_dialog = random.choice(hit_messages)
                    self.dialog_timer = 1000
                    self.show_dialog = True
                
                hit = True
                try:
                    hit_sound.play()
                except:
                    pass
                break
                
        if not hit:
            self.miss_count += 1
            
            miss_messages = [
                "MISSED! FOCUS!",
                f"MISS COUNT: {self.miss_count}/{self.max_misses}",
                "RECALIBRATING TARGETING...",
                "AIM MORE CAREFULLY!"
            ]
            
            if random.random() < 0.3:
                self.current_dialog = random.choice(miss_messages)
                self.dialog_timer = 1500
                self.show_dialog = True
                
            if self.miss_count >= self.max_misses:
                self.game_over = True
                self.current_dialog = "TOO MANY MISSES. SYSTEM SHUTDOWN INITIATED."
                self.dialog_timer = 3000
                self.show_dialog = True
                
        return hit
    
    def reload(self):
        if not self.reloading and self.ammo < self.max_ammo:
            self.reloading = True
            self.reload_time = 0
            try:
                reload_sound.play()
            except:
                pass

def main():
    clock = pygame.time.Clock()
    game = Game()
    
    pygame.mouse.set_visible(False)
    
    crosshair_size = 40
    crosshair_surface = pygame.Surface((crosshair_size, crosshair_size), pygame.SRCALPHA)
    
    pygame.draw.circle(crosshair_surface, CYAN, (crosshair_size//2, crosshair_size//2), 
                      crosshair_size//2 - 2, 1)
    
    segment_count = 8
    for i in range(segment_count):
        angle_start = i * (2 * math.pi / segment_count)
        angle_end = (i + 0.7) * (2 * math.pi / segment_count)
        
        radius = crosshair_size // 4
        center_x, center_y = crosshair_size // 2, crosshair_size // 2
        
        start_x = center_x + int(radius * math.cos(angle_start))
        start_y = center_y + int(radius * math.sin(angle_start))
        end_x = center_x + int(radius * math.cos(angle_end))
        end_y = center_y + int(radius * math.sin(angle_end))
        
        pygame.draw.line(crosshair_surface, MAGENTA, (start_x, start_y), (end_x, end_y), 2)
    
    pygame.draw.circle(crosshair_surface, BRIGHT_RED, 
                      (crosshair_size//2, crosshair_size//2), 3)
    
    pygame.draw.line(crosshair_surface, YELLOW, 
                    (crosshair_size//2, 0), 
                    (crosshair_size//2, crosshair_size//2 - 10), 2)
    pygame.draw.line(crosshair_surface, YELLOW, 
                    (crosshair_size//2, crosshair_size//2 + 10), 
                    (crosshair_size//2, crosshair_size), 2)
    pygame.draw.line(crosshair_surface, YELLOW, 
                    (0, crosshair_size//2), 
                    (crosshair_size//2 - 10, crosshair_size//2), 2)
    pygame.draw.line(crosshair_surface, YELLOW, 
                    (crosshair_size//2 + 10, crosshair_size//2), 
                    (crosshair_size, crosshair_size//2), 2)
    
    corner_len = 7
    pygame.draw.line(crosshair_surface, NEON_GREEN, 
                    (2, 2), (2 + corner_len, 2), 2)
    pygame.draw.line(crosshair_surface, NEON_GREEN, 
                    (2, 2), (2, 2 + corner_len), 2)
    pygame.draw.line(crosshair_surface, NEON_GREEN, 
                    (crosshair_size - 2 - corner_len, 2), (crosshair_size - 2, 2), 2)
    pygame.draw.line(crosshair_surface, NEON_GREEN, 
                    (crosshair_size - 2, 2), (crosshair_size - 2, 2 + corner_len), 2)
    pygame.draw.line(crosshair_surface, NEON_GREEN, 
                    (2, crosshair_size - 2 - corner_len), (2, crosshair_size - 2), 2)
    pygame.draw.line(crosshair_surface, NEON_GREEN, 
                    (2, crosshair_size - 2), (2 + corner_len, crosshair_size - 2), 2)
    pygame.draw.line(crosshair_surface, NEON_GREEN, 
                    (crosshair_size - 2 - corner_len, crosshair_size - 2), 
                    (crosshair_size - 2, crosshair_size - 2), 2)
    pygame.draw.line(crosshair_surface, NEON_GREEN, 
                    (crosshair_size - 2, crosshair_size - 2 - corner_len), 
                    (crosshair_size - 2, crosshair_size - 2), 2)
    
    running = True
    
    show_intro = True
    intro_timer = 3000
    intro_text = [
        "CYBER RANGE 2099",
        "SYSTEM INITIALIZING...",
        "TARGETING SYSTEMS ONLINE",
        "MISSION: ELIMINATE ALL TARGETS"
    ]
    current_intro_text = 0
    
    while running:
        dt = clock.tick(60)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    if game.game_over or game.game_won:
                        game.reset()
                        show_intro = True
                        intro_timer = 3000
                        current_intro_text = 0
                    else:
                        game.reload()
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if show_intro:
                    show_intro = False
                        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_intro:
                    show_intro = False
                else:
                    game.shoot(mouse_x, mouse_y)
        
        if show_intro:
            intro_timer -= dt
            if intro_timer <= 0:
                current_intro_text += 1
                if current_intro_text >= len(intro_text):
                    show_intro = False
                else:
                    intro_timer = 1500
        else:
            game.update(dt)
        
        game.draw(screen)
        
        if show_intro:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))
            
            if current_intro_text < len(intro_text):
                text = intro_text[current_intro_text]
                progress = 1.0 - (intro_timer / 1500)
                chars_to_show = int(len(text) * min(1.0, progress * 1.5))
                display_text = text[:chars_to_show]
                
                glow_size = 2
                for offset_x in range(-glow_size, glow_size + 1):
                    for offset_y in range(-glow_size, glow_size + 1):
                        if offset_x == 0 and offset_y == 0:
                            continue
                        glow_text = main_font.render(display_text, True, CYAN)
                        glow_text.set_alpha(50)
                        screen.blit(glow_text, 
                                   (WIDTH//2 - glow_text.get_width()//2 + offset_x, 
                                    HEIGHT//2 + offset_y))
                
                intro_rendered = main_font.render(display_text, True, WHITE)
                screen.blit(intro_rendered, 
                           (WIDTH//2 - intro_rendered.get_width()//2, HEIGHT//2))
                
                if pygame.time.get_ticks() % 1000 < 500:
                    skip_text = small_font.render("PRESS ANY KEY", True, YELLOW)
                    screen.blit(skip_text, 
                               (WIDTH//2 - skip_text.get_width()//2, HEIGHT - 100))
        
        screen.blit(crosshair_surface, (mouse_x - crosshair_surface.get_width()//2, 
                                        mouse_y - crosshair_surface.get_height()//2))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()