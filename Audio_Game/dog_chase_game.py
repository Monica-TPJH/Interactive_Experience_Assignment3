#!/usr/bin/env python3
"""
Dog Chase Car Game - 狗追车游戏
Sound-controlled racing game where you must outrun a chasing dog

控制方式：
- 声音越大：车辆越快
- 安静：车辆慢速移动
- 目标：保持在狗的前面，不要被狗追上！
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import sys

class DogChaseGame:
    def __init__(self):
        # 音频参数
        self.RATE = 44100
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        
        # 游戏参数
        self.GAME_WIDTH = 12
        self.GAME_HEIGHT = 8
        self.CAR_SIZE = 0.4
        self.DOG_SIZE = 0.3
        
        # 游戏状态
        self.car_x = 2  # 车辆起始X位置
        self.car_y = self.GAME_HEIGHT / 2  # 车辆Y位置（中央）
        self.dog_x = 0.5  # 狗的起始X位置（在车后面）
        self.dog_y = self.GAME_HEIGHT / 2  # 狗的Y位置
        
        self.car_speed = 0  # 当前车速
        self.dog_speed = 0.02  # 狗的速度（会逐渐增加）
        self.base_dog_speed = 0.02
        self.score = 0
        self.game_over = False
        self.game_time = 0
        
        # 音频控制参数
        self.volume_threshold = 0.001  # 最小音量阈值
        self.max_volume = 0.15  # 最大音量
        self.min_car_speed = 0.01  # 最小车速（安静时）
        self.max_car_speed = 0.08  # 最大车速（大声时）
        
        # 初始化音频
        self.setup_audio()
        
        # 初始化图形
        self.setup_graphics()
        
    def setup_audio(self):
        """初始化音频输入"""
        self.p = pyaudio.PyAudio()
        
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
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 9))
        
        # 游戏区域设置
        self.ax.set_xlim(0, self.GAME_WIDTH)
        self.ax.set_ylim(0, self.GAME_HEIGHT)
        self.ax.set_aspect('equal')
        self.ax.set_title('🐕 Dog Chase Car Game - Beautiful Edition', fontsize=24, fontweight='bold', 
                         color='white', pad=20)
        
        # 创建渐变背景
        self.create_gradient_background()
        self.ax.axis('off')
        
        # 创建美丽的赛道
        self.create_beautiful_track()
        
        # 创建精美的车辆
        self.create_beautiful_car()
        
        # 创建可爱的狗
        self.create_beautiful_dog()
        
        # 创建美丽的UI界面
        self.create_beautiful_ui()
        
        # 添加装饰元素
        self.add_decorative_elements()
        
        plt.tight_layout()
    
    def create_gradient_background(self):
        """创建渐变背景"""
        # 天空渐变 (从浅蓝到深蓝)
        y = np.linspace(0, self.GAME_HEIGHT, 100)
        x = np.linspace(0, self.GAME_WIDTH, 100)
        X, Y = np.meshgrid(x, y)
        
        # 创建天空渐变色彩
        colors = np.zeros((100, 100, 3))
        for i in range(100):
            ratio = i / 100
            # 从浅蓝(0.7,0.9,1) 到 深蓝(0.2,0.4,0.8)
            colors[i, :, 0] = 0.7 - 0.5 * ratio  # Red
            colors[i, :, 1] = 0.9 - 0.5 * ratio  # Green  
            colors[i, :, 2] = 1.0 - 0.2 * ratio  # Blue
        
        self.ax.imshow(colors, extent=[0, self.GAME_WIDTH, 0, self.GAME_HEIGHT], 
                      aspect='auto', alpha=0.8)
    
    def create_beautiful_track(self):
        """创建美丽的赛道"""
        # 主赛道 - 使用渐变效果
        track_colors = ['#404040', '#505050', '#606060']
        for i, color in enumerate(track_colors):
            track = patches.Rectangle((0.5 + i*0.02, 2 - i*0.02), 
                                    self.GAME_WIDTH - 1 - i*0.04, 4 + i*0.04, 
                                    facecolor=color, edgecolor='none', alpha=0.8)
            self.ax.add_patch(track)
        
        # 赛道边界 - 发光效果
        for offset in [0.05, 0.03, 0.01]:
            # 上边界
            top_glow = patches.Rectangle((0.5-offset, 5.8-offset), self.GAME_WIDTH-1+2*offset, 0.2+2*offset,
                                       facecolor='white', alpha=0.3-offset*5)
            self.ax.add_patch(top_glow)
            # 下边界
            bottom_glow = patches.Rectangle((0.5-offset, 2-offset), self.GAME_WIDTH-1+2*offset, 0.2+2*offset,
                                          facecolor='white', alpha=0.3-offset*5)
            self.ax.add_patch(bottom_glow)
        
        # 主边界线
        top_line = patches.Rectangle((0.5, 5.8), self.GAME_WIDTH - 1, 0.2, 
                                   facecolor='#FFD700', edgecolor='#FFA500', linewidth=2)
        bottom_line = patches.Rectangle((0.5, 2), self.GAME_WIDTH - 1, 0.2, 
                                      facecolor='#FFD700', edgecolor='#FFA500', linewidth=2)
        self.ax.add_patch(top_line)
        self.ax.add_patch(bottom_line)
        
        # 动态中心虚线
        self.center_dashes = []
        for x in range(1, int(self.GAME_WIDTH * 2)):
            dash_x = x * 0.8
            if dash_x < self.GAME_WIDTH - 1:
                center_dash = patches.Rectangle((dash_x, 3.85), 0.4, 0.3, 
                                              facecolor='#FFFF00', edgecolor='#FFD700', 
                                              linewidth=1, alpha=0.9)
                self.ax.add_patch(center_dash)
                self.center_dashes.append(center_dash)
    
    def create_beautiful_car(self):
        """创建精美的车辆"""
        # 车身阴影
        shadow = patches.FancyBboxPatch(
            (self.car_x - self.CAR_SIZE/2 + 0.05, self.car_y - self.CAR_SIZE/2 - 0.05),
            self.CAR_SIZE, self.CAR_SIZE,
            boxstyle="round,pad=0.02",
            facecolor='black', alpha=0.3
        )
        self.ax.add_patch(shadow)
        self.car_shadow = shadow
        
        # 主车身 - 渐变红色
        self.car_patch = patches.FancyBboxPatch(
            (self.car_x - self.CAR_SIZE/2, self.car_y - self.CAR_SIZE/2),
            self.CAR_SIZE, self.CAR_SIZE,
            boxstyle="round,pad=0.02",
            facecolor='#FF4444', edgecolor='#CC0000', linewidth=3
        )
        self.ax.add_patch(self.car_patch)
        
        # 车身高光
        highlight = patches.FancyBboxPatch(
            (self.car_x - self.CAR_SIZE/3, self.car_y - self.CAR_SIZE/6),
            self.CAR_SIZE/2, self.CAR_SIZE/4,
            boxstyle="round,pad=0.01",
            facecolor='white', alpha=0.6
        )
        self.ax.add_patch(highlight)
        self.car_highlight = highlight
        
        # 车窗 - 蓝色渐变
        window = patches.Rectangle(
            (self.car_x - self.CAR_SIZE/3, self.car_y - self.CAR_SIZE/4),
            self.CAR_SIZE/1.5, self.CAR_SIZE/2,
            facecolor='#87CEEB', edgecolor='#4682B4', linewidth=2
        )
        self.ax.add_patch(window)
        self.car_window = window
        
        # 车灯
        self.car_lights = []
        for light_pos in [(-0.18, 0.12), (0.18, 0.12)]:
            light = patches.Circle(
                (self.car_x + light_pos[0], self.car_y + light_pos[1]),
                0.03, facecolor='#FFFF99', edgecolor='#FFD700', linewidth=1
            )
            self.ax.add_patch(light)
            self.car_lights.append(light)
        
        # 更精美的车轮
        self.car_wheels = []
        wheel_positions = [(-0.15, -0.15), (0.15, -0.15), (-0.15, 0.15), (0.15, 0.15)]
        for wheel_pos in wheel_positions:
            # 轮胎
            wheel = patches.Circle(
                (self.car_x + wheel_pos[0], self.car_y + wheel_pos[1]), 
                0.06, facecolor='#2F2F2F', edgecolor='#000000', linewidth=2
            )
            self.ax.add_patch(wheel)
            # 轮毂
            rim = patches.Circle(
                (self.car_x + wheel_pos[0], self.car_y + wheel_pos[1]), 
                0.03, facecolor='#C0C0C0', edgecolor='#808080', linewidth=1
            )
            self.ax.add_patch(rim)
            self.car_wheels.append((wheel, rim))
    
    def create_beautiful_dog(self):
        """创建可爱的狗 - 新设计"""
        # 狗的阴影
        dog_shadow = patches.Ellipse(
            (self.dog_x + 0.05, self.dog_y - 0.05), self.DOG_SIZE + 0.1, self.DOG_SIZE * 0.9 + 0.05,
            facecolor='black', alpha=0.3
        )
        self.ax.add_patch(dog_shadow)
        self.dog_shadow = dog_shadow
        
        # 狗身体 - 金毛犬风格，更长的身体
        self.dog_patch = patches.Ellipse(
            (self.dog_x, self.dog_y), self.DOG_SIZE + 0.1, self.DOG_SIZE * 0.7,
            facecolor='#FFD700', edgecolor='#DAA520', linewidth=2
        )
        self.ax.add_patch(self.dog_patch)
        
        # 狗头部 - 单独的圆形头部
        self.dog_head = patches.Circle(
            (self.dog_x + 0.12, self.dog_y), self.DOG_SIZE * 0.6,
            facecolor='#FFD700', edgecolor='#DAA520', linewidth=2
        )
        self.ax.add_patch(self.dog_head)
        
        # 狗的腿部
        self.dog_legs = []
        leg_positions = [(-0.08, -0.15), (0.08, -0.15)]  # 前腿和后腿
        for leg_pos in leg_positions:
            leg = patches.Rectangle(
                (self.dog_x + leg_pos[0] - 0.02, self.dog_y + leg_pos[1] - 0.08),
                0.04, 0.08, facecolor='#DAA520', edgecolor='#B8860B'
            )
            self.ax.add_patch(leg)
            self.dog_legs.append(leg)
        
        # 狗的耳朵 - 垂耳设计
        self.dog_ears = []
        for ear_pos in [(-0.05, 0.08), (0.05, 0.08)]:
            ear = patches.Ellipse(
                (self.dog_x + 0.12 + ear_pos[0], self.dog_y + ear_pos[1]),
                0.04, 0.12, facecolor='#DEB887', edgecolor='#CD853F', angle=ear_pos[0]*200
            )
            self.ax.add_patch(ear)
            self.dog_ears.append(ear)
        
        # 狗的眼睛 - 更友善的表情
        self.dog_eyes = []
        for eye_pos in [(-0.03, 0.02), (0.03, 0.02)]:
            # 眼白
            eye_white = patches.Ellipse(
                (self.dog_x + 0.12 + eye_pos[0], self.dog_y + eye_pos[1]),
                0.015, 0.02, facecolor='white', edgecolor='black', linewidth=1
            )
            self.ax.add_patch(eye_white)
            # 瞳孔
            pupil = patches.Circle(
                (self.dog_x + 0.12 + eye_pos[0], self.dog_y + eye_pos[1]),
                0.008, facecolor='black'
            )
            self.ax.add_patch(pupil)
            self.dog_eyes.append((eye_white, pupil))
        
        # 狗的鼻子 - 更大的黑鼻子
        nose = patches.Ellipse(
            (self.dog_x + 0.12, self.dog_y - 0.05), 0.025, 0.015, 
            facecolor='black', edgecolor='none'
        )
        self.ax.add_patch(nose)
        self.dog_nose = nose
        
        # 狗的嘴巴 - 微笑的弧线
        self.dog_mouth = patches.Arc(
            (self.dog_x + 0.12, self.dog_y - 0.08), 0.06, 0.04,
            angle=0, theta1=0, theta2=180, color='black', linewidth=2
        )
        self.ax.add_patch(self.dog_mouth)
        
        # 狗的舌头 - 伸出的舌头
        self.dog_tongue = patches.Ellipse(
            (self.dog_x + 0.16, self.dog_y - 0.08), 0.03, 0.015,
            facecolor='#FF69B4', edgecolor='#FF1493', linewidth=1
        )
        self.ax.add_patch(self.dog_tongue)
        
        # 狗的尾巴 - 卷曲的尾巴
        tail = patches.Arc(
            (self.dog_x - 0.15, self.dog_y + 0.02), 0.12, 0.12,
            angle=45, theta1=0, theta2=270, color='#DAA520', linewidth=4
        )
        self.ax.add_patch(tail)
        self.dog_tail = tail
    
    def create_beautiful_ui(self):
        """创建美丽的UI界面 - 所有面板都在顶部"""
        # 主信息面板 - 顶部左侧
        info_bg = patches.FancyBboxPatch(
            (0.02, 0.85), 0.25, 0.13, transform=self.ax.transAxes,
            boxstyle="round,pad=0.02", 
            facecolor='navy', edgecolor='gold', linewidth=3, alpha=0.9
        )
        self.ax.add_patch(info_bg)
        
        # 信息文字
        self.info_text = self.ax.text(0.03, 0.97, '', transform=self.ax.transAxes,
                                     fontsize=12, fontweight='bold', color='white',
                                     verticalalignment='top')
        
        # 游戏说明面板 - 顶部中央
        instructions_bg = patches.FancyBboxPatch(
            (0.3, 0.85), 0.22, 0.13, transform=self.ax.transAxes,
            boxstyle="round,pad=0.015",
            facecolor='darkgreen', edgecolor='gold', linewidth=2, alpha=0.9
        )
        self.ax.add_patch(instructions_bg)
        
        instructions = (
            "Drive with Voice!\n\n"
            "LOUD = FAST car!\n"
            "Stay ahead!\n"
            "Don't get caught!"
        )
        self.ax.text(0.31, 0.97, instructions, transform=self.ax.transAxes,
                    fontsize=9, fontweight='bold', color='white',
                    verticalalignment='top')
        
        # 音量指示器 - 顶部右侧
        volume_bg = patches.FancyBboxPatch(
            (0.55, 0.92), 0.35, 0.06, transform=self.ax.transAxes,
            boxstyle="round,pad=0.01",
            facecolor='darkblue', edgecolor='gold', linewidth=2, alpha=0.9
        )
        self.ax.add_patch(volume_bg)
        
        # 音量指示器
        self.volume_bar = patches.Rectangle((0.57, 0.935), 0, 0.03, 
                                          transform=self.ax.transAxes,
                                          facecolor='lime', edgecolor='green', linewidth=2)
        self.ax.add_patch(self.volume_bar)
        
        # 音量标签
        self.ax.text(0.57, 0.975, 'VOLUME', transform=self.ax.transAxes,
                    fontsize=10, fontweight='bold', color='white')
    
    def add_decorative_elements(self):
        """添加装饰元素"""
        # 路边的花朵
        self.flowers = []
        flower_positions = [(0.3, 1.5), (0.8, 1.2), (0.2, 6.5), (0.7, 6.8),
                           (11.2, 1.3), (11.7, 1.7), (11.3, 6.2), (11.8, 6.6)]
        colors = ['red', 'yellow', 'pink', 'purple', 'orange']
        
        for i, (x, y) in enumerate(flower_positions):
            color = colors[i % len(colors)]
            # 花瓣
            for angle in range(0, 360, 60):
                petal = patches.Ellipse((x, y), 0.08, 0.04, angle=angle,
                                      facecolor=color, alpha=0.8)
                self.ax.add_patch(petal)
            # 花心
            center = patches.Circle((x, y), 0.02, facecolor='yellow')
            self.ax.add_patch(center)
            self.flowers.append(center)
        
        # 云朵 - 更蓬松
        self.clouds = []
        cloud_positions = [(2, 7), (5, 7.2), (8, 6.8), (10, 7.1)]
        for x, y in cloud_positions:
            cloud_parts = []
            # 创建蓬松的云朵
            for dx, dy, size in [(-0.2, 0, 0.15), (0, 0.1, 0.18), (0.2, 0, 0.15), (0, -0.1, 0.12)]:
                cloud_part = patches.Circle((x + dx, y + dy), size, 
                                          facecolor='white', edgecolor='lightgray', 
                                          alpha=0.8)
                self.ax.add_patch(cloud_part)
                cloud_parts.append(cloud_part)
            self.clouds.append(cloud_parts)
        
        # 美丽的树木
        tree_positions = [(0.2, 1), (0.2, 7), (11.8, 1), (11.8, 7)]
        for x, y in tree_positions:
            # 树干 - 渐变效果
            trunk = patches.Rectangle((x-0.06, y-0.4), 0.12, 0.8, 
                                    facecolor='#8B4513', edgecolor='#654321', linewidth=2)
            self.ax.add_patch(trunk)
            
            # 树冠 - 多层效果
            for size, color, offset in [(0.25, '#228B22', 0), (0.2, '#32CD32', 0.02), (0.15, '#90EE90', 0.04)]:
                crown = patches.Circle((x, y + 0.3 + offset), size, 
                                     facecolor=color, edgecolor='darkgreen', alpha=0.9)
                self.ax.add_patch(crown)
    
    def analyze_audio(self):
        """分析音频信号，返回音量级别"""
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.float32)
            
            # 计算音量（RMS）
            volume = np.sqrt(np.mean(audio_data**2))
            
            # 归一化音量到0-1范围
            normalized_volume = min(volume / self.max_volume, 1.0)
            
            # 如果音量低于阈值，使用最小速度
            if volume < self.volume_threshold:
                normalized_volume = 0.1  # 最小10%速度
            
            return normalized_volume
            
        except Exception as e:
            print(f"音频分析错误: {e}")
            return 0.1  # 返回最小速度
    
    def update_positions(self):
        """更新车辆和狗的位置"""
        # 获取音量并计算车速
        volume_level = self.analyze_audio()
        self.car_speed = self.min_car_speed + (self.max_car_speed - self.min_car_speed) * volume_level
        
        # 更新车辆位置
        self.car_x += self.car_speed
        
        # 限制车辆在赛道内
        self.car_x = max(1, min(self.GAME_WIDTH - 1, self.car_x))
        
        # 更新狗的位置（狗会逐渐加速）
        self.game_time += 1
        speed_increase = self.game_time * 0.00005  # 狗的加速度
        self.dog_speed = self.base_dog_speed + speed_increase
        self.dog_x += self.dog_speed
        
        # 更新车辆所有组件的位置
        self.update_car_graphics()
        
        # 更新狗所有组件的位置
        self.update_dog_graphics()
        
        # 更新动态效果
        self.update_dynamic_effects()
        
        # 更新音量指示器
        volume_level = self.analyze_audio()
        self.volume_bar.set_width(volume_level * 0.31)  # 最大宽度31%
        
        # 根据音量改变音量条颜色
        if volume_level > 0.8:
            self.volume_bar.set_facecolor('red')
        elif volume_level > 0.5:
            self.volume_bar.set_facecolor('orange')
        elif volume_level > 0.2:
            self.volume_bar.set_facecolor('yellow')
        else:
            self.volume_bar.set_facecolor('lime')
        
        # 检查游戏结束条件
        if self.dog_x >= self.car_x:
            self.game_over = True
            print(f"💔 Dog caught you! Final Score: {self.score}")
    
    def update_car_graphics(self):
        """更新车辆图形位置"""
        # 更新车身阴影
        self.car_shadow.set_x(self.car_x - self.CAR_SIZE/2 + 0.05)
        
        # 更新主车身
        self.car_patch.set_x(self.car_x - self.CAR_SIZE/2)
        
        # 更新车身高光
        self.car_highlight.set_x(self.car_x - self.CAR_SIZE/3)
        
        # 更新车窗
        self.car_window.set_x(self.car_x - self.CAR_SIZE/3)
        
        # 更新车灯
        light_positions = [(-0.18, 0.12), (0.18, 0.12)]
        for i, light_pos in enumerate(light_positions):
            self.car_lights[i].center = (self.car_x + light_pos[0], self.car_y + light_pos[1])
        
        # 更新车轮（轮胎和轮毂）
        wheel_positions = [(-0.15, -0.15), (0.15, -0.15), (-0.15, 0.15), (0.15, 0.15)]
        for i, wheel_pos in enumerate(wheel_positions):
            tire, rim = self.car_wheels[i]
            tire.center = (self.car_x + wheel_pos[0], self.car_y + wheel_pos[1])
            rim.center = (self.car_x + wheel_pos[0], self.car_y + wheel_pos[1])
    
    def update_dog_graphics(self):
        """更新狗图形位置 - 新设计"""
        # 更新狗的阴影
        self.dog_shadow.center = (self.dog_x + 0.05, self.dog_y - 0.05)
        
        # 更新狗身体
        self.dog_patch.center = (self.dog_x, self.dog_y)
        
        # 更新狗头部
        self.dog_head.center = (self.dog_x + 0.12, self.dog_y)
        
        # 更新狗的腿部
        leg_positions = [(-0.08, -0.15), (0.08, -0.15)]
        for i, leg_pos in enumerate(leg_positions):
            self.dog_legs[i].set_x(self.dog_x + leg_pos[0] - 0.02)
            self.dog_legs[i].set_y(self.dog_y + leg_pos[1] - 0.08)
        
        # 更新狗的耳朵
        ear_positions = [(-0.05, 0.08), (0.05, 0.08)]
        for i, ear_pos in enumerate(ear_positions):
            self.dog_ears[i].center = (self.dog_x + 0.12 + ear_pos[0], self.dog_y + ear_pos[1])
        
        # 更新狗的眼睛
        eye_positions = [(-0.03, 0.02), (0.03, 0.02)]
        for i, eye_pos in enumerate(eye_positions):
            eye_white, pupil = self.dog_eyes[i]
            eye_white.center = (self.dog_x + 0.12 + eye_pos[0], self.dog_y + eye_pos[1])
            pupil.center = (self.dog_x + 0.12 + eye_pos[0], self.dog_y + eye_pos[1])
        
        # 更新狗的鼻子
        self.dog_nose.center = (self.dog_x + 0.12, self.dog_y - 0.05)
        
        # 更新狗的嘴巴
        self.dog_mouth.set_center((self.dog_x + 0.12, self.dog_y - 0.08))
        
        # 更新狗的舌头（添加摆动效果）
        tongue_sway = 0.01 * np.sin(self.game_time * 0.2)
        self.dog_tongue.center = (self.dog_x + 0.16 + tongue_sway, self.dog_y - 0.08)
        
        # 更新狗的尾巴（弧形尾巴的位置）
        self.dog_tail.set_center((self.dog_x - 0.15, self.dog_y + 0.02))
    
    def update_dynamic_effects(self):
        """更新动态效果"""
        # 让中心线虚线动起来
        dash_offset = (self.game_time * 0.1) % 1.6
        for i, dash in enumerate(self.center_dashes):
            base_x = (i + 1) * 0.8 - dash_offset
            if 0.5 <= base_x <= self.GAME_WIDTH - 1:
                dash.set_x(base_x)
                dash.set_alpha(0.9)
            else:
                dash.set_alpha(0)
        
        # 让花朵轻微摆动
        sway = 0.01 * np.sin(self.game_time * 0.1)
        for i, flower in enumerate(self.flowers):
            base_pos = [(0.3, 1.5), (0.8, 1.2), (0.2, 6.5), (0.7, 6.8),
                       (11.2, 1.3), (11.7, 1.7), (11.3, 6.2), (11.8, 6.6)][i]
            flower.center = (base_pos[0] + sway, base_pos[1])
        
        # 让云朵慢慢移动
        cloud_drift = (self.game_time * 0.005) % 15
        base_positions = [(2, 7), (5, 7.2), (8, 6.8), (10, 7.1)]
        for i, cloud_parts in enumerate(self.clouds):
            base_x = base_positions[i][0] + cloud_drift
            if base_x > 12:
                base_x -= 15  # 循环回来
            for j, part in enumerate(cloud_parts):
                offsets = [(-0.2, 0), (0, 0.1), (0.2, 0), (0, -0.1)][j]
                part.center = (base_x + offsets[0], base_positions[i][1] + offsets[1])
    
    def update_camera(self):
        """更新摄像机视角，跟随车辆"""
        # 让摄像机跟随车辆
        camera_x = self.car_x - 3  # 车辆在屏幕左侧1/4处
        
        # 确保摄像机不会超出边界
        camera_x = max(0, min(camera_x, max(0, self.car_x - 8)))
        
        self.ax.set_xlim(camera_x, camera_x + self.GAME_WIDTH)
    
    def game_loop(self, frame):
        """主游戏循环"""
        if self.game_over:
            # 显示游戏结束信息
            if not hasattr(self, 'game_over_displayed'):
                # 创建美丽的游戏结束界面
                game_over_bg = patches.FancyBboxPatch(
                    (self.car_x - 2, self.GAME_HEIGHT/2 - 2), 4, 4,
                    boxstyle="round,pad=0.3",
                    facecolor='darkred', edgecolor='gold', linewidth=4, alpha=0.95
                )
                self.ax.add_patch(game_over_bg)
                
                game_over_text = (
                    f"GAME OVER!\n\n"
                    f"Distance: {self.score:.1f}m\n\n"
                    f"Performance:\n"
                    f"{'Amazing!' if self.score > 500 else 'Great!' if self.score > 200 else 'Keep trying!'}\n\n"
                    f"Press Ctrl+C to restart\n"
                    f"or close window to exit"
                )
                
                self.game_over_text = self.ax.text(
                    self.car_x, self.GAME_HEIGHT/2, 
                    game_over_text,
                    ha='center', va='center', 
                    fontsize=18, fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='navy', alpha=0.9, 
                             edgecolor='gold', linewidth=3)
                )
                
                # 添加烟花效果
                self.add_game_over_effects()
                
                self.game_over_displayed = True
            return
        
        # 更新位置
        self.update_positions()
        
        # 更新摄像机
        self.update_camera()
        
        # 更新分数（距离）
        self.score += self.car_speed * 10  # 分数基于移动距离
        
        # 计算距离差
        distance_diff = self.car_x - self.dog_x
        
        # 更新信息显示 - 更美观的格式
        volume_level = self.analyze_audio()
        info_text = (
            f"Distance: {self.score:.1f}m\n"
            f"Car Speed: {self.car_speed*1000:.1f}\n"
            f"Dog Speed: {self.dog_speed*1000:.1f}\n"
            f"Lead: {distance_diff:.1f}m\n"
            f"Volume: {volume_level*100:.0f}%\n"
            f"Time: {self.game_time//50:.1f}s"
        )
        self.info_text.set_text(info_text)
        
        # 添加紧张感效果
        if distance_diff < 1.0:  # 狗快追上了
            self.add_danger_effects()
    
    def add_game_over_effects(self):
        """添加游戏结束特效"""
        # 创建粒子效果（简单的圆圈）
        for i in range(20):
            angle = i * 18  # 360/20
            radius = 1.5
            x = self.car_x + radius * np.cos(np.radians(angle))
            y = self.GAME_HEIGHT/2 + radius * np.sin(np.radians(angle))
            
            particle = patches.Circle((x, y), 0.05, 
                                    facecolor='gold', alpha=0.7)
            self.ax.add_patch(particle)
    
    def add_danger_effects(self):
        """添加危险警告效果"""
        # 让屏幕边缘闪红色
        danger_alpha = 0.3 + 0.2 * np.sin(self.game_time * 0.5)
        
        # 创建红色边框效果（只在需要时创建一次）
        if not hasattr(self, 'danger_overlay'):
            self.danger_overlay = patches.Rectangle(
                (0, 0), self.GAME_WIDTH, self.GAME_HEIGHT,
                facecolor='red', alpha=0, edgecolor='red', linewidth=8
            )
            self.ax.add_patch(self.danger_overlay)
        
        self.danger_overlay.set_alpha(danger_alpha * 0.5)
        self.danger_overlay.set_linewidth(8 + 4 * np.sin(self.game_time * 0.5))
    
    def start_game(self):
        """开始游戏"""
        print("🐕 Dog Chase Car Game Started!")
        print("💡 Game Instructions:")
        print("   - Make LOUD sounds to speed up your car!")
        print("   - The louder you are, the faster you go!")
        print("   - Stay ahead of the chasing dog!")
        print("   - The dog gets faster over time!")
        print("   - Don't let the dog catch you!")
        print("   - Close window or press Ctrl+C to exit")
        print("=" * 60)
        
        try:
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
    print("=" * 60)
    print("🐕 狗追车游戏 - Dog Chase Car Game")
    print("=" * 60)
    print("准备开始...")
    
    try:
        game = DogChaseGame()
        game.start_game()
    except KeyboardInterrupt:
        print("\n游戏中断")
    except Exception as e:
        print(f"游戏错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()