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
        self.CAR_SIZE = 0.2
        self.DOG_SIZE = 0.2
        self.PIXEL_SIZE = 0.08  # 像素块大小
        # 车辆像素大小（相对通用像素放大，车体更大一些）
        self.CAR_PIXEL_SIZE = self.PIXEL_SIZE * 1.15
        self.DOG_PIXEL_SIZE = 0.058  # 狗的像素块大小（更大）

        # 游戏状态（车在后，小狗在前）
        self.car_x = 0.5  # 车辆起始X位置（左侧更靠后）
        self.car_y = self.GAME_HEIGHT / 2
        self.dog_x = 2.0  # 狗起始位置在前面
        self.dog_y = self.GAME_HEIGHT / 2

        # 速度参数
        self.car_speed = 0.0
        # 车速更快，并随时间变快（后期更快）
        self.min_car_speed = 0.05
        self.max_car_speed = 0.60
        self.car_accel = 0.0014  # 车辆时间加速度（初期斜率，稍慢）
        # 后期加速阶段（让后期更快）：约10秒后提升加速度
        self.late_game_frames = 400  # 约 400*25ms ≈ 10s 后
        self.late_car_accel = 0.0019  # 后期斜率稍慢
        
        # 小狗速度由音量控制（越大越快） — 适当放慢增长速度并柔化响应
        self.dog_min_speed = 0.03
        self.dog_max_speed = 0.125
        self.dog_speed_exponent = 1.6  # 略增大指数：中段更慢，整体更稳
        self.dog_speed = self.dog_min_speed

        self.score = 0
        self.game_over = False
        self.game_time = 0

        # 音频控制参数
        self.FORMAT = pyaudio.paInt16  # 16-bit PCM

        # 音量控制（归一化到0..1）——降低敏感度：提高门限、扩大归一化分母、加长平滑窗口
        self.volume_threshold = 0.004   # 原 0.0008 → 更不易触发
        self.max_volume = 0.06            # 原 0.04 → 同样RMS得到更低的归一化值
        self.volume_history = [0.0] * 20 # 原 12 帧 → 更平滑、更稳

        # 摄像机固定在初始画面
        self.prev_camera_left = 0.0
        self.freeze_camera = False
        self.freeze_camera_left = None

        # 终点：小狗的目标线
        self.finish_x = self.GAME_WIDTH - 1.0
        # 规则：不要撞到小狗，小狗安全到达终点即胜利
        self.mission_success = False  # True: 小狗安全到达终点
        self.dog_escaped = False      # True: 小狗到达终点
        self.dog_hit = False          # True: 车辆撞到小狗（失败）
        self.catch_margin = 0.2       # 碰撞判定的间距

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
        self.ax.set_title('Dog Run Run Run', fontsize=24, fontweight='bold',
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

    def create_pixel_block(self, x, y, size, color, edge_color=None, linewidth=1, antialiased=None):
        """创建单个像素块
        可选参数：
        - edge_color: 边框颜色（默认与填充色相同）
        - linewidth: 边框线宽
        - antialiased: 是否抗锯齿（None 表示使用默认，False 可获得更“像素”的锐利边缘）
        """
        if edge_color is None:
            edge_color = color
        rect_kwargs = dict(facecolor=color, edgecolor=edge_color, linewidth=linewidth)
        if antialiased is not None:
            rect_kwargs["antialiased"] = antialiased
        pixel = patches.Rectangle((x, y), size, size, **rect_kwargs)
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
            ['T', 'black', 'T', 'T', 'T', 'black', 'T'],
        ]
        self.car_pixels = self.create_pixel_sprite(
            self.car_x - len(car_pattern[0]) * self.CAR_PIXEL_SIZE / 2,
            self.car_y - len(car_pattern) * self.CAR_PIXEL_SIZE / 2,
            car_pattern, self.CAR_PIXEL_SIZE
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
        # 左上角信息框：贴合显示区域，刚好框住信息
        info_rows, info_cols = 20, 32  # 高度与宽度（边框+内容）
        info_size = 0.06               # 单元格尺寸
        info_x, info_y = 0.12, 6.80    # 左下角坐标
        info_bg_pattern = []
        for y in range(info_rows):
            row = []
            for x in range(info_cols):
                row.append('white' if (y == 0 or y == info_rows - 1 or x == 0 or x == info_cols - 1) else 'black')
            info_bg_pattern.append(row)
        self.info_bg_pixels = self.create_pixel_sprite(info_x, info_y, info_bg_pattern, info_size)

        # 音量可视化：放在信息框右侧，紧挨着信息栏
        volume_bg_pattern = []
        for y in range(4):
            row = []
            for x in range(25):
                row.append('yellow' if (y == 0 or y == 3 or x == 0 or x == 24) else 'black')
            volume_bg_pattern.append(row)
        volume_x = info_x + info_cols * info_size + 0.12  # 紧邻信息栏，右侧留一点间距
        volume_y = info_y + 0.40                          # 与原来大致同高度
        volume_cell = 0.06
        self.volume_bg_pixels = self.create_pixel_sprite(volume_x, volume_y, volume_bg_pattern, volume_cell)

        # 严格限制在边框内部，最多100%
        self.volume_pixels = []
        for i in range(23):
            # 进度条像素：黑色描边，关闭抗锯齿，显得更“像素风”
            pixel = self.create_pixel_block(
                volume_x + volume_cell + i * volume_cell,
                volume_y + volume_cell,
                volume_cell,
                'lime',
                edge_color='black',
                linewidth=1.2,
                antialiased=False
            )
            pixel.set_alpha(0)
            self.volume_pixels.append(pixel)

        # 信息文字放在边框内，留出一个像素单元的内边距
        self.info_text = self.ax.text(
            info_x + info_size * 2.0,
            info_y + info_rows * info_size - info_size * 3.5,
            '', fontsize=10, fontweight='bold',
            color='lime', family='monospace',
            verticalalignment='top'
        )
        # 标题放在音量条上方一些
        self.volume_text = self.ax.text(
            volume_x + 0.10, volume_y + volume_cell * 6,
            'VOLUME', fontsize=12, fontweight='bold',
            color='yellow', family='monospace'
        )

        self.hud_groups = [self.info_bg_pixels, self.volume_bg_pixels, self.volume_pixels]
        self.hud_texts = [self.info_text, self.volume_text]

    def add_pixel_decorations(self):
        """添加像素装饰元素"""
        cloud_pattern = [
            ['T', 'white', 'white', 'T'],
            ['white', 'white', 'white', 'white'],
            ['T', 'white', 'white', 'T'],
        ]
        cloud_positions = [(2, 8.5), (5, 7), (8, 6.8), (10, 7.2)]
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

        star_positions = [(6, 7.5), (3.5, 7.8), (9.5, 7.6), (11.2, 7.9)]
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

        # 计时（用于车辆加速）
        self.game_time += 1

        # 车辆速度：随时间逐渐变快，直到最大值（首帧不叠加加速度，避免突兀加速感）
        effective_time = max(0, self.game_time - 1)
        # 分段加速：前期使用 car_accel，超过阈值后使用 late_car_accel（避免斜率回溯导致突然跳变）
        if effective_time <= self.late_game_frames:
            car_v = self.min_car_speed + self.car_accel * effective_time
        else:
            car_v = (self.min_car_speed
                     + self.car_accel * self.late_game_frames
                     + self.late_car_accel * (effective_time - self.late_game_frames))
        self.car_speed = min(car_v, self.max_car_speed)

        # 小狗速度：由音量控制（越大越快），应用次线性映射减弱中段速度
        level_adj = volume_level ** self.dog_speed_exponent
        self.dog_speed = self.dog_min_speed + (self.dog_max_speed - self.dog_min_speed) * level_adj

        # 前进
        self.car_x += self.car_speed
        self.dog_x += self.dog_speed

        # 限制车辆在赛道内（与初始位置一致，避免首帧被强制夹到x=1产生抖动）
        self.car_x = max(0.5, min(self.GAME_WIDTH - 0.5, self.car_x))

        # 更新像素精灵位置
        self.update_pixel_sprites()
        self.update_volume_display(volume_level)

        # 失败：撞到小狗
        if not self.game_over and self.car_x + self.catch_margin >= self.dog_x:
            self.game_over = True
            self.dog_hit = True
            self.mission_success = False
            self.freeze_camera = True
            if self.freeze_camera_left is None:
                self.freeze_camera_left = self.prev_camera_left
            print("🚫 THE DOG DIED. MISSION FAILED.")

        # 成功：小狗安全到达终点
        if not self.game_over and self.dog_x >= self.finish_x:
            self.game_over = True
            self.mission_success = True
            self.dog_escaped = True
            self.freeze_camera = True
            if self.freeze_camera_left is None:
                self.freeze_camera_left = self.prev_camera_left
            print("🏁🐶 DOG IS SAFE! MISSION SUCCESS!")

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
            ['T', 'black', 'T', 'T', 'T', 'black', 'T'],
        ]
        self.car_pixels = self.create_pixel_sprite(
            self.car_x - len(car_pattern[0]) * self.CAR_PIXEL_SIZE / 2,
            self.car_y - len(car_pattern) * self.CAR_PIXEL_SIZE / 2,
            car_pattern, self.CAR_PIXEL_SIZE
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
        total = len(self.volume_pixels)
        # 形态按0%~100%线性增长，满格对应100%
        active_pixels = int(volume_level * total)
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
                        f"DOG IS SAFE!\n\n"
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
                        f"THE DOG DIED. MISSION FAILED.\n\n"
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
            f"VOL: {min(int(round(volume_level*100)), 100)}%  RAW:{raw_vol:.3f}"
        )
        self.info_text.set_text(info_text)

        # 危险提示：与小狗距离过近，可能发生碰撞
        if gap < 0.6:
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
        print("   - LOUDER = DOG FASTER!")
        print("   - CAR SPEEDS UP OVER TIME!")
        print("   - DON'T HIT THE DOG!")
        print("   - LET THE DOG REACH THE FINISH SAFELY!")
        print("   - CLOSE WINDOW OR PRESS CTRL+C TO EXIT")
        print("=" * 60)

        try:
            self.ani = animation.FuncAnimation(
                self.fig, self.game_loop, interval=25,
                blit=False, cache_frame_data=False
            )
            plt.show()
        except KeyboardInterrupt:
            # 将中断交由上层处理（用于在游戏结束后按 Ctrl+C 触发重开）
            raise
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
            # 关闭图形窗口，避免多次重启时累计窗口
            try:
                plt.close(self.fig)
            except Exception:
                pass
        except Exception as e:
            print(f"CLEANUP ERROR: {e}")
        print("✅ PIXEL CLEANUP COMPLETE!")


def main():
    """主函数：支持在游戏结束后按 Ctrl+C 快速重开"""
    while True:
        print("=" * 60)
        print("🕹️ PIXEL CAR CHASE DOG - 8-BIT EDITION")
        print("=" * 60)
        print("LOADING PIXEL WORLD...")

        game = None
        try:
            game = PixelCarChaseDogGame()
            game.start_game()
            # 若窗口正常关闭或未被中断，退出循环
            break
        except KeyboardInterrupt:
            # 只有当游戏已经结束（胜利或失败）时，使用 Ctrl+C 触发重开
            if game is not None and getattr(game, 'game_over', False):
                print("\n🔁 RESTARTING GAME (Ctrl+C after game over)...")
                continue
            else:
                print("\nPIXEL GAME INTERRUPTED")
                break
        except Exception as e:
            print(f"PIXEL GAME ERROR: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
