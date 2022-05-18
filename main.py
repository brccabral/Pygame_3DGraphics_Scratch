import time
import pygame
import sys


class Camera:
    def __init__(self, pos=(0, 0, 0), rot=(0, 0)):
        # receives tuple, but need to convert to list because
        # tuples are immutable and we need to change them
        self.pos = list(pos)
        self.rot = list(rot)

    def update(self, dt, keys):
        s = dt * 10000
        if keys[pygame.K_q]:
            self.pos[1] += s
        if keys[pygame.K_e]:
            self.pos[1] -= s

        if keys[pygame.K_w]:
            self.pos[2] += s
        if keys[pygame.K_s]:
            self.pos[2] -= s
        if keys[pygame.K_a]:
            self.pos[0] -= s
        if keys[pygame.K_d]:
            self.pos[0] += s


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

        self.edges = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        )

        self.camera = Camera((0, 0, -5))

    def run(self):
        self.dt = time.time() - self.last_time
        self.last_time = time.time()
        while True:
            self.screen.fill("black")

            for event in pygame.event.get([pygame.QUIT]):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            for edge in self.edges:
                vertices = self.verts[edge[0]], self.verts[edge[1]]
                points = []
                for x, y, z in vertices:

                    x -= self.camera.pos[0]
                    y -= self.camera.pos[1]
                    z -= self.camera.pos[2]

                    f = self.center_width / z
                    x, y = x * f, y * f
                    points.append(
                        (self.center_width + int(x), self.center_height + int(y))
                    )
                pygame.draw.line(self.screen, (255, 255, 255), points[0], points[1], 1)

            pygame.display.flip()
            self.clock.tick(self.fps)

            keys = pygame.key.get_pressed()
            self.camera.update(self.dt, keys)


if __name__ == "__main__":
    game = GameWindow()
    game.run()
