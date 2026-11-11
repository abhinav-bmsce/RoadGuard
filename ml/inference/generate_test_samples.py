"""
RoadGuard - Generate Realistic Road Damage Test Images
Generates test pavement textures with synthetic road distress (longitudinal cracks, transverse cracks, alligator cracking, and potholes) for unit testing and local verification.
"""

import numpy as np
import cv2
from pathlib import Path


def create_asphalt_texture(w=640, h=640):
    # Base asphalt grey with grain noise
    base_color = 75
    texture = np.random.normal(loc=base_color, scale=12, size=(h, w)).astype(np.uint8)
    texture = cv2.GaussianBlur(texture, (3, 3), 0)
    img = cv2.cvtColor(texture, cv2.COLOR_GRAY2BGR)
    
    # Add subtle road wear streaks
    for _ in range(5):
        y = np.random.randint(0, h)
        cv2.line(img, (0, y), (w, y + np.random.randint(-20, 20)), (60, 60, 60), 2)
    return img


def draw_pothole(img, center=(320, 350), radius=55):
    # Deep dark center with rough jagged edge
    cv2.circle(img, center, radius, (25, 25, 25), -1)
    # Add rough rim
    for i in range(16):
        angle = i * (2 * np.pi / 16)
        r = radius + np.random.randint(-8, 12)
        px = int(center[0] + r * np.cos(angle))
        py = int(center[1] + r * np.sin(angle))
        cv2.circle(img, (px, py), np.random.randint(8, 15), (35, 35, 35), -1)
    # Inner shadow depth
    cv2.circle(img, (center[0] - 5, center[1] - 5), radius // 2, (15, 15, 15), -1)


def draw_longitudinal_crack(img, start_x=240, start_y=80, length=450):
    cur_x, cur_y = start_x, start_y
    for _ in range(length // 15):
        next_x = cur_x + np.random.randint(-5, 6)
        next_y = cur_y + np.random.randint(10, 20)
        cv2.line(img, (cur_x, cur_y), (next_x, next_y), (20, 20, 20), np.random.randint(2, 4))
        cur_x, cur_y = next_x, next_y


def draw_transverse_crack(img, start_x=80, start_y=300, length=480):
    cur_x, cur_y = start_x, start_y
    for _ in range(length // 15):
        next_x = cur_x + np.random.randint(10, 20)
        next_y = cur_y + np.random.randint(-4, 5)
        cv2.line(img, (cur_x, cur_y), (next_x, next_y), (22, 22, 22), np.random.randint(2, 4))
        cur_x, cur_y = next_x, next_y


def draw_alligator_crack(img, top_left=(280, 220), width=180, height=160):
    # Intersecting fatigue mesh
    for x in range(top_left[0], top_left[0] + width, 25):
        pts = []
        for y in range(top_left[1], top_left[1] + height, 20):
            pts.append([x + np.random.randint(-6, 7), y + np.random.randint(-4, 5)])
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        cv2.polylines(img, [pts], isClosed=False, color=(20, 20, 20), thickness=2)

    for y in range(top_left[1], top_left[1] + height, 25):
        pts = []
        for x in range(top_left[0], top_left[0] + width, 20):
            pts.append([x + np.random.randint(-4, 5), y + np.random.randint(-6, 7)])
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        cv2.polylines(img, [pts], isClosed=False, color=(20, 20, 20), thickness=2)


def generate_samples(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Pothole image
    img1 = create_asphalt_texture()
    draw_pothole(img1, (320, 360), 65)
    cv2.imwrite(str(out_dir / "road_pothole_severe.jpg"), img1)

    # 2. Longitudinal crack
    img2 = create_asphalt_texture()
    draw_longitudinal_crack(img2, 280, 50, 520)
    cv2.imwrite(str(out_dir / "road_longitudinal_crack.jpg"), img2)

    # 3. Transverse crack
    img3 = create_asphalt_texture()
    draw_transverse_crack(img3, 60, 310, 500)
    cv2.imwrite(str(out_dir / "road_transverse_crack.jpg"), img3)

    # 4. Multi-damage: Alligator crack + Pothole
    img4 = create_asphalt_texture()
    draw_alligator_crack(img4, (120, 200), 200, 180)
    draw_pothole(img4, (450, 420), 50)
    cv2.imwrite(str(out_dir / "road_multi_hazard.jpg"), img4)

    print(f"Generated 4 sample test road images in {out_dir}")


if __name__ == "__main__":
    generate_samples(Path("ml/inference/samples"))
    generate_samples(Path("docs/samples"))

