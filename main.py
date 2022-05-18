import math
import time
import pygame
import sys


class Camera:
    def __init__(self, pos=(0, 0, 0), rot=(0, 0)):
        # receives tuple, but need to convert to list because
        # tuples are immutable and we need to change them
        self.pos = list(pos)
        self.rot = list(rot)
        self.mouse_sensitivity = 200

    def update(self, dt):
        keys = pygame.key.get_pressed()

        s = dt * 100
        if keys[pygame.K_q]:
            self.pos[1] += s
        if keys[pygame.K_e]:
            self.pos[1] -= s

        x, y = s * math.sin(self.rot[1]), s * math.cos(self.rot[1])

        if keys[pygame.K_w]:
            self.pos[0] += x
            self.pos[2] += y
        if keys[pygame.K_s]:
            self.pos[0] -= x
            self.pos[2] -= y
        if keys[pygame.K_a]:
            self.pos[0] -= y
            self.pos[2] += x
        if keys[pygame.K_d]:
            self.pos[0] += y
            self.pos[2] -= x

        x, y = pygame.mouse.get_rel()
        x /= self.mouse_sensitivity
        y /= self.mouse_sensitivity
        self.rot[0] += y
        self.rot[1] += x


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

        self.faces = (
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (0, 3, 7, 4),
            (1, 2, 6, 5),
        )

        self.colors = (
            (255, 0, 0),
            (255, 128, 0),
            (255, 255, 0),
            (255, 255, 255),
            (0, 0, 255),
            (0, 255, 0),
        )

        self.camera = Camera((0, 0, -5))

        # pygame.event.get()
        # pygame.mouse.get_rel()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def run(self):
        self.dt = time.time() - self.last_time
        self.last_time = time.time()

        while True:
            self.screen.fill("black")

            for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # update verts coordinates from camera position
            vert_list = []
            screen_coords = []
            for x, y, z in self.verts:
                x -= self.camera.pos[0]
                y -= self.camera.pos[1]
                z -= self.camera.pos[2]

                x, z = self.rotate2d((x, z), self.camera.rot[1])
                y, z = self.rotate2d((y, z), self.camera.rot[0])

                vert_list.append((x, y, z))

                f = self.center_width / z
                x, y = x * f, y * f
                screen_coords.append(
                    (self.center_width + int(x), self.center_height + int(y))
                )

            self.draw_edges()

            face_list = []
            face_color = []
            depth = []
            for face_index, face in enumerate(self.faces):
                x, y = screen_coords[face_index]
                on_screen = False
                for face_vertice in face:
                    z = vert_list[face_vertice][2]

                    # check if face is on screen
                    if z > 0 and x > 0 and x < self.width and y > 0 and y < self.height:
                        on_screen = True
                        break

                if on_screen:
                    coords = [screen_coords[on_index] for on_index in face]
                    face_list.append(coords)
                    face_color.append(self.colors[face_index])

                    depth.append(
                        sum(
                            sum(
                                vert_list[face_screen_index][p_index]
                                for face_screen_index in face
                            )
                            ** 2
                            for p_index in range(3)
                        )
                    )

            order = sorted(range(len(face_list)), key=lambda i: depth[i], reverse=True)
            for order_index in order:
                try:
                    pygame.draw.polygon(
                        self.screen, face_color[order_index], face_list[order_index]
                    )
                except Exception:
                    pass

            pygame.display.flip()
            self.clock.tick(self.fps)

            self.camera.update(self.dt)

    def draw_edges(self):

        for edge in self.edges:
            vertices = self.verts[edge[0]], self.verts[edge[1]]
            points = []
            for x, y, z in vertices:

                x -= self.camera.pos[0]
                y -= self.camera.pos[1]
                z -= self.camera.pos[2]

                x, z = self.rotate2d((x, z), self.camera.rot[1])
                y, z = self.rotate2d((y, z), self.camera.rot[0])

                f = self.center_width / z
                x, y = x * f, y * f
                points.append((self.center_width + int(x), self.center_height + int(y)))
            pygame.draw.line(self.screen, (255, 255, 255), points[0], points[1], 1)

    def rotate2d(self, pos, radian):
        x, y = pos
        s, c = math.sin(radian), math.cos(radian)

        # in pygame the rotation is clockwise
        return x * c - y * s, y * c + x * s


if __name__ == "__main__":
    game = GameWindow()
    game.run()
