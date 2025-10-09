#!/usr/bin/env python3
"""
Enhanced Cartoon Car Audio Game
- Colorful cartoon graphics
- High voice = LEFT, Low voice = RIGHT
- Dynamic road and scenery
- Fun visual effects
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.patches import Circle, FancyBboxPatch
import random
import sys

class EnhancedCarGame:
    def __init__(self):
        # Audio setup
        self.RATE = 44100
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        
        # Game world
        self.WORLD_WIDTH = 10
        self.WORLD_HEIGHT = 14
        self.ROAD_LEFT = 2.5
        self.ROAD_RIGHT = 7.5
        
        # Game objects
        self.car_x = 5.0  # Center of road
        self.car_y = 2.5
        self.obstacles = []
        self.road_lines = []
        self.background_items = []
        
        # Game state
        self.score = 0
        self.game_over = False
        self.speed = 0.2
        self.car_tilt = 0  # For turning animation
        
        # Audio control (inverted as requested)
        self.volume_history = []
        self.movement_sensitivity = 0.15
        self.volume_threshold = 0.002
        
        # Colors
        self.colors = {
            'sky': '#87CEEB',
            'grass': '#32CD32',
            'road': '#404040',
            'car': '#FF4500',
            'obstacle': ['#4169E1', '#8A2BE2', '#FF1493', '#00CED1'],
            'trees': '#228B22',
            'flowers': ['#FF69B4', '#FFD700', '#FF6347']
        }
        
        self.setup_audio()
        self.setup_graphics()
        self.create_world()
    
    def setup_audio(self):
        """Initialize audio input"""
        self.p = pyaudio.PyAudio()
        
        print("🎵 Setting up audio...")
        
        # Find input device
        device_id = None
        for i in range(self.p.get_device_count()):
            device = self.p.get_device_info_by_index(i)
            if device['maxInputChannels'] > 0:
                device_id = i
                print(f"Using: {device['name']}")
                break
        
        if device_id is None:
            print("❌ No microphone found!")
            sys.exit(1)
        
        try:
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=1,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=device_id
            )
            print("✅ Microphone ready!")
        except Exception as e:
            print(f"❌ Audio error: {e}")
            sys.exit(1)
    
    def setup_graphics(self):
        """Create the game window"""
        plt.style.use('default')
        self.fig, self.ax = plt.subplots(figsize=(8, 10))
        self.ax.set_xlim(0, self.WORLD_WIDTH)
        self.ax.set_ylim(0, self.WORLD_HEIGHT)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Window styling
        self.fig.patch.set_facecolor(self.colors['sky'])
        self.ax.set_facecolor(self.colors['sky'])
        
        plt.tight_layout()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    def create_world(self):
        """Create the game world background"""
        # Grass on sides
        left_grass = patches.Rectangle(
            (0, 0), self.ROAD_LEFT, self.WORLD_HEIGHT,
            facecolor=self.colors['grass'], edgecolor='none'
        )
        right_grass = patches.Rectangle(
            (self.ROAD_RIGHT, 0), self.WORLD_WIDTH - self.ROAD_RIGHT, self.WORLD_HEIGHT,
            facecolor=self.colors['grass'], edgecolor='none'
        )
        self.ax.add_patch(left_grass)
        self.ax.add_patch(right_grass)
        
        # Road
        road = patches.Rectangle(
            (self.ROAD_LEFT, 0), self.ROAD_RIGHT - self.ROAD_LEFT, self.WORLD_HEIGHT,
            facecolor=self.colors['road'], edgecolor='none'
        )
        self.ax.add_patch(road)
        
        # Road center lines
        for y in range(-2, int(self.WORLD_HEIGHT) + 4, 1):
            line = patches.Rectangle(
                (self.WORLD_WIDTH/2 - 0.08, y), 0.16, 0.6,
                facecolor='yellow', edgecolor='none'
            )
            self.road_lines.append(line)
            self.ax.add_patch(line)
        
        # Trees and flowers
        self.create_scenery()
        
        # Create player car
        self.create_player_car()
        
        # UI Elements
        self.create_ui()
    
    def create_scenery(self):
        """Add trees and flowers to grass areas"""
        # Trees on left side
        for i in range(6):
            x = random.uniform(0.3, self.ROAD_LEFT - 0.3)
            y = random.uniform(1, self.WORLD_HEIGHT - 1)
            self.create_tree(x, y)
        
        # Trees on right side  
        for i in range(6):
            x = random.uniform(self.ROAD_RIGHT + 0.3, self.WORLD_WIDTH - 0.3)
            y = random.uniform(1, self.WORLD_HEIGHT - 1)
            self.create_tree(x, y)
        
        # Flowers scattered around
        for i in range(12):
            side = random.choice(['left', 'right'])
            if side == 'left':
                x = random.uniform(0.2, self.ROAD_LEFT - 0.2)
            else:
                x = random.uniform(self.ROAD_RIGHT + 0.2, self.WORLD_WIDTH - 0.2)
            y = random.uniform(0.5, self.WORLD_HEIGHT - 0.5)
            self.create_flower(x, y)
    
    def create_tree(self, x, y):
        """Create a cartoon tree"""
        # Trunk
        trunk = patches.Rectangle(
            (x - 0.05, y - 0.15), 0.1, 0.3,
            facecolor='#8B4513', edgecolor='none'
        )
        self.ax.add_patch(trunk)
        
        # Leaves (multiple circles for fullness)
        for dx, dy, size in [(-0.08, 0.1, 0.12), (0.08, 0.1, 0.12), (0, 0.15, 0.15)]:
            leaves = Circle((x + dx, y + dy), size,
                          facecolor=self.colors['trees'], 
                          edgecolor='darkgreen', linewidth=0.5)
            self.ax.add_patch(leaves)
    
    def create_flower(self, x, y):
        """Create a small colorful flower"""
        color = random.choice(self.colors['flowers'])
        flower = Circle((x, y), 0.08, facecolor=color, edgecolor='none')
        self.ax.add_patch(flower)
    
    def create_player_car(self):
        """Create the player's cartoon car"""
        # Main body with rounded corners
        self.car_body = FancyBboxPatch(
            (self.car_x - 0.35, self.car_y - 0.25),
            0.7, 0.5,
            boxstyle="round,pad=0.05",
            facecolor=self.colors['car'],
            edgecolor='darkred',
            linewidth=2
        )
        self.ax.add_patch(self.car_body)
        
        # Car roof
        self.car_roof = FancyBboxPatch(
            (self.car_x - 0.25, self.car_y - 0.1),
            0.5, 0.3,
            boxstyle="round,pad=0.03",
            facecolor='#B22222',
            edgecolor='black',
            linewidth=1
        )
        self.ax.add_patch(self.car_roof)
        
        # Windows
        self.car_window = FancyBboxPatch(
            (self.car_x - 0.2, self.car_y - 0.05),
            0.4, 0.2,
            boxstyle="round,pad=0.02",
            facecolor='lightblue',
            edgecolor='black',
            linewidth=1
        )
        self.ax.add_patch(self.car_window)
        
        # Wheels
        self.wheel1 = Circle((self.car_x - 0.2, self.car_y - 0.25), 0.08,
                           facecolor='black', edgecolor='gray', linewidth=2)
        self.wheel2 = Circle((self.car_x + 0.2, self.car_y - 0.25), 0.08,
                           facecolor='black', edgecolor='gray', linewidth=2)
        self.ax.add_patch(self.wheel1)
        self.ax.add_patch(self.wheel2)
        
        # Headlights
        self.light1 = Circle((self.car_x - 0.15, self.car_y + 0.2), 0.05,
                           facecolor='yellow', edgecolor='orange', linewidth=1)
        self.light2 = Circle((self.car_x + 0.15, self.car_y + 0.2), 0.05,
                           facecolor='yellow', edgecolor='orange', linewidth=1)
        self.ax.add_patch(self.light1)
        self.ax.add_patch(self.light2)
    
    def create_ui(self):
        """Create game UI elements"""
        # Score display
        self.score_text = self.ax.text(
            0.3, self.WORLD_HEIGHT - 0.5, f'Score: {self.score}',
            fontsize=14, fontweight='bold', color='white',
            bbox=dict(boxstyle='round', facecolor='navy', alpha=0.8)
        )
        
        # Control instructions
        self.control_text = self.ax.text(
            0.3, self.WORLD_HEIGHT - 1.2,
            'LOUD = LEFT ⬅️\nQUIET = RIGHT ➡️',
            fontsize=10, fontweight='bold', color='black',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.9)
        )
        
        # Volume indicator
        self.volume_indicator = self.ax.text(
            0.3, self.WORLD_HEIGHT - 2,
            'Volume: ||||||||',
            fontsize=9, color='green',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
    
    def create_obstacle_car(self, x, y):
        """Create an obstacle car"""
        color = random.choice(self.colors['obstacle'])
        
        # Car body
        body = FancyBboxPatch(
            (x - 0.3, y - 0.2), 0.6, 0.4,
            boxstyle="round,pad=0.03",
            facecolor=color, edgecolor='black', linewidth=1
        )
        self.ax.add_patch(body)
        
        # Wheels
        wheel1 = Circle((x - 0.15, y - 0.2), 0.06,
                       facecolor='black', edgecolor='gray', linewidth=1)
        wheel2 = Circle((x + 0.15, y - 0.2), 0.06,
                       facecolor='black', edgecolor='gray', linewidth=1)
        self.ax.add_patch(wheel1)
        self.ax.add_patch(wheel2)
        
        return {
            'x': x, 'y': y,
            'body': body,
            'wheel1': wheel1,
            'wheel2': wheel2
        }
    
    def get_audio_control(self):
        """Get movement from audio input"""
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.float32)
            
            # Calculate volume
            volume = np.sqrt(np.mean(audio**2))
            
            # Track volume history for smoothing
            self.volume_history.append(volume)
            if len(self.volume_history) > 8:
                self.volume_history.pop(0)
            
            avg_volume = sum(self.volume_history) / len(self.volume_history)
            
            # Control logic: HIGH volume = LEFT, LOW volume = RIGHT
            if avg_volume > self.volume_threshold:
                # LOUD = move LEFT
                strength = min(avg_volume / self.volume_threshold, 4.0)
                movement = -self.movement_sensitivity * strength
                direction = "LEFT"
                self.car_tilt = max(self.car_tilt - 0.1, -0.15)  # Tilt left
            else:
                # QUIET = move RIGHT  
                movement = self.movement_sensitivity * 0.7
                direction = "RIGHT"
                self.car_tilt = min(self.car_tilt + 0.1, 0.15)  # Tilt right
            
            return movement, avg_volume, direction
            
        except Exception as e:
            print(f"Audio error: {e}")
            return 0, 0, "ERROR"
    
    def update_car(self, movement):
        """Update car position and animation"""
        # Move car
        self.car_x += movement
        
        # Keep on road
        self.car_x = max(self.ROAD_LEFT + 0.4, min(self.ROAD_RIGHT - 0.4, self.car_x))
        
        # Update car graphics with tilt animation
        # Body
        self.car_body.set_x(self.car_x - 0.35)
        
        # Roof  
        self.car_roof.set_x(self.car_x - 0.25)
        
        # Window
        self.car_window.set_x(self.car_x - 0.2)
        
        # Wheels
        self.wheel1.center = (self.car_x - 0.2, self.car_y - 0.25)
        self.wheel2.center = (self.car_x + 0.2, self.car_y - 0.25)
        
        # Headlights
        self.light1.center = (self.car_x - 0.15, self.car_y + 0.2)
        self.light2.center = (self.car_x + 0.15, self.car_y + 0.2)
    
    def spawn_obstacles(self):
        """Create new obstacles"""
        if random.random() < 0.012:  # 1.2% chance per frame
            x = random.uniform(self.ROAD_LEFT + 0.3, self.ROAD_RIGHT - 0.3)
            y = self.WORLD_HEIGHT + 0.5
            obstacle = self.create_obstacle_car(x, y)
            self.obstacles.append(obstacle)
    
    def update_obstacles(self):
        """Move obstacles and check collisions"""
        to_remove = []
        
        for obs in self.obstacles:
            # Move down
            obs['y'] -= self.speed * 12
            
            # Update graphics
            obs['body'].set_y(obs['y'] - 0.2)
            obs['wheel1'].center = (obs['x'] - 0.15, obs['y'] - 0.2)
            obs['wheel2'].center = (obs['x'] + 0.15, obs['y'] - 0.2)
            
            # Remove if off screen
            if obs['y'] < -0.5:
                to_remove.append(obs)
                self.score += 15
            
            # Check collision
            elif self.check_collision(obs):
                self.game_over = True
                print(f"💥 CRASH! Final Score: {self.score}")
        
        # Clean up
        for obs in to_remove:
            obs['body'].remove()
            obs['wheel1'].remove()
            obs['wheel2'].remove()
            self.obstacles.remove(obs)
    
    def check_collision(self, obstacle):
        """Simple collision detection"""
        car_left = self.car_x - 0.35
        car_right = self.car_x + 0.35
        car_top = self.car_y + 0.25
        car_bottom = self.car_y - 0.25
        
        obs_left = obstacle['x'] - 0.3
        obs_right = obstacle['x'] + 0.3
        obs_top = obstacle['y'] + 0.2
        obs_bottom = obstacle['y'] - 0.2
        
        return (car_left < obs_right and car_right > obs_left and
                car_bottom < obs_top and car_top > obs_bottom)
    
    def update_road_animation(self):
        """Animate road markings"""
        for line in self.road_lines:
            current_y = line.get_y()
            new_y = current_y - self.speed * 15
            
            if new_y < -1:
                new_y = self.WORLD_HEIGHT + 1
            
            line.set_y(new_y)
    
    def game_loop(self, frame):
        """Main game update"""
        if self.game_over:
            if not hasattr(self, 'game_over_shown'):
                self.game_over_text = self.ax.text(
                    self.WORLD_WIDTH/2, self.WORLD_HEIGHT/2,
                    f'💥 GAME OVER! 💥\n\nFinal Score: {self.score}\n\nClose window to exit',
                    ha='center', va='center', fontsize=16, fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle='round', facecolor='red', alpha=0.95, pad=1)
                )
                self.game_over_shown = True
            return
        
        # Get input and move car
        movement, volume, direction = self.get_audio_control()
        self.update_car(movement)
        
        # Update game world
        self.spawn_obstacles()
        self.update_obstacles()
        self.update_road_animation()
        
        # Update UI
        self.score += 1
        self.score_text.set_text(f'Score: {self.score}')
        
        # Volume visualization
        volume_bars = "█" * int(min(volume * 2000, 10))
        self.volume_indicator.set_text(f'Volume: {volume_bars}\nMoving: {direction}')
        
        # Increase difficulty
        self.speed = min(0.5, 0.2 + self.score / 5000)
    
    def start(self):
        """Start the game"""
        print("🏎️  Enhanced Cartoon Car Game!")
        print("=" * 40)
        print("🎤 Make LOUD sounds to go LEFT")
        print("🔇 Stay QUIET to go RIGHT")
        print("🚗 Avoid the colorful cars!")
        print("🏆 Score points by surviving!")
        print("=" * 40)
        
        try:
            ani = animation.FuncAnimation(
                self.fig, self.game_loop, interval=60,
                blit=False, cache_frame_data=False
            )
            plt.show()
        except KeyboardInterrupt:
            print("\n👋 Thanks for playing!")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'stream'):
                self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, 'p'):
                self.p.terminate()
        except Exception:
            pass
        print("✅ Game closed cleanly!")


def main():
    """Run the game"""
    print("🎮 Enhanced Cartoon Car Audio Game")
    print("🎵 Voice-controlled driving adventure!")
    
    try:
        game = EnhancedCarGame()
        game.start()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()