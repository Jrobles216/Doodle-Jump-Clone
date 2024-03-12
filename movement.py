import math
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

CANVAS_DIMS = (400, 600)

class Vector:

    # Initialiser
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    # Returns a string representation of the vector
    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    # Tests the equality of this vector and another
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Tests the inequality of this vector and another
    def __ne__(self, other):
        return not self.__eq__(other)

    # Returns a tuple with the point corresponding to the vector
    def get_p(self):
        return (self.x, self.y)

    # Returns a copy of the vector
    def copy(self):
        return Vector(self.x, self.y)

    # Adds another vector to this vector
    def add(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __add__(self, other):
        return self.copy().add(other)

    # Negates the vector (makes it point in the opposite direction)
    def negate(self):
        return self.multiply(-1)

    def __neg__(self):
        return self.copy().negate()

    # Subtracts another vector from this vector
    def subtract(self, other):
        return self.add(-other)

    def __sub__(self, other):
        return self.copy().subtract(other)

    # Multiplies the vector by a scalar
    def multiply(self, k):
        self.x *= k
        self.y *= k
        return self

    def __mul__(self, k):
        return self.copy().multiply(k)

    def __rmul__(self, k):
        return self.copy().multiply(k)

    # Divides the vector by a scalar
    def divide(self, k):
        return self.multiply(1/k)

    def __truediv__(self, k):
        return self.copy().divide(k)

    # Normalizes the vector
    def normalize(self):
        return self.divide(self.length())

    # Returns a normalized version of the vector
    def get_normalized(self):
        return self.copy().normalize()

    # Returns the dot product of this vector with another one
    def dot(self, other):
        return self.x * other.x + self.y * other.y

    # Returns the length of the vector
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    # Returns the squared length of the vector
    def length_squared(self):
        return self.x**2 + self.y**2

    # Reflect this vector on a normal
    def reflect(self, normal):
        n = normal.copy()
        n.multiply(2*self.dot(normal))
        self.subtract(n)
        return self

    # Returns the angle between this vector and another one
    def angle(self, other):
        return math.acos(self.dot(other) / (self.length() * other.length()))

    # Rotates the vector 90 degrees anticlockwise
    def rotate_anti(self):
        self.x, self.y = -self.y, self.x
        return self

    # Rotates the vector according to an angle theta given in radians
    def rotate_rad(self, theta):
        rx = self.x * math.cos(theta) - self.y * math.sin(theta)
        ry = self.x * math.sin(theta) + self.y * math.cos(theta)
        self.x, self.y = rx, ry
        return self

    # Rotates the vector according to an angle theta given in degrees
    def rotate(self, theta):
        theta_rad = theta / 180 * math.pi
        return self.rotate_rad(theta_rad)
    
    # project the vector onto a given vector
    def get_proj(self, vec):
        unit = vec.get_normalized()
        return unit.multiply(self.dot(unit))
    
class Wheel:
    def __init__(self, pos, radius,idle,width,height,jumpRight,jumpLeft,runRight,runLeft):
        self.pos = pos
        self.vel = Vector()
        self.radius = radius
        self.idle = idle
        self.width = width
        self.height = height
        self.frame_rate = 0
        self.index = 0
        self.jumpRight = jumpRight
        self.jumpLeft = jumpLeft
        self.runRight = runRight
        self.runLeft = runLeft

    def on_ground(self):
        for platform in platforms:
            if platform.intersects(self.pos,self.radius):
                return True
        # REMOVE THIS IF STATEMENT AFTER ADDING PLATFORM GENERATION    
        if self.pos.y == CANVAS_DIMS[1] - self.radius:
            return True
        # KEEP THIS ELSE STATEMENT AFTER ADDING PLATFORM GENERATION
        else:
            return False

    def draw(self, canvas):
        self.frame_rate += 1

        if self.frame_rate % 5 == 0:
            self.index += 1

        if self.index == 15:
                self.index = 0

        image_center = (self.width / 2, self.height / 2)
        image_size = (self.width, self.height)
        image_position = self.pos.get_p()
        image_radius = (self.radius * 2.5, self.radius * 2.5)

        if self.on_ground() == False:
            if self.vel.x < 0:
                canvas.draw_image(self.jumpLeft[self.index], image_center, image_size, image_position, image_radius)
            else:
                canvas.draw_image(self.jumpRight[self.index], image_center, image_size, image_position, image_radius)
        elif self.vel.x != 0:
            if self.vel.x > 0:
                canvas.draw_image(self.runRight[self.index], image_center, image_size, image_position, image_radius)
            elif self.vel.x < 0:
                canvas.draw_image(self.runLeft[self.index], image_center, image_size, image_position, image_radius)
        else:
            canvas.draw_image(self.idle[self.index], image_center, image_size, image_position, image_radius)
        
        
    def update(self):
        self.pos.add(self.vel)
        self.vel.multiply(0.8)

        # X AXIS PLAYER WRAP AROUND 
        if self.pos.x > CANVAS_DIMS[0] + self.radius:
            self.pos.x = -self.radius
        if self.pos.x < -self.radius:
            self.pos.x = CANVAS_DIMS[0] + self.radius

        # Y AXIS GRAVITY ON PLAYER
        if self.pos.y < CANVAS_DIMS[1] - self.radius or self.vel.y <= 0:
            self.vel.subtract(Vector(0, -0.5))
        # POSSIBLY REMOVE THIS ELIF
        elif self.pos.y > CANVAS_DIMS[1] - self.radius:
            self.pos.y = CANVAS_DIMS[1] - self.radius
        
        # CALCULATES IF THE PLAYER INTERSECTS ANY OF THE PLATFORMS
        for platform in platforms:
            if platform.intersects(self.pos, self.radius):
                closest_point = platform.closest_point_on_segment(self.pos)
                normal = (self.pos - closest_point).get_normalized()
                self.pos = closest_point + normal.multiply(self.radius)

class Keyboard:
    def __init__(self):
        self.right = False
        self.left = False
        self.space = False

    def keyDown(self, key):
        if key == simplegui.KEY_MAP['right'] or key == simplegui.KEY_MAP['d']:
            self.right = True
        
        if key == simplegui.KEY_MAP['left'] or key == simplegui.KEY_MAP['a']:
            self.left = True

        if key == simplegui.KEY_MAP['space']:
            self.space = True

    def keyUp(self, key):
        if key == simplegui.KEY_MAP['right'] or key == simplegui.KEY_MAP['d']:
            self.right = False

        if key == simplegui.KEY_MAP['left'] or key == simplegui.KEY_MAP['a']:
            self.left = False

        if key == simplegui.KEY_MAP['space']:
            self.space = False

class Interaction:
    def __init__(self, wheel, keyboard):
        self.wheel = wheel
        self.keyboard = keyboard
        self.count = 0
        self.jump = False

    def update(self):
        # MOVE RIGHT
        if self.keyboard.left and self.keyboard.right:
            self.wheel.vel.x = 0
        elif self.keyboard.right:
            self.wheel.vel.add(Vector(0.5, 0))
        elif self.keyboard.left:
            self.wheel.vel.add(Vector(-0.5, 0))
        else:
            self.wheel.vel.x = 0

        if self.wheel.on_ground():
            # AUTO JUMP TO BE ADDED AFTER COMBINING - Remove the space bar keybind when doing this
            if self.count >= 50:
                self.jump = True
            else:
                self.count += 1

            if self.jump == True and self.keyboard.space:
                self.wheel.vel.add(Vector(0, -40 ))
                self.count = 0
                self.jump = False
            

class Platform:
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.line_colour = 'black'

    def draw(self, canvas):
        canvas.draw_line(self.start_pos.get_p(), self.end_pos.get_p(), 5, self.line_colour)

    # CALCULATES IF THE PLAYER WILL INTERSECT WITH THE PLATFORM POSITION
    def intersects(self, point, radius):
        line_vec = self.end_pos - self.start_pos
        point_to_start = point - self.start_pos

        line_length_squared = line_vec.length_squared()
        dot_product = point_to_start.dot(line_vec)

        t = max(0, min(dot_product / line_length_squared, 1))

        closest_point = self.start_pos + line_vec.multiply(t)

        distance_squared = (point - closest_point).length_squared()

        return distance_squared <= radius ** 2

    # CALCUATES THE NEAREST POINT ON THE PLATFORM FOR THE BALL TO LAND ON
    def closest_point_on_segment(self, point):
        line_vec = self.end_pos - self.start_pos
        point_to_start = point - self.start_pos

        line_length_squared = line_vec.length_squared()
        dot_product = point_to_start.dot(line_vec)

        t = max(0, min(dot_product / line_length_squared, 1))

        closest_point = self.start_pos + line_vec.multiply(t)

        return closest_point


def draw(canvas):
    inter.update()
    wheel.update()
    wheel.draw(canvas)

    for platform in platforms:
        platform.draw(canvas)

idle = [simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(1).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(2).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(3).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(4).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(5).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(6).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(7).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(8).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(9).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(10).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(11).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(12).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(13).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(14).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Idle(15).png")
       ]

jumpRight = [simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(1).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(2).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(3).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(4).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(5).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(6).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(7).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(8).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(9).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(10).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(11).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(12).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(13).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(14).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Jump(15).png")
       ]

jumpLeft = [simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(1).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(2).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(3).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(4).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(5).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(6).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(7).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(8).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(9).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(10).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(11).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(12).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(13).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(14).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/JumpLeft(15).png")
       ]

runRight = [simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(1).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(2).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(3).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(4).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(5).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(6).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(7).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(8).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(9).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(10).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(11).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(12).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(13).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(14).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/Run(15).png")
       ]

runLeft = [simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(1).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(2).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(3).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(4).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(5).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(6).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(7).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(8).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(9).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(10).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(11).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(12).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(13).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(14).png"),
       simplegui.load_image("https://www.cs.rhul.ac.uk/home/zlac385/cs1822/RunLeft(15).png")
       ]

kbd = Keyboard()
wheel = Wheel(Vector(CANVAS_DIMS[0]/2, CANVAS_DIMS[1]-40), 20, idle, 614, 564,jumpRight,jumpLeft,runRight,runLeft)
inter = Interaction(wheel,kbd)

# BASIC PLATFORM GENERATION TO TEST PLATFORM JUMPING
p = Platform(Vector(100, CANVAS_DIMS[1]-50), Vector(300, CANVAS_DIMS[1]-50))
platforms = [p]
initial_height = CANVAS_DIMS[1]-50
for i in range(0,3):
    initial_height -= 100
    platforms.append(Platform(Vector(100, initial_height), Vector(300, initial_height)))

frame = simplegui.create_frame("Doodle Jump", CANVAS_DIMS[0], CANVAS_DIMS[1])
frame.set_canvas_background('#87CEEB')

frame.set_draw_handler(draw)
frame.set_keydown_handler(kbd.keyDown)
frame.set_keyup_handler(kbd.keyUp)

frame.start()