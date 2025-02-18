import io
import sys
import pygame
from io import BytesIO
from PIL import Image

from yandex_map_library import *
from distance import lonlat_distance


class MapApp:
    def __init__(self, size):
        self.screen = pygame.display.set_mode(size)
        self.z = 10
        self.coord = [123, 45]
        self.update_map()

    def update_map(self):
        bytes_img = get_static_map(ll=','.join(map(str, self.coord)), z=self.z)
        img = pygame.image.load(BytesIO(bytes_img))
        self.screen.blit(img, (0, 0))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_PAGEUP:
                        self.z = min(21, self.z + 1)
                    if event.key == pygame.K_PAGEDOWN:
                        self.z = max(0, self.z - 1)
                    self.update_map()

            pygame.display.flip()


if __name__ == '__main__':
    app = MapApp((600, 450))
    app.run()
