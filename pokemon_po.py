import pygame
import random
import os
import math
import json
import time
import pandas as pd
from itertools import cycle

os.chdir(os.path.dirname(__file__))

# data importing for node weights
weight_file = 'xy_weights.xlsx'
df = pd.read_excel(io=weight_file)
WEIGHT_LIST = []
for i, rows in df.iterrows():
    WEIGHT_LIST.append(rows.tolist())

pygame.init()
SIZE = [500, 500]
SCREEN = pygame.display.set_mode(SIZE)
I_FOLDER = "images"
P = dict(BACKGROUND='PokePo_map.png',
         NODE='node.png',
         LOGO='logo.png',
         PLAYER='head.png',
         POKE1='poke_1.png',
         POKE2='poke_2.png',
         POKE3='poke_3.png',
         POKE4='poke_4.png',
         POKE5='poke_5.png',
         POKE6='poke_6.png',
         POKE7='poke_7.png',
         POKE8='poke_8.png',
         POKE9='poke_9.png',
         POKE10='poke_10.png',
         POKE11='poke_11.png',
         POKE12='poke_12.png',
         POKE13='poke_13.png',
         POKE14='poke_14.png',
         POKE15='poke_15.png',
         POKE16='poke_16.png',
         POKE17='poke_17.png',
         POKE18='poke_18.png',
         POKE19='poke_19.png',
         POKE20='poke_20.png',
         )
PICS = {k: os.path.join(I_FOLDER, v) for k, v in P.items()}
# set to scale up or down how fast things run, (0,1) slows game down, (1, inf) speeds up, 1 keeps default
TIME_SCALE = 100
SESSION_TIME = 720 / TIME_SCALE
FPS = 60
HUMAN = 'HUMAN'
AGENT = 'AGENT'
CONTROL = AGENT
LETTER = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10}

# custom events
player_walked_event = pygame.USEREVENT+1
player_can_walk_event = pygame.USEREVENT+2


def image_load(name):
    return pygame.image.load(name).convert_alpha()


def poke_points():
    # we fit the data and got an equation: y=410.9192e^(-0.2142t)
    # which gives a mean of 4.6685
    u = 4.6685
    x = random.expovariate(1 / u)
    # no clamp for floats exists in python so this works for that
    # and since x~exp(1/3) returns a lot of values between 1/3 and 1 we ceil instead of floor
    return max(min(math.ceil(x), 20), 1)


def poke_times():
    # The mean and std come from the data we were given
    # fitted using python
    u = 30.2
    s = 9.2
    x = random.gauss(u, s)
    return x * 1000 / TIME_SCALE


def poke_spawn_weights(x, y):
    # These weights come from the data
    # total num poke spawned at (x,y) / total overall
    weight = WEIGHT_LIST[y-1][x-1]
    return weight


def distance_r2(node1, node2):
    return math.sqrt((node1.x-node2.x)*(node1.x-node2.x) + (node1.y-node2.y)*(node1.y-node2.y))


class Node(pygame.sprite.Sprite):
    def __init__(self, name, x, y, weight):
        super().__init__()

        self.name = name
        self.x = x
        self.y = y
        self.weight = weight
        self.image = image_load(PICS['NODE'])
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.adjacent_nodes = self.get_adjacent()

        self.pokes_seen_here = []
        self.poke_curr_here = None

        self.poke_count = 0
        self.sum_poke_points = 0

    def print_data(self):
        print(' ------------- ')
        print(self.name)
        print(self.pokes_seen_here[-1])
        print('weight: ' + str(self.weight))
        print('total poke seen: ' + str(self.poke_count))
        print('sum poke points: ' + str(self.sum_poke_points))

    def get_row(self):
        # names are like 'A10' so name[0] is always a letter
        self_row = self.name[0]
        return self_row

    def get_column(self):
        # names are like 'A10' so name[1:] is always a number
        self_column = int(self.name[1:])
        return self_column

    def get_adjacent(self):
        my_row = self.get_row()
        my_col = self.get_column()

        if my_row == 'A':
            up_row = my_row
        else:
            up_row = list(LETTER.keys())[LETTER[my_row] - 2]
        if my_row == 'J':
            down_row = my_row
        else:
            down_row = list(LETTER.keys())[LETTER[my_row]]

        if my_col == 10:
            right_col = my_col
        else:
            right_col = my_col + 1
        if my_col == 1:
            left_col = my_col
        else:
            left_col = my_col - 1

        #     1 2 3
        #     | | |
        # A - X O X
        # B - O P O
        # C - X O X
        # where O is visible and X not
        up = up_row + str(my_col)
        down = down_row + str(my_col)
        right = my_row + str(right_col)
        left = my_row + str(left_col)
        adjacent = [up, down, right, left]
        return adjacent


class Grid:
    def __init__(self):
        self.width = 10
        self.height = 10
        self.spacing = 45
        # dict of locations of intersections by pixel as tuples
        # eg grid_locs['A1'] returns (45, 45, weight)
        self.grid_locs = {}
        t = LETTER
        for x in range(1, self.height + 1):
            for y in t:
                new_node = Node(y+str(x), x*self.spacing, t[y]*self.spacing, poke_spawn_weights(x, t[y]))
                self.grid_locs[y+str(x)] = new_node


class Pokemon(pygame.sprite.Sprite):
    def __init__(self, points, node, count, spawn_time):
        super().__init__()

        self.count = count

        self.current_node = node
        self.x = self.current_node.x
        self.y = self.current_node.y

        self.points = points
        self.sprites = [image_load(PICS['POKE1']),
                        image_load(PICS['POKE2']),
                        image_load(PICS['POKE3']),
                        image_load(PICS['POKE4']),
                        image_load(PICS['POKE5']),
                        image_load(PICS['POKE6']),
                        image_load(PICS['POKE7']),
                        image_load(PICS['POKE8']),
                        image_load(PICS['POKE9']),
                        image_load(PICS['POKE10']),
                        image_load(PICS['POKE11']),
                        image_load(PICS['POKE12']),
                        image_load(PICS['POKE13']),
                        image_load(PICS['POKE14']),
                        image_load(PICS['POKE15']),
                        image_load(PICS['POKE16']),
                        image_load(PICS['POKE17']),
                        image_load(PICS['POKE18']),
                        image_load(PICS['POKE19']),
                        image_load(PICS['POKE20'])
                        ]
        # lists are 0 indexed so -1 to correct for the fact that points are [1,20]
        self.image = self.sprites[self.points-1]
        # pokemon are started invisible and updated by the player vision function
        self.image.set_alpha(0)

        self.rect = self.image.get_rect()
        self.rect.x = self.x - 10
        self.rect.y = self.y - 10

        # life time default is 15 sec scaled by TIME_SCALE
        self.time = 15 / TIME_SCALE
        self.life_start = spawn_time
        self.alive = True

        self.collect_data_on_node()

    def collect_data_on_node(self):
        # here we update the corresponding node:
        # so it tracks the value and time of spawn, est time of death for each pokemon at that node
        # i figured time of death could be useful to track error in the simulation since it's clearly tied to fps
        self.current_node.pokes_seen_here.append({'value': self.points,
                                                  'spawn_time': self.life_start / 1000,
                                                  'est_death_time': self.life_start / 1000 + 15 / TIME_SCALE})
        self.current_node.poke_count += 1
        self.current_node.sum_poke_points += self.points

    def update(self):
        self.check_time()

    def check_time(self):
        if pygame.time.get_ticks() - self.life_start >= self.time * 1000:
            self.time_up()

    def time_up(self):
        self.kill()
        self.current_node.poke_curr_here = None
        self.alive = False
        # print('poke: ' + str(self.count) + ' dying at ' + str(pygame.time.get_ticks()/1000))


class Player(pygame.sprite.Sprite):
    def __init__(self, node, vision_func):
        super().__init__()

        self.current_node = node
        self.x = self.current_node.x
        self.y = self.current_node.y

        self.step = 45
        # human walkspeed found here https://deepblue.lib.umich.edu/bitstream/handle/2027.42/67419/10.1177_0022022199030002003.pdf;jsessionid=A0778AA95E2F557ECFD15EC6DDAAA75B?sequence=2
        # titled "The Pace of Life in 31 Countries" on page 13 of the pdf
        # for simplicity we assume 3 mph which means it takes 8 minutes to walk .4 miles or the distance of 1 cell
        # so our timescale will be based on the fact that it takes 8 seconds to talk from intersection to intersection
        self.walk_time = 8 / TIME_SCALE
        self.can_walk = True
        # pass a function to vision_type it will be used to check which pokemon should be blitted
        self.vision_function = vision_func
        self.visible_nodes = []
        self.vision_radius = 90

        self.image = image_load(PICS['PLAYER'])
        self.rect = self.image.get_rect()
        self.rect.x = self.x - 10
        self.rect.y = self.y - 10

        self.points = 0

    def start_walk_timer(self):
        # creates a timer that triggers and event after the time elapses
        self.player_walked()
        pygame.time.set_timer(player_can_walk_event, int(self.walk_time * 1000), True)

    def player_walked(self):
        e = pygame.event.Event(player_walked_event)
        pygame.event.post(e)

    def move_up(self):
        if self.rect.centery > 50 and self.can_walk:
            self.rect = self.rect.move(0, -self.step)
            self.start_walk_timer()

    def move_down(self):
        if self.rect.centery < 450 and self.can_walk:
            self.rect = self.rect.move(0, self.step)
            self.start_walk_timer()

    def move_left(self):
        if self.rect.centerx > 50 and self.can_walk:
            self.rect = self.rect.move(-self.step, 0)
            self.start_walk_timer()

    def move_right(self):
        if self.rect.centerx < 450 and self.can_walk:
            self.rect = self.rect.move(self.step, 0)
            self.start_walk_timer()

    def player_vision_adjacent(self):
        visible = self.current_node.adjacent_nodes
        return visible

    def player_vision_radius(self):
        # the nodes are 45 pixels apart so we can use that and the current node to calculate the nodes in the radius
        # the grid starts at 45 pix on top and 45 on left
        current_row = self.current_node.get_row()
        current_row_index = LETTER[current_row]
        current_col = self.current_node.get_column()

        # we can divide the radius by 45 and floor it to get the number of rows/cols we can see away from center
        node_delta = math.floor(self.vision_radius / 45)

        visible = []
        lett_keys = list(LETTER.keys())
        for x in range(node_delta+1):
            for y in range(node_delta+1):
                if current_col + x <= 10:
                    if current_row_index + y - 1 < len(lett_keys):
                        if x * x + y * y <= node_delta * node_delta:
                            n_row = lett_keys[current_row_index + y - 1]
                            visible.append(n_row + str(current_col + x))
                    if current_row_index - y - 1 >= 0:
                        if x * x + y * y <= node_delta * node_delta:
                            n_row = lett_keys[current_row_index - y - 1]
                            visible.append(n_row + str(current_col + x))
                if current_col - x >= 1:
                    if current_row_index + y - 1 < len(lett_keys):
                        if x * x + y * y <= node_delta * node_delta:
                            n_row = lett_keys[current_row_index + y - 1]
                            visible.append(n_row + str(current_col - x))
                    if current_row_index - y - 1 >= 0:
                        if x * x + y * y <= node_delta * node_delta:
                            n_row = lett_keys[current_row_index - y - 1]
                            visible.append(n_row + str(current_col - x))
        return visible

    def check_vision(self):
        self.visible_nodes = self.vision_function(self)

    def control_movement(self):
        if self.can_walk:
            if CONTROL == HUMAN:
                # input handling for movement
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_UP]:
                    self.move_up()
                elif pressed[pygame.K_RIGHT]:
                    self.move_right()
                elif pressed[pygame.K_DOWN]:
                    self.move_down()
                elif pressed[pygame.K_LEFT]:
                    self.move_left()

    def update(self):
        self.check_vision()
        self.control_movement()


class Agent:
    def __init__(self, player, grid):
        self.player = player
        self.grid = grid
        self.visible_poke = []
        self.target_queue = []
        self.path_list = cycle([self.grid.grid_locs['H1'],
                                self.grid.grid_locs['H2'],
                                self.grid.grid_locs['H3'],
                                self.grid.grid_locs['H4']
                                ])
        # self.path_list = cycle([self.grid.grid_locs['B3'],
        #                         self.grid.grid_locs['C7'],
        #                         self.grid.grid_locs['H1'],
        #                         self.grid.grid_locs['D4'],
        #                         self.grid.grid_locs['J6'],
        #                         self.grid.grid_locs['A5'],
        #                         self.grid.grid_locs['I2']
        #                         ])
        # self.path_list = cycle([self.grid.grid_locs['C2'],
        #                         self.grid.grid_locs['C9']])
        self.current_target = None
        self.not_moving = True
        self.grabbing_poke = False
        self.point_threshold = 1

    def move_left(self):
        self.player.move_left()

    def move_right(self):
        self.player.move_right()

    def move_up(self):
        self.player.move_up()

    def move_down(self):
        self.player.move_down()

    def decide_path(self):
        for poke in self.visible_poke:
            # print(poke.current_node.name)
            if self.target_queue[0].poke_curr_here:
                if poke.points >= self.point_threshold and poke.points >= self.target_queue[0].poke_curr_here.points:
                    if distance_r2(poke.current_node, self.player.current_node) <= \
                            distance_r2(self.player.current_node, self.target_queue[0]):
                        self.target_queue[0] = poke.current_node
                        return
            else:
                if poke.points >= self.point_threshold:
                    self.target_queue[0] = poke.current_node
                    return
        self.target_queue.append(next(self.path_list))

    def go_to(self):
        if len(self.target_queue) > 0:
            self.current_target = self.target_queue[0]
            node = self.current_target
            # print('current node: ' + self.player.current_node.name)
            # print('target: ' + node.name)
            # print(node.name)
            if node:
                # print('moving to next location...')
                # row index [1, 10] be careful arrays are 0 indexed
                player_row_index = self.player.current_node.get_row()
                player_col_index = self.player.current_node.get_column()

                if node.get_column() < player_col_index:
                    self.move_left()
                elif LETTER[node.get_row()] < LETTER[player_row_index]:
                    self.move_up()
                elif node.get_column() > player_col_index:
                    self.move_right()
                elif LETTER[node.get_row()] > LETTER[player_row_index]:
                    self.move_down()

                if self.player.current_node == node:
                    self.target_queue.pop(0)
        self.decide_path()

    def strategy(self, **kwargs):
        self.visible_poke = kwargs['visible']
        self.go_to()
        return


class Game:
    def __init__(self):
        self.screen = SCREEN
        pygame.display.set_caption("Pokemon Po Sim")
        self.background = image_load(PICS['BACKGROUND'])
        self.logo = image_load(PICS['LOGO'])
        pygame.display.set_icon(self.logo)
        self.font = pygame.font.SysFont('Comic Sans MS', 15)

        self.node_list = pygame.sprite.Group()
        self.visible_node_list = pygame.sprite.Group()
        self.pokes_list = pygame.sprite.Group()
        self.visible_poke_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()

        self.grid = Grid()
        for node in self.grid.grid_locs:
            self.node_list.add(self.grid.grid_locs[node])

        spawn_key = random.choice(list(self.grid.grid_locs.keys()))
        print(spawn_key)
        self.player = Player(node=self.grid.grid_locs[spawn_key], vision_func=Player.player_vision_radius)
        self.all_sprites_list.add(self.player)

        self.fps = FPS

        self.poke_count = 0

        self.agent = Agent(self.player, self.grid)

        # this starts a timer that kills the game after "12 hours" or 720 seconds scaled by TIME_SCALE
        pygame.time.set_timer(pygame.QUIT, int(SESSION_TIME * 1000), True)

    def spawn_pokemon(self):
        nodes = self.grid.grid_locs
        node_weights = [i.weight for i in nodes.values()]
        node_names = [n.name for n in nodes.values()]
        # this chooses with replacement from all nodes on the grid weighted by their respective weights
        # the returned value is the name of the node in a list eg ['A1']
        choice = random.choices(population=node_names, weights=node_weights)

        curr_time = pygame.time.get_ticks()
        new_poke = Pokemon(poke_points(), node=nodes[choice[0]], count=self.poke_count, spawn_time=curr_time)
        nodes[choice[0]].poke_curr_here = new_poke
        self.poke_count += 1

        # print('----------------------------')
        # print('spawning a poke')
        # print('at node: ' + choice[0])
        # print('value: ' + str(new_poke.points))
        # print('count: ' + str(self.poke_count))
        # print('start: ' + str(new_poke.life_start))
        # print('death at: ' + str(new_poke.life_start + 15 / TIME_SCALE))
        # new_poke.current_node.print_data()

        self.pokes_list.add(new_poke)
        self.all_sprites_list.add(new_poke)
        # this creates a loop of poke spawning based on the timer
        pygame.time.set_timer(pygame.USEREVENT, int(poke_times()), True)

    def run(self):
        clock = pygame.time.Clock()
        # pokemon spawn timer
        pygame.time.set_timer(pygame.USEREVENT, int(poke_times()), True)
        play = True
        while play:
            # caps fps
            clock.tick(self.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    node_data = {}
                    run_data_dump = {}
                    for node in self.grid.grid_locs.values():
                        node_data[node.name] = {'weight': node.weight,
                                                'pokes_seen': node.pokes_seen_here,
                                                'count': node.poke_count,
                                                'sum_points': node.sum_poke_points}
                        run_data_dump['elapsed_time'] = pygame.time.get_ticks() / 1000
                        run_data_dump['score'] = self.player.points
                        run_data_dump['total_poke_created'] = self.poke_count
                        run_data_dump['nodes'] = node_data

                        time_now = time.strftime("%Y%m%d-%H%M%S")
                        j_time_now = time_now + '.json'
                        with open(j_time_now, 'w') as out:
                            json.dump(run_data_dump, out)
                    pygame.quit()
                    quit()
                if event.type == pygame.USEREVENT:
                    self.spawn_pokemon()
                if event.type == player_walked_event:
                    self.player.can_walk = False
                    # print('-------------')
                    # print('walked at: ' + str(pygame.time.get_ticks()/1000))
                if event.type == player_can_walk_event:
                    self.player.can_walk = True
                    # print('player can move again: ' + str(pygame.time.get_ticks()/1000))

            # check for collision with new node so we can update player current node
            node_hit_list = pygame.sprite.spritecollide(self.player, self.node_list, False)
            for node in node_hit_list:
                self.player.current_node = node
                # print(self.player.current_node.name)
            # check for collision with pokemon and kill them if it happens then increment points
            pokes_hit_list = pygame.sprite.spritecollide(self.player, self.pokes_list, True)
            for poke in pokes_hit_list:
                self.player.points += poke.points
                # print(self.player.points)

            self.all_sprites_list.update()

            for node in self.player.visible_nodes:
                self.visible_node_list.add(self.grid.grid_locs[node])
            for node in self.visible_node_list:
                if node.name not in self.player.visible_nodes:
                    self.visible_node_list.remove(node)

            for poke in self.pokes_list:
                if poke.current_node.name in self.player.visible_nodes:
                    self.visible_poke_list.add(poke)
                else:
                    self.visible_poke_list.remove(poke)

            for poke in self.pokes_list:
                poke.image.set_alpha(0)
            for poke in self.visible_poke_list:
                poke.image.set_alpha(255)

            self.screen.blit(self.background, (0, 0))
            self.visible_node_list.draw(self.screen)
            self.all_sprites_list.draw(self.screen)
            self.visible_poke_list.draw(self.screen)

            if CONTROL == AGENT:
                self.agent.strategy(visible=self.visible_poke_list.sprites())

            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
