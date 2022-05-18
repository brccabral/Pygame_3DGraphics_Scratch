import time
import pygame
import sys


class GameWindow:
    def __init__(self):
        pygame.init()
        self.width = 400
        self.height = 400
        self.center_width = self.width // 2
        self.center_height = self.height // 2
        self.window_surface = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.dt = 0
        self.fps = 60

    def run(self):
        self.dt = time.time() - self.last_time
        self.last_time = time.time()
        while True:
            self.window_surface.fill("black")

            for event in pygame.event.get([pygame.QUIT]):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    game = GameWindow()
    game.run()
