import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Emoji Slice - Top-to-Bottom Edition")

clock = pygame.time.Clock()

NEGATIVE_EMOJIS = [
    "negative/bomb.png",
    "negative/scare.png",
    "negative/spider.png",
    "negative/smile.png",
    "negative/skull.png"
]

POSITIVE_EMOJIS = [
    "positive/angel.png",
    "positive/emoji.png",
    "positive/party.png",
    "positive/smile.png",
    "positive/star.png",
    "positive/thumb.png"
]

font_big = pygame.font.SysFont("comicsansms", 48, bold=True)
font_small = pygame.font.SysFont("comicsansms", 28, bold=True)


bg_surface = pygame.Surface((WIDTH, HEIGHT))
for y in range(HEIGHT):
    r = 30 + int(40 * (y / HEIGHT))
    g = 20 + int(50 * (y / HEIGHT))
    b = 60 + int(80 * (y / HEIGHT))
    pygame.draw.line(bg_surface, (r, g, b), (0, y), (WIDTH, y))


class Emoji(pygame.sprite.Sprite):
    def __init__(self, image_path, is_negative):
        super().__init__()
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (64, 64))
        self.image = self.original_image.copy()

        
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH - 40), -40))

        
        self.vy = random.uniform(5, 9)   
        self.vx = random.uniform(-1, 1)  

        self.is_negative = is_negative
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.choice([-4, -2, 2, 4])

    def update(self):
        # move down
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # rotate
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)

        # remove when out of screen
        if self.rect.top > HEIGHT + 50:
            self.kill()

class FloatingText:
    def __init__(self, text, pos, color=(255,255,255)):
        self.text = text
        self.pos = list(pos)
        self.color = color
        self.lifetime = 60
        self.size = 36

    def update(self):
        self.pos[1] -= 1
        self.lifetime -= 1
        self.size += 1

    def draw(self, surface):
        alpha = max(0, int(255 * (self.lifetime / 60)))
        text_surf = pygame.font.SysFont("comicsansms", self.size, bold=True).render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        glow = pygame.Surface((text_surf.get_width()+10, text_surf.get_height()+10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (self.color[0], self.color[1], self.color[2], 80), glow.get_rect())
        surface.blit(glow, (self.pos[0]-5, self.pos[1]-5))
        surface.blit(text_surf, self.pos)

class Trail:
    def __init__(self):
        self.points = []

    def add_point(self, pos):
        self.points.append([pos, 20])

    def update(self):
        for p in self.points:
            p[1] -= 1
        self.points = [p for p in self.points if p[1] > 0]

    def draw(self, surface):
        for i in range(1, len(self.points)):
            p1, life1 = self.points[i-1]
            p2, life2 = self.points[i]
            alpha = int(200 * (life2 / 20))
            pygame.draw.line(surface, (0, 255, 200, alpha), p1, p2, 4)

def game_loop():
    emojis = pygame.sprite.Group()
    floating_texts = []
    trail = Trail()
    
    score = 0
    lives = 3
    combo = 0

    running = True
    paused = False
    spawn_timer = 0
    spawn_delay = 30

    while running:
        screen.blit(bg_surface, (0,0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused

        if not paused and lives > 0:
            
            spawn_timer += 1
            if spawn_timer >= spawn_delay:
                spawn_timer = 0
                if random.random() < 0.7:
                    path = random.choice(NEGATIVE_EMOJIS)
                    emoji = Emoji(path, True)
                else:
                    path = random.choice(POSITIVE_EMOJIS)
                    emoji = Emoji(path, False)
                emojis.add(emoji)

            
            emojis.update()
            trail.update()
            for t in floating_texts:
                t.update()
            floating_texts = [t for t in floating_texts if t.lifetime > 0]

            
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                trail.add_point(pos)
                for emoji in emojis:
                    if emoji.rect.collidepoint(pos):
                        if emoji.is_negative:
                            score += 1
                            combo += 1
                            floating_texts.append(FloatingText("+1", pos, (0,255,0)))
                            if combo == 3:
                                score += 3
                                floating_texts.append(FloatingText("3 Combo!", pos, (255,215,0)))
                            if combo == 5:
                                score += 5
                                floating_texts.append(FloatingText("5 Combo!", pos, (255,50,200)))
                                combo = 0
                        else:
                            score -= 1
                            lives -= 1
                            combo = 0
                            floating_texts.append(FloatingText("-1", pos, (255,0,0)))
                        emoji.kill()

        
        emojis.draw(screen)
        trail.draw(screen)
        for t in floating_texts:
            t.draw(screen)

        
        hud_bg = pygame.Surface((200,60), pygame.SRCALPHA)
        pygame.draw.rect(hud_bg, (0,0,0,150), hud_bg.get_rect(), border_radius=15)
        screen.blit(hud_bg, (20,20))
        screen.blit(font_small.render(f"Score: {score}", True, (255,255,255)), (30,30))
        screen.blit(font_small.render(f"Lives: {lives}", True, (255,80,80)), (30,55))

        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,150))
            screen.blit(overlay, (0,0))
            pause_text = font_big.render("PAUSED", True, (255,255,255))
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2))

        if lives <= 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            screen.blit(overlay, (0,0))
            go_text = font_big.render("GAME OVER", True, (255,100,100))
            screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
