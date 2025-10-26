import cv2


def setup_camera(preferred_index=None, max_index=3, width=None, height=None):
    """Probe camera indices and return an opened VideoCapture and the camera index.

    preferred_index: try this index first if provided.
    max_index: maximum index to probe (inclusive).
    width/height: optional desired frame size to set on the capture.

    Returns: (cap, camera_index). If no camera opened, raises RuntimeError.
    """
    indices = []
    if preferred_index is not None:
        indices.append(preferred_index)
    indices.extend(i for i in range(0, max_index + 1) if i != preferred_index)

    cap = None
    opened_idx = None
    for i in indices:
        try:
            c = cv2.VideoCapture(i)
            if not c.isOpened():
                c.release()
                continue
            # try to grab a frame to ensure camera is usable
            ret, _ = c.read()
            if not ret:
                c.release()
                continue
            cap = c
            opened_idx = i
            break
        except Exception:
            continue

    if cap is None:
        raise RuntimeError('No usable camera found (probed indices {}).'.format(indices))

    # optionally set resolution
    if width is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
    if height is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))

    return cap, opened_idx
