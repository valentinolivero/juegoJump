# IMPORTAR LIBRERIAS
import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy

# INICIALIZAR PYGAME
mixer.init()
pygame.init()

# TAMANIO DE VENTANA
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# CREAR VENTANA DE JUEGO
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Salta Pavimento')

# SETEAR FRAMERATE
clock = pygame.time.Clock()
FPS = 60

# CARGAR MUSICA Y SONIDOS
pygame.mixer.music.load('assets/music1_loop.mp3')
pygame.mixer.music.set_volume(0.6)

jump_fx = pygame.mixer.Sound('assets/jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('assets/death.mp3')
death_fx.set_volume(0.5)


# VARIABLES DE JUEGO
SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0

# DEFINIR COLORES
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRA_NA_TE = (140, 3, 28)
PANEL = (153, 217, 234)

# DEFINIR FUENTE
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

# CARGAR IMAGEN
jumpy_image = pygame.image.load('assets/jump.png').convert_alpha()
bg_image = pygame.image.load('assets/bg.png').convert_alpha()
platform_image = pygame.image.load('assets/wood.png').convert_alpha()
# SPRITESHEET (ENEMIGO)
bird_sheet_img = pygame.image.load('assets/bird.png').convert_alpha()
bird_sheet = SpriteSheet(bird_sheet_img)


# FUNCION PARA DIBUJAR TEXTO
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# FUNCION PARA DIBUJAR PANEL


def draw_panel():
    pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2)
    draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)


# FUNCION PARA DIBUJAR EL FONDO
def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0 + bg_scroll))
    screen.blit(bg_image, (0, -600 + bg_scroll))

# CLASE JUGADOR


class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(jumpy_image, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

    def move(self):
        # RESETEAR VARIABLES
        scroll = 0
        dx = 0
        dy = 0

        # PROCESAR KEY INPUT
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx = -10
            self.flip = True
        if key[pygame.K_d]:
            dx = 10
            self.flip = False

        # GRAVEDAD
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ASEGURAR QUE EL JUGADOR NO SE SALGA DE LOS LIMITES DE LA PANTALLA
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        # VERIFICAR COLISION CON PLATAFORMAS
        for platform in platform_group:
            # COLISION DE DIR Y
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # VERIFICAR SI ESTA ARRIBA DE LA PLATAFORMA
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
                        jump_fx.play()

        # cVERIFICAR SI EL JUGADOR TOCA LA PARTE SUPERIOR DEL DISPLAY
        if self.rect.top <= SCROLL_THRESH:
            # IF EL JUGADOR ESTA SALTANDO
            if self.vel_y < 0:
                scroll = -dy

        # ACTUALIZAR RECT
        self.rect.x += dx
        self.rect.y += dy + scroll

        # ACTUALIZAR MASCARA
        self.mask = pygame.mask.from_surface(self.image)

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip,
                    False), (self.rect.x - 12, self.rect.y - 5))

# PLATAFORMA CLASE


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        # MOVER PLATAFORMA HACIA LOS LADOS SI ES PLAT CON MOVIMIENTO
        if self.moving == True:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        # CAMBIAR DIRECCION DE LA PLATAFORMA
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1
            self.move_counter = 0

        # ACTUALIZAR DY DE LA PLATAFORMA
        self.rect.y += scroll

        # VERIFICAR SI LA PLAT SE FUE DE LOS LIMITES
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# CLASE AUXILIAR PARA TEXTO


def text_objects(text, font):
    textSurface = font.render(text, True, WHITE)
    return textSurface, textSurface.get_rect()

# START MENU/SPLASH CLASE


def game_intro():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        screen.fill(GRA_NA_TE)
        # GENERAR TEXTO
        largeText = pygame.font.SysFont("Lucida Sans", 115)
        TextSurf, TextRect = text_objects("UNLa", largeText)
        TextRect.center = ((SCREEN_WIDTH/2), (SCREEN_HEIGHT/2))

        smallText = pygame.font.SysFont("Lucida Sans", 20)
        SmallSurf, SmallRect = text_objects(
            "Presiona ESPACIO para jugar", smallText)
        SmallRect.center = ((SCREEN_WIDTH/2), (SCREEN_HEIGHT/2 + 75))
        # DIBUJAR EN PANTALLA
        screen.blit(TextSurf, TextRect)
        screen.blit(SmallSurf, SmallRect)
        pygame.display.update()
        clock.tick(15)
        # PRESIONAR CUALQUIER TECLA PARA EMPEZAR
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            intro = False


# INSTANCIAR JUGADOR
pavimento = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

# CREAR SPRITE GROUPS
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# CREAR PLATAFORMA DE COMIENZO
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
platform_group.add(platform)

game_intro()
pygame.mixer.music.play(-1, 0.0)
# LOOP DE JUEGO
run = True
while run:

    clock.tick(FPS)

    if game_over == False:
        scroll = pavimento.move()

        # DIBUJAR FONDO
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        # GENERAR PLATAFORMAS
        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 500:
                p_moving = True
            else:
                p_moving = False
            platform = Platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)

        # ACTUALIZAR PLATAFORMAS
        platform_group.update(scroll)

        # GENERAR ENEMIGOS
        if len(enemy_group) == 0 and score > 1500:
            enemy = Enemy(SCREEN_WIDTH, 100, bird_sheet, 1.5)
            enemy_group.add(enemy)

        # ACTUALIZAR ENEMIGOS
        enemy_group.update(scroll, SCREEN_WIDTH)

        # ACTUALIZAR PUNTAJES
        if scroll > 0:
            score += scroll

        # DIBUJAR LINEA HIGH SCORE
        pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH),
                         (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
        draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH -
                  130, score - high_score + SCROLL_THRESH)

        # DIBUJAR SPRITES
        platform_group.draw(screen)
        enemy_group.draw(screen)
        pavimento.draw()

        # DIBUJAR PANEL
        draw_panel()

        # VERIF GAME OVER
        if pavimento.rect.top > SCREEN_HEIGHT:
            game_over = True
            death_fx.play()
        # VERIFICAR CLISION CON ENEMIGO
        if pygame.sprite.spritecollide(pavimento, enemy_group, False):
            if pygame.sprite.spritecollide(pavimento, enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
                death_fx.play()
    else:
        if fade_counter < SCREEN_WIDTH:
            fade_counter += 5
            for y in range(0, 6, 2):
                pygame.draw.rect(
                    screen, BLACK, (0, y * 100, fade_counter, 100))
                pygame.draw.rect(
                    screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100, SCREEN_WIDTH, 100))
        else:
            draw_text('PERDISTE!', font_big, RED, 130, 200)
            draw_text('PUNTAJE: ' + str(score), font_big, WHITE, 130, 250)
            draw_text('PULSA ESPACIO Y JUGÁ !',
                      font_big, WHITE, 40, 300)
            # ACTUALIZAR HIGH SCORE
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                # RESETEAR VARIABLES
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                # REPOSICIONAR PAVIMENTO
                pavimento.rect.center = (
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
                # RESETEAR ENEMIGOS
                enemy_group.empty()
                # RESETEAR PLATAFORMAS
                platform_group.empty()
                # CREAR PLATAFORMA INICIAL
                platform = Platform(SCREEN_WIDTH // 2 - 50,
                                    SCREEN_HEIGHT - 50, 100, False)
                platform_group.add(platform)

    # EVENT HANDLER
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # ACTUALIZAR HIGH SCORE
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            run = False

    # ACTUALIZAR DISPLAY
    pygame.display.update()
