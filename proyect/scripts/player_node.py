import rospy
import math
from geometry_msgs.msg import Pose2D, Twist
from std_msgs.msg import Int32, String
from proyect.msg import MazeLayout

class PlayerNode:
    def __init__(self):
        rospy.init_node('player_node', anonymous=False)
        
        # Posición y orientación del jugador
        self.x = 2.0
        self.y = 2.0
        self.theta = 0.0  # Orientación en radianes
        
        # Velocidad
        self.speed = 0.1  # Celdas por tick
        self.rotation_speed = 0.15
        
        # Salud
        self.health = 100
        
        # Laberinto
        self.maze_layout = None
        
        # Estado del juego
        self.game_state = "welcome"
        
        # Publishers
        self.pose_pub = rospy.Publisher('/player/pose', Pose2D, queue_size=10)
        self.health_pub = rospy.Publisher('/player/health', Int32, queue_size=10)
        
        # Subscribers
        rospy.Subscriber('/input/movement', Twist, self.movement_callback)
        rospy.Subscriber('/maze/layout', MazeLayout, self.maze_callback)
        rospy.Subscriber('/game/state', String, self.state_callback)
        
        rospy.loginfo("Player Node Initialized")
    
    def state_callback(self, msg):
        self.game_state = msg.data
        if msg.data == "playing" and self.maze_layout is not None:
            # Resetear posición al iniciar
            self.x = self.maze_layout.player_start.x
            self.y = self.maze_layout.player_start.y
            self.theta = 0.0
            self.health = 100
    
    def maze_callback(self, msg):
        self.maze_layout = msg
        self.x = msg.player_start.x
        self.y = msg.player_start.y
    
    def is_wall(self, x, y):
        """Verifica si una posición es una pared"""
        if self.maze_layout is None:
            return True
        
        # Convertir a índices del grid
        gx = int(round(x))
        gy = int(round(y))
        
        if gx < 0 or gx >= self.maze_layout.width or gy < 0 or gy >= self.maze_layout.height:
            return True
        
        idx = gy * self.maze_layout.width + gx
        if idx < len(self.maze_layout.walls):
            return self.maze_layout.walls[idx] == 1
        
        return True
    
    def movement_callback(self, msg):
        """Procesa comandos de movimiento"""
        if self.game_state != "playing":
            return
        
        # Rotación
        if msg.angular.z != 0:
            self.theta += msg.angular.z * self.rotation_speed
            # Normalizar ángulo
            self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
        
        # Movimiento hacia adelante/atrás
        if msg.linear.x != 0:
            # Calcular nueva posición
            new_x = self.x + msg.linear.x * self.speed * math.cos(self.theta)
            new_y = self.y + msg.linear.x * self.speed * math.sin(self.theta)
            
            # Verificar colisión con paredes
            if not self.is_wall(new_x, new_y):
                self.x = new_x
                self.y = new_y
    
    def publish_state(self):
        """Publica el estado actual del jugador"""
        pose_msg = Pose2D()
        pose_msg.x = self.x
        pose_msg.y = self.y
        pose_msg.theta = self.theta
        self.pose_pub.publish(pose_msg)
        
        health_msg = Int32()
        health_msg.data = self.health
        self.health_pub.publish(health_msg)
    
    def run(self):
        rate = rospy.Rate(30)
        while not rospy.is_shutdown():
            self.publish_state()
            rate.sleep()

if __name__ == '__main__':
    try:
        player = PlayerNode()
        player.run()
    except rospy.ROSInterruptException:
        pass
