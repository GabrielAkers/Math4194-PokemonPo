import pygame
import sys
import random

# the width of this grid is actually slightly more than 400 pixels and each gridline is 44 pixels apart
# so we add a little extra to make it all work fine, trust me it just works
grid_sp = 45
grid_x = 10
grid_y = 10
# dict of locations of intersections by pixel as tuples
# eg grid_locs['A1'] returns (45, 45)
grid_locs = {}
T = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10}
for x in T:
    for y in range(1, grid_y+1):
        grid_locs[x+str(y)] = (T[x]*grid_sp, y*grid_sp)


def main():
    pygame.init()

    # loads
    logo = pygame.image.load("logo32x32.png")
    face = pygame.image.load("head.png")
    face_rect = face.get_rect()
    background = pygame.image.load("PokePo_map.png")

    pygame.display.set_icon(logo)
    pygame.display.set_caption("Pokemon Po")
    screen = pygame.display.set_mode((500, 500))

    screen.blit(background, (0, 0))
    # spawn player
    # pick a random location from the grid dict
    spawn_key = random.choice(list(grid_locs.keys()))
    print(spawn_key)
    spawn_x, spawn_y = grid_locs[spawn_key]
    face_rect.left = spawn_x-12.5
    face_rect.top = spawn_y-12.5
    screen.blit(face, face_rect)

    pygame.display.flip()

    while 1:
        # run game at f fps
        f = 10
        pygame.time.Clock().tick(f)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    print("UP")
                    if face_rect.top > 50:
                        face_rect = face_rect.move(0, -grid_sp)
                elif event.key == pygame.K_DOWN:
                    print("DOWN")
                    if face_rect.bottom < 450:
                        face_rect = face_rect.move(0, grid_sp)
                elif event.key == pygame.K_RIGHT:
                    print("RIGHT")
                    if face_rect.right < 450:
                        face_rect = face_rect.move(grid_sp, 0)
                elif event.key == pygame.K_LEFT:
                    print("LEFT")
                    if face_rect.left > 50:
                        face_rect = face_rect.move(-grid_sp, 0)
        screen.blit(background, (0, 0))
        screen.blit(face, face_rect)
        pygame.display.flip()


if __name__ == "__main__":
    main()
