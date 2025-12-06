import rospy
import pygame
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, String
from std_srvs.srv import Trigger

class InputNode:
    def __init__(self):
        rospy.init_node('input_node', anonymous=False)
        
        # Publishers
        self.movement_pub = rospy.Publisher('/input/movement', Twist, queue_size=10)
        self.shoot_pub = rospy.Publisher('/input/shoot', Bool, queue_size=10)
        
        # Estado del juego
        self.game_state = "welcome"
        rospy.Subscriber('/game/state', String, self.state_callback)
        
        # Servicios
        rospy.wait_for_service('/game/start')
        rospy.wait_for_service('/game/restart')
        self.start_service = rospy.ServiceProxy('/game/start', Trigger)
        self.restart_service = rospy.ServiceProxy('/game/restart', Trigger)
        
        # Inicializar pygame para capturar teclas
        pygame.init()
        
        rospy.loginfo("Input Node Initialized")
    
    def state_callback(self, msg):
        self.game_state = msg.data
    
    def process_input(self):
        """Procesa el input del teclado"""
        keys = pygame.key.get_pressed()
        
        # Comandos de juego
        if self.game_state == "welcome":
            if keys[pygame.K_RETURN]:
                try:
                    self.start_service()
                    rospy.loginfo("Start game service called")
                except rospy.ServiceException as e:
                    rospy.logerr(f"Service call failed: {e}")
        
        elif self.game_state == "game_over" or self.game_state == "win":
            if keys[pygame.K_r]:
                try:
                    self.restart_service()
                    rospy.loginfo("Restart game service called")
                except rospy.ServiceException as e:
                    rospy.logerr(f"Service call failed: {e}")
        
        elif self.game_state == "playing":
            # Movimiento
            twist = Twist()
            
            # WASD o flechas
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                twist.linear.x = 1.0
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                twist.linear.x = -1.0
            
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                twist.angular.z = 1.0
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                twist.angular.z = -1.0
            
            self.movement_pub.publish(twist)
            
            # Disparo
            if keys[pygame.K_SPACE]:
                shoot_msg = Bool()
                shoot_msg.data = True
                self.shoot_pub.publish(shoot_msg)
    
    def run(self):
        rate = rospy.Rate(30)  # 30 Hz
        while not rospy.is_shutdown():
            # Procesar eventos de pygame
            pygame.event.pump()
            
            self.process_input()
            rate.sleep()

if __name__ == '__main__':
    try:
        node = InputNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
