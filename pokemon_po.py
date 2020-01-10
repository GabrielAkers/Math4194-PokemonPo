import pygame
import random
import os
import math

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


def image_load(name):
    return pygame.image.load(name)


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
    # x = random.gauss(u, s)
    x = 3
    return math.floor(x)*1000


def poke_spawn_weights(x, y):
    # TODO: I'm just assigning random weights for now such that they sum to 1 (or pretty close)
    r = [random.random() for i in range(101)]
    s = sum(r)
    r = [i/s for i in r]
    z = x+10*(y-1)
    return r[z]


class Node:
    def __init__(self, name, x, y, weight):
        self.name = name
        self.x = x
        self.y = y
        self.weight = weight


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
    def __init__(self, points, x, y):
        super().__init__()
        # the poke sprites are 20x20 pixels and x,y are for top left corner
        self.x = x
        self.y = y
        self.points = points
        # life time remaining default is 15 sec
        self.time = 15
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

    def update_time(self, elapsed_time):
        # TODO: Finish this
        self.time = self.time - elapsed_time
        if self.time <= 0:
            self.time_up()

    def time_up(self):
        self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.step = 45
        self.image = image_load(PICS['PLAYER'])
        self.rect = self.image.get_rect()
        self.rect.left = x-12.5
        self.rect.top = y-12.5
        self.points = 0

    def move(self, key):
        if key == pygame.K_UP:
            # print("UP")
            if self.rect.top > 50:
                self.rect = self.rect.move(0, -self.step)
        elif key == pygame.K_DOWN:
            # print("DOWN")
            if self.rect.bottom < 450:
                self.rect = self.rect.move(0, self.step)
        elif key == pygame.K_RIGHT:
            # print("RIGHT")
            if self.rect.right < 450:
                self.rect = self.rect.move(self.step, 0)
        elif key == pygame.K_LEFT:
            # print("LEFT")
            if self.rect.left > 50:
                self.rect = self.rect.move(-self.step, 0)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Pokemon Po Sim")
        self.background = image_load(PICS['BACKGROUND'])
        self.logo = image_load(PICS['LOGO'])
        self.grid = Grid()
        spawn_key = random.choice(list(self.grid.grid_locs.keys()))
        print(spawn_key)
        self.pokes_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.player = Player(self.grid.grid_locs[spawn_key].x, self.grid.grid_locs[spawn_key].y)
        self.all_sprites_list.add(self.player)

    def spawn_pokemon(self):
        print('spawning a poke')
        pop = self.grid.grid_locs
        weights = [i.weight for i in pop.values()]
        names = [n.name for n in pop.values()]
        choice = random.choices(population=names, weights=weights)
        print(choice[0])
        print((self.grid.grid_locs[choice[0]].x, self.grid.grid_locs[choice[0]].y))
        new_poke = Pokemon(poke_points(), self.grid.grid_locs[choice[0]].x, self.grid.grid_locs[choice[0]].y)
        print('value: ' + str(new_poke.points))
        self.pokes_list.add(new_poke)
        self.all_sprites_list.add(new_poke)
        pygame.time.set_timer(pygame.USEREVENT, poke_times(), True)

    def run(self):
        clock = pygame.time.Clock()
        # pokemon spawn timer
        pygame.time.set_timer(pygame.USEREVENT, poke_times(), True)
        play = True
        while play:
            # 30(?) fps
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.USEREVENT:
                    self.spawn_pokemon()
                if event.type == pygame.KEYDOWN:
                    self.player.move(event.key)
            pokes_hit_list = pygame.sprite.spritecollide(self.player, self.pokes_list, True)
            for poke in pokes_hit_list:
                self.player.points += poke.points
                print(self.player.points)
            self.screen.blit(self.background, (0, 0))
            # self.screen.blit(self.player.sprite, self.player.rect)
            self.all_sprites_list.draw(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
