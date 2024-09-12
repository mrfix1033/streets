import random
from queue import Queue

import pygame
import road_generator
import cProfile
from options import *


class MyGame:
    def __init__(self, WIDTH=1280, HEIGHT=720, FPS=60):
        self.WIDTH = int(WIDTH)
        self.HEIGHT = int(HEIGHT)
        self.FPS = FPS
        self.centerX = self.WIDTH // 2
        self.centerY = self.HEIGHT // 2
        self.initPyGame()
        self.extraInit()
        self.gameCycle()

    def initPyGame(self):
        pygame.init()
        self.display = pygame.display
        self.screen = self.display.set_mode((self.WIDTH, self.HEIGHT))
        self.display.set_caption("Streets")
        self.clock = pygame.time.Clock()

    def extraInit(self):
        # self.speed_paint = 1  # после заражения клетки клетка начинается заполняться
        self.spread_queue = Queue()
        self.queue_history = set()
        self.is_spreading_started = False

        self.color_handler = ColorHandler()
        self.default_color = (100, 100, 100)
        self.paint_color = (150, 0, 200)
        self.null_color = (0, 0, 0)

        if generate_map_0_or_load_from_file_1:
            with open("streets.txt") as file:
                self.board = [list(map(int, line.strip())) for line in file.readlines()]
        else:
            width, height = self.WIDTH // scale, self.HEIGHT // scale
            self.board = [[0] * width for _ in range(height)]

            for option in generator_options:
                option[:2] = (option[0] // scale, option[1] // scale)
            for road in road_generator.generate((0, 0), (width, height), generator_options):
                road.render_to_board(self.board)
            print('\n'.join(''.join(map(str, i)) for i in self.board))
        self.board_to_render = [[self.null_color] * len(this_string) for this_string in self.board]
        self.changed_board = []

        x = len(max(self.board, key=lambda string: len(string)))
        y = len(self.board)
        print(
            f"Board size: ({x}, {y}); with scale: ({x * scale}, {y * scale}); max: ({self.WIDTH}, {self.HEIGHT})")

        for y in range(len(self.board)):
            board_string_now = self.board[y]
            board_for_render_string_now = self.board_to_render[y]
            for x in range(len(board_string_now)):
                if board_string_now[x]:
                    def create_func(x, y):
                        # def set_func(color):
                        #     board_for_render_string_now[x] = color

                        def set_func(color):
                            self.changed_board.append((x, y, color))

                        return set_func

                    self.color_handler.smoothly_paint_cell(create_func(x, y), board_for_render_string_now[x],
                                                           self.default_color, self.FPS // speed_enabling)

    def gameCycle(self):
        self.running = True
        while self.running:
            self.clock.tick(self.FPS)
            self.doTick()
            self.extraDoTick()
            self.display.flip()
        pygame.quit()

    def doTick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                self.clicked(event)

    def extraDoTick(self):
        self.random_click()
        self.process_spread()
        self.color_handler.tick()
        self.draw()

    def clicked(self, event):
        _pos = event.pos
        pos = tuple(map(lambda i: i // scale, _pos))
        if 0 <= pos[1] < len(self.board_to_render) and 0 <= pos[0] < len(self.board_to_render[pos[1]]):
            data = self.board[pos[1]][pos[0]]
            if data:
                self.start_spreading(pos)

    def start_spreading(self, pos):
        self.spread_queue.put(pos)
        self.is_spreading_started = True
        if paint_black_after_starting_spreading:
            self.screen.fill("black")
        self.queue_history.clear()
        self.paint_color = tuple(random.randint(150, 230) for _ in range(3))

    def random_click(self):
        if random.random() < random_click_chance:
            pos = (random.randint(0, len(self.board[0]) - 1), random.randint(0, len(self.board) - 1))
            if self.board[pos[1]][pos[0]]:
                self.start_spreading(pos)

    def process_spread(self):
        size = min(self.spread_queue.qsize(), spread_per_second)  # self.spread_queue.qsize()
        for i in range(size):
            self.spread(self.spread_queue.get())

    def draw(self):
        if self.is_spreading_started:
            pass
        # print(len(self.board_to_render) * len(self.board_to_render[0]))
        # for y in range(len(self.board_to_render)):
        #     string_now = self.board_to_render[y]
        #     for x in range(len(string_now)):
        #         data = string_now[x]
        #         data = data
        #         pygame.draw.rect(self.screen, data, (x * scale, y * scale, scale, scale))  # быстрый
        for element in self.changed_board:
            pygame.draw.rect(self.screen, element[2],
                             (element[0] * scale, element[1] * scale, scale, scale))  # быстрый
            self.board_to_render[element[1]][element[0]] = element[2]
        self.changed_board.clear()
        my_font = pygame.font.SysFont("Comic Sans MS", 24)
        # self.screen.blit(my_font.render(str(round(self.clock.get_fps(), 1)), True, self.default_color, self.null_color), (6, 0))
        # self.screen.blit(my_font.render(str(self.spread_queue.qsize()), True, self.default_color, self.null_color), (60, 0))

    def spread(self, pos):
        # def set_func(color):
        #     self.board_to_render[pos[1]][pos[0]] = color
        def set_func(color):
            self.changed_board.append((pos[0], pos[1], color))

        self.color_handler.smoothly_paint_cell(set_func, self.board_to_render[pos[1]][pos[0]], self.paint_color,
                                               self.FPS // speed_spreading_color
                                               )

        deltas = (1, 0), (0, 1), (-1, 0), (0, -1)
        for delta in deltas:
            new_x, new_y = pos[0] + delta[0], pos[1] + delta[1]
            if 0 <= new_y < len(self.board_to_render) and 0 <= new_x < len(self.board_to_render[new_y]):
                if not self.board[new_y][new_x]:
                    continue
                coords = new_x, new_y
                if coords in self.queue_history:
                    continue
                self.queue_history.add(coords)
                self.spread_queue.put(coords)


class ColorHandler:
    class Handler:
        def __init__(self, func_to_set, color_now, color_new, do_it_in_n_ticks):
            self.func_to_set = func_to_set
            self.color_now = color_now
            self.color_new = color_new
            self.do_it_in_n_ticks = do_it_in_n_ticks
            self.step_now = 1

        def tick(self):
            color_delta = self.sub(self.color_new, self.color_now)
            part_color_delta = self.mul(color_delta, self.step_now / self.do_it_in_n_ticks)
            now_new_color = self.plus(self.color_now, part_color_delta)
            self.func_to_set(now_new_color)
            if self.step_now == self.do_it_in_n_ticks:
                return True
            self.step_now += 1
            return False

        def plus(self, c1, c2):
            return c1[0] + c2[0], c1[1] + c2[1], c1[2] + c2[2]

        def sub(self, c1, c2):
            return c1[0] - c2[0], c1[1] - c2[1], c1[2] - c2[2]

        def mul(self, c, multiplier):
            return c[0] * multiplier, c[1] * multiplier, c[2] * multiplier

    def __init__(self):
        self.list = set()

    def smoothly_paint_cell(self, func_to_set, color_now, color_new, do_it_in_n_ticks):
        self.list.add(ColorHandler.Handler(func_to_set, color_now, color_new, do_it_in_n_ticks))

    def tick(self):
        to_remove_set = set()
        for handler in self.list:
            if handler.tick():
                to_remove_set.add(handler)
        self.list.difference_update(to_remove_set)


with cProfile.Profile() as pr:
    game = MyGame()
    stats = pr.getstats()

    # Calculate percall for each function and sort by it
    results_sorted_by_percall = sorted(stats, key=lambda x: x[3])  # x[3] / x[1]  # total_time / callcount

    # Print the sorted results
    for func_stat in results_sorted_by_percall:
        func = func_stat[0]
        ncalls = func_stat[1]
        total_time = func_stat[3]
        percall_time = total_time / ncalls
        print(f"{round(percall_time * 1e9)}ns {total_time}\t{ncalls} - {func}")
