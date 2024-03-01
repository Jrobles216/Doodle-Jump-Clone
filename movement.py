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
    def __init__(self, pos, radius):
        self.pos = pos
        self.vel = Vector()
        self.radius = radius
        self.colour = 'green'
        self.line_colour = 'black'

    def on_ground(self):
        if self.pos.y == CANVAS_DIMS[1] - self.radius:
            return True
        else:
            return False

    def draw(self, canvas):
        canvas.draw_circle(self.pos.get_p(), self.radius, 1, self.line_colour, self.colour)
        
    def update(self):
        self.pos.add(self.vel)
        self.vel.multiply(0.8)

        if self.pos.x > CANVAS_DIMS[0] + self.radius:
            self.pos.x = -self.radius
        if self.pos.x < -self.radius:
            self.pos.x = CANVAS_DIMS[0] + self.radius

        if self.pos.y < CANVAS_DIMS[1] - self.radius:
            self.vel.subtract(Vector(0, -1))
        elif self.pos.y > CANVAS_DIMS[1] - self.radius:
            self.pos.y = CANVAS_DIMS[1] - self.radius
        
        if platform.intersects(self.pos, self.radius):
            # Collision detected, adjust position
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

    def update(self):
        if self.keyboard.right:
            self.wheel.vel.add(Vector(1, 0))

        if self.keyboard.left:
            self.wheel.vel.add(Vector(-1, 0))

        if self.wheel.on_ground():
            if self.keyboard.space:
                self.wheel.vel.add(Vector(0, -40))

class Platform:
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.line_colour = 'brown'

    def draw(self, canvas):
        canvas.draw_line(self.start_pos.get_p(), self.end_pos.get_p(), 5, self.line_colour)

    def intersects(self, point, radius):
        # Collision detection between a point (center of the wheel) and the line segment
        line_vec = self.end_pos - self.start_pos
        point_to_start = point - self.start_pos

        line_length_squared = line_vec.length_squared()
        dot_product = point_to_start.dot(line_vec)

        # Parametric value of the projection of the point onto the line segment
        t = max(0, min(dot_product / line_length_squared, 1))

        # Closest point on the line segment to the center of the wheel
        closest_point = self.start_pos + line_vec.multiply(t)

        # Calculate distance between the closest point and the center of the wheel
        distance_squared = (point - closest_point).length_squared()

        return distance_squared <= radius ** 2

    def closest_point_on_segment(self, point):
        line_vec = self.end_pos - self.start_pos
        point_to_start = point - self.start_pos

        line_length_squared = line_vec.length_squared()
        dot_product = point_to_start.dot(line_vec)

        # Parametric value of the projection of the point onto the line segment
        t = max(0, min(dot_product / line_length_squared, 1))

        # Closest point on the line segment to the given point
        closest_point = self.start_pos + line_vec.multiply(t)

        return closest_point


def draw(canvas):
    inter.update()
    wheel.update()
    wheel.draw(canvas)
    platform.draw(canvas)

kbd = Keyboard()
wheel = Wheel(Vector(CANVAS_DIMS[0]/2, CANVAS_DIMS[1]-40),20)
inter = Interaction(wheel,kbd)
platform = Platform(Vector(100, CANVAS_DIMS[1]-100), Vector(300, CANVAS_DIMS[1]-100))

frame = simplegui.create_frame("movement", CANVAS_DIMS[0], CANVAS_DIMS[1])
frame.set_canvas_background('#87CEEB')

frame.set_draw_handler(draw)
frame.set_keydown_handler(kbd.keyDown)
frame.set_keyup_handler(kbd.keyUp)

frame.start()