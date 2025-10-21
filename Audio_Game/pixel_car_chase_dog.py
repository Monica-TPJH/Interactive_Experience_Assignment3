#!/usr/bin/env python3
"""
Pixel Car Chase Dog Game - 像素风车追狗游戏
8-bit style sound-controlled chasing game where you (the car) must catch the dog

控制方式：
- 声音越大：车辆越快
- 安静：车辆慢速移动
- 目标：追上前方的小狗，别让它跑到终点！

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


class PixelCarChaseDogGame:
    def __init__(self):
        # 音频参数
        self.RATE = 44100
        self.CHUNK = 1024
        self.CHANNELS = 1

        # 游戏参数
        self.GAME_WIDTH = 12
        self.GAME_HEIGHT = 8
        self.CAR_SIZE = 0.4
        self.DOG_SIZE = 0.3
        self.PIXEL_SIZE = 0.08  # 像素块大小
        self.DOG_PIXEL_SIZE = 0.06  # 狗的像素块大小（更小）

        # 游戏状态（车在后，小狗在前）
        self.car_x = 0.5  # 车辆起始X位置（左侧更靠后）
        self.car_y = self.GAME_HEIGHT / 2
        self.dog_x = 2.0  # 狗起始位置在前面
        self.dog_y = self.GAME_HEIGHT / 2

        self.car_speed = 0
        # 让小狗有稳定前进速度并逐渐加速，但不要过快
        self.base_dog_speed = 0.08
        self.dog_speed = self.base_dog_speed
        self.dog_accel = 0.00018
        self.score = 0
        self.game_over = False
        self.game_time = 0

        # 音频控制参数
        self.FORMAT = pyaudio.paInt16  # 16-bit PCM

        # 音量控制（归一化到0..1）
        self.volume_threshold = 0.0003
        self.max_volume = 0.04
        self.volume_history = [0.0] * 8
        self.min_car_speed = 0.07
        self.max_car_speed = 0.22

        # 摄像机固定在初始画面
        self.prev_camera_left = 0.0
        self.freeze_camera = False
        self.freeze_camera_left = None

        # 终点：小狗的目标线（车需在其到达前抓到）
        self.finish_x = self.GAME_WIDTH - 1.0
        self.mission_success = False  # True: 抓到小狗
        self.dog_escaped = False      # True: 小狗到达终点
        self.catch_margin = 0.3       # 抓捕判定的间距

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

        # 初始化音频与图形
        self.setup_audio()

    def setup_audio(self):
        """初始化音频系统"""
        self.p = pyaudio.PyAudio()

        # 初始化图形
        self.setup_graphics()

        # 选择输入设备
        input_devices = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels', 0) > 0:
                input_devices.append((i, device_info))

        if input_devices:
            print("可用输入设备:")
            for idx, info in input_devices:
                print(f"  - index={idx}, name={info.get('name')}, channels={info.get('maxInputChannels')}, defaultSR={info.get('defaultSampleRate')}")

        try:
            default_info = self.p.get_default_input_device_info()
            input_device = default_info.get('index')
            print(f"优先选择系统默认输入设备: index={input_device}, name={default_info.get('name')}")
        except Exception:
            input_device = None

        if input_device is None and input_devices:
            preferred_names = ['Built-in Microphone', 'MacBook', 'Microphone', '内建麦克风']
            for idx, info in input_devices:
                name = (info.get('name') or '').lower()
                if any(p.lower() in name for p in preferred_names):
                    input_device = idx
                    print(f"匹配到首选麦克风: index={idx}, name={info.get('name')}")
                    break

        if input_device is None and input_devices:
            input_device = input_devices[0][0]
            print(f"使用第一个可用输入设备: index={input_device}, name={input_devices[0][1].get('name')}")

        if input_device is None:
            print("❌ 未找到音频输入设备!")
            sys.exit(1)

        try:
            print(f"[DEBUG] 选择的音频输入设备: index={input_device}, name={self.p.get_device_info_by_index(input_device).get('name')}")
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

        self.ax.set_xlim(0, self.GAME_WIDTH)
        self.ax.set_ylim(0, self.GAME_HEIGHT)
        self.ax.set_aspect('equal')
        self.ax.set_title('🕹️ PIXEL CAR CHASE DOG - 8-BIT EDITION', fontsize=24, fontweight='bold',
                          color='white', pad=20, family='monospace')

        self.fig.patch.set_facecolor('#000033')
        self.ax.set_facecolor('#000033')

        self.create_pixel_background()
        self.ax.axis('off')

        self.create_pixel_track()
        # 终点线（狗的目标）
        self.create_finish_line()

        self.create_pixel_car()
        self.create_pixel_dog()
        self.create_pixel_ui()
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
                if color != 'T':
                    pixel_x = x + col_idx * size
                    pixel_y = y + (len(pattern) - 1 - row_idx) * size
                    pixel = self.create_pixel_block(pixel_x, pixel_y, size,
                                                    self.pixel_colors.get(color, color))
                    pixels.append(pixel)
        return pixels

    def create_pixel_background(self):
        """创建像素风格背景"""
        for x in range(0, int(self.GAME_WIDTH / self.PIXEL_SIZE)):
            for y in range(int(6 / self.PIXEL_SIZE), int(self.GAME_HEIGHT / self.PIXEL_SIZE)):
                if y % 3 == 0:
                    color = '#4169E1'
                elif y % 3 == 1:
                    color = '#6495ED'
                else:
                    color = '#87CEEB'
                self.create_pixel_block(x * self.PIXEL_SIZE, y * self.PIXEL_SIZE,
                                        self.PIXEL_SIZE, color)

        for x in range(0, int(self.GAME_WIDTH / self.PIXEL_SIZE)):
            for y in range(0, int(2 / self.PIXEL_SIZE)):
                color = '#228B22' if (x + y) % 2 == 0 else '#32CD32'
                self.create_pixel_block(x * self.PIXEL_SIZE, y * self.PIXEL_SIZE,
                                        self.PIXEL_SIZE, color)

    def create_pixel_track(self):
        """创建像素化赛道"""
        track_y_start = int(2 / self.PIXEL_SIZE)
        track_y_end = int(6 / self.PIXEL_SIZE)

        for x in range(int(0.5 / self.PIXEL_SIZE), int((self.GAME_WIDTH - 0.5) / self.PIXEL_SIZE)):
            for y in range(track_y_start, track_y_end):
                if y == track_y_start or y == track_y_end - 1:
                    color = '#FFD700'
                elif (x + y) % 4 == 0:
                    color = '#404040'
                elif (x + y) % 4 == 2:
                    color = '#505050'
                else:
                    color = '#606060'
                self.create_pixel_block(x * self.PIXEL_SIZE, y * self.PIXEL_SIZE,
                                        self.PIXEL_SIZE, color)

        self.center_pixels = []
        center_y = int(4 / self.PIXEL_SIZE)
        for x in range(1, int(self.GAME_WIDTH / self.PIXEL_SIZE), 4):
            for i in range(2):
                pixel = self.create_pixel_block((x + i) * self.PIXEL_SIZE,
                                                center_y * self.PIXEL_SIZE,
                                                self.PIXEL_SIZE, '#FFFF00')
                self.center_pixels.append(pixel)

    def create_finish_line(self):
        """创建终点线（狗的目标，棋盘格）"""
        line_x = max(self.PIXEL_SIZE, self.finish_x - 0.2)
        start_y = 2.0
        end_y = 6.0
        size = self.PIXEL_SIZE
        y = start_y
        toggle = 0
        self.finish_pixels = []
        while y < end_y:
            color = '#000000' if toggle % 2 == 0 else '#FFFFFF'
            px = self.create_pixel_block(line_x, y, size, color, edge_color=color)
            self.finish_pixels.append(px)
            px2 = self.create_pixel_block(line_x + size, y, size,
                                          ('#FFFFFF' if color == '#000000' else '#000000'),
                                          edge_color=('#FFFFFF' if color == '#000000' else '#000000'))
            self.finish_pixels.append(px2)
            y += size
            toggle += 1

    def create_pixel_car(self):
        """创建像素风格车辆"""
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
        """创建像素风格狗"""
        dog_pattern = [
            ['dog_brown', 'dog_brown', 'dog_brown', 'T', 'T', 'dog_brown', 'dog_brown', 'dog_brown'],
            ['dog_brown', 'dog_brown', 'dog_brown', 'T', 'T', 'dog_brown', 'dog_brown', 'dog_brown'],
            ['T', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'T'],
            ['dog_gold', 'dog_gold', 'white', 'black', 'black', 'white', 'dog_gold', 'dog_gold'],
            ['dog_gold', 'dog_gold', 'dog_gold', 'black', 'black', 'dog_gold', 'dog_gold', 'dog_gold'],
            ['dog_gold', 'dog_gold', 'black', 'pink', 'pink', 'black', 'dog_gold', 'dog_gold'],
            ['T', 'dog_gold', 'dog_gold', 'pink', 'pink', 'dog_gold', 'dog_gold', 'T'],
            ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],
            ['dog_gold', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_gold'],
            ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],
            ['T', 'dog_brown', 'T', 'dog_brown', 'dog_brown', 'T', 'dog_brown', 'T'],
            ['T', 'black', 'T', 'black', 'black', 'T', 'black', 'T'],
        ]
        self.dog_pixels = self.create_pixel_sprite(
            self.dog_x - len(dog_pattern[0]) * self.DOG_PIXEL_SIZE / 2,
            self.dog_y - len(dog_pattern) * self.DOG_PIXEL_SIZE / 2,
            dog_pattern, self.DOG_PIXEL_SIZE
        )

    def create_pixel_ui(self):
        """创建像素风格UI界面"""
        info_bg_pattern = []
        for y in range(8):
            row = []
            for x in range(20):
                row.append('white' if (y == 0 or y == 7 or x == 0 or x == 19) else 'black')
            info_bg_pattern.append(row)
        self.info_bg_pixels = self.create_pixel_sprite(0.2, 6.5, info_bg_pattern, 0.06)

        volume_bg_pattern = []
        for y in range(4):
            row = []
            for x in range(25):
                row.append('yellow' if (y == 0 or y == 3 or x == 0 or x == 24) else 'black')
            volume_bg_pattern.append(row)
        self.volume_bg_pixels = self.create_pixel_sprite(6.5, 7.2, volume_bg_pattern, 0.06)

        # 严格限制在边框内部，最多100%
        self.volume_pixels = []
        for i in range(23):
            pixel = self.create_pixel_block(6.5 + 0.06 + i * 0.06, 7.2 + 0.06, 0.06, 'lime')
            pixel.set_alpha(0)
            self.volume_pixels.append(pixel)

        self.info_text = self.ax.text(0.25, 7.7, '', fontsize=10, fontweight='bold',
                                      color='lime', family='monospace',
                                      verticalalignment='top')
        self.volume_text = self.ax.text(6.6, 7.6, 'VOLUME', fontsize=12, fontweight='bold',
                                        color='yellow', family='monospace')

        self.hud_groups = [self.info_bg_pixels, self.volume_bg_pixels, self.volume_pixels]
        self.hud_texts = [self.info_text, self.volume_text]

    def add_pixel_decorations(self):
        """添加像素装饰元素"""
        cloud_pattern = [
            ['T', 'white', 'white', 'T'],
            ['white', 'white', 'white', 'white'],
            ['T', 'white', 'white', 'T'],
        ]
        cloud_positions = [(2, 6.5), (5, 7), (8, 6.8), (10, 7.2)]
        self.cloud_pixels = []
        for x, y in cloud_positions:
            clouds = self.create_pixel_sprite(x, y, cloud_pattern, 0.12)
            self.cloud_pixels.extend(clouds)

        flower_pattern = [
            ['T', 'pink', 'T'],
            ['pink', 'yellow', 'pink'],
            ['T', 'pink', 'T'],
            ['T', 'green', 'T'],
        ]
        flower_positions = [(0.5, 1.2), (1.2, 1.5), (11, 1.3), (11.5, 1.8)]
        self.flower_pixels = []
        for x, y in flower_positions:
            flowers = self.create_pixel_sprite(x, y, flower_pattern, 0.08)
            self.flower_pixels.extend(flowers)

        star_positions = [(1, 7.5), (3.5, 7.8), (9.5, 7.6), (11.2, 7.9)]
        self.star_pixels = []
        for x, y in star_positions:
            star = self.create_pixel_block(x, y, 0.1, 'white')
            self.star_pixels.append(star)

    def analyze_audio(self):
        """分析音频信号，返回音量级别"""
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            if audio_data.size == 0:
                return 0.0
            audio_float = audio_data.astype(np.float32) / 32768.0
            volume = float(np.sqrt(np.mean(np.square(audio_float))))
            self.volume_history.pop(0)
            self.volume_history.append(volume)
            smooth_volume = float(np.mean(self.volume_history))
            normalized_volume = min(smooth_volume / float(self.max_volume), 1.0)
            if smooth_volume < self.volume_threshold:
                normalized_volume = 0.0
            self.last_raw_volume = smooth_volume
            self.last_volume = normalized_volume
            print(f"[DEBUG] 原始RMS: {smooth_volume:.5f} | 归一化: {normalized_volume:.3f}")
            return normalized_volume
        except Exception as e:
            print(f"音频分析错误: {e}")
            return getattr(self, 'last_volume', 0.0)

    def update_positions(self):
        """更新车辆和狗的位置（车追狗）"""
        volume_level = self.analyze_audio()
        self.car_speed = self.min_car_speed + (self.max_car_speed - self.min_car_speed) * volume_level

        # 前进
        self.car_x += self.car_speed

        # 限制车辆在赛道内
        self.car_x = max(1, min(self.GAME_WIDTH - 1, self.car_x))

        # 狗前进并加速
        self.game_time += 1
        self.dog_speed = self.base_dog_speed + self.game_time * self.dog_accel
        self.dog_x += self.dog_speed

        # 更新像素精灵位置
        self.update_pixel_sprites()
        self.update_volume_display(volume_level)

        # 成功：车追上狗
        if not self.game_over and self.car_x + self.catch_margin >= self.dog_x:
            self.game_over = True
            self.mission_success = True
            self.freeze_camera = True
            if self.freeze_camera_left is None:
                self.freeze_camera_left = self.prev_camera_left
            print("🏁🚗 CAUGHT THE DOG! MISSION SUCCESS!")

        # 失败：狗到达终点
        if not self.game_over and self.dog_x >= self.finish_x:
            self.game_over = True
            self.dog_escaped = True
            self.freeze_camera = True
            if self.freeze_camera_left is None:
                self.freeze_camera_left = self.prev_camera_left
            print("💨🐶 DOG ESCAPED! TRY AGAIN!")

    def update_pixel_sprites(self):
        """更新像素精灵位置"""
        for pixel in getattr(self, 'car_pixels', []):
            pixel.remove()
        for pixel in getattr(self, 'dog_pixels', []):
            pixel.remove()

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

        # 狗表情在追逐中也变化
        if (self.game_time // 90) % 2 == 0:
            dog_pattern = [
                ['dog_brown', 'dog_brown', 'dog_brown', 'T', 'T', 'dog_brown', 'dog_brown', 'dog_brown'],
                ['dog_brown', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_brown'],
                ['dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown'],
                ['dog_gold', 'dog_gold', 'white', 'black', 'black', 'white', 'dog_gold', 'dog_gold'],
                ['dog_gold', 'dog_gold', 'dog_gold', 'black', 'black', 'dog_gold', 'dog_gold', 'dog_gold'],
                ['dog_gold', 'dog_gold', 'black', 'pink', 'pink', 'black', 'dog_gold', 'dog_gold'],
                ['T', 'dog_gold', 'dog_gold', 'pink', 'pink', 'dog_gold', 'dog_gold', 'T'],
                ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],
                ['dog_gold', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_gold'],
                ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],
                ['T', 'dog_brown', 'T', 'dog_brown', 'dog_brown', 'T', 'dog_brown', 'T'],
                ['T', 'black', 'T', 'black', 'black', 'T', 'black', 'T'],
            ]
        else:
            dog_pattern = [
                ['dog_brown', 'dog_brown', 'dog_brown', 'T', 'T', 'dog_brown', 'dog_brown', 'dog_brown'],
                ['dog_brown', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_brown'],
                ['dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown'],
                ['dog_gold', 'dog_gold', 'car_red', 'black', 'black', 'car_red', 'dog_gold', 'dog_gold'],
                ['dog_gold', 'dog_gold', 'dog_gold', 'black', 'black', 'dog_gold', 'dog_gold', 'dog_gold'],
                ['dog_gold', 'dog_gold', 'black', 'car_red', 'car_red', 'black', 'dog_gold', 'dog_gold'],
                ['T', 'dog_gold', 'car_red', 'pink', 'pink', 'car_red', 'dog_gold', 'T'],
                ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],
                ['dog_gold', 'dog_brown', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_brown', 'dog_gold'],
                ['dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold', 'dog_gold'],
                ['T', 'dog_brown', 'T', 'dog_brown', 'dog_brown', 'T', 'dog_brown', 'T'],
                ['T', 'black', 'T', 'black', 'black', 'T', 'black', 'T'],
            ]
        self.dog_pixels = self.create_pixel_sprite(
            self.dog_x - len(dog_pattern[0]) * self.DOG_PIXEL_SIZE / 2,
            self.dog_y - len(dog_pattern) * self.DOG_PIXEL_SIZE / 2,
            dog_pattern, self.DOG_PIXEL_SIZE
        )

    def update_volume_display(self, volume_level):
        """更新音量显示"""
        volume_level = max(0.0, min(float(volume_level), 1.0))
        active_pixels = int(volume_level * len(self.volume_pixels))
        if volume_level > 0.0 and active_pixels == 0:
            active_pixels = 1
        for i, pixel in enumerate(self.volume_pixels):
            if i < active_pixels:
                pixel.set_alpha(1)
                if volume_level > 0.8:
                    pixel.set_facecolor('red')
                elif volume_level > 0.5:
                    pixel.set_facecolor('orange')
                else:
                    pixel.set_facecolor('lime')
            else:
                pixel.set_alpha(0)

    def update_dynamic_effects(self):
        """更新动态效果"""
        dash_offset = (self.game_time // 10) % 4
        for i, pixel in enumerate(self.center_pixels):
            pixel.set_alpha(1 if (i + dash_offset) % 8 < 4 else 0.3)
        for i, star in enumerate(self.star_pixels):
            star.set_alpha(1 if (self.game_time + i * 10) % 60 < 30 else 0.5)

    def update_camera(self):
        """更新摄像机视角（固定）"""
        camera_x = 0.0
        dx = camera_x - self.prev_camera_left
        self.ax.set_xlim(camera_x, camera_x + self.GAME_WIDTH)
        if dx != 0:
            self.shift_hud(dx)
        self.prev_camera_left = camera_x

    def shift_hud(self, dx):
        """HUD随相机平移"""
        try:
            for group in self.hud_groups:
                for rect in group:
                    x, y = rect.get_xy()
                    rect.set_xy((x + dx, y))
            for txt in self.hud_texts:
                x, y = txt.get_position()
                txt.set_position((x + dx, y))
        except Exception:
            pass

    def game_loop(self, frame):
        """主游戏循环"""
        if self.game_over:
            if not hasattr(self, 'game_over_displayed'):
                if getattr(self, 'mission_success', False):
                    success_text = (
                        f"CAUGHT THE DOG!\n\n"
                        f"DISTANCE: {self.score:.1f}M\n"
                        f"RATING: {'LEGEND!' if self.score > 700 else 'AWESOME!' if self.score > 500 else 'GREAT!'}\n\n"
                        f"PRESS CTRL+C TO RESTART"
                    )
                    self.game_over_text = self.ax.text(
                        self.car_x, self.GAME_HEIGHT/2,
                        success_text,
                        ha='center', va='center',
                        fontsize=20, fontweight='bold',
                        color='lime', family='monospace',
                        bbox=dict(boxstyle='round,pad=1', facecolor='black', alpha=0.9,
                                  edgecolor='lime', linewidth=3)
                    )
                    self.add_pixel_success_effects()
                else:
                    game_over_text = (
                        f"DOG ESCAPED!\n\n"
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
                    self.add_pixel_game_over_effects()
                self.game_over_displayed = True
            return

        self.update_positions()
        self.update_camera()
        self.update_dynamic_effects()

        # 分数基于车辆移动距离
        self.score += self.car_speed * 10

        # 间距与剩余距离
        gap = max(0.0, self.dog_x - self.car_x)
        to_finish = max(0.0, self.finish_x - self.dog_x)

        volume_level = getattr(self, 'last_volume', 0.0)
        raw_vol = getattr(self, 'last_raw_volume', 0.0)
        info_text = (
            f"DIST: {self.score:.1f}M\n"
            f"SPEED: {self.car_speed*1000:.0f}\n"
            f"DOG: {self.dog_speed*1000:.0f}\n"
            f"GAP: {gap:.1f}M  LEFT:{to_finish:.1f}M\n"
            f"VOL: {min(int(round(volume_level*100)), 100)}%  RAW:{raw_vol:.3f}\n"
            f"TIME: {self.game_time//50:.0f}S"
        )
        self.info_text.set_text(info_text)

        # 危险提示：小狗接近终点或距离拉大
        if to_finish < 1.0 or gap > 2.0:
            self.add_pixel_danger_effects()

    def add_pixel_game_over_effects(self):
        """像素风格失败特效（红色爆炸）"""
        explosion_pattern = [
            ['T', 'yellow', 'T'],
            ['yellow', 'white', 'yellow'],
            ['T', 'yellow', 'T'],
        ]
        for i in range(8):
            angle = i * 45
            radius = 1.5
            x = self.car_x + radius * np.cos(np.radians(angle))
            y = self.GAME_HEIGHT/2 + radius * np.sin(np.radians(angle))
            self.create_pixel_sprite(x, y, explosion_pattern, 0.1)

    def add_pixel_danger_effects(self):
        """像素风格危险警告效果（红色闪烁边框）"""
        if self.game_time % 20 < 10:
            for x in range(0, int(self.GAME_WIDTH / 0.2)):
                self.create_pixel_block(x * 0.2, self.GAME_HEIGHT - 0.2, 0.2, 'red')
                self.create_pixel_block(x * 0.2, 0, 0.2, 'red')
            for y in range(0, int(self.GAME_HEIGHT / 0.2)):
                self.create_pixel_block(0, y * 0.2, 0.2, 'red')
                self.create_pixel_block(self.GAME_WIDTH - 0.2, y * 0.2, 0.2, 'red')

    def add_pixel_success_effects(self):
        """像素风格胜利特效（绿色烟花+奖杯）"""
        explosion_pattern = [
            ['T', 'lime', 'T'],
            ['lime', 'white', 'lime'],
            ['T', 'lime', 'T'],
        ]
        for i in range(10):
            angle = i * 36
            radius = 1.8
            x = self.car_x + radius * np.cos(np.radians(angle))
            y = self.GAME_HEIGHT/2 + radius * np.sin(np.radians(angle))
            self.create_pixel_sprite(x, y, explosion_pattern, 0.1)

        trophy = [
            ['T','yellow','yellow','yellow','T'],
            ['yellow','yellow','white','yellow','yellow'],
            ['yellow','yellow','yellow','yellow','yellow'],
            ['T','yellow','yellow','yellow','T'],
            ['T','T','yellow','T','T'],
            ['T','T','yellow','T','T'],
            ['T','yellow','yellow','yellow','T'],
        ]
        self.create_pixel_sprite(self.car_x - 0.25, self.GAME_HEIGHT/2 + 1.2, trophy, 0.12)

    def start_game(self):
        """开始游戏"""
        print("🕹️ PIXEL CAR CHASE DOG GAME STARTED!")
        print("💡 8-BIT GAME INSTRUCTIONS:")
        print("   - MAKE LOUD SOUNDS TO SPEED UP!")
        print("   - CATCH THE DOG BEFORE IT REACHES THE FINISH!")
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
    print("🕹️ PIXEL CAR CHASE DOG - 8-BIT EDITION")
    print("=" * 60)
    print("LOADING PIXEL WORLD...")

    try:
        game = PixelCarChaseDogGame()
        game.start_game()
    except KeyboardInterrupt:
        print("\nPIXEL GAME INTERRUPTED")
    except Exception as e:
        print(f"PIXEL GAME ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
