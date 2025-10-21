#!/usr/bin/env python3
"""
Face Avatar Pixel Car Chase Dog Game

功能:
- 启动前先用摄像头录入人脸, 成功后将人脸转换为像素风头像
- 识别好的人脸头像显示在游戏右侧区域
- 必须录入成功后才开始游戏

依赖: opencv-python, numpy, matplotlib, pyaudio (游戏已使用)

用法:
- 直接运行本文件。摄像头窗口中按 C 键拍摄, 按 Q 键退出
"""

import time
from typing import Optional, Tuple

import numpy as np

try:
    import cv2
except Exception:
    print("需要安装 OpenCV: pip install opencv-python")
    raise

try:
    from pixel_car_chase_dog import PixelCarChaseDogGame
except Exception:
    # 兼容从项目根目录运行
    from Audio_Game.pixel_car_chase_dog import PixelCarChaseDogGame


def _largest_face(faces: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    if faces is None or len(faces) == 0:
        return None
    areas = [(w * h, (x, y, w, h)) for (x, y, w, h) in faces]
    areas.sort(key=lambda t: t[0], reverse=True)
    return areas[0][1]


def _pixelate_rgb(img_rgb: np.ndarray, grid: int = 16, out_size: int = 128) -> np.ndarray:
    """将RGB图像像素化+颜色量化为像素风头像"""
    if img_rgb is None or img_rgb.size == 0:
        raise ValueError("空图像，无法像素化")
    h, w = img_rgb.shape[:2]
    # 保证正方形: 以中心裁剪到正方形
    side = min(h, w)
    y0 = (h - side) // 2
    x0 = (w - side) // 2
    patch = img_rgb[y0:y0 + side, x0:x0 + side]

    # 缩小到grid×grid再放大
    small = cv2.resize(patch, (grid, grid), interpolation=cv2.INTER_AREA)

    # 简单调色板量化（每通道4级: 0, 85, 170, 255）
    step = 85
    quant = ((small // step) * step).astype(np.uint8)

    # 放大输出
    out = cv2.resize(quant, (out_size, out_size), interpolation=cv2.INTER_NEAREST)

    # 轻微对比增强，增加“像素味道”
    out = cv2.convertScaleAbs(out, alpha=1.15, beta=0)
    return out


def _open_any_camera(preferred_indices=(0, 1, 2)) -> Optional[cv2.VideoCapture]:
    """在 macOS 上尝试多种后端与索引打开摄像头。成功则返回已打开的 VideoCapture。"""
    backends = []
    cap_avf = getattr(cv2, 'CAP_AVFOUNDATION', None)
    if cap_avf is not None:
        backends.append(cap_avf)
    backends.append(None)  # 默认后端

    for backend in backends:
        for idx in preferred_indices:
            cap = cv2.VideoCapture(idx, backend) if backend is not None else cv2.VideoCapture(idx)
            if cap.isOpened():
                return cap
            cap.release()
    return None


def capture_face_avatar(window_name: str = "Face Capture", timeout_s: int = 60) -> np.ndarray:
    """打开摄像头捕获人脸，返回像素化的RGB头像图像 (H, W, 3)"""
    cap = _open_any_camera()
    if not cap or not cap.isOpened():
        raise RuntimeError(
            "无法打开摄像头。请检查: 1) 系统偏好设置>安全性与隐私>隐私>相机 是否允许 VS Code/Terminal/python; 2) 其它应用是否占用摄像头; 3) 外接摄像头已连接。"
        )

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        cap.release()
        raise RuntimeError("无法加载人脸分类器: " + cascade_path)

    print("打开摄像头... 按 C 拍摄头像, 按 Q 退出")
    start = time.time()
    avatar: Optional[np.ndarray] = None

    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.putText(frame, "Press 'C' to capture, 'Q' to quit", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q')):
            cap.release()
            cv2.destroyAllWindows()
            raise KeyboardInterrupt("用户取消")
        if key in (ord('c'), ord('C')) and len(faces) > 0:
            # 使用最大的人脸
            (x, y, w, h) = _largest_face(faces)
            pad = int(0.1 * max(w, h))
            x0 = max(0, x - pad)
            y0 = max(0, y - pad)
            x1 = min(frame.shape[1], x + w + pad)
            y1 = min(frame.shape[0], y + h + pad)
            face_bgr = frame[y0:y1, x0:x1]
            face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
            avatar = _pixelate_rgb(face_rgb, grid=18, out_size=100)
            break

        if timeout_s and (time.time() - start) > timeout_s:
            print("超时未拍摄，自动退出")
            cap.release()
            cv2.destroyAllWindows()
            raise TimeoutError("人脸录入超时")

    cap.release()
    cv2.destroyAllWindows()
    if avatar is None:
        raise RuntimeError("未获取到头像")
    return avatar


def choose_image_as_avatar() -> np.ndarray:
    """弹出文件选择或命令行输入，选择一张图片作为头像; 检测最大人脸并像素化。"""
    # 优先使用文件选择对话框
    img_path: Optional[str] = None
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        img_path = filedialog.askOpenFileDialog(title='选择头像图片')  # type: ignore[attr-defined]
    except Exception:
        # 某些环境没有Tk，退回命令行
        pass

    if not img_path:
        try:
            img_path = input("未能打开摄像头。请输入一张图片路径作为头像(回车跳过退出): ").strip()
        except Exception:
            img_path = None

    if not img_path:
        raise RuntimeError("未选择图片")

    bgr = cv2.imread(img_path)
    if bgr is None:
        raise RuntimeError("无法读取所选图片: " + img_path)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    # 尝试检测人脸以裁剪；若失败则居中裁剪
    try:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if not face_cascade.empty():
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
            if len(faces) > 0:
                (x, y, w, h) = _largest_face(faces)
                pad = int(0.2 * max(w, h))
                x0 = max(0, x - pad)
                y0 = max(0, y - pad)
                x1 = min(bgr.shape[1], x + w + pad)
                y1 = min(bgr.shape[0], y + h + pad)
                rgb = cv2.cvtColor(bgr[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
    except Exception:
        pass

    return _pixelate_rgb(rgb, grid=18, out_size=160)


class FaceAvatarCarChaseGame(PixelCarChaseDogGame):
    def __init__(self, avatar_img_rgb: np.ndarray):
        self.avatar_img_rgb = avatar_img_rgb
        super().__init__()

    def setup_graphics(self):
        # 先构建基础像素世界
        super().setup_graphics()

        # 在右侧放置玩家头像（像素风）
        try:
            img = self.avatar_img_rgb
            if img is not None:
                # 头像显示区域（以游戏世界坐标计）
                # 缩小到不超过左侧信息框大小（信息框约高1.2、宽1.92世界单位）
                w_units = 1.2
                h_units = 1.2
                x0 = self.GAME_WIDTH - w_units - 0.4  # 右侧留边距
                # 放在右上角（顶部同样留边距）
                y0 = self.GAME_HEIGHT - h_units - 0.4
                self.avatar_artist = self.ax.imshow(img, extent=(x0, x0 + w_units, y0, y0 + h_units), zorder=8)

                # 简单的像素边框
                border_color = '#FFFFFF'
                border_size = 0.06
                for dx in np.arange(0, w_units + border_size, border_size):
                    self.create_pixel_block(x0 + dx, y0, border_size, border_color)
                    self.create_pixel_block(x0 + dx, y0 + h_units - border_size, border_size, border_color)
                for dy in np.arange(0, h_units + border_size, border_size):
                    self.create_pixel_block(x0, y0 + dy, border_size, border_color)
                    self.create_pixel_block(x0 + w_units - border_size, y0 + dy, border_size, border_color)
        except Exception as e:
            print(f"绘制头像失败: {e}")


def main():
    print("=" * 60)
    print("🧑‍🎤 人脸头像录入 (像素风)")
    print("- 请面对摄像头，按 C 拍摄头像，按 Q 退出")
    print("=" * 60)
    try:
        avatar = capture_face_avatar()
    except KeyboardInterrupt:
        print("用户取消，退出")
        return
    except Exception as e:
        print(f"头像录入失败: {e}")
        # 摄像头不可用时，尝试从图片选择
        try:
            print("改为选择本地图片作为头像...")
            avatar = choose_image_as_avatar()
        except Exception as e2:
            print(f"图片选取也失败: {e2}")
            return

    print("头像已录入，启动游戏...")
    try:
        game = FaceAvatarCarChaseGame(avatar)
        game.start_game()
    except KeyboardInterrupt:
        print("\nPIXEL GAME INTERRUPTED")
    except Exception as e:
        print(f"PIXEL GAME ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
