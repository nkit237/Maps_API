import io
import sys

import pygame
import pygame_gui
from io import BytesIO
from PIL import Image

from yandex_map_library import *
from distance import lonlat_distance


class GUI:
    def __init__(self, size, theme):
        self.manager = pygame_gui.UIManager(size)
        self.theme_toggle = pygame_gui.elements.UIDropDownMenu(
            MapApp.THEMES,
            MapApp.THEMES[0],
            pygame.rect.Rect(10, 10, 100, 30),
            self.manager
        )
        self.search_field = pygame_gui.elements.UITextEntryLine(
            pygame.rect.Rect(120, 10, 200, 30),
            self.manager
        )
        self.submit_btn = pygame_gui.elements.UIButton(
            pygame.rect.Rect(330, 10, 80, 30),
            'Искать',
            self.manager
        )
        self.clear_btn = pygame_gui.elements.UIButton(
            pygame.rect.Rect(420, 10, 80, 30),
            'Сброс',
            self.manager
        )

    def update(self, td):
        self.manager.update(td)

    def draw_ui(self, surf):
        self.manager.draw_ui(surf)

    def process_event(self, event):
        self.manager.process_events(event)
        changes = {}
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.theme_toggle:
                changes['theme'] = event.text
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN or
                event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.submit_btn):
            changes['search'] = self.search_field.text
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.clear_btn:
            changes['search'] = 'clear'
        return changes


class MapApp:
    DELTA_LON = 200
    DELTA_LAT = 90
    THEMES = 'light', 'dark'
    KEYS = (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_PAGEDOWN, pygame.K_PAGEUP)

    def __init__(self, size):
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.z = 1
        self.coord = [0, 0]
        self.theme = MapApp.THEMES[0]
        self.point = None
        self.spn = None
        self.img = None
        self.update_map()
        self.clock = pygame.time.Clock()
        self.gui = GUI(size, self.theme)

    def update_map(self):
        bytes_img = get_static_map(ll=','.join(map(str, self.coord)), spn=self.spn, z=self.z, theme=self.theme,
                                   pt=self.point)
        self.img = pygame.image.load(BytesIO(bytes_img))
        self.screen.blit(self.img, (0, 0))

    def process_keys(self, event):
        if event.type == pygame.KEYDOWN and event.key in MapApp.KEYS:
            self.spn = None
            if event.key == pygame.K_PAGEUP:
                self.z = min(21, self.z + 1)
            if event.key == pygame.K_PAGEDOWN:
                self.z = max(1, self.z - 1)
            if event.key == pygame.K_LEFT:
                self.coord[0] = (self.coord[0] - MapApp.DELTA_LON * 2 ** -self.z + 180) % 360 - 180
            if event.key == pygame.K_RIGHT:
                self.coord[0] = (self.coord[0] + MapApp.DELTA_LON * 2 ** -self.z + 180) % 360 - 180
            if event.key == pygame.K_UP:
                self.coord[1] = min((self.coord[1] + MapApp.DELTA_LAT * 2 ** -self.z), 85)
            if event.key == pygame.K_DOWN:
                self.coord[1] = max((self.coord[1] - MapApp.DELTA_LAT * 2 ** -self.z), -85)
            return True

    def process_event(self, event):
        keys = self.process_keys(event)
        results = self.gui.process_event(event)
        self.theme = results.get('theme') or self.theme
        if keys or results:
            addr = results.get('search') or False
            if addr:
                if addr == 'clear':
                    self.point = None
                else:
                    self.search_map(addr)
            self.update_map()

    def search_map(self, addr):
        toponym = get_toponym(addr)
        self.spn = get_spn(toponym)
        coord = get_toponym_coord(toponym)
        self.point = ','.join(map(str, coord)) + ',pm2dgl'
        self.coord = list(map(float, coord))

    def run(self):
        while True:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                self.process_event(event)

            self.screen.blit(self.img, (0, 0))
            self.gui.update(time_delta)
            self.gui.draw_ui(self.screen)

            pygame.display.flip()


if __name__ == '__main__':
    app = MapApp((600, 450))
    app.run()
