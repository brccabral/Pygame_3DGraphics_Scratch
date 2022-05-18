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
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.dt = 0
        self.fps = 60

        # the cube center is at (0, 0, 0) - (x, y, z)
        self.verts = (
            (-1, -1, -1),
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, 1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, 1, 1),
        )

    def run(self):
        self.dt = time.time() - self.last_time
        self.last_time = time.time()
        while True:
            self.screen.fill("black")

            for event in pygame.event.get([pygame.QUIT]):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            for x, y, z in self.verts:
                # shift in z axis
                z += 5

                # projection coefficient
                # using because it is a square screen, in tutorial they use 200 hardcoded
                f = self.center_width / z
                x, y = x * f, y * f

                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (self.center_width + int(x), self.center_height + int(y)),
                    6,
                )

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    game = GameWindow()
    game.run()
