#!/usr/bin/env python3
"""
声音控制开车游戏 - Audio Driving Game
根据麦克风输入的声音大小控制车辆左右移动，避开障碍物

控制方式：
- 安静：车辆居中
- 小声：车辆轻微移动
- 大声：车辆快速移动
- 左右移动通过声音的频率特征判断

游戏目标：避开从上方掉落的障碍物，坚持越久得分越高！
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import random
import sys

class AudioCarGame:
    def __init__(self):
        # 音频参数
        self.RATE = 44100
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        
        # 游戏参数
        self.GAME_WIDTH = 10
        self.GAME_HEIGHT = 15
        self.CAR_WIDTH = 0.8
        self.CAR_HEIGHT = 1.2
        self.OBSTACLE_WIDTH = 0.6
        self.OBSTACLE_HEIGHT = 0.8
        
        # 游戏状态
        self.car_x = self.GAME_WIDTH / 2  # 车辆X位置
        self.car_y = 2  # 车辆Y位置（固定）
        self.obstacles = []  # 障碍物列表
        self.score = 0
        self.game_over = False
        self.game_speed = 0.05  # 游戏速度 (减慢初始速度)
        self.game_over_displayed = False  # 游戏结束显示状态
        
        # 音频控制参数
        self.audio_buffer = np.zeros(self.CHUNK * 4)  # 音频缓冲区
        self.volume_threshold = 0.001  # 音量阈值
        self.max_volume = 0.1  # 最大音量（用于归一化）
        self.sensitivity = 2.0  # 控制敏感度
        
        # 音频分析
        self.freq_bands = {
            'low': (80, 300),     # 低频 - 向左
            'high': (2000, 8000)  # 高频 - 向右
        }
        
        # 初始化音频
        self.setup_audio()
        
        # 初始化图形
        self.setup_graphics()
        
    def setup_audio(self):
        """初始化音频输入"""
        self.p = pyaudio.PyAudio()
        
        # 寻找可用的输入设备
        print("🎮 初始化音频设备...")
        input_device = None
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_device = i
                print(f"找到音频设备: {device_info['name']}")
                break
        
        if input_device is None:
            print("❌ 未找到音频输入设备!")
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
            print("✅ 音频流初始化成功!")
        except Exception as e:
            print(f"❌ 音频流初始化失败: {e}")
            sys.exit(1)
    
    def setup_graphics(self):
        """初始化游戏图形界面"""
        self.fig, self.ax_game = plt.subplots(1, 1, figsize=(10, 12))
        
        # 游戏区域设置
        self.ax_game.set_xlim(0, self.GAME_WIDTH)
        self.ax_game.set_ylim(0, self.GAME_HEIGHT)
        self.ax_game.set_aspect('equal')
        self.ax_game.set_title('🚗 Cartoon Car Adventure', fontsize=18, fontweight='bold', color='darkblue')
        self.ax_game.set_facecolor('lightblue')  # Sky blue background
        self.ax_game.axis('off')  # Remove axes for cleaner cartoon look
        
        self.ax_game.axis('off')  # Remove axes for cleaner cartoon look
        
        # Draw cartoon road with grass on sides
        road_patch = patches.Rectangle((1, 0), self.GAME_WIDTH-2, self.GAME_HEIGHT, 
                                     facecolor='gray', edgecolor='darkgray', linewidth=2)
        self.ax_game.add_patch(road_patch)
        
        # Left grass area
        left_grass = patches.Rectangle((0, 0), 1, self.GAME_HEIGHT, 
                                     facecolor='green', alpha=0.8)
        self.ax_game.add_patch(left_grass)
        
        # Right grass area  
        right_grass = patches.Rectangle((self.GAME_WIDTH-1, 0), 1, self.GAME_HEIGHT, 
                                      facecolor='green', alpha=0.8)
        self.ax_game.add_patch(right_grass)
        
        # Road markings (dashed yellow lines)
        for y in range(0, int(self.GAME_HEIGHT), 2):
            center_line = patches.Rectangle((self.GAME_WIDTH/2 - 0.05, y), 0.1, 0.8, 
                                          facecolor='yellow', alpha=0.9)
            self.ax_game.add_patch(center_line)
        
        # Add some cartoon trees
        self.add_cartoon_scenery()
        
        # Create cartoon car with more details
        car_body = patches.FancyBboxPatch(
            (self.car_x - self.CAR_WIDTH/2, self.car_y - self.CAR_HEIGHT/2),
            self.CAR_WIDTH, self.CAR_HEIGHT,
            boxstyle="round,pad=0.1", 
            facecolor='red', edgecolor='darkred', linewidth=3
        )
        self.ax_game.add_patch(car_body)
        self.car_patch = car_body
        
        # Car windows
        window = patches.Rectangle(
            (self.car_x - self.CAR_WIDTH/3, self.car_y - self.CAR_HEIGHT/4),
            self.CAR_WIDTH/1.5, self.CAR_HEIGHT/2,
            facecolor='lightblue', edgecolor='blue', linewidth=1
        )
        self.ax_game.add_patch(window)
        self.car_window = window
        
        # Car wheels
        left_wheel = patches.Circle((self.car_x - self.CAR_WIDTH/3, self.car_y - self.CAR_HEIGHT/2), 
                                  0.15, facecolor='black', edgecolor='gray')
        right_wheel = patches.Circle((self.car_x + self.CAR_WIDTH/3, self.car_y - self.CAR_HEIGHT/2), 
                                   0.15, facecolor='black', edgecolor='gray')
        self.ax_game.add_patch(left_wheel)
        self.ax_game.add_patch(right_wheel)
        self.car_wheels = [left_wheel, right_wheel]
        
        # 障碍物列表（用于绘制）
        self.obstacle_patches = []
        
        # 分数显示
        self.score_text = self.ax_game.text(0.05, 0.95, f'Score: {self.score}', 
                                          transform=self.ax_game.transAxes,
                                          fontsize=16, fontweight='bold', color='white',
                                          bbox=dict(boxstyle='round', facecolor='darkblue', alpha=0.8))
        
        # 游戏说明 - 简化版本
        instructions = (
            "🎮 Drive with your voice!\n"
            "🔊 High sounds → RIGHT\n"
            "🔇 Low sounds → LEFT\n"
            "🚫 Avoid obstacles!"
        )
        self.ax_game.text(0.05, 0.15, instructions, transform=self.ax_game.transAxes,
                         fontsize=12, fontweight='bold', color='white',
                         bbox=dict(boxstyle='round', facecolor='green', alpha=0.8))
        
        plt.tight_layout()
    
    def add_cartoon_scenery(self):
        """添加卡通风景元素"""
        # Add some cartoon trees on the sides
        tree_positions = [(0.5, 3), (0.5, 7), (0.5, 11), (9.5, 2), (9.5, 6), (9.5, 10)]
        
        for x, y in tree_positions:
            # Tree trunk
            trunk = patches.Rectangle((x-0.1, y-0.5), 0.2, 1, 
                                    facecolor='brown', edgecolor='saddlebrown')
            self.ax_game.add_patch(trunk)
            
            # Tree crown
            crown = patches.Circle((x, y+0.3), 0.3, 
                                 facecolor='forestgreen', edgecolor='darkgreen')
            self.ax_game.add_patch(crown)
        
        # Add clouds in the sky (top area)
        cloud_positions = [(2, 13.5), (5, 14), (8, 13.2)]
        for x, y in cloud_positions:
            # Cloud circles
            for dx in [-0.3, 0, 0.3]:
                cloud_circle = patches.Circle((x + dx, y), 0.2, 
                                            facecolor='white', edgecolor='lightgray', alpha=0.8)
                self.ax_game.add_patch(cloud_circle)
    
    def analyze_audio(self):
        """分析音频信号，返回控制指令"""
        try:
            # 读取音频数据
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.float32)
            
            # 更新音频缓冲区
            self.audio_buffer = np.roll(self.audio_buffer, -len(audio_data))
            self.audio_buffer[-len(audio_data):] = audio_data
            
            # 计算音量（RMS）
            volume = np.sqrt(np.mean(audio_data**2))
            
            # 如果音量太小，返回居中控制
            if volume < self.volume_threshold:
                return 0, volume, "安静 - 居中"
            
            # 频谱分析
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/self.RATE)
            magnitude = np.abs(fft)
            
            # 分析不同频段的能量
            low_energy = 0
            high_energy = 0
            
            for i, freq in enumerate(freqs[:len(freqs)//2]):  # 只看正频率
                if self.freq_bands['low'][0] <= freq <= self.freq_bands['low'][1]:
                    low_energy += magnitude[i]
                elif self.freq_bands['high'][0] <= freq <= self.freq_bands['high'][1]:
                    high_energy += magnitude[i]
            
            # 计算左右倾向
            total_energy = low_energy + high_energy
            if total_energy > 0:
                # 归一化能量差异
                energy_diff = (high_energy - low_energy) / total_energy
                # 结合音量大小
                control_strength = min(volume / self.max_volume, 1.0) * self.sensitivity
                movement = energy_diff * control_strength
                
                # 生成控制指令描述
                if abs(movement) < 0.1:
                    direction = "居中"
                elif movement > 0:
                    direction = f"右移 ({movement:.2f})"
                else:
                    direction = f"左移 ({movement:.2f})"
                
                return movement, volume, direction
            else:
                return 0, volume, "无有效频率"
                
        except Exception as e:
            print(f"音频分析错误: {e}")
            return 0, 0, "错误"
    
    def update_car_position(self, movement):
        """更新车辆位置"""
        # 应用移动控制
        self.car_x += movement
        
        # 限制在游戏区域内（考虑道路边界）
        road_left = 1 + self.CAR_WIDTH/2
        road_right = self.GAME_WIDTH - 1 - self.CAR_WIDTH/2
        self.car_x = max(road_left, min(road_right, self.car_x))
        
        # 更新车辆图形位置
        self.car_patch.set_x(self.car_x - self.CAR_WIDTH/2)
        
        # 更新车窗位置
        if hasattr(self, 'car_window'):
            self.car_window.set_x(self.car_x - self.CAR_WIDTH/3)
        
        # 更新车轮位置
        if hasattr(self, 'car_wheels'):
            self.car_wheels[0].center = (self.car_x - self.CAR_WIDTH/3, self.car_y - self.CAR_HEIGHT/2)
            self.car_wheels[1].center = (self.car_x + self.CAR_WIDTH/3, self.car_y - self.CAR_HEIGHT/2)
    
    def spawn_obstacle(self):
        """生成新的障碍物"""
        if random.random() < 0.015:  # 1.5% 概率生成障碍物 (降低生成频率)
            # 在道路范围内随机位置
            road_left = 1 + self.OBSTACLE_WIDTH/2
            road_right = self.GAME_WIDTH - 1 - self.OBSTACLE_WIDTH/2
            x = random.uniform(road_left, road_right)
            y = self.GAME_HEIGHT
            
            # Create cartoon-style obstacle car
            colors = ['orange', 'purple', 'yellow', 'pink']
            color = random.choice(colors)
            
            # Main car body with rounded corners
            obstacle_patch = patches.FancyBboxPatch(
                (x - self.OBSTACLE_WIDTH/2, y - self.OBSTACLE_HEIGHT/2),
                self.OBSTACLE_WIDTH, self.OBSTACLE_HEIGHT,
                boxstyle="round,pad=0.05",
                facecolor=color, edgecolor='darkred', linewidth=2
            )
            
            obstacle = {
                'x': x,
                'y': y,
                'patch': obstacle_patch,
                'color': color
            }
            
            self.obstacles.append(obstacle)
            self.ax_game.add_patch(obstacle_patch)
    
    def update_obstacles(self):
        """更新障碍物位置"""
        obstacles_to_remove = []
        
        for obstacle in self.obstacles:
            # 向下移动 (减慢障碍物速度)
            obstacle['y'] -= self.game_speed * 12  # 从20降到12，减慢40%
            obstacle['patch'].set_y(obstacle['y'] - self.OBSTACLE_HEIGHT/2)
            
            # 检查是否超出屏幕
            if obstacle['y'] < -1:
                obstacles_to_remove.append(obstacle)
                self.score += 10  # 成功避开障碍物得分
            
            # 检查碰撞
            if self.check_collision(obstacle):
                self.game_over = True
                print(f"💥 Game Over! Final Score: {self.score}")
        
        # 移除超出屏幕的障碍物
        for obstacle in obstacles_to_remove:
            obstacle['patch'].remove()
            self.obstacles.remove(obstacle)
    
    def check_collision(self, obstacle):
        """检查车辆与障碍物的碰撞"""
        car_left = self.car_x - self.CAR_WIDTH/2
        car_right = self.car_x + self.CAR_WIDTH/2
        car_top = self.car_y + self.CAR_HEIGHT/2
        car_bottom = self.car_y - self.CAR_HEIGHT/2
        
        obs_left = obstacle['x'] - self.OBSTACLE_WIDTH/2
        obs_right = obstacle['x'] + self.OBSTACLE_WIDTH/2
        obs_top = obstacle['y'] + self.OBSTACLE_HEIGHT/2
        obs_bottom = obstacle['y'] - self.OBSTACLE_HEIGHT/2
        
        # AABB 碰撞检测
        return (car_left < obs_right and car_right > obs_left and
                car_bottom < obs_top and car_top > obs_bottom)
    
    def game_loop(self, frame):
        """主游戏循环"""
        if self.game_over:
            # 显示游戏结束信息 (只显示一次)
            if not self.game_over_displayed:
                # 清除之前可能存在的游戏结束文本
                for text in self.ax_game.texts:
                    if 'Game Over' in text.get_text() or 'Final Score' in text.get_text():
                        text.remove()
                
                # 创建更好看的游戏结束界面
                game_over_text = (
                    f"💥 GAME OVER! 💥\n\n"
                    f"🏆 Final Score: {self.score}\n\n"
                    f"🎯 Performance:\n"
                    f"{'⭐⭐⭐' if self.score > 1000 else '⭐⭐' if self.score > 500 else '⭐'}\n\n"
                    f"Press Ctrl+C to restart\n"
                    f"or close window to exit"
                )
                
                self.game_over_text = self.ax_game.text(
                    self.GAME_WIDTH/2, self.GAME_HEIGHT/2, 
                    game_over_text,
                    ha='center', va='center', 
                    fontsize=14, fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle='round,pad=1', facecolor='red', alpha=0.9, edgecolor='darkred', linewidth=3)
                )
                
                # 添加一个半透明覆盖层
                overlay = patches.Rectangle(
                    (0, 0), self.GAME_WIDTH, self.GAME_HEIGHT,
                    facecolor='black', alpha=0.3
                )
                self.ax_game.add_patch(overlay)
                
                self.game_over_displayed = True
            return
        
        # 分析音频输入
        movement, volume, direction = self.analyze_audio()
        
        # 更新车辆位置
        self.update_car_position(movement)
        
        # 生成和更新障碍物
        self.spawn_obstacle()
        self.update_obstacles()
        
        # 更新分数显示
        self.score += 1  # 每帧得1分
        self.score_text.set_text(f'Score: {self.score}')
        
        # 逐渐增加游戏难度 (更慢的难度增长)
        self.game_speed = min(0.2, 0.05 + self.score / 15000)  # 更慢的速度增长
    
    def start_game(self):
        """开始游戏"""
        print("🚗 Audio Controlled Car Game Started!")
        print("💡 Game Instructions:")
        print("   - Make low frequency sounds (like 'mmm~') to move LEFT")
        print("   - Make high frequency sounds (like 'aaa~') to move RIGHT") 
        print("   - Stay quiet to keep car centered")
        print("   - Avoid orange obstacles!")
        print("   - Game speed increases gradually")
        print("   - Close window or press Ctrl+C to exit")
        print("=" * 50)
        
        try:
            # 开始动画循环
            self.ani = animation.FuncAnimation(
                self.fig, self.game_loop, interval=50, 
                blit=False, cache_frame_data=False
            )
            plt.show()
        except KeyboardInterrupt:
            print("\n👋 游戏被用户中断")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理游戏资源...")
        try:
            if hasattr(self, 'stream'):
                self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, 'p'):
                self.p.terminate()
        except Exception as e:
            print(f"清理错误: {e}")
        print("✅ 清理完成!")


def main():
    """主函数"""
    print("=" * 50)
    print("🎮 声音控制开车游戏")
    print("=" * 50)
    print("准备开始...")
    
    try:
        game = AudioCarGame()
        game.start_game()
    except KeyboardInterrupt:
        print("\n游戏中断")
    except Exception as e:
        print(f"游戏错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()