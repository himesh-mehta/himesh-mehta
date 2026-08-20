import math
import random
import os
from PIL import Image, ImageDraw, ImageFont

# Canvas Dimensions
WIDTH, HEIGHT = 1200, 350
FPS = 15
TOTAL_FRAMES = 90  # 6 seconds loop at 15 fps
OUTPUT_PATHS = ["assets/hero-animated-v3.gif", "assets/hero-animated-v2.gif", "assets/hero-animated.gif"]

os.makedirs("assets", exist_ok=True)
os.makedirs("fonts", exist_ok=True)

def get_fonts():
    space_path = "fonts/SpaceGrotesk-Bold.ttf"
    inter_path = "fonts/Inter-Medium.ttf"
    mono_path = "fonts/JetBrainsMono-Regular.ttf"

    name_font = ImageFont.truetype(space_path, 54)
    sub1_font = ImageFont.truetype(inter_path, 19)
    sub2_font = ImageFont.truetype(mono_path, 12)
    hud_font = ImageFont.truetype(mono_path, 10)

    return name_font, sub1_font, sub2_font, hud_font

NAME_FONT, SUB1_FONT, SUB2_FONT, HUD_FONT = get_fonts()

# Fixed seed for deterministic particle trajectories & nodes
random.seed(42)

# Neural Network Nodes on left and right flanks (Framing edges)
LEFT_NODES = []
for _ in range(10):
    x = random.randint(35, 180)
    y = random.randint(35, HEIGHT - 35)
    LEFT_NODES.append((x, y))

RIGHT_NODES = []
for _ in range(10):
    x = random.randint(WIDTH - 180, WIDTH - 35)
    y = random.randint(35, HEIGHT - 35)
    RIGHT_NODES.append((x, y))

# Floating Cyber Ambient Particles
PARTICLES = []
for _ in range(22):
    PARTICLES.append({
        'x': random.uniform(0, WIDTH),
        'y': random.uniform(0, HEIGHT),
        'speed': random.uniform(0.3, 0.7),
        'size': random.uniform(1.0, 1.6),
        'angle': random.uniform(0, math.pi * 2),
        'cyan_bias': random.random()
    })

# Circuit / Data Bus lines on top & bottom borders
CIRCUIT_LINES = [
    (50, 25, 170, 25, 190, 45, 280, 45),
    (WIDTH - 50, 25, WIDTH - 170, 25, WIDTH - 190, 45, WIDTH - 280, 45),
    (50, HEIGHT - 25, 150, HEIGHT - 25, 170, HEIGHT - 45, 260, HEIGHT - 45),
    (WIDTH - 50, HEIGHT - 25, WIDTH - 150, HEIGHT - 25, WIDTH - 170, HEIGHT - 45, WIDTH - 260, HEIGHT - 45),
]

def draw_spaced_text(draw, x, y, text, font, fill, letter_spacing=0):
    """Draw text with custom letter-spacing (tracking)."""
    if letter_spacing == 0:
        draw.text((x, y), text, font=font, fill=fill)
        return
    curr_x = x
    for char in text:
        draw.text((curr_x, y), char, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), char, font=font)
        char_w = bbox[2] - bbox[0]
        curr_x += char_w + letter_spacing

def measure_spaced_text(draw, text, font, letter_spacing=0):
    """Calculate width and height of text with custom letter-spacing."""
    bbox = draw.textbbox((0, 0), text, font=font)
    h = bbox[3] - bbox[1]
    if letter_spacing == 0:
        return bbox[2] - bbox[0], h
    total_w = 0
    for i, char in enumerate(text):
        c_bbox = draw.textbbox((0, 0), char, font=font)
        total_w += (c_bbox[2] - c_bbox[0])
        if i < len(text) - 1:
            total_w += letter_spacing
    return total_w, h

def render_frame(f_idx):
    # Pure dark background (NO blue oval, NO background shape)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (6, 8, 15, 255))
    draw = ImageDraw.Draw(img)

    t = f_idx / TOTAL_FRAMES

    # 1. Subtle Cyber Grid lines on outer flanks (reduced opacity by 25%)
    grid_alpha = int(10 + 4 * math.sin(t * math.pi * 2))
    for gx in range(0, WIDTH + 60, 60):
        if gx < 200 or gx > WIDTH - 200:
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(0, 180, 255, int(grid_alpha * 0.35)), width=1)
    
    for gy in [40, 80, HEIGHT - 80, HEIGHT - 40]:
        draw.line([(0, gy), (WIDTH, gy)], fill=(0, 140, 220, int(grid_alpha * 0.15)), width=1)

    # 2. Draw Circuit / Data Bus traces with traveling micro-packets
    for seg in CIRCUIT_LINES:
        x1, y1, x2, y2, x3, y3, x4, y4 = seg
        draw.line([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], fill=(0, 180, 255, 25), width=1)
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
        draw.ellipse([px - 1.0, py - 1.0, px + 1.0, py + 1.0], fill=(180, 240, 255, 140))

    # 3. Neural Network Nodes on left & right flanks (25% reduced brightness for zero title competition)
    all_nodes = [(LEFT_NODES, (35, 180)), (RIGHT_NODES, (WIDTH - 180, WIDTH - 35))]
    node_activate_prog = min(1.0, max(0.0, (f_idx - 10) / 25.0))
    if node_activate_prog > 0:
        for node_group, _ in all_nodes:
            for i, n1 in enumerate(node_group):
                for j, n2 in enumerate(node_group):
                    if i < j:
                        dist = math.hypot(n1[0] - n2[0], n1[1] - n2[1])
                        if dist < 75:
                            wave = math.sin((n1[0] + n1[1]) * 0.05 - f_idx * 0.15)
                            alpha = int(min(255, max(0, (24 + 16 * wave) * node_activate_prog)))
                            color = (0, 210, 255, alpha) if (i + j) % 3 != 0 else (160, 100, 255, alpha)
                            draw.line([n1, n2], fill=color, width=1)
                
                n_pulse = math.sin(f_idx * 0.2 + i)
                n_rad = 1.3 + 0.4 * n_pulse
                n_alpha = int(min(255, max(0, (75 + 35 * n_pulse) * node_activate_prog)))
                draw.ellipse([n1[0] - n_rad, n1[1] - n_rad, n1[0] + n_rad, n1[1] + n_rad], 
                             fill=(200, 245, 255, n_alpha))

    # 4. Floating Cyber Ambient Micro Dust (Subtle)
    for p in PARTICLES:
        px = (p['x'] + math.cos(p['angle']) * f_idx * p['speed']) % WIDTH
        py = (p['y'] + math.sin(p['angle']) * f_idx * p['speed']) % HEIGHT
        p_alpha = int(45 + 35 * math.sin(f_idx * 0.1 + p['x']))
        p_col = (140, 230, 255, p_alpha) if p['cyan_bias'] > 0.4 else (190, 140, 255, p_alpha)
        draw.ellipse([px - p['size'], py - p['size'], px + p['size'], py + p['size']], fill=p_col)

    # 5. Technical Interface Metadata (Top corners HUD in JetBrains Mono)
    if f_idx >= 5:
        hud_alpha = min(130, int((f_idx - 5) * 12))
        hud_lines_left = [
            "SYS_CORE // 01.AI.NEURAL",
            "STATUS   // ONLINE · OPTIMIZED",
            f"FRAME_SEQ // {f_idx:03d} / 090"
        ]
        for idx, line in enumerate(hud_lines_left):
            draw.text((35, 35 + idx * 14), line, font=HUD_FONT, fill=(0, 220, 255, int(hud_alpha * 0.8)))

        hud_lines_right = [
            "LATENCY // 1.2ms [ZERO_LOSS]",
            "AGENTIC // ACTIVE_THREADS: 16",
            "MODEL   // HYPER_CONVERGENCE"
        ]
        for idx, line in enumerate(hud_lines_right):
            bbox = draw.textbbox((0, 0), line, font=HUD_FONT)
            tw = bbox[2] - bbox[0]
            draw.text((WIDTH - 35 - tw, 35 + idx * 14), line, font=HUD_FONT, fill=(170, 180, 240, int(hud_alpha * 0.8)))

    # 6. REFINED TYPOGRAPHY SYSTEM (Centered Unified Group)
    name_str = "HIMESH MEHTA"
    sub1_str = "BUILDING INTELLIGENT SYSTEMS"
    sub2_str = "AI / ML · FULL STACK · AGENTIC SYSTEMS"

    name_spacing = -1
    sub1_spacing = 0.5
    sub2_spacing = 1.0

    name_w, name_h = measure_spaced_text(draw, name_str, NAME_FONT, name_spacing)
    sub1_w, sub1_h = measure_spaced_text(draw, sub1_str, SUB1_FONT, sub1_spacing)
    sub2_w, sub2_h = measure_spaced_text(draw, sub2_str, SUB2_FONT, sub2_spacing)

    gap1 = 11  # 11px below name
    gap2 = 11  # 11px below tagline
    total_group_h = name_h + gap1 + sub1_h + gap2 + sub2_h
    start_y = (HEIGHT - total_group_h) // 2

    name_x = (WIDTH - name_w) // 2
    name_y = start_y

    sub1_x = (WIDTH - sub1_w) // 2
    sub1_y = name_y + name_h + gap1

    sub2_x = (WIDTH - sub2_w) // 2
    sub2_y = sub1_y + sub1_h + gap2

    # --- Line 1: HIMESH MEHTA (Space Grotesk 54px, #F5F7FA, tracking: -1px) ---
    if f_idx >= 18:
        name_prog = min(1.0, (f_idx - 18) / 16.0)
        is_glitching = (18 <= f_idx <= 24 and f_idx % 2 == 0)
        disp_x = random.randint(-2, 2) if is_glitching else 0
        disp_y = random.randint(-1, 1) if is_glitching else 0

        # Draw Near-White Space Grotesk Title
        draw_spaced_text(draw, name_x + disp_x, name_y + disp_y, name_str, NAME_FONT, 
                         (245, 247, 250, int(255 * name_prog)), name_spacing)

        # Subtle clean light sweep across title
        if 32 <= f_idx <= 54:
            sweep_p = (f_idx - 32) / 22.0
            sweep_x = name_x - 20 + int((name_w + 40) * sweep_p)
            draw.line([(sweep_x - 6, name_y - 2), (sweep_x + 6, name_y + name_h + 4)], 
                      fill=(255, 255, 255, int(115 * math.sin(sweep_p * math.pi))), width=1)

    # --- Line 2: BUILDING INTELLIGENT SYSTEMS (Inter Medium 19px, near-white) ---
    if f_idx >= 32:
        sub1_prog = min(1.0, (f_idx - 32) / 14.0)
        y_offset = int((1.0 - sub1_prog) * 6)
        draw_spaced_text(draw, sub1_x, sub1_y + y_offset, sub1_str, SUB1_FONT, 
                         (235, 240, 248, int(245 * sub1_prog)), sub1_spacing)

    # --- Line 3: AI / ML · FULL STACK · AGENTIC SYSTEMS (JetBrains Mono 12px, muted cyan/blue-gray) ---
    if f_idx >= 42:
        sub2_prog = min(1.0, (f_idx - 42) / 14.0)
        y_offset = int((1.0 - sub2_prog) * 5)
        draw_spaced_text(draw, sub2_x, sub2_y + y_offset, sub2_str, SUB2_FONT, 
                         (135, 175, 210, int(215 * sub2_prog)), sub2_spacing)

    # 7. Corner Cyber Brackets
    bracket_len = 22
    bracket_alpha = min(120, int(f_idx * 5))
    b_col = (0, 190, 255, bracket_alpha)
    draw.line([(20, 20), (20 + bracket_len, 20)], fill=b_col, width=2)
    draw.line([(20, 20), (20, 20 + bracket_len)], fill=b_col, width=2)
    draw.line([(WIDTH - 20, 20), (WIDTH - 20 - bracket_len, 20)], fill=b_col, width=2)
    draw.line([(WIDTH - 20, 20), (WIDTH - 20, 20 + bracket_len)], fill=b_col, width=2)
    draw.line([(20, HEIGHT - 20), (20 + bracket_len, HEIGHT - 20)], fill=b_col, width=2)
    draw.line([(20, HEIGHT - 20), (20, HEIGHT - 20 - bracket_len)], fill=b_col, width=2)
    draw.line([(WIDTH - 20, HEIGHT - 20), (WIDTH - 20 - bracket_len, HEIGHT - 20)], fill=b_col, width=2)
    draw.line([(WIDTH - 20, HEIGHT - 20), (WIDTH - 20, HEIGHT - 20 - bracket_len)], fill=b_col, width=2)

    # 8. Bottom Progress Line
    draw.line([(0, HEIGHT - 2), (WIDTH, HEIGHT - 2)], fill=(0, 170, 255, 45), width=2)
    scan_dot_x = int((f_idx / TOTAL_FRAMES) * WIDTH)
    draw.line([(scan_dot_x - 15, HEIGHT - 2), (scan_dot_x + 15, HEIGHT - 2)], fill=(255, 255, 255, 170), width=2)

    # 9. Seamless Loop Fade
    if f_idx >= 80:
        fade_prog = (f_idx - 80) / 10.0
        dark_alpha = int(255 * fade_prog)
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (6, 8, 15, dark_alpha))
        img = Image.alpha_composite(img, overlay)
    elif f_idx <= 6:
        fade_prog = 1.0 - (f_idx / 6.0)
        dark_alpha = int(255 * fade_prog)
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (6, 8, 15, dark_alpha))
        img = Image.alpha_composite(img, overlay)

    return img.convert("RGB")

print("Rendering high quality animation sequence hero-animated-v3.gif...")
frames = []
for i in range(TOTAL_FRAMES):
    frames.append(render_frame(i))

print("Exporting optimized GIF to all targets...")
for path in OUTPUT_PATHS:
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=False
    )
    print(f"Successfully generated at {path}")