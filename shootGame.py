import pygame
import random
import os

FPS = 60
R = 0
G = 0
B = 0
WIDTH = 500
HEIGHT = 600
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# 遊戲初始化&創視窗
pygame.init()
# 音效初始化
pygame.mixer.init()

# 設定畫面大小
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# 設定標題
pygame.display.set_caption("第一個遊戲")

clock = pygame.time.Clock()

# 載入圖片
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)

# 設定視窗左上圖標
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())

# 爆炸圖片
expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []

for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)

power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()

# 文字
font_name = os.path.join("font.ttf")

# 載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))

shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))

expl_sound = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.4)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    # 要用的文字，是否反鋸齒，顏色
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.centerx = x;
    text_rect.top = y
    surf.blit(text_surface, text_rect)


def new_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)


def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 15
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, (255, 255, 255), outline_rect, 2)


def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# 初始畫面
def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, '太空生存戰!', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, '←→移動飛船 空白艦發射子彈~', 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, '按任意鍵開始遊戲!', 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            # 按下叉叉
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # 顯示的圖片  ，變形圖片
        self.image = pygame.transform.scale(player_img, (50, 38))  # 改變大小
        # 把黑色變透明
        self.image.set_colorkey(BLACK)
        # 圖片的位置  把圖片框起來
        self.rect = self.image.get_rect()

        self.radius = 20
        # pygame.draw.circle(self.image,RED, self.rect.center, self.radius)

        # 圖片位置
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        # self.rect.x = 200
        # self.rect.y = 200
        # 速度
        self.speedx = 8

        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 1

    def update(self):
        # 判斷鍵盤按鍵是否被按下
        key_pressed = pygame.key.get_pressed()
        # 判斷右鍵是否被按下
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        # 卡住圖片
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # 若圖片超出畫面
        # if self.rect.left > WIDTH:
        #     self.rect.right = 0

    def shoot(self):
        if not (self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 700)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # 顯示的圖片
        self.image_ori = random.choice(rock_imgs)
        self.image = self.image_ori.copy()
        self.image_ori.set_colorkey(BLACK)
        # 圖片的位置  把圖片框起來
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        # 圖片位置
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        # 速度
        self.speedy = random.randrange(2, 6)
        self.speedx = random.randrange(-3, 3)  # 可能前進或後退

        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        # 中心重新定位
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()

        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            # 速度
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)  # 可能前進或後退


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # 顯示的圖片
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        # 圖片的位置  把圖片框起來
        self.rect = self.image.get_rect()

        # 圖片位置
        self.rect.centerx = x
        self.rect.bottom = y
        # 速度
        self.speedy = -10  # 往上飛

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        # 顯示的圖片
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        # 更新到第幾張圖
        self.frame = 0
        # 從初始化到現在的毫秒數
        self.last_update = pygame.time.get_ticks()
        # 過多少毫秒更新到下一張圖
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        # 顯示的圖片
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        # 圖片的位置  把圖片框起來
        self.rect = self.image.get_rect()

        # 圖片位置
        self.rect.center = center
        # 速度
        self.speedy = 3  # 往上飛

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


pygame.mixer.music.play(-1)  # 音樂無限重複撥放
score = 0
# 遊戲迴圈
running = True
show_init = True

while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        # 建立一個群組
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        player = Player()
        all_sprites.add(player)

        for i in range(8):
            new_rock()

    # 一秒鐘最多執行幾次
    clock.tick(FPS)
    # 取得輸入
    # 回傳game中所有的事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 更新遊戲
    # 執行all_sprites群組中update的函式
    all_sprites.update()

    # 判斷石頭、子彈是否碰撞(物件一，物件二，物件一是否刪除，物件二是否刪除)
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        random.choice(expl_sound).play()
        score += hit.radius  # 加分的分數
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        # 掉寶機率
        if random.random() > 0.1:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

    # 碰撞判斷改為圓形  石頭、飛船
    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits:
        new_rock()
        player.health -= hit.radius
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
    if player.lives == 0 and not (death_expl.alive()):
        show_init = True

    # 飛船、寶物相撞
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == 'shield':
            player.health += 20
            if player.health >= 100:
                player.health = 100
            shield_sound.play()
        elif hit.type == 'gun':
            player.gunup()
            gun_sound.play()

    # 畫面顯示
    # 改變畫面顏色
    screen.fill((R, G, B))

    # 畫在螢幕上，座標
    screen.blit(background_img, (0, 0))

    # 將群組中的東西放到螢幕上
    all_sprites.draw((screen))
    # 畫面更新
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_health(screen, player.health, 5, 10)

    draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)

    pygame.display.update()

# 結束視窗
pygame.quit()
