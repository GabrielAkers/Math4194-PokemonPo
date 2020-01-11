import pygame
import random
import os
import math
import json
import time

os.chdir(os.path.dirname(__file__))
pygame.init()
SIZE = [500, 500]
I_FOLDER = "images"
P = dict(BACKGROUND='PokePo_map.png',
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
TIME_SCALE = 10
FPS = 30

# custom events
player_walked_event = pygame.USEREVENT+1
player_can_walk_event = pygame.USEREVENT+2


def image_load(name):
    return pygame.image.load(name).convert_alpha()


def poke_points():
    # TODO: at first im just assuming this is some kind of exponential distribution based on the data we saw
    # TODO: assuming mean is 3
    u = 3
    x = random.expovariate(1 / u)
    # no clamp for floats exists in python so this works for that
    # and since x~exp(1/3) returns a lot of values between 1/3 and 1 we ceil instead of floor
    return max(min(math.ceil(x), 20), 1)


def poke_times():
    # TODO: assuming gaussian distribution
    # TODO: assuming mean 30 sd 5
    u = 30
    s = 5
    x = random.gauss(u, s)
    return x * 1000 / TIME_SCALE


def poke_spawn_weights(x, y):
    # TODO: I'm just assigning random weights for now such that they sum to 1 (or pretty close)
    r = [random.random() for i in range(101)]
    s = sum(r)
    r = [i/s for i in r]
    z = x+10*(y-1)
    return r[z]


def player_vision_adjacent(current_node):
    # calcs adjacent nodes to the one passed and returns it as a list
    # does so iteratively starting with top and moving clockwise
    # TODO

    return adjacent_list


class Node:
    def __init__(self, name, x, y, weight):
        self.name = name
        self.x = x
        self.y = y
        self.weight = weight

        self.pokes_seen_here = []

        self.poke_count = 0
        self.sum_poke_points = 0

    def print_data(self):
        print(' ------------- ')
        print(self.name)
        print(self.pokes_seen_here[-1])
        print('weight: ' + str(self.weight))
        print('total poke seen: ' + str(self.poke_count))
        print('sum poke points: ' + str(self.sum_poke_points))


class Grid:
    def __init__(self):
        self.width = 10
        self.height = 10
        self.spacing = 45
        # dict of locations of intersections by pixel as tuples
        # eg grid_locs['A1'] returns (45, 45, weight)
        self.grid_locs = {}
        t = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10}
        for x in t:
            for y in range(1, self.height + 1):
                new_node = Node(x+str(y), t[x]*self.spacing, y*self.spacing, poke_spawn_weights(t[x], y))
                self.grid_locs[x+str(y)] = new_node


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

        self.rect = self.image.get_rect()
        self.rect.x = self.x - 10
        self.rect.y = self.y - 10

        # life time default is 15 sec scaled by TIME_SCALE
        self.time = 15 / TIME_SCALE
        self.life_start = spawn_time

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
        print('poke: ' + str(self.count) + ' dying at ' + str(pygame.time.get_ticks()/1000))


class Player(pygame.sprite.Sprite):
    def __init__(self, node, vision_func, human_control):
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
        self.human = human_control

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
        self.rect = self.rect.move(0, -self.step)
        self.start_walk_timer()

    def move_down(self):
        self.rect = self.rect.move(0, self.step)
        self.start_walk_timer()

    def move_left(self):
        self.rect = self.rect.move(-self.step, 0)
        self.start_walk_timer()

    def move_right(self):
        self.rect = self.rect.move(self.step, 0)
        self.start_walk_timer()

    def check_vision(self):
        visible_nodes = self.vision_function(self.current_node)
        return visible_nodes

    def update(self):
        # input handling for movement
        pressed = pygame.key.get_pressed()
        if self.human:
            if self.can_walk:
                if pressed[pygame.K_UP]:
                    if self.rect.centery > 50:
                        self.move_up()
                elif pressed[pygame.K_RIGHT]:
                    if self.rect.centerx < 450:
                        self.move_right()
                elif pressed[pygame.K_DOWN]:
                    if self.rect.centery < 450:
                        self.move_down()
                elif pressed[pygame.K_LEFT]:
                    if self.rect.centerx > 50:
                        self.move_left()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Pokemon Po Sim")
        self.background = image_load(PICS['BACKGROUND'])
        self.logo = image_load(PICS['LOGO'])
        pygame.display.set_icon(self.logo)

        self.grid = Grid()

        self.pokes_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()

        spawn_key = random.choice(list(self.grid.grid_locs.keys()))
        self.player = Player(node=self.grid.grid_locs[spawn_key], vision_func=player_vision_adjacent, human_control=True)
        self.all_sprites_list.add(self.player)

        self.fps = FPS

        self.poke_count = 0

    def spawn_pokemon(self):
        nodes = self.grid.grid_locs
        node_weights = [i.weight for i in nodes.values()]
        node_names = [n.name for n in nodes.values()]
        # this chooses with replacement from all nodes on the grid weighted by their respective weights
        # the returned value is the name of the node in a list eg ['A1']
        choice = random.choices(population=node_names, weights=node_weights)

        curr_time = pygame.time.get_ticks()
        new_poke = Pokemon(poke_points(), node=nodes[choice[0]], count=self.poke_count, spawn_time=curr_time)
        self.poke_count += 1

        # print('----------------------------')
        # print('spawning a poke')
        # print('at node: ' + choice[0])
        # print('value: ' + str(new_poke.points))
        # print('count: ' + str(self.poke_count))
        # print('start: ' + str(new_poke.life_start))
        # print('death at: ' + str(new_poke.life_start + 15 / TIME_SCALE))
        new_poke.current_node.print_data()

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
                    # print('walking...')
                if event.type == player_can_walk_event:
                    self.player.can_walk = True
                    # print('player can move again')

            pokes_hit_list = pygame.sprite.spritecollide(self.player, self.pokes_list, True)
            for poke in pokes_hit_list:
                self.player.points += poke.points
                print(self.player.points)

            self.all_sprites_list.update()
            self.screen.blit(self.background, (0, 0))
            self.all_sprites_list.draw(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
