import math
import random
import os
from PIL import Image, ImageDraw, ImageFont

# Canvas Dimensions
WIDTH, HEIGHT = 1200, 350
FPS = 15
TOTAL_FRAMES = 90  # 6 seconds loop at 15 fps
OUTPUT_PATH = "assets/hero-animated.gif"

# Ensure output directory
os.makedirs("assets", exist_ok=True)

# Clean, modern, high-contrast typography
def get_fonts():
    # Primary Main Title Font (Bold, Modern)
    name_font = None
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"]:
        if os.path.exists(p):
            try:
                name_font = ImageFont.truetype(p, 54)
                break
            except: pass
    if not name_font: name_font = ImageFont.load_default()

    # Subtitle 1 Font
    sub_font = None
    for p in ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(p):
            try:
                sub_font = ImageFont.truetype(p, 22)
                break
            except: pass
    if not sub_font: sub_font = ImageFont.load_default()

    # Subtitle 2 / Tags Font
    tag_font = None
    for p in ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(p):
            try:
                tag_font = ImageFont.truetype(p, 16)
                break
            except: pass
    if not tag_font: tag_font = ImageFont.load_default()

    # Technical Mono Font for HUD
    mono_font = None
    for p in ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/cour.ttf"]:
        if os.path.exists(p):
            try:
                mono_font = ImageFont.truetype(p, 12)
                break
            except: pass
    if not mono_font: mono_font = ImageFont.load_default()

    return name_font, sub_font, tag_font, mono_font

NAME_FONT, SUB_FONT, TAG_FONT, MONO_FONT = get_fonts()

# Fixed seed for deterministic particle trajectories & nodes
random.seed(42)

# Generate Neural Network Nodes around left and right edges (framing center)
LEFT_NODES = []
for _ in range(16):
    x = random.randint(30, 260)
    y = random.randint(35, HEIGHT - 35)
    LEFT_NODES.append((x, y))

RIGHT_NODES = []
for _ in range(16):
    x = random.randint(WIDTH - 260, WIDTH - 30)
    y = random.randint(35, HEIGHT - 35)
    RIGHT_NODES.append((x, y))

# Floating Cyber Ambient Particles
PARTICLES = []
for _ in range(40):
    PARTICLES.append({
        'x': random.uniform(0, WIDTH),
        'y': random.uniform(0, HEIGHT),
        'speed': random.uniform(0.3, 1.2),
        'size': random.uniform(1.0, 2.5),
        'angle': random.uniform(0, math.pi * 2),
        'cyan_bias': random.random()
    })

# Circuit lines on top & bottom borders
CIRCUIT_LINES = [
    (50, 25, 200, 25, 220, 45, 380, 45),
    (WIDTH - 50, 25, WIDTH - 200, 25, WIDTH - 220, 45, WIDTH - 380, 45),
    (50, HEIGHT - 25, 180, HEIGHT - 25, 200, HEIGHT - 45, 340, HEIGHT - 45),
    (WIDTH - 50, HEIGHT - 25, WIDTH - 180, HEIGHT - 25, WIDTH - 200, HEIGHT - 45, WIDTH - 340, HEIGHT - 45),
]

# Pre-calculate clean text dimensions
temp_img = Image.new("RGB", (100, 100))
temp_d = ImageDraw.Draw(temp_img)

TEXT_NAME = "HIMESH MEHTA"
bbox_name = temp_d.textbbox((0, 0), TEXT_NAME, font=NAME_FONT)
W_NAME, H_NAME = bbox_name[2] - bbox_name[0], bbox_name[3] - bbox_name[1]

TEXT_SUB1 = "BUILDING INTELLIGENT SYSTEMS"
bbox_sub1 = temp_d.textbbox((0, 0), TEXT_SUB1, font=SUB_FONT)
W_SUB1, H_SUB1 = bbox_sub1[2] - bbox_sub1[0], bbox_sub1[3] - bbox_sub1[1]

TEXT_SUB2 = "AI / ML  ·  FULL STACK  ·  AGENTIC SYSTEMS"
bbox_sub2 = temp_d.textbbox((0, 0), TEXT_SUB2, font=TAG_FONT)
W_SUB2, H_SUB2 = bbox_sub2[2] - bbox_sub2[0], bbox_sub2[3] - bbox_sub2[1]

TOTAL_TEXT_HEIGHT = H_NAME + 22 + H_SUB1 + 14 + H_SUB2
START_Y = (HEIGHT - TOTAL_TEXT_HEIGHT) // 2

def render_frame(f_idx):
    # Deep, premium dark cyber background
    img = Image.new("RGB", (WIDTH, HEIGHT), (6, 8, 14))
    draw = ImageDraw.Draw(img)

    t = f_idx / TOTAL_FRAMES

    # 1. Perspective grid lines (faint cyan/electric blue)
    grid_alpha = int(40 + 20 * math.sin(t * math.pi * 2))
    for gx in range(0, WIDTH + 70, 70):
        if gx < 300 or gx > WIDTH - 300:
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(0, 140, 210), width=1)
    
    for gy in [35, 75, HEIGHT - 75, HEIGHT - 35]:
        draw.line([(0, gy), (WIDTH, gy)], fill=(0, 110, 180), width=1)

    # 2. Circuit Traces with moving light pulses
    for seg in CIRCUIT_LINES:
        x1, y1, x2, y2, x3, y3, x4, y4 = seg
        draw.line([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], fill=(0, 160, 240), width=1)
        pulse_pos = ((f_idx * 3.5) % 300) / 300.0
        if pulse_pos < 0.5:
            px = x1 + (x2 - x1) * (pulse_pos * 2)
            py = y1
        elif pulse_pos < 0.7:
            p_sub = (pulse_pos - 0.5) / 0.2
            px = x2 + (x3 - x2) * p_sub
            py = y2 + (y3 - y2) * p_sub
        else:
            p_sub = (pulse_pos - 0.7) / 0.3
            px = x3 + (x4 - x3) * p_sub
            py = y3 + (y4 - y3) * p_sub
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(220, 245, 255))

    # 3. Left and Right Neural Network Nodes
    all_nodes = [(LEFT_NODES, (30, 260)), (RIGHT_NODES, (WIDTH - 260, WIDTH - 30))]
    node_prog = min(1.0, max(0.0, (f_idx - 5) / 25.0))
    if node_prog > 0:
        for node_group, _ in all_nodes:
            for i, n1 in enumerate(node_group):
                for j, n2 in enumerate(node_group):
                    if i < j:
                        dist = math.hypot(n1[0] - n2[0], n1[1] - n2[1])
                        if dist < 85:
                            wave = math.sin((n1[0] + n1[1]) * 0.05 - f_idx * 0.15)
                            if wave > -0.2:
                                col = (0, 180, 235) if (i + j) % 3 != 0 else (140, 90, 220)
                                draw.line([n1, n2], fill=col, width=1)
                
                n_pulse = math.sin(f_idx * 0.2 + i)
                n_rad = 2.0 + 1.0 * n_pulse
                draw.ellipse([n1[0] - n_rad, n1[1] - n_rad, n1[0] + n_rad, n1[1] + n_rad], fill=(190, 240, 255))

    # 4. Floating Particles
    for p in PARTICLES:
        px = (p['x'] + math.cos(p['angle']) * f_idx * p['speed']) % WIDTH
        py = (p['y'] + math.sin(p['angle']) * f_idx * p['speed']) % HEIGHT
        p_col = (130, 220, 255) if p['cyan_bias'] > 0.4 else (180, 130, 245)
        draw.ellipse([px - p['size'], py - p['size'], px + p['size'], py + p['size']], fill=p_col)

    # 5. Technical Interface Metadata (HUD)
    if f_idx >= 5:
        # Top Left
        draw.text((35, 38), "SYS_CORE // 01.AI.NEURAL", font=MONO_FONT, fill=(0, 200, 240))
        draw.text((35, 53), "STATUS   // ONLINE · ACTIVE", font=MONO_FONT, fill=(0, 200, 240))
        draw.text((35, 68), f"FRAME    // {f_idx:03d} / 090", font=MONO_FONT, fill=(0, 200, 240))

        # Top Right
        t_right_1 = "LATENCY // 1.2ms [ZERO_LOSS]"
        t_right_2 = "AGENTIC // ACTIVE_THREADS: 16"
        t_right_3 = "SYSTEM  // HYPER_CONVERGENCE"
        
        tw1 = draw.textbbox((0, 0), t_right_1, font=MONO_FONT)[2]
        tw2 = draw.textbbox((0, 0), t_right_2, font=MONO_FONT)[2]
        tw3 = draw.textbbox((0, 0), t_right_3, font=MONO_FONT)[2]

        draw.text((WIDTH - 35 - tw1, 38), t_right_1, font=MONO_FONT, fill=(160, 170, 235))
        draw.text((WIDTH - 35 - tw2, 53), t_right_2, font=MONO_FONT, fill=(160, 170, 235))
        draw.text((WIDTH - 35 - tw3, 68), t_right_3, font=MONO_FONT, fill=(160, 170, 235))

    # 6. TYPOGRAPHY (Smooth upward cinematic entrance, clean & readable)

    # --- 1. Main Title: "HIMESH MEHTA" ---
    # Entrance timeline: Frame 12 to 90
    if f_idx >= 12:
        name_prog = min(1.0, (f_idx - 12) / 18.0)
        # Smooth ease-out curve
        ease = 1.0 - math.pow(1.0 - name_prog, 3)
        cur_y = int(START_Y + (1.0 - ease) * 35)
        cur_x = (WIDTH - W_NAME) // 2

        # Draw Clean White Main Title
        draw.text((cur_x, cur_y), TEXT_NAME, font=NAME_FONT, fill=(255, 255, 255))

    # --- 2. Subtitle 1: "BUILDING INTELLIGENT SYSTEMS" ---
    # Entrance timeline: Frame 26 to 90
    if f_idx >= 26:
        sub1_prog = min(1.0, (f_idx - 26) / 16.0)
        ease1 = 1.0 - math.pow(1.0 - sub1_prog, 3)
        sub1_y = int(START_Y + H_NAME + 22 + (1.0 - ease1) * 25)
        sub1_x = (WIDTH - W_SUB1) // 2

        draw.text((sub1_x, sub1_y), TEXT_SUB1, font=SUB_FONT, fill=(0, 220, 255))
        
        # Subtle horizontal accent lines on left and right of subtitle
        dash_len = int(45 * ease1)
        draw.line([(sub1_x - 18 - dash_len, sub1_y + 12), (sub1_x - 18, sub1_y + 12)], fill=(0, 190, 240), width=1)
        draw.line([(sub1_x + W_SUB1 + 18, sub1_y + 12), (sub1_x + W_SUB1 + 18 + dash_len, sub1_y + 12)], fill=(0, 190, 240), width=1)

    # --- 3. Subtitle 2: "AI / ML · FULL STACK · AGENTIC SYSTEMS" ---
    # Entrance timeline: Frame 38 to 90
    if f_idx >= 38:
        sub2_prog = min(1.0, (f_idx - 38) / 16.0)
        ease2 = 1.0 - math.pow(1.0 - sub2_prog, 3)
        sub2_y = int(START_Y + H_NAME + 22 + H_SUB1 + 14 + (1.0 - ease2) * 20)
        sub2_x = (WIDTH - W_SUB2) // 2

        draw.text((sub2_x, sub2_y), TEXT_SUB2, font=TAG_FONT, fill=(200, 215, 240))

    # 7. Framing Corner Cyber Brackets
    bracket_len = 35
    b_col = (0, 180, 240)
    # Top-Left
    draw.line([(20, 20), (20 + bracket_len, 20)], fill=b_col, width=2)
    draw.line([(20, 20), (20, 20 + bracket_len)], fill=b_col, width=2)
    # Top-Right
    draw.line([(WIDTH - 20, 20), (WIDTH - 20 - bracket_len, 20)], fill=b_col, width=2)
    draw.line([(WIDTH - 20, 20), (WIDTH - 20, 20 + bracket_len)], fill=b_col, width=2)
    # Bottom-Left
    draw.line([(20, HEIGHT - 20), (20 + bracket_len, HEIGHT - 20)], fill=b_col, width=2)
    draw.line([(20, HEIGHT - 20), (20, HEIGHT - 20 - bracket_len)], fill=b_col, width=2)
    # Bottom-Right
    draw.line([(WIDTH - 20, HEIGHT - 20), (WIDTH - 20 - bracket_len, HEIGHT - 20)], fill=b_col, width=2)
    draw.line([(WIDTH - 20, HEIGHT - 20), (WIDTH - 20, HEIGHT - 20 - bracket_len)], fill=b_col, width=2)

    # 8. Bottom Progress Tracker Line
    draw.line([(0, HEIGHT - 2), (WIDTH, HEIGHT - 2)], fill=(0, 150, 220), width=1)
    scan_x = int((f_idx / TOTAL_FRAMES) * WIDTH)
    draw.line([(scan_x - 30, HEIGHT - 2), (scan_x + 30, HEIGHT - 2)], fill=(255, 255, 255), width=2)

    # 9. Seamless Loop Fade (Last 10 frames blend out, first 6 frames blend in)
    if f_idx >= 80:
        fade_prog = (f_idx - 80) / 10.0
        # Darken to black
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (6, 8, 14))
        img = Image.blend(img, overlay, fade_prog)
    elif f_idx <= 6:
        fade_prog = 1.0 - (f_idx / 6.0)
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (6, 8, 14))
        img = Image.blend(img, overlay, fade_prog)

    return img

print("Rendering clean typography animation sequence...")
frames = []
for i in range(TOTAL_FRAMES):
    if i % 15 == 0:
        print(f"Rendering frame {i}/{TOTAL_FRAMES}...")
    frames.append(render_frame(i))

print("Exporting optimized GIF...")
frames[0].save(
    OUTPUT_PATH,
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True
)
print(f"Successfully generated hero animation GIF at {OUTPUT_PATH}")