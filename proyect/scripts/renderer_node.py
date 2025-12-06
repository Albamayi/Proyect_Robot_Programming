import rospy
import pygame
import math
from std_msgs.msg import String, Int32
from geometry_msgs.msg import Pose2D
from proyect.msg import MazeLayout, CollectibleArray, EnemyArray, ProjectileArray

class GameRenderer:
    def __init__(self):
        rospy.init_node('renderer_node', anonymous=False)
        
        # Configuración de pantalla
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.CELL_SIZE = 40
        
        # Colores
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (50, 120, 200)
        self.RED = (255, 50, 50)
        self.GREEN = (50, 255, 50)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (100, 100, 100)
        self.DARK_GRAY = (50, 50, 50)
        self.CYAN = (0, 255, 255)
        self.ORANGE = (255, 165, 0)
        
        # Estado del juego
        self.game_state = "welcome"
        self.maze_layout = None
        self.player_pose = None
        self.collectibles = []
        self.enemies = []
        self.projectiles = []
        self.score = 0
        
        # Inicializar Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Maze Navigator - ROS Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Subscribers
        rospy.Subscriber('/game/state', String, self.state_callback)
        rospy.Subscriber('/maze/layout', MazeLayout, self.maze_callback)
        rospy.Subscriber('/player/pose', Pose2D, self.player_callback)
        rospy.Subscriber('/collectibles/positions', CollectibleArray, self.collectibles_callback)
        rospy.Subscriber('/enemies/positions', EnemyArray, self.enemies_callback)
        rospy.Subscriber('/projectiles/active', ProjectileArray, self.projectiles_callback)
        rospy.Subscriber('/game/score', Int32, self.score_callback)
        
        rospy.loginfo("Renderer Node Initialized")
    
    def state_callback(self, msg):
        self.game_state = msg.data
    
    def maze_callback(self, msg):
        self.maze_layout = msg
    
    def player_callback(self, msg):
        self.player_pose = msg
    
    def collectibles_callback(self, msg):
        self.collectibles = msg.collectibles
    
    def enemies_callback(self, msg):
        self.enemies = msg.enemies
    
    def projectiles_callback(self, msg):
        self.projectiles = msg.projectiles
    
    def score_callback(self, msg):
        self.score = msg.data
    
    def draw_maze(self):
        """Dibuja el laberinto"""
        if self.maze_layout is None:
            return
        
        for y in range(self.maze_layout.height):
            for x in range(self.maze_layout.width):
                idx = y * self.maze_layout.width + x
                if idx < len(self.maze_layout.walls) and self.maze_layout.walls[idx] == 1:
                    # Dibujar pared
                    rect = pygame.Rect(
                        x * self.CELL_SIZE,
                        y * self.CELL_SIZE,
                        self.CELL_SIZE,
                        self.CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, self.GRAY, rect)
                    pygame.draw.rect(self.screen, self.DARK_GRAY, rect, 2)
    
    def draw_player(self):
        """Dibuja el jugador como una nave espacial"""
        if self.player_pose is None:
            return
        
        # Convertir posición del laberinto a píxeles
        px = int(self.player_pose.x * self.CELL_SIZE + self.CELL_SIZE / 2)
        py = int(self.player_pose.y * self.CELL_SIZE + self.CELL_SIZE / 2)
        
        # Dibujar nave (triángulo apuntando en la dirección theta)
        size = 15
        angle = self.player_pose.theta
        
        # Calcular puntos del triángulo
        points = [
            (px + size * math.cos(angle), py + size * math.sin(angle)),  # Punta
            (px + size * math.cos(angle + 2.5), py + size * math.sin(angle + 2.5)),  # Izquierda
            (px + size * math.cos(angle - 2.5), py + size * math.sin(angle - 2.5))   # Derecha
        ]
        
        pygame.draw.polygon(self.screen, self.BLUE, points)
        pygame.draw.polygon(self.screen, self.CYAN, points, 2)
    
    def draw_collectibles(self):
        """Dibuja los objetos coleccionables"""
        for item in self.collectibles:
            if not item.collected:
                px = int(item.x * self.CELL_SIZE + self.CELL_SIZE / 2)
                py = int(item.y * self.CELL_SIZE + self.CELL_SIZE / 2)
                
                # Dibujar círculo amarillo (moneda/estrella)
                pygame.draw.circle(self.screen, self.YELLOW, (px, py), 8)
                pygame.draw.circle(self.screen, self.ORANGE, (px, py), 8, 2)
    
    def draw_enemies(self):
        """Dibuja los enemigos"""
        for enemy in self.enemies:
            if enemy.state == "patrolling":
                px = int(enemy.x * self.CELL_SIZE + self.CELL_SIZE / 2)
                py = int(enemy.y * self.CELL_SIZE + self.CELL_SIZE / 2)
                
                # Dibujar enemigo como círculo rojo
                pygame.draw.circle(self.screen, self.RED, (px, py), 12)
                pygame.draw.circle(self.screen, (150, 0, 0), (px, py), 12, 2)
    
    def draw_projectiles(self):
        """Dibuja los proyectiles"""
        for proj in self.projectiles:
            px = int(proj.x * self.CELL_SIZE + self.CELL_SIZE / 2)
            py = int(proj.y * self.CELL_SIZE + self.CELL_SIZE / 2)
            
            # Dibujar proyectil como pequeño círculo verde
            pygame.draw.circle(self.screen, self.GREEN, (px, py), 4)
    
    def draw_hud(self):
        """Dibuja la interfaz de usuario (score, etc.)"""
        score_text = self.small_font.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Mostrar número de coleccionables
        collected_count = sum(1 for c in self.collectibles if c.collected)
        total_count = len(self.collectibles)
        items_text = self.small_font.render(f"Items: {collected_count}/{total_count}", True, self.WHITE)
        self.screen.blit(items_text, (10, 40))
    
    def draw_welcome_screen(self):
        """Dibuja la pantalla de bienvenida"""
        self.screen.fill(self.BLACK)
        
        title = self.font.render("MAZE NAVIGATOR", True, self.CYAN)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH / 2, 150))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "Use WASD or Arrow Keys to move",
            "Press SPACE to shoot",
            "Collect all items and avoid enemies!",
            "",
            "Press ENTER to start"
        ]
        
        y_offset = 250
        for instruction in instructions:
            text = self.small_font.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH / 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35
    
    def draw_game_over_screen(self):
        """Dibuja la pantalla de game over"""
        # Dibujar el juego de fondo semi-transparente
        self.draw_game()
        
        # Overlay oscuro
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("GAME OVER", True, self.RED)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH / 2, 200))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH / 2, 280))
        self.screen.blit(score_text, score_rect)
        
        restart = self.small_font.render("Press R to restart", True, self.WHITE)
        restart_rect = restart.get_rect(center=(self.WINDOW_WIDTH / 2, 350))
        self.screen.blit(restart, restart_rect)
    
    def draw_win_screen(self):
        """Dibuja la pantalla de victoria"""
        # Dibujar el juego de fondo semi-transparente
        self.draw_game()
        
        # Overlay oscuro
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("YOU WIN!", True, self.GREEN)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH / 2, 200))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH / 2, 280))
        self.screen.blit(score_text, score_rect)
        
        restart = self.small_font.render("Press R to restart", True, self.WHITE)
        restart_rect = restart.get_rect(center=(self.WINDOW_WIDTH / 2, 350))
        self.screen.blit(restart, restart_rect)
    
    def draw_game(self):
        """Dibuja el juego en estado de juego"""
        self.screen.fill(self.BLACK)
        self.draw_maze()
        self.draw_collectibles()
        self.draw_enemies()
        self.draw_projectiles()
        self.draw_player()
        self.draw_hud()
    
    def render(self):
        """Renderiza el frame actual según el estado del juego"""
        if self.game_state == "welcome":
            self.draw_welcome_screen()
        elif self.game_state == "playing" or self.game_state == "paused":
            self.draw_game()
            if self.game_state == "paused":
                pause_text = self.font.render("PAUSED", True, self.WHITE)
                pause_rect = pause_text.get_rect(center=(self.WINDOW_WIDTH / 2, self.WINDOW_HEIGHT / 2))
                self.screen.blit(pause_text, pause_rect)
        elif self.game_state == "game_over":
            self.draw_game_over_screen()
        elif self.game_state == "win":
            self.draw_win_screen()
        
        pygame.display.flip()
    
    def run(self):
        rate = rospy.Rate(30)  # 30 FPS
        while not rospy.is_shutdown():
            # Manejar eventos de Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rospy.signal_shutdown("Window closed")
                    return
            
            self.render()
            self.clock.tick(30)
            rate.sleep()
        
        pygame.quit()

if __name__ == '__main__':
    try:
        renderer = GameRenderer()
        renderer.run()
    except rospy.ROSInterruptException:
        pygame.quit()
