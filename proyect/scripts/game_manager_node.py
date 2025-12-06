import rospy
from std_msgs.msg import String, Int32, Bool
from std_srvs.srv import Trigger, TriggerResponse, SetBool, SetBoolResponse
from proyect.msg import LevelInfo

class GameManager:
    def __init__(self):
        rospy.init_node('game_manager_node', anonymous=False)
        
        # Estados del juego
        self.WELCOME = "welcome"
        self.PLAYING = "playing"
        self.PAUSED = "paused"
        self.WIN = "win"
        self.GAME_OVER = "game_over"
        
        self.current_state = self.WELCOME
        self.level_number = 1
        self.total_collectibles = 0
        self.collected_items = 0
        
        # Publishers
        self.state_pub = rospy.Publisher('/game/state', String, queue_size=10, latch=True)
        self.level_info_pub = rospy.Publisher('/game/level_info', LevelInfo, queue_size=10, latch=True)
        
        # Subscribers
        rospy.Subscriber('/collectibles/collected', Int32, self.collectible_callback)
        rospy.Subscriber('/collision/player_hit', Bool, self.player_hit_callback)
        rospy.Subscriber('/game/score', Int32, self.score_callback)
        
        # Services
        rospy.Service('/game/start', Trigger, self.start_game)
        rospy.Service('/game/restart', Trigger, self.restart_game)
        rospy.Service('/game/pause', SetBool, self.pause_game)
        
        # Publicar estado inicial
        self.publish_state()
        self.publish_level_info()
        
        rospy.loginfo("Game Manager Node Initialized - State: WELCOME")
    
    def publish_state(self):
        msg = String()
        msg.data = self.current_state
        self.state_pub.publish(msg)
        rospy.loginfo(f"Game State: {self.current_state}")
    
    def publish_level_info(self):
        msg = LevelInfo()
        msg.level_number = self.level_number
        msg.total_collectibles = self.total_collectibles
        msg.total_enemies = 3  # Fijo por ahora
        msg.time_limit = 0.0  # Sin límite de tiempo por ahora
        self.level_info_pub.publish(msg)
    
    def start_game(self, req):
        if self.current_state == self.WELCOME or self.current_state == self.GAME_OVER or self.current_state == self.WIN:
            self.current_state = self.PLAYING
            self.collected_items = 0
            self.publish_state()
            rospy.loginfo("Game Started!")
            return TriggerResponse(success=True, message="Game started successfully")
        return TriggerResponse(success=False, message="Cannot start game from current state")
    
    def restart_game(self, req):
        self.current_state = self.WELCOME
        self.collected_items = 0
        self.level_number = 1
        self.publish_state()
        self.publish_level_info()
        rospy.loginfo("Game Restarted!")
        
        # Pequeño delay y luego auto-start
        rospy.sleep(0.5)
        self.current_state = self.PLAYING
        self.publish_state()
        
        return TriggerResponse(success=True, message="Game restarted successfully")
    
    def pause_game(self, req):
        if req.data:  # Pausar
            if self.current_state == self.PLAYING:
                self.current_state = self.PAUSED
                self.publish_state()
                return SetBoolResponse(success=True, message="Game paused")
        else:  # Reanudar
            if self.current_state == self.PAUSED:
                self.current_state = self.PLAYING
                self.publish_state()
                return SetBoolResponse(success=True, message="Game resumed")
        return SetBoolResponse(success=False, message="Invalid pause state")
    
    def collectible_callback(self, msg):
        if self.current_state == self.PLAYING:
            self.collected_items += 1
            rospy.loginfo(f"Collected item! Total: {self.collected_items}/{self.total_collectibles}")
            
            # Verificar victoria
            if self.total_collectibles > 0 and self.collected_items >= self.total_collectibles:
                self.current_state = self.WIN
                self.publish_state()
                rospy.loginfo("🎉 YOU WIN! All collectibles obtained!")
    
    def player_hit_callback(self, msg):
        if msg.data and self.current_state == self.PLAYING:
            self.current_state = self.GAME_OVER
            self.publish_state()
            rospy.loginfo("💀 GAME OVER! Player hit by enemy!")
    
    def score_callback(self, msg):
        # Solo para logging por ahora
        pass
    
    def set_total_collectibles(self, total):
        self.total_collectibles = total
        self.publish_level_info()
    
    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            rate.sleep()

if __name__ == '__main__':
    try:
        manager = GameManager()
        manager.run()
    except rospy.ROSInterruptException:
        pass
