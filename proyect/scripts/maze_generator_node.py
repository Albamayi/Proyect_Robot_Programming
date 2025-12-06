import rospy
from proyect.msg import MazeLayout
from geometry_msgs.msg import Point
from std_msgs.msg import String

class MazeGenerator:
    def __init__(self):
        rospy.init_node('maze_generator_node', anonymous=False)
        
        # Dimensiones del laberinto
        self.width = 20
        self.height = 15
        self.cell_size = 40  # píxeles
        
        # Publishers
        self.maze_pub = rospy.Publisher('/maze/layout', MazeLayout, queue_size=10, latch=True)
        
        # Subscriber al estado del juego
        rospy.Subscriber('/game/state', String, self.game_state_callback)
        
        # Generar laberinto inicial
        self.generate_maze()
        
        rospy.loginfo("Maze Generator Node Initialized")
    
    def generate_maze(self):
        """Genera un laberinto simple con paredes en los bordes y algunos obstáculos"""
        maze_msg = MazeLayout()
        maze_msg.width = self.width
        maze_msg.height = self.height
        
        # Inicializar todo como espacio libre (0)
        walls = [0] * (self.width * self.height)
        
        # Crear paredes en los bordes
        for x in range(self.width):
            walls[x] = 1  # Pared superior
            walls[x + (self.height - 1) * self.width] = 1  # Pared inferior
        
        for y in range(self.height):
            walls[y * self.width] = 1  # Pared izquierda
            walls[y * self.width + (self.width - 1)] = 1  # Pared derecha
        
        # Añadir algunos obstáculos internos (paredes simples)
        # Paredes verticales
        for y in range(3, 7):
            walls[5 + y * self.width] = 1
        
        for y in range(9, 13):
            walls[10 + y * self.width] = 1
        
        for y in range(3, 8):
            walls[15 + y * self.width] = 1
        
        # Paredes horizontales
        for x in range(7, 13):
            walls[x + 5 * self.width] = 1
        
        for x in range(3, 9):
            walls[x + 10 * self.width] = 1
        
        maze_msg.walls = walls
        
        # Posición inicial del jugador (esquina inferior izquierda, pero dentro del laberinto)
        maze_msg.player_start = Point(2.0, 2.0, 0.0)
        
        # Posición de salida (esquina superior derecha)
        maze_msg.exit_position = Point(self.width - 3.0, self.height - 3.0, 0.0)
        
        self.maze_pub.publish(maze_msg)
        rospy.loginfo(f"Maze generated: {self.width}x{self.height}")
    
    def game_state_callback(self, msg):
        # Regenerar el laberinto cuando se reinicia el juego
        if msg.data == "welcome":
            self.generate_maze()
            rospy.loginfo("Maze regenerated for new game")
    
    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        generator = MazeGenerator()
        generator.run()
    except rospy.ROSInterruptException:
        pass
