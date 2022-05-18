import math
import time
from typing import List, Tuple
import pygame
import sys
import os
from settings import pacman_points


class Camera:
    def __init__(self, pos=(0, 0, 0), rot=(0, 0)):
        # receives tuple, but need to convert to list because
        # tuples are immutable and we need to change them
        self.pos = list(pos)
        self.rot = list(rot)
        self.mouse_sensitivity = 200
        self.minZ = 1

    @property
    def rotX(self) -> Tuple[float, float]:
        """Sin and Cos for camera X

        Returns:
            Tuple[float, float]: Sin and Cos for camera X
        """
        return math.sin(self.rot[0]), math.cos(self.rot[0])

    @property
    def rotY(self) -> Tuple[float, float]:
        """Sin and Cos for camera Y

        Returns:
            Tuple[float, float]: Sin and Cos for camera Y
        """
        return math.sin(self.rot[1]), math.cos(self.rot[1])

    def update(self, dt):
        keys = pygame.key.get_pressed()

        s = dt * 10
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

        # control minZ to clip vertices
        if keys[pygame.K_0]:
            self.minZ = 0.4
        if keys[pygame.K_1]:
            self.minZ = 1
        if keys[pygame.K_2]:
            self.minZ = 2
        if keys[pygame.K_9]:
            self.minZ = 9
        if keys[pygame.K_MINUS]:
            self.minZ = max(0.4, self.minZ - 50 * dt)
        if keys[pygame.K_EQUALS]:
            self.minZ += 50 * dt

        x, y = pygame.mouse.get_rel()
        x /= self.mouse_sensitivity
        y /= self.mouse_sensitivity
        self.rot[0] += y
        self.rot[1] += x


class Cube:
    # the cube center is at (0, 0, 0) - (x, y, z)
    vertices = (
        (-1, -1, -1),
        (1, -1, -1),
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (1, 1, 1),
        (-1, 1, 1),
    )

    edges = (
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

    faces = (
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
        (0, 3, 7, 4),
        (1, 2, 6, 5),
    )

    colors = (
        (255, 0, 0),
        (255, 128, 0),
        (255, 255, 0),
        (255, 255, 255),
        (0, 0, 255),
        (0, 255, 0),
    )

    def __init__(self, pos=(0, 0, 0)):
        x, y, z = pos
        self.verts = [(x + X / 2, y + Y / 2, z + Z / 2) for X, Y, Z in self.vertices]


class GameWindow:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("3D Graphics")
        self.width = 800
        self.height = 600
        self.center_width = self.width // 2
        self.center_height = self.height // 2

        self.fov = 90 / 180 * math.pi
        self.half_fov = self.fov / 2
        self.projY = self.center_height / math.tan(self.half_fov)
        self.projX = (
            self.center_width / math.tan(self.half_fov) / (self.width / self.height)
        )

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.dt = 0
        self.fps = 60

        self.camera = Camera((0, 0, -5))

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.cubes: List[Cube] = []
        self.show_edges = False

    def run(self):
        self.dt = time.time() - self.last_time
        self.last_time = time.time()

        while True:
            self.screen.fill((128, 128, 255))

            for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # loop through all objects to get all faces

            face_list = []
            face_color = []
            depth = []

            for obj in self.cubes:

                if self.show_edges:
                    self.draw_edges(obj)

                # update obj verts coordinates from camera position
                vert_list = [self.get3D(v) for v in obj.verts]

                for face_index, face in enumerate(obj.faces):
                    # get verts for one face
                    verts = [vert_list[vert_index] for vert_index in face]

                    # clip verts
                    # creates a new edge for this face
                    i = 0
                    while i < len(verts):
                        if verts[i][2] < self.camera.minZ:  # behind camera
                            sides = []
                            prev_vert = verts[i - 1]
                            next_vert = verts[(i + 1) % len(verts)]
                            if prev_vert[2] > self.camera.minZ:
                                sides.append(
                                    self.getZ(verts[i], prev_vert, self.camera.minZ)
                                )
                            if next_vert[2] > self.camera.minZ:
                                sides.append(
                                    self.getZ(verts[i], next_vert, self.camera.minZ)
                                )
                            verts = verts[:i] + sides + verts[i + 1 :]
                            i += len(sides) - 1
                        i += 1

                    if len(verts) > 2:
                        # add face (gen 2d poly / get color / average face depth)
                        face_list.append([self.get2D(v) for v in verts])
                        face_color.append(obj.colors[face_index])
                        depth += [
                            sum(
                                sum(v[i] / len(verts) for v in verts) ** 2
                                for i in range(3)
                            )
                        ]

            # draw all faces from all objects
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

    def draw_edges(self, obj):

        for edge in obj.edges:
            vertices = obj.verts[edge[0]], obj.verts[edge[1]]
            points = []
            for vert in vertices:

                x, y, z = self.get3D(vert)

                f = self.fov / z
                x, y = x * f, y * f
                points.append((self.center_width + int(x), self.center_height + int(y)))
            pygame.draw.line(self.screen, (255, 255, 255), points[0], points[1], 1)

    def rotate2d(
        self, pos: Tuple[float, float], rot: Tuple[float, float]
    ) -> Tuple[float, float]:
        """Rotate a point in a plain according to its rotation (sin, cos) in that plain

        Args:
            pos (Tuple[float, float]): x, y in a plain
            rot (Tuple[float, float]): sin, cos in a plain

        Returns:
            Tuple[float, float]: resulted rotated x, y in that plain
        """

        x, y = pos
        s, c = rot

        # in pygame the rotation is clockwise
        return x * c - y * s, y * c + x * s

    def add_cubes(self, points):
        """Adds cubes at each point location. Points is a list of tuples containing coordinates (x,z)

        Args:
            points (tuple[int, int]): list of (x,z)
        """
        self.cubes = [Cube((x, 0, z)) for x, z in points]

    def get3D(self, point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Translates x,y,z from 3D

        Args:
            point (Tuple[float, float, float]): _description_

        Returns:
            Tuple[float, float, float]: _description_
        """
        x, y, z = (
            point[0] - self.camera.pos[0],
            point[1] - self.camera.pos[1],
            point[2] - self.camera.pos[2],
        )
        x, z = self.rotate2d((x, z), self.camera.rotY)
        y, z = self.rotate2d((y, z), self.camera.rotX)

        return x, y, z

    def get2D(self, vert: Tuple[float, float, float]) -> Tuple[float, float]:
        """Convers 3D to 2D projection

        Args:
            vert (Tuple[float, float, float]): vertice with x,y,z coords

        Returns:
            Tuple[float, float]: x,y screen coords
        """
        return self.center_width + int(
            vert[0] / vert[2] * self.projX
        ), self.center_height + int(vert[1] / vert[2] * self.projY)

    def getZ(
        self, A: Tuple[float, float, float], B: Tuple[float, float, float], newZ: float
    ) -> Tuple[float, float, float]:
        """Creates a new vertice at newZ based on verts A and B

        Args:
            A (Tuple[float, float, float]): vertice A
            B (Tuple[float, float, float]): vertice B
            newZ (float): clip posistion Z

        Returns:
            Tuple[float, float, float]: new vertice
        """

        if B[2] == A[2] or newZ < A[2] or newZ > B[2]:
            return None
        dx, dy, dz = B[0] - A[0], B[1] - A[1], B[2] - A[2]
        i = (newZ - A[2]) / dz
        return A[0] + dx * i, A[1] + dy * i, newZ


if __name__ == "__main__":
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    game = GameWindow()
    game.add_cubes(pacman_points)
    game.show_edges = False
    game.run()
