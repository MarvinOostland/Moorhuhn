from email.mime import image
import pygame
import random
import os


class Settings(object):
    window_width = 1280
    window_height = 720
    fps = 60
    chicken_size = (130, 130)
    bullet_size = (10, 10)
    border = 10
    timeunit = 60
    path_image = os.path.join(os.path.dirname(__file__), "images")
    path_sound = os.path.join(os.path.dirname(__file__), "sounds")
    path_highscore = os.path.join(os.path.dirname(__file__), "highscore.txt")
    scroll = 0


class Background():
    def __init__(self, filename1, filename2, x, y):
        self.image1 = pygame.image.load(
            os.path.join(Settings.path_image, filename1))
        self.image2 = pygame.image.load(
            os.path.join(Settings.path_image, filename2))
        #self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))
        self.rect1 = self.image1.get_rect()
        self.rect1.x = x
        self.rect1.y = y
        self.rect2 = self.image2.get_rect()
        self.rect2.x = x
        self.rect2.y = y

    def drawbg(self, screen, x, y):
        width1 = self.image1.get_width()
        width2 = self.image2.get_width()
        for i in range(y):
            screen.blit(self.image2, ((i*width2) - Settings.scroll,
                        Settings.window_height - 0))
            screen.blit(self.image1, ((i*width1) - Settings.scroll,
                        Settings.window_height - self.image1.get_height()))

    def get_rect(self):
        return self.rect

    def draw(self, screen):
        self.drawbg(screen, 1, 2)


class Timer(object):
    def __init__(self, duration, with_start=True):
        self.duration = duration
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duration

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duration
            return True
        return False


class Ammo(pygame.sprite.Sprite):
    def __init__(self, filename):
        super().__init__(os.path.join(Settings.path_image, filename))
        self.rect = self.get_rect()
        self.images = []
        for i in range(17):
            bitmap = pygame.image.load(os.path.join(
                Settings.path_image, f"Ammo{i}.png"))
            self.images.append(bitmap)
        self.frameindex = 0
        self.image = self.images[self.frameindex]
        self.image = pygame.transform.scale(self.image, (Settings.bullet_size))
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Chicken(pygame.sprite.Sprite):
    def __init__(self, filename, g):
        super().__init__()
        self.images = []
        for i in range(13):
            bitmap = pygame.image.load(os.path.join(
                Settings.path_image, f"Moohuen{i}.png"))
            self.images.append(bitmap)
        self.frameindex = 0
        self.image = self.images[self.frameindex]
        self.image = pygame.transform.scale(self.image, Settings.chicken_size)
        self.rect = self.image.get_rect()
        self.rect.left = random.randint(
            Settings.border, Settings.window_width - Settings.border)
        self.rect.top = random.randint(
            Settings.border, Settings.window_height - Settings.border)
        self.t = 0
        self.spawnrate = 0
        self.x_speed = random.randint(-5, -2)
        self.y_speed = 0
        self.position = random.randint(0, Settings.window_width)
        self.animationtimer = Timer(100)
        self.check_death = False
        self.got_shot = False

    def move(self):
        self.rect.move_ip(self.x_speed, self.y_speed)

    def kill_animation(self):
        self.check_death = True
        self.animationtimer = Timer(30)
        for k in range(7):
            bitmap2 = pygame.image.load(os.path.join(
                Settings.path_image, f"Die{k}.png"))
            self.images.append(bitmap2)

    def update(self):
        self.move()
        if self.animationtimer.is_next_stop_reached():
            self.image = self.images[self.frameindex]
            self.frameindex += 1
            if self.frameindex == len(self.images) - 1:
                self.frameindex = 0
                if self.check_death == True:
                    self.kill()
            self.image = self.images[self.frameindex]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Mouse(pygame.sprite.Sprite):
    def __init__(self, filename="1.png"):
        super().__init__()
        self.change_image(filename)

    def draw(self, screen):
        screen.blit(self.image, pygame.mouse.get_pos())

    def change_image(self, filename):
        self.image = pygame.image.load(os.path.join(
            Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 35))
        self.rect = self.image.get_rect()


class Game(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (Settings.window_width, Settings.window_height))
        self.captions = pygame.display.set_caption("Moorhuhn")
        self.clock = pygame.time.Clock()
        self.running = True
        self.background1 = Background(
            "backgroundcombined.png", "sky.png", 0, 0)
        self.mouse = Mouse()
        self.pause = False
        self.start_menu1 = True
        pygame.mouse.set_visible(False)
        self.chickens = pygame.sprite.Group()
        self.t = 0
        self.t2 = 0
        self.font_normalsize = pygame.font.Font(
            pygame.font.get_default_font(), 16)
        self.points = 0
        self.gameover = False

    def run(self):
        while self.running:
            self.clock.tick(Settings.fps)
            if self.start_menu1 == True:
                self.start_menu()
            else:
                self.watch_for_events()
                self.draw()
            if not self.pause and not self.gameover and self.start_menu1 == False:
                self.update()
                self.timer_event()
            elif self.pause == True:
                self.paused()
            elif self.gameover == True:
                self.gameover_check()
            self.save_highscore()
            pygame.display.flip()

    def paused(self):
        screenfill = pygame.Surface(
            (Settings.window_width, Settings.window_height))
        screenfill.fill((170, 170, 170))
        screenfill.set_alpha(180)
        self.screen.blit(screenfill, (0, 0))
        pause = self.font_normalsize.render("Paused", False, (255, 255, 255))
        score = self.font_normalsize.render(
            f"Highscore:{self.get_highscore()}", False, (255, 255, 255))
        self.screen.blit(pause, (
            Settings.window_width // 2 - pause.get_width() // 2, Settings.window_height // 2 - pause.get_height() // 2))
        self.screen.blit(score, (
            Settings.window_width // 2 - score.get_width() // 2, Settings.window_height // 2.1 - score.get_height() // 2.1))

    def gameover_check(self):
        gameover_screenfill = pygame.Surface(
            (Settings.window_width, Settings.window_height))
        gameover_screenfill.fill((170, 170, 170))
        gameover_screenfill.set_alpha(180)
        self.screen.blit(gameover_screenfill, (0, 0))
        gameover = self.font_normalsize.render(
            "Game Over", False, (255, 255, 255))
        question = self.font_normalsize.render(
            "to restart the game press Space", False, (255, 255, 255))
        gameover_score = self.font_normalsize.render(
            f"Points:{self.points}", False, (255, 255, 255))
        self.screen.blit(gameover, (
            Settings.window_width // 2 - gameover.get_width() // 2, Settings.window_height // 2 - gameover.get_height() // 2))
        self.screen.blit(question, (
            Settings.window_width // 2 - question.get_width() // 2,
            Settings.window_height // 2.1 - question.get_height() // 2.1))
        self.screen.blit(gameover_score, (
            Settings.window_width // 2 - gameover_score.get_width() // 2,
            Settings.window_height // 2.2 - gameover_score.get_height() // 2.2))

    def start_menu(self):
        start_menu_screenfill = pygame.Surface(
            (Settings.window_width, Settings.window_height))
        start_menu_screenfill.fill((170, 170, 170))
        start_menu_screenfill.set_alpha(180)
        self.screen.blit(start_menu_screenfill, (0, 0))
        start_menu_title = self.font_normalsize.render(
            "Moorhuhn", False, (255, 255, 255))
        start_menu_start = self.font_normalsize.render(
            "To Start press Space", False, (255, 255, 255))
        start_menu_exit = self.font_normalsize.render(
            "For Exit press Escape", False, (255, 255, 255))
        self.screen.blit(start_menu_title, (
            Settings.window_width // 2 - start_menu_title.get_width() // 2, Settings.window_height // 2.3 - start_menu_title.get_height() // 2.3))
        self.screen.blit(start_menu_start, (
            Settings.window_width // 2 - start_menu_start.get_width() // 2,
            Settings.window_height // 2.1 - start_menu_start.get_height() // 2.1))
        self.screen.blit(start_menu_exit, (
            Settings.window_width // 2 - start_menu_exit.get_width() // 2,
            Settings.window_height // 2.2 - start_menu_exit.get_height() // 2.2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_menu1 = False
                    self.running = True
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def timer_event(self):
        self.timertime = pygame.time.get_ticks() / 1000
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        timer = font.render(f"Time:{self.timertime}", False, (255, 255, 255))
        self.screen.blit(timer, (
            Settings.window_width - timer.get_width() - 10, 10))
        if self.running == True:
            self.t + 1
            if self.timertime > 120:
                self.gameover = True
                self.running = False

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for chicken in self.chickens:
                    hits = chicken.rect.collidepoint(*pygame.mouse.get_pos())
                    if hits == True:
                        burst_sound = pygame.mixer.Sound(os.path.join(
                            Settings.path_sound, "gun_shot_sound.ogg"))
                        pygame.mixer.Sound.play(burst_sound)
                        pygame.mixer.Sound.set_volume(burst_sound, 0.3)
                        self.points += abs(chicken.x_speed)
                        Chicken.kill_animation(chicken)

                if event.button == 3:
                    self.pause = not self.pause
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause = not self.pause
                if event.key == pygame.K_SPACE:
                    if self.gameover == True:
                        self.reset()

    def reset(self):
        self.points = 0
        self.chickens.empty()
        self.gameover = False

    @staticmethod
    def get_highscore() -> int:
        """
        Getting highscore from file
        """

        with open(Settings.path_highscore, 'r', encoding='utf8') as file:
            highscore = int(file.read())

        return highscore

    @staticmethod
    def set_highscore(highscore: int) -> None:
        """
        Setting highscore to file
        """

        with open(Settings.path_highscore, 'w', encoding='utf8') as file:
            file.write(str(highscore))

    def save_highscore(self) -> None:
        """
        Saving highscore to file
        """

        if self.points > Game.get_highscore():
            Game.set_highscore(self.points)

    def checkmousepostion(self) -> None:
        """
        Checking mouse position
        """
        if pygame.mouse.get_pos()[0] >= Settings.window_width - 100 and Settings.scroll < 1500:
            Settings.scroll += 10
        elif pygame.mouse.get_pos()[0] <= 0 + 100 and Settings.scroll > 0:
            Settings.scroll -= 10

    def update(self):
        self.checkmousepostion()
        self.t += 1
        if self.t >= Settings.timeunit:
            self.t = 0
            if len(self.chickens) <= (Settings.window_width + Settings.window_height) / 100:
                self.chickens.add(Chicken("Moohuen(i).png", self.chickens))
                spawn_sound = pygame.mixer.Sound(os.path.join(
                    Settings.path_sound, "big_chicken_pops_up.ogg"))
                pygame.mixer.Sound.play(spawn_sound)
                pygame.mixer.Sound.set_volume(spawn_sound, 0.3)
        self.chickens.update()
        chicken_is_hovered = False
        for chicken in self.chickens:
            hits = chicken.rect.collidepoint(*pygame.mouse.get_pos())
            if hits == True:
                chicken_is_hovered = True
        if chicken_is_hovered == True:
            self.mouse.change_image("3.png")
        else:
            self.mouse.change_image("1.png")
        self.mouse.update()
        self.mouse.draw(self.screen)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.background1.draw(self.screen)
        self.chickens.draw(self.screen)
        self.mouse.draw(self.screen)
        points = self.font_normalsize.render(
            f"Points: {self.points}", False, (255, 255, 255))
        self.screen.blit(points, (0, 10))


if __name__ == "__main__":
    game = Game()
    game.run()
