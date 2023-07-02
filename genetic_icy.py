import sys
import pygame
import random
import copy

GAME_FPS = 150
WIDTH, HEIGHT = 1000, 700
JUMPING_HEIGHT = 20
MAX_ACCELERATION = 13
VEL_X = 3  # Setting the moving speed.
VEL_Y = JUMPING_HEIGHT  # Setting the jumping height.
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
GAMEPLAY_SOUND_LENGTH = 31  # 31 seconds.
SHELVES_COUNT = 100  # Number of shelves in the game.
MAX_GENERATIONS = 10
MUTATION_RATE = 0.05

# Images:
BODY_IMAGE = pygame.image.load("Assets/body.png")
BACKGROUND = pygame.image.load("Assets/background.png")
BRICK_IMAGE = pygame.image.load("Assets/brick_block.png")
SHELF_BRICK_IMAGE = pygame.image.load("Assets/shelf_brick.png")

# Walls settings:
WALLS_Y = -128
WALL_WIDTH = 128
WALLS_ROLLING_SPEED = 2
RIGHT_WALL_BOUND = WIDTH - WALL_WIDTH
LEFT_WALL_BOUND = WALL_WIDTH

# Background settings:
BACKGROUND_WIDTH = WIDTH - 2 * WALL_WIDTH  # 2*64 is for two walls on the sides.
BACKGROUND_ROLLING_SPEED = 1
BACKGROUND_Y = HEIGHT - BACKGROUND.get_height()
background_y = BACKGROUND_Y


def setGlobals() :
    global WIDTH,HEIGHT,JUMPING_HEIGHT,MAX_ACCELERATION,VEL_X,VEL_Y,WIN,GAMEPLAY_SOUND_LENGTH,SHELVES_COUNT,WALLS_Y,WALL_WIDTH,WALLS_ROLLING_SPEED,BACKGROUND_WIDTH,BACKGROUND_ROLLING_SPEED,BACKGROUND_Y,background_y
    
    WIDTH, HEIGHT = 1000, 700
    JUMPING_HEIGHT = 30
    MAX_ACCELERATION = 13
    VEL_X = 3  # Setting the moving speed.
    VEL_Y = JUMPING_HEIGHT  # Setting the jumping height.
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    GAMEPLAY_SOUND_LENGTH = 31  # 31 seconds.
    SHELVES_COUNT = 500  # Number of shelves in the game.



    # Walls settings:
    WALLS_Y = -128
    WALL_WIDTH = 128
    WALLS_ROLLING_SPEED = 2
    

    # Background settings:
    BACKGROUND_WIDTH = WIDTH - 2 * WALL_WIDTH  # 2*64 is for two walls on the sides.
    BACKGROUND_ROLLING_SPEED = 1
    BACKGROUND_Y = HEIGHT - BACKGROUND.get_height()
    background_y = BACKGROUND_Y

# Booleans:


# Colors:
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
bodies = []

class Shelf:
    def __init__(self, number):
        self.number = number
        self.image = None
        self.width = random.randint(4, 7) * 32
        self.x = random.randint(LEFT_WALL_BOUND, RIGHT_WALL_BOUND - self.width)
        self.y = - number * 130 + HEIGHT - 25
        self.rect = pygame.Rect(self.x, self.y, self.width, 32)


class Body:
    def __init__(self):
        self.turn_chance = 0.5
        self.max_score = 0
        self.direction = ""
        self.turning_rate = 1
        self.max_turning_rate = 0
        self.jumping_rate= 1
        self.max_jumping_rate = 0
        self.speed = 3
        self.jumping = False
        self.falling = False
        self.standing = False
        self.rolling_down = False
        self.new_movement = False
        self.current_direction = None
        self.current_standing_shelf = None
        self.size = 64
        self.x = WIDTH / 2 - self.size / 2
        self.y = HEIGHT - 25 - self.size
        self.vel_y = 0
        self.acceleration = 0
        self.jumpable = self.vel_y <= 0  # If body is hitting a level, then it can jump only if the body is going down.



total_shelves_list = []
for num in range(0, SHELVES_COUNT + 1):  # Creating all the game shelves.
    new_shelf = Shelf(num)
    if num % 50 == 0:
        new_shelf.width = BACKGROUND_WIDTH
        new_shelf.rect.width = BACKGROUND_WIDTH
        new_shelf.x = WALL_WIDTH
        new_shelf.rect.x = WALL_WIDTH

    total_shelves_list.append(new_shelf)
reset_list = copy.deepcopy(total_shelves_list)
# Sounds:
JUMPING_SOUND = pygame.mixer.Sound("Assets/jumping_sound.wav")
GAMEPLAY_SOUND = pygame.mixer.Sound("Assets/gameplay_sound.wav")
HOORAY_SOUND = pygame.mixer.Sound("Assets/hooray_sound.wav")


def Move(body):  # Moving the body according to the wanted direction.
    
    if body.current_direction == "Left":
        if body.x - body.acceleration >= LEFT_WALL_BOUND:  # If the body isn't about to pass the left wall on the next step.
            body.x -= body.acceleration  # Take the step.
        else:  # If the body is about to pass the left wall on the next step.
            body.x = LEFT_WALL_BOUND  # Force it to stay inside.
    else:  # If direction is right
        if body.x + body.acceleration <= RIGHT_WALL_BOUND - body.size:  # If the body isn't about to pass the right wall on the next step.
            body.x += body.acceleration  # Take the step.
        else:  # If the body is about to pass the right wall on the next step.
            body.x = RIGHT_WALL_BOUND - body.size  # Force the body to stay inside.
    body.acceleration -= 1  # Decreasing body's movement speed.


def HandleMovement(body,key):  # Handling the Left/Right buttons pressing.
    if key == "Left" and body.x > LEFT_WALL_BOUND:  # If pressed "Left", and body is inside the bounding.
        body.current_direction = "Left"
        if body.acceleration + body.speed <= MAX_ACCELERATION:  # If body's movement speed isn't maxed.
            body.acceleration += body.speed  # Accelerating the body's movement speed.
        else:
            body.acceleration = MAX_ACCELERATION
    if key == "Right" and body.x < RIGHT_WALL_BOUND:  # If pressed "Right", and body is inside the bounding.
        body.current_direction = "Right"
        if body.acceleration + body.speed <= MAX_ACCELERATION:  # If body's movement speed isn't maxed.
            body.acceleration += body.speed  # Accelerating the body's movement speed.
        else:
            body.acceleration = MAX_ACCELERATION

display = None
def DrawWindow(bodies,start):  # Basically, drawing the screen.
    global WALLS_Y,display
    font = pygame.font.SysFont("Arial", 26)
    HandleBackground(MaxBody(bodies))
    for shelf in total_shelves_list:
        for x in range(shelf.rect.x, shelf.rect.x + shelf.width, 32):
            WIN.blit(SHELF_BRICK_IMAGE, (x, shelf.rect.y))  # Drawing the shelf.
            if shelf.number % 10 == 0 and shelf.number != 0:
                shelf_number = pygame.Rect(shelf.rect.x + shelf.rect.width / 2 - 16, shelf.rect.y,
                                           16 * len(str(shelf.number)), 25)
                pygame.draw.rect(WIN, GRAY, shelf_number)
                txt = font.render(str(shelf.number), True, BLACK)
                WIN.blit(txt,
                         (shelf.rect.x + shelf.rect.width / 2 - 16, shelf.rect.y))  # Drawing the number of the shelf.
    for y in range(WALLS_Y, HEIGHT, 108):  # Drawing the walls.
        WIN.blit(BRICK_IMAGE, (0, y))
        WIN.blit(BRICK_IMAGE, (WIDTH - WALL_WIDTH, y))
        for body in bodies :
            WIN.blit(BODY_IMAGE, (body.x, body.y))  # Drawing the body.
    pygame.display.update()
    if start == True :
        display = pygame.display


def OnShelf(body):  # Checking whether the body is on a shelf, returning True/False.
    global  BACKGROUND_ROLLING_SPEED
    if body.vel_y <= 0:  # Means the body isn't moving upwards, so now it's landing.
        for shelf in total_shelves_list:
            if body.y <= shelf.rect.y - body.size <= body.y - body.vel_y:  # If y values collide.shelf.rect.y - body.size >= body.y and shelf.rect.y - body.size <= body.y - body.vel_y
                if body.x + body.size * 2 / 3 >= shelf.rect.x and body.x + body.size * 1 / 3 <= shelf.rect.x + shelf.width:  # if x values collide.
                    body.y = shelf.rect.y - body.size
                    if shelf.number > body.max_score :
                            body.max_score = shelf.number
                    if body.current_standing_shelf != shelf.number and shelf.number % 50 == 0 and shelf.number != 0:
                        BACKGROUND_ROLLING_SPEED += 1  # Rolling speed increases every 50 shelves.
                        body.current_standing_shelf = shelf.number
                        
                    if shelf.number % 100 == 0 and shelf.number != 0:
                        HOORAY_SOUND.play()
                    if shelf.number == SHELVES_COUNT:
                        GameOver()
                    return True
    else:  # Means body in not on a shelf.
        body.jumping, body.standing, body.falling = False, False, True


def ScreenRollDown(body):  # Increasing the y values of all elements.
    global background_y, WALLS_Y
    for shelf in total_shelves_list:
        shelf.rect.y += 1
    body.y += 1
    background_y += 0.5
    if background_y == BACKGROUND_Y + 164:
        background_y = BACKGROUND_Y
    WALLS_Y += WALLS_ROLLING_SPEED
    if WALLS_Y == 0:
        WALLS_Y = -108


def GameOver():  # Quitting the game.
    pygame.quit()
    sys.exit(1)

dead_generation = []
def CheckIfTouchingFloor(body):  # Checking if the body is still on the main ground.
 
    if body.y > HEIGHT - body.size:
        if not body.rolling_down:  # Still on the starting point of the game, can't lose yet.
            body.y = HEIGHT - body.size
            body.standing, body.falling = True, False
        else:  # In a more advanced part of the game, when can already lose.
            
            dead_generation.append(copy.deepcopy(body))
            bodies.remove(body)


def HandleBackground(body): # Drawing the background.
    if body.y >= total_shelves_list[100].rect.y:
        WIN.blit(BACKGROUND, (32, background_y))


def MaxBody(bodies):
    max = bodies[0]
    for body in bodies :
        if body.max_score > max.max_score :
            max = body
    return max


def create_initial_population(num):
    for i in range(num):
        body = Body()
        body.speed = random.randint(1, 5)
        body.max_turning_rate = random.randint(10, 50)
        body.max_jumping_rate = random.randint(5, 20)
        body.turning_chance = random.randint(0, 1)
        bodies.append(body)

def select_parents(population, num_parents):
    parents = []
    sorted_population = sorted(population, key=lambda x: x.max_score, reverse=True)
    print("-----")
    for p in sorted_population :
        print(p.max_score)
    print("-----")
    for i in range(num_parents):
        parents.append(sorted_population[i])
    return parents


def crossover(parent1, parent2):
    speed = parent1.speed if random.random() < 0.5 else parent2.speed
    jump = parent1.max_jumping_rate if random.random() < 0.5 else parent2.max_jumping_rate
    turn = parent1.max_turning_rate if random.random() < 0.5 else parent2.max_turning_rate
    chance = parent1.turning_chance if random.random() < 0.5 else parent2.turning_chance
    body = Body()
    body.speed = speed
    body.max_turning_rate = turn
    body.max_jumping_rate = jump
    body.turning_chance = chance
    return body

def mutate(child):
   

    if random.random() < MUTATION_RATE:
        child.speed = random.randint(1, 5)

    if random.random() < MUTATION_RATE:
        child.max_jumping_rate = random.randint(5, 20)

    if random.random() < MUTATION_RATE:
        child.max_turning_rate = random.randint(10, 50)

    if random.random() < MUTATION_RATE:
        child.turning_chance = random.randint(10, 50)

    return child

def generate_offspring(parents, numoffspring):
    offspring = []
    for _ in range(numoffspring):
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)
        child = crossover(parent1, parent2)
        child = mutate(child)
        offspring.append(child)
    return offspring

def main():  # Main function.
    global total_shelves_list ,VEL_Y, background_y,WALLS_Y,display,MAX_GENERATIONS,bodies
    game_running = True
    start = True
    create_initial_population(20)
    print("Rate--------")
    for b in bodies :
        print(b.max_turning_rate)
    print("Rate--------")
    paused = False
    sound_timer = 0
    music_played = False;
    for generation in range(MAX_GENERATIONS):
        setGlobals()        
        total_shelves_list = copy.deepcopy(reset_list)
        
        while game_running and not paused:
            if not bodies:
                parents = select_parents(dead_generation,5)
                bodies = generate_offspring(parents,17)
                bodies.extend(parents[:3])
                print("Rate--------")
                for b in bodies :
                    print(b.max_turning_rate)
                print("Rate--------")
                break
            DrawWindow(bodies,start)  # Draw shelves, body and background.
            start = False
            for body in bodies :
                on_ground = not body.rolling_down and body.y == HEIGHT - 25 - body.size
                if not music_played:
                    if sound_timer % (56 * GAMEPLAY_SOUND_LENGTH) == 0:  # 56 = Program loops count per second.
                        GAMEPLAY_SOUND.play()
                        music_played = True;
                    else:
                        music_played = False;
                sound_timer += 1
                if body.rolling_down:  # If screen should roll down.
                    if body == MaxBody(bodies) :
                        for _ in range(BACKGROUND_ROLLING_SPEED):
                            ScreenRollDown(MaxBody(bodies))
                if body.turning_rate == body.max_turning_rate :
                    chance = random.randint(0,1)
                    if chance > body.turning_chance :
                        body.direction = "Left"
                    else :
                        body.direction = "Right"

                    body.turning_rate = 0
                else :
                    body.turning_rate +=1
                HandleMovement(body,body.direction)
                if body.acceleration != 0:  # If there's any movement.
                    Move(body)
                
                if(body.standing or on_ground): 
                    if body.jumping_rate == body.max_jumping_rate : 
                        body.vel_y = VEL_Y  # Resets the body's jumping velocity.
                        body.jumping, body.standing, body.falling = True, False, False
                        body.jumping_rate = 0
                    else :
                        body.jumping_rate +=1
                if body.jumping and body.vel_y >= 0:  # Jumping up.
                    if body.vel_y == VEL_Y:  # First moment of the jump.
                        JUMPING_SOUND.play()
                    body.y -= body.vel_y
                    body.vel_y -= 1
                    if body.y <= HEIGHT / 5:  # If the body get to the top quarter of the screen.
                        for b in bodies :
                            b.rolling_down = True  
                        if body == MaxBody(bodies) :
                            for _ in range(20):  # Rolling 10 times -> Rolling faster, so he can't pass the top of the screen.
                                ScreenRollDown(MaxBody(bodies))
                    if not body.vel_y:  # Standing in the air.
                        body.jumping, body.standing, body.falling = False, False, True
                if body.falling:  # Falling down.
                    if OnShelf(body):  # Standing on a shelf.
                        #print("Standing...")
                        body.jumping, body.standing, body.falling = False, True, False
                    else:  # Not standing - keep falling down.
                        #print("Falling...")
                        body.y -= body.vel_y
                        body.vel_y -= 1
                CheckIfTouchingFloor(body)
                if body.standing and not OnShelf(body) and not on_ground:  # If falling from a shelf.
                    #print("Falling from shelf...")
                    body.vel_y = 0  # Falls slowly from the shelf and not as it falls at the end of a jumping.
                    body.standing, body.falling = False, True
                if body.acceleration == MAX_ACCELERATION - 1:  # While on max acceleration, getting a jumping height boost.
                    VEL_Y = JUMPING_HEIGHT + 5
                else:  # If not on max acceleration.
                    VEL_Y = JUMPING_HEIGHT  # Back to normal jumping height.

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
            pygame.time.Clock().tick(GAME_FPS)


if __name__ == "__main__":
    main()
