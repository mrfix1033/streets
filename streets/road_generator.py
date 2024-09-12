import random


class Road:
    def __init__(self, startX, startY, endX, endY):
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY

    def render_to_board(self, board):
        for y in range(self.startY, self.endY):
            if not y < len(board):
                break
            board_string_for_this_y = board[y]
            for x in range(self.startX, self.endX):
                if not x < len(board_string_for_this_y):
                    break
                board_string_for_this_y[x] = 1

    def __str__(self):
        return f"({self.startX}, {self.startY}) - ({self.endX}, {self.endY})"

    def __repr__(self):
        return self.__str__()


def generate(start_pos, end_pos, generator_params):
    roads = []
    width, height = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
    indexOfFirstVerticalRoad = -1

    this_generator_params = generator_params[0]
    min_distance_between_main_roads = this_generator_params[0]
    max_distance_between_main_roads = this_generator_params[1]

    number = random.randint(min_distance_between_main_roads, max_distance_between_main_roads)

    while number < width + height:
        isHorizontal = number < height
        if isHorizontal:
            startX = start_pos[0]
            endX = end_pos[0]
            y = start_pos[1] + number
            road = Road(startX, y, endX, y + 1)
            roads.append(road)
        else:
            if indexOfFirstVerticalRoad == -1:
                indexOfFirstVerticalRoad = len(roads)
            startY = start_pos[1]
            endY = end_pos[1]
            x = start_pos[0] + number - height
            road = Road(x, startY, x + 1, endY)
            roads.append(road)
        number += random.randint(min_distance_between_main_roads, max_distance_between_main_roads)

    if len(generator_params) != 1 and roads:
        old_len_roads = len(roads)
        generator_params = generator_params[1:]

        nowHorRoad = roads[0]
        nowVerRoad = roads[indexOfFirstVerticalRoad]
        roads += generate(start_pos, (nowVerRoad.endX, nowHorRoad.endY), generator_params)
        for vRI in range(indexOfFirstVerticalRoad + 1, old_len_roads):
            nextVerRoad = roads[vRI]
            roads += generate((nowVerRoad.startX, start_pos[1]), (nextVerRoad.endX, nowHorRoad.endY), generator_params)
            nowVerRoad = nextVerRoad
        roads += generate((nowVerRoad.startX, start_pos[1]), (end_pos[0], nowHorRoad.endY), generator_params)

        for hRI in range(1, indexOfFirstVerticalRoad):  # horizontalRoadIndex
            nextHorRoad = roads[hRI]
            nowVerRoad = roads[indexOfFirstVerticalRoad]
            roads += generate((start_pos[0], nowHorRoad.startY), (nowVerRoad.endX, nextHorRoad.endY), generator_params)
            for vRI in range(indexOfFirstVerticalRoad + 1, old_len_roads):
                nextVerRoad = roads[vRI]
                roads += generate((nowVerRoad.startX, nowHorRoad.startY), (nextVerRoad.endX, nextHorRoad.endY), generator_params)
                nowVerRoad = nextVerRoad
            roads += generate((nowVerRoad.startX, nowHorRoad.startY), (end_pos[0], nextHorRoad.endY), generator_params)
            nowHorRoad = nextHorRoad

        nowVerRoad = roads[indexOfFirstVerticalRoad]
        roads += generate((start_pos[0], nowHorRoad.startY), (roads[indexOfFirstVerticalRoad].endX, end_pos[1]), generator_params)
        for vRI in range(indexOfFirstVerticalRoad + 1, old_len_roads):
            nextVerRoad = roads[vRI]
            roads += generate((nowVerRoad.startX, nowHorRoad.startY), (nextVerRoad.endX, end_pos[1]), generator_params)
            nowVerRoad = nextVerRoad

        roads += generate((nowVerRoad.startX, nowHorRoad.startY), end_pos, generator_params)
    return roads
