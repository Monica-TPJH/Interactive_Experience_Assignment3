#!/usr/bin/env python3
"""
Pixel Dog Chase Car Game - 像素风狗追车游戏
8-bit style sound-controlled racing game where you must outrun a chasing dog

控制方式：
- 声音越大：车辆越快
- 安静：车辆慢速移动
- 目标：保持在狗的前面，不要被狗追上！

像素风格特色：
- 8位游戏画面
- 像素化角色和环境
- 复古色彩搭配
- 像素化音效提示
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import sys

class PixelDogChaseGame:
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
        self.PIXEL_SIZE = 0.08  # 像素块大小
        self.DOG_PIXEL_SIZE = 0.06  # 狗的像素块大小（更小）
        
        # 游戏状态
        self.car_x = 2  # 车辆起始X位置
        self.car_y = self.GAME_HEIGHT / 2  # 车辆Y位置（中央）
        self.dog_x = 0.5  # 狗的起始X位置（在车后面）
        self.dog_y = self.GAME_HEIGHT / 2  # 狗的Y位置
        
        self.car_speed = 0  # 当前车速
        self.dog_speed = 0.08  # 狗的速度（会逐渐增加）- 加快
        self.base_dog_speed = 0.08
        self.score = 0
        self.game_over = False
        self.game_time = 0
        
        # 音频控制参数
        self.volume_threshold = 0.0005  # 更低的最小音量阈值（更灵敏）
        self.max_volume = 0.25  # 更高的最大音量（更宽容）
        self.volume_history = [0.1] * 5  # 音量历史用于平滑
        self.min_car_speed = 0.07  # 最小车速（安静时）- 加快
        self.max_car_speed = 0.22  # 最大车速（大声时）- 加快
        
        # 像素风格色彩
        self.pixel_colors = {
            'sky': '#87CEEB',
            'ground': '#228B22',
            'track': '#404040',
            'car_red': '#FF0000',
            'car_blue': '#0000FF',
            'dog_brown': '#8B4513',
            'dog_gold': '#FFD700',
            'white': '#FFFFFF',
            'black': '#000000',
            'yellow': '#FFFF00',
            'green': '#00FF00',
            'pink': '#FF69B4'
        }
        
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
        """初始化像素风格游戏图形界面"""
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 9))
        
        # 游戏区域设置
        self.ax.set_xlim(0, self.GAME_WIDTH)
        self.ax.set_ylim(0, self.GAME_HEIGHT)
        self.ax.set_aspect('equal')
        self.ax.set_title('🕹️ PIXEL DOG CHASE - 8-BIT EDITION', fontsize=24, fontweight='bold', 
                         color='white', pad=20, family='monospace')
        
        # 设置背景为纯色像素风格
        self.fig.patch.set_facecolor('#000033')  # 深蓝色背景
        self.ax.set_facecolor('#000033')
        
        # 创建像素风格背景
        self.create_pixel_background()
        self.ax.axis('off')
        
        # 创建像素化赛道
        self.create_pixel_track()
        
        # 创建像素风格车辆
        self.create_pixel_car()
        
        # 创建像素风格狗
        self.create_pixel_dog()
        
        # 创建像素风格UI界面
        self.create_pixel_ui()
        
        # 添加像素装饰元素
        self.add_pixel_decorations()
        
        plt.tight_layout()
    
    def create_pixel_block(self, x, y, size, color, edge_color=None):
        """创建单个像素块"""
        if edge_color is None:
            edge_color = color
        pixel = patches.Rectangle((x, y), size, size, 
                                facecolor=color, edgecolor=edge_color, 
                                linewidth=1)
        self.ax.add_patch(pixel)
        return pixel
    
    def create_pixel_sprite(self, x, y, pattern, size):
        """根据图案创建像素精灵"""
        pixels = []
        for row_idx, row in enumerate(pattern):
            for col_idx, color in enumerate(row):
                if color != 'T':  # T表示透明
                    pixel_x = x + col_idx * size
                    pixel_y = y + (len(pattern) - 1 - row_idx) * size
                    pixel = self.create_pixel_block(pixel_x, pixel_y, size, 
                                                  self.pixel_colors.get(color, color))
                    pixels.append(pixel)
        return pixels
    
    def create_pixel_background(self):
        """创建像素风格背景"""
        # 天空 - 使用像素块创建
        for x in range(0, int(self.GAME_WIDTH / self.PIXEL_SIZE)):
            for y in range(int(6 / self.PIXEL_SIZE), int(self.GAME_HEIGHT / self.PIXEL_SIZE)):
                # 渐变天空效果
                if y % 3 == 0:
                    color = '#4169E1'  # 皇家蓝
                elif y % 3 == 1:
                    color = '#6495ED'  # 矢车菊蓝
                else:
                    color = '#87CEEB'  # 天空蓝
                self.create_pixel_block(x * self.PIXEL_SIZE, y * self.PIXEL_SIZE, 
                                      self.PIXEL_SIZE, color)
        
        # 地面 - 绿色像素块
        for x in range(0, int(self.GAME_WIDTH / self.PIXEL_SIZE)):
            for y in range(0, int(2 / self.PIXEL_SIZE)):
                # 交替绿色
                if (x + y) % 2 == 0:
                    color = '#228B22'  # 森林绿
                else:
                    color = '#32CD32'  # 酸橙绿
                self.create_pixel_block(x * self.PIXEL_SIZE, y * self.PIXEL_SIZE, 
                                      self.PIXEL_SIZE, color)
    
    def create_pixel_track(self):
        """创建像素化赛道"""
        # 主赛道
        track_y_start = int(2 / self.PIXEL_SIZE)
        track_y_end = int(6 / self.PIXEL_SIZE)
        
        for x in range(int(0.5 / self.PIXEL_SIZE), int((self.GAME_WIDTH - 0.5) / self.PIXEL_SIZE)):
            for y in range(track_y_start, track_y_end):
                # 赛道颜色模式
                if y == track_y_start or y == track_y_end - 1:
                    color = '#FFD700'  # 金色边界
                elif (x + y) % 4 == 0:
                    color = '#404040'  # 深灰
                elif (x + y) % 4 == 2:
                    color = '#505050'  # 中灰
                else:
                    color = '#606060'  # 浅灰
                
                self.create_pixel_block(x * self.PIXEL_SIZE, y * self.PIXEL_SIZE, 
                                      self.PIXEL_SIZE, color)
        
        # 中心线 - 像素化虚线
        self.center_pixels = []
        center_y = int(4 / self.PIXEL_SIZE)
        for x in range(1, int(self.GAME_WIDTH / self.PIXEL_SIZE), 4):
            for i in range(2):  # 每个虚线段2个像素宽
                pixel = self.create_pixel_block((x + i) * self.PIXEL_SIZE, 
                                              center_y * self.PIXEL_SIZE, 
                                              self.PIXEL_SIZE, '#FFFF00')
                self.center_pixels.append(pixel)
    
    def create_pixel_car(self):
        """创建像素风格车辆"""
        # 8位风格车辆图案
        car_pattern = [
            ['T', 'T', 'car_red', 'car_red', 'car_red', 'T', 'T'],
            ['T', 'car_red', 'white', 'white', 'white', 'car_red', 'T'],
            ['car_red', 'white', 'car_blue', 'car_blue', 'car_blue', 'white', 'car_red'],
            ['car_red', 'car_red', 'car_red', 'car_red', 'car_red', 'car_red', 'car_red'],
            ['black', 'T', 'black', 'T', 'black', 'T', 'black'],
        ]
        
        self.car_pixels = self.create_pixel_sprite(
            self.car_x - len(car_pattern[0]) * self.PIXEL_SIZE / 2,
            self.car_y - len(car_pattern) * self.PIXEL_SIZE / 2,
            car_pattern, self.PIXEL_SIZE
        )
    
    def create_pixel_dog(self):
        """创建像素风格狗 - 改进版更可爱"""
        # 8位风格狗的图案 - 更详细更可爱的设计
        dog_pattern = [
            ['dog_brown', 'dog_brown', 'T', 'dog_brown', 'dog_brown', 'T', 'dog_brown', 'dog_brown'],  # 更大更明显的耳朵
            ['dog_brown', 'dog_brown', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_brown', 'dog_brown'],  # 耳朵底部
            ['T', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'T'],  # 头部顶部
            ['dog_gold', 'dog_gold', 'white', 'black', 'black', 'white', 'dog_gold', 'dog_gold'],  # 眼睛
            ['dog_gold', 'dog_gold', 'dog_gold', 'black', 'black', 'dog_gold', 'dog_gold', 'dog_gold'],  # 鼻子
            ['dog_gold', 'dog_gold', 'black', 'pink', 'pink', 'black', 'dog_gold', 'dog_gold'],  # 嘴巴
            ['T', 'dog_gold', 'dog_gold', 'pink', 'pink', 'dog_gold', 'dog_gold', 'T'],  # 舌头
            ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],  # 脖子
            ['dog_gold', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_gold'],  # 身体上部
            ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],  # 身体下部
            ['T', 'dog_brown', 'T', 'dog_brown', 'dog_brown', 'T', 'dog_brown', 'T'],  # 四条腿
            ['T', 'black', 'T', 'black', 'black', 'T', 'black', 'T'],  # 爪子
        ]
        
        self.dog_pixels = self.create_pixel_sprite(
            self.dog_x - len(dog_pattern[0]) * self.DOG_PIXEL_SIZE / 2,
            self.dog_y - len(dog_pattern) * self.DOG_PIXEL_SIZE / 2,
            dog_pattern, self.DOG_PIXEL_SIZE
        )
    
    def create_pixel_ui(self):
        """创建像素风格UI界面"""
        # 信息面板背景 - 像素风格
        info_bg_pattern = []
        for y in range(8):
            row = []
            for x in range(20):
                if y == 0 or y == 7 or x == 0 or x == 19:
                    row.append('white')  # 边框
                else:
                    row.append('black')  # 内部
            info_bg_pattern.append(row)
        
        # 创建信息面板
        self.info_bg_pixels = self.create_pixel_sprite(0.2, 6.5, info_bg_pattern, 0.06)
        
        # 音量指示器背景
        volume_bg_pattern = []
        for y in range(4):
            row = []
            for x in range(25):
                if y == 0 or y == 3 or x == 0 or x == 24:
                    row.append('yellow')  # 边框
                else:
                    row.append('black')  # 内部
            volume_bg_pattern.append(row)
        
        self.volume_bg_pixels = self.create_pixel_sprite(6.5, 7.2, volume_bg_pattern, 0.06)
        
        # 音量条像素
        self.volume_pixels = []
        for i in range(23):  # 23个像素宽的音量条
            pixel = self.create_pixel_block(6.5 + 0.06 + i * 0.06, 7.2 + 0.06, 
                                          0.06, 'green')
            pixel.set_alpha(0)  # 初始隐藏
            self.volume_pixels.append(pixel)
        
        # 游戏说明 - 使用文字但像素风格字体
        self.info_text = self.ax.text(0.25, 7.7, '', fontsize=10, fontweight='bold', 
                                     color='lime', family='monospace',
                                     verticalalignment='top')
        
        self.volume_text = self.ax.text(6.6, 7.6, 'VOLUME', fontsize=12, fontweight='bold', 
                                       color='yellow', family='monospace')
    
    def add_pixel_decorations(self):
        """添加像素装饰元素"""
        # 像素化云朵
        cloud_pattern = [
            ['T', 'white', 'white', 'T'],
            ['white', 'white', 'white', 'white'],
            ['T', 'white', 'white', 'T'],
        ]
        
        # 添加几朵云
        cloud_positions = [(2, 6.5), (5, 7), (8, 6.8), (10, 7.2)]
        self.cloud_pixels = []
        for x, y in cloud_positions:
            clouds = self.create_pixel_sprite(x, y, cloud_pattern, 0.12)
            self.cloud_pixels.extend(clouds)
        
        # 像素化花朵
        flower_pattern = [
            ['T', 'pink', 'T'],
            ['pink', 'yellow', 'pink'],
            ['T', 'pink', 'T'],
            ['T', 'green', 'T'],
        ]
        
        # 添加路边花朵
        flower_positions = [(0.5, 1.2), (1.2, 1.5), (11, 1.3), (11.5, 1.8)]
        self.flower_pixels = []
        for x, y in flower_positions:
            flowers = self.create_pixel_sprite(x, y, flower_pattern, 0.08)
            self.flower_pixels.extend(flowers)
        
        # 像素化星星 (背景装饰)
        star_positions = [(1, 7.5), (3.5, 7.8), (9.5, 7.6), (11.2, 7.9)]
        self.star_pixels = []
        for x, y in star_positions:
            star = self.create_pixel_block(x, y, 0.1, 'white')
            self.star_pixels.append(star)
    
    def analyze_audio(self):
        """分析音频信号，返回音量级别"""
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.float32)
            # 计算音量（RMS）
            volume = np.sqrt(np.mean(audio_data**2))
            # 平滑音量（移动平均）
            self.volume_history.pop(0)
            self.volume_history.append(volume)
            smooth_volume = np.mean(self.volume_history)
            # 归一化音量到0-1范围
            normalized_volume = min(smooth_volume / self.max_volume, 1.0)
            # 如果音量低于阈值，使用最小速度
            if smooth_volume < self.volume_threshold:
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
        speed_increase = self.game_time * 0.00025  # 狗的加速度 - 加快加速
        self.dog_speed = self.base_dog_speed + speed_increase
        self.dog_x += self.dog_speed
        
        # 更新像素精灵位置
        self.update_pixel_sprites()
        
        # 更新音量指示器
        self.update_volume_display(volume_level)
        
        # 检查游戏结束条件
        if self.dog_x >= self.car_x:
            self.game_over = True
            print(f"💔 8-BIT DOG CAUGHT YOU! FINAL SCORE: {self.score}")
    
    def update_pixel_sprites(self):
        """更新像素精灵位置"""
        # 移除旧的像素
        for pixel in self.car_pixels:
            pixel.remove()
        for pixel in self.dog_pixels:
            pixel.remove()
        
        # 重新创建车辆像素
        car_pattern = [
            ['T', 'T', 'car_red', 'car_red', 'car_red', 'T', 'T'],
            ['T', 'car_red', 'white', 'white', 'white', 'car_red', 'T'],
            ['car_red', 'white', 'car_blue', 'car_blue', 'car_blue', 'white', 'car_red'],
            ['car_red', 'car_red', 'car_red', 'car_red', 'car_red', 'car_red', 'car_red'],
            ['black', 'T', 'black', 'T', 'black', 'T', 'black'],
        ]
        
        self.car_pixels = self.create_pixel_sprite(
            self.car_x - len(car_pattern[0]) * self.PIXEL_SIZE / 2,
            self.car_y - len(car_pattern) * self.PIXEL_SIZE / 2,
            car_pattern, self.PIXEL_SIZE
        )
        
        # 重新创建狗像素 - 根据时间添加动画效果
        # 每30帧切换一次狗的表情
        if (self.game_time // 30) % 2 == 0:
            # 正常可爱表情
            dog_pattern = [
                ['T', 'T', 'dog_brown', 'dog_brown', 'dog_brown', 'dog_brown', 'T', 'T'],  # 耳朵顶部
                ['T', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'T'],  # 耳朵
                ['dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown'],  # 头部顶部
                ['dog_gold', 'dog_gold', 'white', 'black', 'black', 'white', 'dog_gold', 'dog_gold'],  # 眼睛
                ['dog_gold', 'dog_gold', 'dog_gold', 'black', 'black', 'dog_gold', 'dog_gold', 'dog_gold'],  # 鼻子
                ['dog_gold', 'dog_gold', 'black', 'pink', 'pink', 'black', 'dog_gold', 'dog_gold'],  # 嘴巴
                ['T', 'dog_gold', 'dog_gold', 'pink', 'pink', 'dog_gold', 'dog_gold', 'T'],  # 舌头
                ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],  # 脖子
                ['dog_gold', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_gold'],  # 身体上部
                ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],  # 身体下部
                ['T', 'dog_brown', 'T', 'dog_brown', 'dog_brown', 'T', 'dog_brown', 'T'],  # 四条腿
                ['T', 'black', 'T', 'black', 'black', 'T', 'black', 'T'],  # 爪子
            ]
        else:
            # 兴奋追逐表情
            dog_pattern = [
                ['T', 'T', 'dog_brown', 'dog_brown', 'dog_brown', 'dog_brown', 'T', 'T'],  # 耳朵顶部
                ['T', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'T'],  # 耳朵
                ['dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown'],  # 头部顶部
                ['dog_gold', 'dog_gold', 'car_red', 'black', 'black', 'car_red', 'dog_gold', 'dog_gold'],  # 兴奋眼睛
                ['dog_gold', 'dog_gold', 'dog_gold', 'black', 'black', 'dog_gold', 'dog_gold', 'dog_gold'],  # 鼻子
                ['dog_gold', 'dog_gold', 'black', 'car_red', 'car_red', 'black', 'dog_gold', 'dog_gold'],  # 兴奋嘴巴
                ['T', 'dog_gold', 'car_red', 'pink', 'pink', 'car_red', 'dog_gold', 'T'],  # 兴奋舌头
                ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],  # 脖子
                ['dog_gold', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_gold'],  # 身体上部
                ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],  # 身体下部
                ['T', 'dog_brown', 'T', 'dog_brown', 'dog_brown', 'T', 'dog_brown', 'T'],  # 四条腿
                ['T', 'black', 'T', 'black', 'black', 'T', 'black', 'T'],  # 爪子
            ]
        
        self.dog_pixels = self.create_pixel_sprite(
            self.dog_x - len(dog_pattern[0]) * self.DOG_PIXEL_SIZE / 2,
            self.dog_y - len(dog_pattern) * self.DOG_PIXEL_SIZE / 2,
            dog_pattern, self.DOG_PIXEL_SIZE
        )
    
    def update_volume_display(self, volume_level):
        """更新音量显示"""
        # 更新音量条
        active_pixels = int(volume_level * len(self.volume_pixels))
        
        for i, pixel in enumerate(self.volume_pixels):
            if i < active_pixels:
                pixel.set_alpha(1)
                # 根据音量级别改变颜色
                if volume_level > 0.8:
                    pixel.set_facecolor('red')
                elif volume_level > 0.5:
                    pixel.set_facecolor('yellow')
                else:
                    pixel.set_facecolor('green')
            else:
                pixel.set_alpha(0)
    
    def update_dynamic_effects(self):
        """更新动态效果"""
        # 让中心线像素动起来
        dash_offset = (self.game_time // 10) % 4
        for i, pixel in enumerate(self.center_pixels):
            # 根据偏移量显示/隐藏像素
            if (i + dash_offset) % 8 < 4:
                pixel.set_alpha(1)
            else:
                pixel.set_alpha(0.3)
        
        # 让星星闪烁
        for i, star in enumerate(self.star_pixels):
            if (self.game_time + i * 10) % 60 < 30:
                star.set_alpha(1)
            else:
                star.set_alpha(0.5)
    
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
                # 创建像素风格游戏结束界面
                game_over_text = (
                    f"GAME OVER!\n\n"
                    f"DISTANCE: {self.score:.1f}M\n"
                    f"RATING: {'AWESOME!' if self.score > 500 else 'GREAT!' if self.score > 200 else 'TRY AGAIN!'}\n\n"
                    f"PRESS CTRL+C TO RESTART"
                )
                
                self.game_over_text = self.ax.text(
                    self.car_x, self.GAME_HEIGHT/2, 
                    game_over_text,
                    ha='center', va='center', 
                    fontsize=20, fontweight='bold',
                    color='red', family='monospace',
                    bbox=dict(boxstyle='round,pad=1', facecolor='black', alpha=0.9, 
                             edgecolor='red', linewidth=3)
                )
                
                # 添加像素风格游戏结束效果
                self.add_pixel_game_over_effects()
                
                self.game_over_displayed = True
            return
        
        # 更新位置
        self.update_positions()
        
        # 更新摄像机
        self.update_camera()
        
        # 更新动态效果
        self.update_dynamic_effects()
        
        # 更新分数（距离）
        self.score += self.car_speed * 10  # 分数基于移动距离
        
        # 计算距离差
        distance_diff = self.car_x - self.dog_x
        
        # 更新信息显示 - 像素风格
        volume_level = self.analyze_audio()
        info_text = (
            f"DIST: {self.score:.1f}M\n"
            f"SPEED: {self.car_speed*1000:.0f}\n"
            f"DOG: {self.dog_speed*1000:.0f}\n"
            f"LEAD: {distance_diff:.1f}M\n"
            f"VOL: {volume_level*100:.0f}%\n"
            f"TIME: {self.game_time//50:.0f}S"
        )
        self.info_text.set_text(info_text)
        
        # 危险警告效果 - 像素风格
        if distance_diff < 1.0:
            self.add_pixel_danger_effects()
    
    def add_pixel_game_over_effects(self):
        """添加像素风格游戏结束特效"""
        # 创建像素烟花效果
        explosion_pattern = [
            ['T', 'yellow', 'T'],
            ['yellow', 'white', 'yellow'],
            ['T', 'yellow', 'T'],
        ]
        
        # 在车辆周围创建爆炸效果
        for i in range(8):
            angle = i * 45  # 每45度一个爆炸
            radius = 1.5
            x = self.car_x + radius * np.cos(np.radians(angle))
            y = self.GAME_HEIGHT/2 + radius * np.sin(np.radians(angle))
            
            self.create_pixel_sprite(x, y, explosion_pattern, 0.1)
    
    def add_pixel_danger_effects(self):
        """添加像素风格危险警告效果"""
        # 让边框闪烁红色
        if self.game_time % 20 < 10:  # 每20帧闪烁一次
            # 创建红色边框像素
            for x in range(0, int(self.GAME_WIDTH / 0.2)):
                # 顶部边框
                self.create_pixel_block(x * 0.2, self.GAME_HEIGHT - 0.2, 0.2, 'red')
                # 底部边框
                self.create_pixel_block(x * 0.2, 0, 0.2, 'red')
            
            for y in range(0, int(self.GAME_HEIGHT / 0.2)):
                # 左边框
                self.create_pixel_block(0, y * 0.2, 0.2, 'red')
                # 右边框
                self.create_pixel_block(self.GAME_WIDTH - 0.2, y * 0.2, 0.2, 'red')
    
    def start_game(self):
        """开始游戏"""
        print("🕹️ PIXEL DOG CHASE GAME STARTED!")
        print("💡 8-BIT GAME INSTRUCTIONS:")
        print("   - MAKE LOUD SOUNDS TO SPEED UP!")
        print("   - LOUDER = FASTER!")
        print("   - STAY AHEAD OF THE PIXEL DOG!")
        print("   - DOG GETS FASTER OVER TIME!")
        print("   - DON'T GET CAUGHT!")
        print("   - CLOSE WINDOW OR PRESS CTRL+C TO EXIT")
        print("=" * 60)
        
        try:
            self.ani = animation.FuncAnimation(
                self.fig, self.game_loop, interval=25, 
                blit=False, cache_frame_data=False
            )
            plt.show()
        except KeyboardInterrupt:
            print("\n👋 PIXEL GAME INTERRUPTED")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("🧹 CLEANING UP PIXEL RESOURCES...")
        try:
            if hasattr(self, 'stream'):
                self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, 'p'):
                self.p.terminate()
        except Exception as e:
            print(f"CLEANUP ERROR: {e}")
        print("✅ PIXEL CLEANUP COMPLETE!")


def main():
    """主函数"""
    print("=" * 60)
    print("🕹️ PIXEL DOG CHASE GAME - 8-BIT EDITION")
    print("=" * 60)
    print("LOADING PIXEL WORLD...")
    
    try:
        game = PixelDogChaseGame()
        game.start_game()
    except KeyboardInterrupt:
        print("\nPIXEL GAME INTERRUPTED")
    except Exception as e:
        print(f"PIXEL GAME ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()