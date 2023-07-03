import sys
import pygame
import random
import copy
import numpy as np
from collections import deque
import tensorflow as tf
import pickle


GAME_FPS = 150
WIDTH, HEIGHT = 1000, 700
JUMPING_HEIGHT = 20
MAX_ACCELERATION = 13
VEL_X = 3  # Setting the moving speed.
VEL_Y = JUMPING_HEIGHT  # Setting the jumping height.
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
GAMEPLAY_SOUND_LENGTH = 31  # 31 seconds.
SHELVES_COUNT = 500  # Number of shelves in the game.

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

# Booleans:
gamma = 0.99
exploration_proba = 1
exploration_decreasing_decay = 0.001

min_exploration_proba = 0.01
# Colors:
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def setGlobals() :
    global WIDTH,HEIGHT,JUMPING_HEIGHT,MAX_ACCELERATION,VEL_X,VEL_Y,WIN,GAMEPLAY_SOUND_LENGTH,SHELVES_COUNT,WALLS_Y,WALL_WIDTH,WALLS_ROLLING_SPEED,BACKGROUND_WIDTH,BACKGROUND_ROLLING_SPEED,BACKGROUND_Y,background_y
    
    WIDTH, HEIGHT = 1000, 700
    JUMPING_HEIGHT = 20
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
        self.size = 64
        self.x = WIDTH / 2 - self.size / 2
        self.y = HEIGHT - 25 - self.size
        self.vel_y = 0
        self.acceleration = 0
        self.jumpable = self.vel_y <= 0  
        self.score = 0
        self.previous_score = 0
        self.jumping = False
        self.falling = False
        self.standing = False
        self.rolling_down = False
        self.new_movement = False
        self.current_direction = None
        self.current_standing_shelf = None
        self.max = 0
         
        
        action_size = 3


body = Body()

total_shelves_list = []
with open('shelves_data', 'rb') as file:
    total_shelves_list = pickle.load(file)
copy_shelves = copy.deepcopy(total_shelves_list)

# Sounds:
JUMPING_SOUND = pygame.mixer.Sound("Assets/jumping_sound.wav")
GAMEPLAY_SOUND = pygame.mixer.Sound("Assets/gameplay_sound.wav")
HOORAY_SOUND = pygame.mixer.Sound("Assets/hooray_sound.wav")


def Move(direction):  # Moving the body according to the wanted direction.
    if direction == "Left":
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


def HandleMovement(action):  # Handling the Left/Right buttons pressing.
    global body
    if action == "left" and body.x > LEFT_WALL_BOUND:  # If pressed "Left", and body is inside the bounding.
        body.current_direction = "Left"
        if body.acceleration + 3 <= MAX_ACCELERATION:  # If body's movement speed isn't maxed.
            body.acceleration += 3  # Accelerating the body's movement speed.
        else:
            body.acceleration = MAX_ACCELERATION
    if action == "right" and body.x < RIGHT_WALL_BOUND:  # If pressed "Right", and body is inside the bounding.
        body.current_direction = "Right"
        if body.acceleration + 3 <= MAX_ACCELERATION:  # If body's movement speed isn't maxed.
            body.acceleration += 3  # Accelerating the body's movement speed.
        else:
            body.acceleration = MAX_ACCELERATION


def DrawWindow():  # Basically, drawing the screen.
    global WALLS_Y
    font = pygame.font.SysFont("Arial", 26)
    HandleBackground()
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
    WIN.blit(BODY_IMAGE, (body.x, body.y))  # Drawing the body.
    pygame.display.update()


def OnShelf():  # Checking whether the body is on a shelf, returning True/False.
    global  BACKGROUND_ROLLING_SPEED 
    if body.vel_y <= 0:  # Means the body isn't moving upwards, so now it's landing.
        for shelf in total_shelves_list:
            if body.y <= shelf.rect.y - body.size <= body.y - body.vel_y:  # If y values collide.shelf.rect.y - body.size >= body.y and shelf.rect.y - body.size <= body.y - body.vel_y
                if body.x + body.size * 2 / 3 >= shelf.rect.x and body.x + body.size * 1 / 3 <= shelf.rect.x + shelf.width:  # if x values collide.
                    body.y = shelf.rect.y - body.size
                    body.score = shelf.number
                    body.previous_score = body.score
                    if shelf.number >= body.max:
                        body.max = shelf.number
                    #print(body.score)
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


def ScreenRollDown():  # Increasing the y values of all elements.
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

def Reset() :
    global body,total_shelves_list
    setGlobals()        
    total_shelves_list = copy.deepcopy(copy_shelves)
    body = Body()

def CheckIfTouchingFloor():  # Checking if the body is still on the main ground.
    global body
    if body.y > HEIGHT - body.size:
        if not body.rolling_down:  # Still on the starting point of the game, can't lose yet.
            body.y = HEIGHT - body.size
            body.standing, body.falling = True, False
        else:  # In a more advanced part of the game, when can already lose.
            body = None



def HandleBackground(): # Drawing the background.
    if body.y >= total_shelves_list[500].rect.y:
        WIN.blit(BACKGROUND, (32, background_y))
        
class QNetwork(tf.keras.Model):
    def __init__(self, action_size):
        super(QNetwork, self).__init__()
        self.action_size = action_size
        self.dense1 = tf.keras.layers.Dense(64, activation='relu')
        self.dense2 = tf.keras.layers.Dense(64, activation='relu')
        self.dense3 = tf.keras.layers.Dense(self.action_size)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        q_values = self.dense3(x)
        return q_values

    def get_config(self):
        return {'action_size': self.action_size}

    @classmethod
    def from_config(cls, config):
        return cls(**config)

action_size = 4
q_network = tf.keras.Sequential()
q_network.add(tf.keras.layers.Dense(124, activation='relu', input_shape=(6,)))
q_network.add(tf.keras.layers.Dense(124, activation='relu'))
q_network.add(tf.keras.layers.Dense(action_size))
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
action_mapping = {'jump':0,'left':1,'right':2,'stand':3}
q_network = model = tf.keras.models.load_model('q_network_saved_data')
q_network.compile(optimizer,loss='mean_squared_error')
memory = []
def learn():
    print("Learning...")
    random.shuffle(memory)
    num_elements = min(50, len(memory))
    batch_current_state = []
    batch_action = []
    batch_reward = []
    batch_next_state = []
    for _ in range(num_elements):
        item = memory.pop()
        current_state = item["current_state"]
        action = item["action"]
        reward = item["reward"]
        next_state = item["next_state"]

        batch_current_state.append(current_state)
        batch_action.append(action)
        batch_reward.append(reward)
        batch_next_state.append(next_state)

    batch_current_state = np.array(batch_current_state)
    batch_action_indices = [action_mapping[a] for a in batch_action]  # Convert actions to indices

    batch_reward = np.array(batch_reward)
    batch_next_state = np.array(batch_next_state)

    batch_current_state = np.squeeze(batch_current_state)
    batch_next_state = np.squeeze(batch_next_state)

    current_q_values = q_network.predict(batch_current_state)
    next_q_values = q_network.predict(batch_next_state)
    max_next_q_values = np.max(next_q_values, axis=1)

    target_q_values = batch_reward + gamma * max_next_q_values

    current_q_values[np.arange(num_elements), batch_action_indices] = target_q_values

    q_network.fit(batch_current_state, current_q_values, epochs=1, verbose=0)

def main():  
    global body,VEL_Y,gamma,exploration_proba
    game_running = True
    paused = False
    sound_timer = 0
    time = 0
    for i in range(100) :
        while game_running:
            current_state = tf.convert_to_tensor([list([body.x, body.y, body.score,body.standing,body.falling,body.jumping])])  # Convert current state to a tensor
            on_ground = not body.rolling_down and body.y == HEIGHT - 25 - body.size
            if sound_timer % (56 * GAMEPLAY_SOUND_LENGTH) == 0:  # 56 = Program loops count per second.
                GAMEPLAY_SOUND.play()
            sound_timer += 1
            if body.rolling_down:  # If screen should roll down.
                for _ in range(BACKGROUND_ROLLING_SPEED):
                    ScreenRollDown()
            DrawWindow()  
            if np.random.uniform(0, 1) < exploration_proba:    
                action = random.choice(['jump','left', 'right','stand'])
            else:
                q_values = q_network(current_state)  # Get Q-values from the Q-network
                print(q_values)
                action_index = tf.argmax(q_values[0]).numpy()  # Choose the action index with the highest Q-value
                print(tf.argmax(q_values[0]).numpy())
                action = list(action_mapping.keys())[action_index]  # Convert the action index to the corresponding string action
                
            print(exploration_proba)
            if action != "jump" :
                HandleMovement(action)  
                if body.acceleration != 0:  
                    Move(body.current_direction)
            if action == "jump" :
                if  (body.standing or on_ground):  # If enter "Space" and currently not in mid-jump.
                    body.vel_y = VEL_Y  # Resets the body's jumping velocity.
                    body.jumping, body.standing, body.falling = True, False, False
            if body.jumping and body.vel_y >= 0:  # Jumping up.
                if body.vel_y == VEL_Y:  # First moment of the jump.
                    JUMPING_SOUND.play()
                #print("Jumping...")
                body.y -= body.vel_y
                body.vel_y -= 1
                if body.y <= HEIGHT / 5:  
                    body.rolling_down = True  # Starts rolling down the screen.
                    for _ in range(10):  # Rolling 10 times -> Rolling faster, so he can't pass the top of the screen.
                        ScreenRollDown()
                if not body.vel_y:  # Standing in the air.
                    body.jumping, body.standing, body.falling = False, False, True
            if body.falling:  # Falling down.
                if OnShelf():  # Standing on a shelf.
                    #print("Standing...")
                    body.jumping, body.standing, body.falling = False, True, False
                else:  # Not standing - keep falling down.
                    #print("Falling...")
                    body.y -= body.vel_y
                    body.vel_y -= 1
            CheckIfTouchingFloor()
            if body == None :
                Reset()
                break
            if body.standing and not OnShelf() and not on_ground:  # If falling from a shelf.
                #print("Falling from shelf...")
                body.vel_y = 0  # Falls slowly from the shelf and not as it falls at the end of a jumping.
                body.standing, body.falling = False, True
            if body.acceleration == MAX_ACCELERATION - 1:  # While on max acceleration, getting a jumping height boost.
                VEL_Y = JUMPING_HEIGHT + 5
            else:  # If not on max acceleration.
                VEL_Y = JUMPING_HEIGHT  # Back to normal jumping height.

            
            next_state = tf.convert_to_tensor([list((body.x, body.y,body.score,body.standing,body.falling,body.jumping))])  
            reward = (body.score - body.previous_score) * 100
            #print(body.score/(body.y/100))
            if action == 'jump' and body.jumping:
                reward -= 1000
            if body.score > body.max:
                reward += 1000
            if action == "jump":
                if not body.jumping:
                    reward += 1000
            consecutive_right_steps = 0
            consecutive_no_action = 0
            consecutive_left_steps = 0 
            consecutive_no_progress = 0
            center_x = WIDTH / 2  # Calculate the center position on the x-axis

            distance_to_center = abs(body.x - center_x)


            penalty = 5  
            if not body.jumping and not body.falling:
                if action == "left":
                    reward -= distance_to_center * 3
                    if body.score > body.previous_score:
                        reward += (body.score - body.previous_score) * 100
                        consecutive_left_steps = 0  
                    else:
                        reward -= penalty * consecutive_left_steps + 10
                        consecutive_left_steps += 1
                if action == "right":
                    reward -= distance_to_center * 3
                    if body.score > body.previous_score:
                        reward += (body.score - body.previous_score) * 100
                        consecutive_right_steps = 0  
                    else:
                        reward -= penalty * consecutive_right_steps + 10
                        consecutive_right_steps += 1
                if action == "stand":
                    reward -= distance_to_center  * 10
                    if body.score > body.previous_score:
                        reward += (body.score - body.previous_score) * 100
                        consecutive_no_action = 0  
                    else:
                        print(reward)
                        reward -= penalty * consecutive_right_steps
                        consecutive_no_action += 1
            if body.score <= body.previous_score:
                consecutive_no_progress+=1
                reward-=10*consecutive_no_progress
                if body.jumping or body.falling:
                    reward-=10
            else:
                consecutive_no_progress = 0
            if body.falling:
                reward-=10
            if (body.jumping or body.falling) and (action == "left" or action == "right"):
                reward += 50
            memory.append({'current_state':current_state,'action':action,'reward':reward,'next_state':next_state})

            time+=1
            if time % 30 == 0:
                learn()

            exploration_proba = exploration_proba*0.9999
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_running = False
            pygame.time.Clock().tick(GAME_FPS)
    print("SAVING NETWORK")
    q_network.save('q_network_saved_data')
    print("NETWORK SAVED")

if __name__ == "__main__":
    main()