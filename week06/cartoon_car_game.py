#!/usr/bin/env python3
"""
Cartoon Car Audio Game - Simple Voice Controlled Driving
- High voice/loud sound: Move LEFT
- Low voice/quiet sound: Move RIGHT
- Avoid obstacles on the road
- Pure visual game with cartoon-style graphics
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.patches import Circle, Polygon
import random
import time
import sys

class CartoonCarGame:
    def __init__(self):
        # Audio parameters
        self.RATE = 44100
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        
        # Game dimensions
        self.ROAD_WIDTH = 8
        self.ROAD_HEIGHT = 12
        self.CAR_SIZE = 0.6
        self.OBSTACLE_SIZE = 0.5
        
        # Game state
        self.car_x = self.ROAD_WIDTH / 2  # Car X position
        self.car_y = 2  # Car Y position (fixed)
        self.obstacles = []
        self.road_markings = []
        self.score = 0
        self.game_over = False
        self.game_speed = 0.15
        
        # Audio control
        self.volume_threshold = 0.003
        self.movement_speed = 0.12
        self.last_volumes = []  # Track volume history
        
        # Visual elements
        self.trees = []
        self.clouds = []
        
        # Initialize
        self.setup_audio()
        self.setup_graphics()
        self.create_scenery()
        
    def setup_audio(self):
        """Initialize audio input"""
        self.p = pyaudio.PyAudio()
        
        print("🎮 Initializing audio...")
        input_device = None
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_device = i
                print(f"Found audio device: {device_info['name']}")
                break
        
        if input_device is None:
            print("❌ No audio input device found!")
            sys.exit(1)
        
        try:
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=input_device
            )
            print("✅ Audio stream ready!")
        except Exception as e:
            print(f"❌ Audio setup failed: {e}")
            sys.exit(1)
    
    def setup_graphics(self):
        """Setup the game window"""
        self.fig, self.ax = plt.subplots(figsize=(10, 12))
        self.ax.set_xlim(0, self.ROAD_WIDTH)
        self.ax.set_ylim(0, self.ROAD_HEIGHT)
        self.ax.set_aspect('equal')
        self.ax.axis('off')  # Remove axes for clean look
        
        # Set background color (sky blue)
        self.fig.patch.set_facecolor('#87CEEB')
        self.ax.set_facecolor('#87CEEB')
        
        plt.tight_layout()
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    
    def create_scenery(self):
        """Create background scenery"""
        # Draw road
        road_left = self.ROAD_WIDTH * 0.2
        road_right = self.ROAD_WIDTH * 0.8
        road_patch = patches.Rectangle(
            (road_left, 0), road_right - road_left, self.ROAD_HEIGHT,
            facecolor='#404040', edgecolor='none'
        )
        self.ax.add_patch(road_patch)
        
        # Road markings (dashed lines)
        center_x = self.ROAD_WIDTH / 2
        for y in range(0, int(self.ROAD_HEIGHT) + 2, 1):
            marking = patches.Rectangle(
                (center_x - 0.05, y), 0.1, 0.4,
                facecolor='white', edgecolor='none'
            )
            self.road_markings.append(marking)
            self.ax.add_patch(marking)
        
        # Create trees on sides
        for i in range(8):
            # Left side trees
            tree_x = random.uniform(0.2, road_left - 0.3)
            tree_y = random.uniform(1, self.ROAD_HEIGHT - 1)
            self.create_tree(tree_x, tree_y)
            
            # Right side trees
            tree_x = random.uniform(road_right + 0.3, self.ROAD_WIDTH - 0.2)
            tree_y = random.uniform(1, self.ROAD_HEIGHT - 1)
            self.create_tree(tree_x, tree_y)
        
        # Create clouds
        for i in range(4):
            cloud_x = random.uniform(0.5, self.ROAD_WIDTH - 0.5)
            cloud_y = random.uniform(self.ROAD_HEIGHT * 0.7, self.ROAD_HEIGHT - 0.5)
            self.create_cloud(cloud_x, cloud_y)
        
        # Create cartoon car
        self.create_car()
        
        # Game info text
        self.score_text = self.ax.text(
            0.1, self.ROAD_HEIGHT - 0.3, f'Score: {self.score}', 
            fontsize=16, fontweight='bold', color='white',
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.7)
        )
        
        self.control_text = self.ax.text(
            0.1, self.ROAD_HEIGHT - 0.8, 'LOUD = LEFT\nQUIET = RIGHT', 
            fontsize=12, fontweight='bold', color='yellow',
            bbox=dict(boxstyle='round', facecolor='darkgreen', alpha=0.8)
        )
    
    def create_tree(self, x, y):
        """Create a cartoon tree"""
        # Tree trunk
        trunk = patches.Rectangle(
            (x - 0.05, y - 0.2), 0.1, 0.4,
            facecolor='#8B4513', edgecolor='none'
        )
        self.ax.add_patch(trunk)
        
        # Tree leaves (circle)
        leaves = Circle((x, y + 0.1), 0.15, 
                       facecolor='#228B22', edgecolor='#006400', linewidth=1)
        self.ax.add_patch(leaves)
        
        self.trees.append([trunk, leaves])
    
    def create_cloud(self, x, y):
        """Create a cartoon cloud"""
        # Multiple circles for cloud effect
        cloud_parts = []
        for i, (dx, dy, size) in enumerate([(-0.1, 0, 0.12), (0.1, 0, 0.12), (0, 0.08, 0.1)]):
            cloud_part = Circle((x + dx, y + dy), size, 
                              facecolor='white', edgecolor='lightgray', linewidth=1, alpha=0.8)
            self.ax.add_patch(cloud_part)
            cloud_parts.append(cloud_part)
        
        self.clouds.append(cloud_parts)
    
    def create_car(self):
        """Create cartoon car"""
        car_x = self.car_x
        car_y = self.car_y
        
        # Car body (main rectangle)
        self.car_body = patches.Rectangle(
            (car_x - self.CAR_SIZE/2, car_y - self.CAR_SIZE/3),
            self.CAR_SIZE, self.CAR_SIZE * 0.67,
            facecolor='red', edgecolor='darkred', linewidth=2
        )
        self.ax.add_patch(self.car_body)
        
        # Car roof
        roof_width = self.CAR_SIZE * 0.7
        roof_height = self.CAR_SIZE * 0.3
        self.car_roof = patches.Rectangle(
            (car_x - roof_width/2, car_y),
            roof_width, roof_height,
            facecolor='darkred', edgecolor='black', linewidth=1
        )
        self.ax.add_patch(self.car_roof)
        
        # Car wheels
        wheel_radius = self.CAR_SIZE * 0.15
        self.wheel_left = Circle(
            (car_x - self.CAR_SIZE/3, car_y - self.CAR_SIZE/3), wheel_radius,
            facecolor='black', edgecolor='gray', linewidth=2
        )
        self.wheel_right = Circle(
            (car_x + self.CAR_SIZE/3, car_y - self.CAR_SIZE/3), wheel_radius,
            facecolor='black', edgecolor='gray', linewidth=2
        )
        self.ax.add_patch(self.wheel_left)
        self.ax.add_patch(self.wheel_right)
        
        # Car windows
        window_width = self.CAR_SIZE * 0.5
        window_height = self.CAR_SIZE * 0.2
        self.car_window = patches.Rectangle(
            (car_x - window_width/2, car_y + 0.05),
            window_width, window_height,
            facecolor='lightblue', edgecolor='black', linewidth=1
        )
        self.ax.add_patch(self.car_window)
    
    def create_obstacle(self, x, y):
        """Create a cartoon obstacle (another car)"""
        # Obstacle body
        obstacle_body = patches.Rectangle(
            (x - self.OBSTACLE_SIZE/2, y - self.OBSTACLE_SIZE/3),
            self.OBSTACLE_SIZE, self.OBSTACLE_SIZE * 0.67,
            facecolor='blue', edgecolor='darkblue', linewidth=2
        )
        self.ax.add_patch(obstacle_body)
        
        # Obstacle wheels
        wheel_radius = self.OBSTACLE_SIZE * 0.12
        wheel_left = Circle(
            (x - self.OBSTACLE_SIZE/3, y - self.OBSTACLE_SIZE/3), wheel_radius,
            facecolor='black', edgecolor='gray', linewidth=1
        )
        wheel_right = Circle(
            (x + self.OBSTACLE_SIZE/3, y - self.OBSTACLE_SIZE/3), wheel_radius,
            facecolor='black', edgecolor='gray', linewidth=1
        )
        self.ax.add_patch(wheel_left)
        self.ax.add_patch(wheel_right)
        
        return {
            'x': x, 'y': y,
            'body': obstacle_body,
            'wheel_left': wheel_left,
            'wheel_right': wheel_right
        }
    
    def analyze_audio(self):
        """Analyze audio and return movement direction"""
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.float32)
            
            # Calculate volume (RMS)
            volume = np.sqrt(np.mean(audio_data**2))
            
            # Keep track of recent volumes for smoothing
            self.last_volumes.append(volume)
            if len(self.last_volumes) > 5:
                self.last_volumes.pop(0)
            
            avg_volume = sum(self.last_volumes) / len(self.last_volumes)
            
            # Simple control: loud = left, quiet = right
            if avg_volume > self.volume_threshold:
                # LOUD sound = move LEFT
                movement = -self.movement_speed * min(avg_volume / self.volume_threshold, 3.0)
                direction = "LEFT (loud)"
            else:
                # QUIET = move RIGHT
                movement = self.movement_speed * 0.5
                direction = "RIGHT (quiet)"
            
            return movement, avg_volume, direction
            
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return 0, 0, "error"
    
    def update_car_position(self, movement):
        """Update car position"""
        self.car_x += movement
        
        # Keep car on road
        road_left = self.ROAD_WIDTH * 0.2 + self.CAR_SIZE/2
        road_right = self.ROAD_WIDTH * 0.8 - self.CAR_SIZE/2
        self.car_x = max(road_left, min(road_right, self.car_x))
        
        # Update car graphics
        car_x = self.car_x
        car_y = self.car_y
        
        self.car_body.set_x(car_x - self.CAR_SIZE/2)
        self.car_roof.set_x(car_x - self.CAR_SIZE*0.7/2)
        self.car_window.set_x(car_x - self.CAR_SIZE*0.5/2)
        self.wheel_left.center = (car_x - self.CAR_SIZE/3, car_y - self.CAR_SIZE/3)
        self.wheel_right.center = (car_x + self.CAR_SIZE/3, car_y - self.CAR_SIZE/3)
    
    def spawn_obstacle(self):
        """Spawn new obstacles"""
        if random.random() < 0.015:  # 1.5% chance per frame
            road_left = self.ROAD_WIDTH * 0.2 + self.OBSTACLE_SIZE/2
            road_right = self.ROAD_WIDTH * 0.8 - self.OBSTACLE_SIZE/2
            x = random.uniform(road_left, road_right)
            y = self.ROAD_HEIGHT + 1
            
            obstacle = self.create_obstacle(x, y)
            self.obstacles.append(obstacle)
    
    def update_obstacles(self):
        """Update obstacle positions"""
        obstacles_to_remove = []
        
        for obstacle in self.obstacles:
            # Move obstacle down
            obstacle['y'] -= self.game_speed * 15
            
            # Update graphics
            obstacle['body'].set_y(obstacle['y'] - self.OBSTACLE_SIZE/3)
            obstacle['wheel_left'].center = (
                obstacle['x'] - self.OBSTACLE_SIZE/3, 
                obstacle['y'] - self.OBSTACLE_SIZE/3
            )
            obstacle['wheel_right'].center = (
                obstacle['x'] + self.OBSTACLE_SIZE/3, 
                obstacle['y'] - self.OBSTACLE_SIZE/3
            )
            
            # Check if obstacle is off screen
            if obstacle['y'] < -1:
                obstacles_to_remove.append(obstacle)
                self.score += 10
            
            # Check collision
            if self.check_collision(obstacle):
                self.game_over = True
                print(f"💥 Game Over! Final Score: {self.score}")
        
        # Remove off-screen obstacles
        for obstacle in obstacles_to_remove:
            obstacle['body'].remove()
            obstacle['wheel_left'].remove()
            obstacle['wheel_right'].remove()
            self.obstacles.remove(obstacle)
    
    def check_collision(self, obstacle):
        """Check if car hits obstacle"""
        car_left = self.car_x - self.CAR_SIZE/2
        car_right = self.car_x + self.CAR_SIZE/2
        car_top = self.car_y + self.CAR_SIZE/3
        car_bottom = self.car_y - self.CAR_SIZE/3
        
        obs_left = obstacle['x'] - self.OBSTACLE_SIZE/2
        obs_right = obstacle['x'] + self.OBSTACLE_SIZE/2
        obs_top = obstacle['y'] + self.OBSTACLE_SIZE/3
        obs_bottom = obstacle['y'] - self.OBSTACLE_SIZE/3
        
        return (car_left < obs_right and car_right > obs_left and
                car_bottom < obs_top and car_top > obs_bottom)
    
    def update_road_markings(self):
        """Animate road markings to show movement"""
        for marking in self.road_markings:
            current_y = marking.get_y()
            new_y = current_y - self.game_speed * 20
            
            if new_y < -0.5:
                new_y = self.ROAD_HEIGHT + 0.5
            
            marking.set_y(new_y)
    
    def game_loop(self, frame):
        """Main game loop"""
        if self.game_over:
            # Show game over message
            if not hasattr(self, 'game_over_text'):
                self.game_over_text = self.ax.text(
                    self.ROAD_WIDTH/2, self.ROAD_HEIGHT/2,
                    f'GAME OVER!\nFinal Score: {self.score}\n\nClose window to exit',
                    ha='center', va='center', fontsize=18, fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle='round', facecolor='red', alpha=0.9, pad=1)
                )
            return
        
        # Get audio input and move car
        movement, volume, direction = self.analyze_audio()
        self.update_car_position(movement)
        
        # Update game elements
        self.spawn_obstacle()
        self.update_obstacles()
        self.update_road_markings()
        
        # Update score
        self.score += 1
        self.score_text.set_text(f'Score: {self.score}')
        
        # Increase difficulty gradually
        self.game_speed = min(0.4, 0.15 + self.score / 8000)
        
        # Update control indicator
        volume_bar = "█" * int(min(volume * 1000, 10))
        self.control_text.set_text(f'LOUD = LEFT\nQUIET = RIGHT\nVol: {volume_bar}\n{direction}')
    
    def start_game(self):
        """Start the game"""
        print("🏎️  Cartoon Car Audio Game!")
        print("=" * 40)
        print("🎤 Controls:")
        print("   LOUD sound = Move LEFT")
        print("   QUIET/Silent = Move RIGHT")
        print("   Avoid the blue cars!")
        print("   Close window to exit")
        print("=" * 40)
        
        try:
            ani = animation.FuncAnimation(
                self.fig, self.game_loop, interval=50,
                blit=False, cache_frame_data=False
            )
            plt.show()
        except KeyboardInterrupt:
            print("\n👋 Game interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        try:
            if hasattr(self, 'stream'):
                self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, 'p'):
                self.p.terminate()
        except Exception:
            pass
        print("✅ Cleanup complete!")


def main():
    """Main function"""
    print("🎮 Cartoon Car Audio Game")
    print("=" * 30)
    
    try:
        game = CartoonCarGame()
        game.start_game()
    except KeyboardInterrupt:
        print("\nGame interrupted")
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()