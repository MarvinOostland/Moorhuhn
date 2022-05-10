from fileinput import filename
import math
from math import sqrt
from time import time
from tkinter import Y

import pygame
import random
import os


class Settings(object):
    window_width = 1280
    window_height = 720
    fps = 60
    chicken_size = (130, 130)
    border = 10
    timeunit = 60
    path_image = os.path.join(os.path.dirname(__file__), "images")
    path_sound = os.path.join(os.path.dirname(__file__), "sounds")
    path_highscore = os.path.join(os.path.dirname(__file__), "highscore.txt")


class Background():
    def __init__(self,filename,x,y):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename))
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def is_near_border(self, mouse_x, mouse_y):
        if mouse_x < Settings.border or mouse_x > Settings.window_width - Settings.border:
            return True
        elif mouse_y < Settings.border or mouse_y > Settings.window_height - Settings.border:
            return True
        else:
            return False
    
    def move(self, mouse_x, mouse_y):
        if self.is_near_border(mouse_x, mouse_y):
            self.rect.x -= 1
            self.rect.y -= 1
        else:
            self.rect.x = mouse_x
            self.rect.y = mouse_y
    
    def get_rect(self):
        return self.rect

    def draw(self, screen):
        screen.blit(self.image,self.rect)

class Timer(object):
    def __init__(self, duration, with_start = True):
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


class Bullets(pygame.sprite.Sprite):
    def __init__ (self,filename, x, y):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename))
        self.image = pygame.transform.scale(self.image, Settings.chicken_size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Chicken(pygame.sprite.Sprite):
    def __init__(self, filename, g):
        super().__init__()
        self.images = []
        for i in range(13):
            bitmap = pygame.image.load(os.path.join(Settings.path_image, f"Moohuen{i}.png"))
            self.images.append(bitmap)
        self.image = self.images[0]
        self.image = pygame.transform.scale(self.image, Settings.chicken_size)
        self.rect = self.image.get_rect()
        self.rect.left = random.randint(Settings.border, Settings.window_width - Settings.border)
        self.rect.top = random.randint(Settings.border, Settings.window_height - Settings.border)
        self.t = 0
        self.spawnrate = 0
        self.x_speed = random.randint(-5, -2)
        self.y_speed = 0
        self.position = random.randint(0, Settings.window_width)
        self.animationtimer = Timer(100)
        self.frameindex = 0

    def move(self):
        self.rect.move_ip(self.x_speed, self.y_speed)

    def update(self):
        self.move()
        if self.animationtimer.is_next_stop_reached():
            self.image = self.images[self.frameindex]
            self.frameindex += 1
            if self.frameindex == len(self.images)- 1:
                self.frameindex = 0
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Mouse(pygame.sprite.Sprite):
    def __init__(self, filename="1.png"):
        super().__init__()
        self.change_image(filename)

    def draw(self, screen):
        screen.blit(self.image, pygame.mouse.get_pos())

    def change_image(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 35))
        self.rect = self.image.get_rect()


class Game(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Settings.window_width, Settings.window_height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.background1 = Background("Farm.jpg", 0, 0)
        self.mouse = Mouse()
        self.pause = False
        pygame.mouse.set_visible(False)
        self.chickens = pygame.sprite.Group()
        self.t = 0
        self.t2 = 0
        self.font_normalsize = pygame.font.Font(pygame.font.get_default_font(), 16)
        self.points = 0
        self.gameover = False

    def run(self):
        while self.running:
            self.clock.tick(Settings.fps)
            self.watch_for_events()
            self.draw()
            if not self.pause and not self.gameover:
                self.update()
            elif self.pause == True:
                self.paused()
            elif self.gameover == True:
                self.gameover_check()
            self.save_highscore()
            pygame.display.flip()

    def paused(self):
        screenfill = pygame.Surface((Settings.window_width, Settings.window_height))
        screenfill.fill((170, 170, 170))
        screenfill.set_alpha(180)
        self.screen.blit(screenfill, (0, 0))
        pause = self.font_normalsize.render("Paused", False, (255, 255, 255))
        score = self.font_normalsize.render(f"Highscore:{self.get_highscore()}", False, (255, 255, 255))
        self.screen.blit(pause, (
        Settings.window_width // 2 - pause.get_width() // 2, Settings.window_height // 2 - pause.get_height() // 2))
        self.screen.blit(score, (
        Settings.window_width // 2 - score.get_width() // 2, Settings.window_height // 2.1 - score.get_height() // 2.1))

    def gameover_check(self):
        gameover_screenfill = pygame.Surface((Settings.window_width, Settings.window_height))
        gameover_screenfill.fill((170,170,170))
        gameover_screenfill.set_alpha(180)
        self.screen.blit(gameover_screenfill, (0,0))
        gameover = self.font_normalsize.render("Game Over", False, (255,255,255))
        question = self.font_normalsize.render("to restart the game press Space", False, (255,255,255))
        gameover_score = self.font_normalsize.render(f"Points:{self.points}", False, (255, 255, 255))
        self.screen.blit(gameover, (
            Settings.window_width // 2 - gameover.get_width() // 2, Settings.window_height // 2 - gameover.get_height() // 2))
        self.screen.blit(question, (
            Settings.window_width // 2 - question.get_width() // 2,
            Settings.window_height // 2.1 - question.get_height() // 2.1))
        self.screen.blit(gameover_score, (
            Settings.window_width // 2 - gameover_score.get_width() // 2,
            Settings.window_height // 2.2 - gameover_score.get_height() // 2.2))


    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for chicken in self.chickens:
                    hits = chicken.rect.collidepoint(*pygame.mouse.get_pos())
                    if hits == True:
                        burst_sound = pygame.mixer.Sound(os.path.join(Settings.path_sound, "gun_shot_sound.ogg"))
                        pygame.mixer.Sound.play(burst_sound)
                        pygame.mixer.Sound.set_volume(burst_sound, 0.3)
                        self.points += abs(chicken.x_speed)
                        chicken.kill()
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

    def update(self):
        self.t += 1
        if self.t >= Settings.timeunit:
            self.t = 0
            if len(self.chickens) <= (Settings.window_width + Settings.window_height) / 100:
                self.chickens.add(Chicken("Moohuen(i).png", self.chickens))
                spawn_sound = pygame.mixer.Sound(os.path.join(Settings.path_sound, "big_chicken_pops_up.ogg"))
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
        points = self.font_normalsize.render(f"Points: {self.points}", False, (255, 255, 255))
        self.screen.blit(points, (0, 10))


if __name__ == "__main__":
    game = Game()
    game.run()
