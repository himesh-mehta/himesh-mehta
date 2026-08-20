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
    inter_path = "fonts/Inter-Medium.otf" if os.path.exists("fonts/Inter-Medium.otf") else "fonts/Inter-Medium.ttf"
    mono_path = "fonts/JetBrainsMono-Regular.ttf"

    name_font = ImageFont.truetype(space_path, 60)
    sub1_font = ImageFont.truetype(inter_path, 21)
    sub2_font = ImageFont.truetype(mono_path, 12)
    hud_font = ImageFont.truetype(mono_path, 10)

    return name_font, sub1_font, sub2_font, hud_font

NAME_FONT, SUB1_FONT, SUB2_FONT, HUD_FONT = get_fonts()

# Fixed seed for deterministic particle trajectories & nodes
random.seed(42)

# Neural Network Nodes on left and right flanks (Framing edges)
LEFT_NODES = []
for _ in range(10):
    x = random.randint(35, 175)
    y = random.randint(35, HEIGHT - 35)
    LEFT_NODES.append((x, y))

RIGHT_NODES = []
for _ in range(10):
    x = random.randint(WIDTH - 175, WIDTH - 35)
    y = random.randint(35, HEIGHT - 35)
    RIGHT_NODES.append((x, y))

# Floating Cyber Ambient Particles (confine outside center zone)
PARTICLES = []
for _ in range(20):
    PARTICLES.append({
        'x': random.choice([random.uniform(0, 300), random.uniform(WIDTH - 300, WIDTH)]),
        'y': random.uniform(0, HEIGHT),
        'speed': random.uniform(0.3, 0.6),
        'size': random.uniform(1.0, 1.5),
        'angle': random.uniform(0, math.pi * 2),
        'cyan_bias': random.random()
    })

# Circuit / Data Bus lines on top & bottom borders
CIRCUIT_LINES = [
    (50, 25, 160, 25, 180, 45, 260, 45),
    (WIDTH - 50, 25, WIDTH - 160, 25, WIDTH - 180, 45, WIDTH - 260, 45),
    (50, HEIGHT - 25, 140, HEIGHT - 25, 160, HEIGHT - 45, 240, HEIGHT - 45),
    (WIDTH - 50, HEIGHT - 25, WIDTH - 140, HEIGHT - 25, WIDTH - 160, HEIGHT - 45, WIDTH - 240, HEIGHT - 45),
]

def render_frame(f_idx):
    # Pure dark background (NO blue oval, NO background shape)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (6, 8, 15, 255))
    draw = ImageDraw.Draw(img)

    t = f_idx / TOTAL_FRAMES

    # 1. Subtle Cyber Grid lines on outer flanks only
    grid_alpha = int(10 + 4 * math.sin(t * math.pi * 2))
    for gx in range(0, WIDTH + 60, 60):
        if gx < 190 or gx > WIDTH - 190:
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(0, 180, 255, int(grid_alpha * 0.3)), width=1)
    
    for gy in [40, 80, HEIGHT - 80, HEIGHT - 40]:
        draw.line([(0, gy), (WIDTH, gy)], fill=(0, 140, 220, int(grid_alpha * 0.12)), width=1)

    # 2. Draw Circuit / Data Bus traces with traveling micro-packets
    for seg in CIRCUIT_LINES:
        x1, y1, x2, y2, x3, y3, x4, y4 = seg
        draw.line([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], fill=(0, 180, 255, 22), width=1)
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
        draw.ellipse([px - 1.0, py - 1.0, px + 1.0, py + 1.0], fill=(180, 240, 255, 120))

    # 3. Neural Network Nodes on left & right flanks (Dimmed to keep text dominant)
    all_nodes = [(LEFT_NODES, (35, 175)), (RIGHT_NODES, (WIDTH - 175, WIDTH - 35))]
    node_activate_prog = min(1.0, max(0.0, (f_idx - 10) / 25.0))
    if node_activate_prog > 0:
        for node_group, _ in all_nodes:
            for i, n1 in enumerate(node_group):
                for j, n2 in enumerate(node_group):
                    if i < j:
                        dist = math.hypot(n1[0] - n2[0], n1[1] - n2[1])
                        if dist < 70:
                            wave = math.sin((n1[0] + n1[1]) * 0.05 - f_idx * 0.15)
                            alpha = int(min(255, max(0, (20 + 14 * wave) * node_activate_prog)))
                            color = (0, 210, 255, alpha) if (i + j) % 3 != 0 else (160, 100, 255, alpha)
                            draw.line([n1, n2], fill=color, width=1)
                
                n_pulse = math.sin(f_idx * 0.2 + i)
                n_rad = 1.2 + 0.4 * n_pulse
                n_alpha = int(min(255, max(0, (65 + 30 * n_pulse) * node_activate_prog)))
                draw.ellipse([n1[0] - n_rad, n1[1] - n_rad, n1[0] + n_rad, n1[1] + n_rad], 
                             fill=(200, 245, 255, n_alpha))

    # 4. Floating Cyber Ambient Micro Dust (Confined to flanks, zero particles over text)
    for p in PARTICLES:
        px = (p['x'] + math.cos(p['angle']) * f_idx * p['speed'])
        if 320 < px < WIDTH - 320:
            px = (px + 400) % WIDTH
        py = (p['y'] + math.sin(p['angle']) * f_idx * p['speed']) % HEIGHT
        p_alpha = int(40 + 30 * math.sin(f_idx * 0.1 + p['x']))
        p_col = (140, 230, 255, p_alpha) if p['cyan_bias'] > 0.4 else (190, 140, 255, p_alpha)
        draw.ellipse([px - p['size'], py - p['size'], px + p['size'], py + p['size']], fill=p_col)

    # 5. Technical Interface Metadata
    if f_idx >= 5:
        hud_alpha = min(120, int((f_idx - 5) * 10))
        hud_lines_left = [
            "SYS_CORE // 01.AI.NEURAL",
            "STATUS   // ONLINE · OPTIMIZED",
            f"FRAME_SEQ // {f_idx:03d} / 090"
        ]
        for idx, line in enumerate(hud_lines_left):
            draw.text((35, 35 + idx * 14), line, font=HUD_FONT, fill=(0, 220, 255, int(hud_alpha * 0.75)))

        hud_lines_right = [
            "LATENCY // 1.2ms [ZERO_LOSS]",
            "AGENTIC // ACTIVE_THREADS: 16",
            "MODEL   // HYPER_CONVERGENCE"
        ]
        for idx, line in enumerate(hud_lines_right):
            bbox = draw.textbbox((0, 0), line, font=HUD_FONT)
            tw = bbox[2] - bbox[0]
            draw.text((WIDTH - 35 - tw, 35 + idx * 14), line, font=HUD_FONT, fill=(170, 180, 240, int(hud_alpha * 0.75)))

    # 6. EXACT VISUAL BOUNDING-BOX POSITIONING (Proper non-overlapping vertical breathing room)
    name_str = "HIMESH MEHTA"
    sub1_str = "BUILDING INTELLIGENT SYSTEMS"
    sub2_str = "AI / ML · FULL STACK · AGENTIC SYSTEMS"

    # Measure exact visual ink boundaries
    bb_n = draw.textbbox((0, 0), name_str, font=NAME_FONT)
    name_vis_h = bb_n[3] - bb_n[1]
    name_vis_w = bb_n[2] - bb_n[0]

    bb_s1 = draw.textbbox((0, 0), sub1_str, font=SUB1_FONT)
    sub1_vis_h = bb_s1[3] - bb_s1[1]
    sub1_vis_w = bb_s1[2] - bb_s1[0]

    bb_s2 = draw.textbbox((0, 0), sub2_str, font=SUB2_FONT)
    sub2_vis_h = bb_s2[3] - bb_s2[1]
    sub2_vis_w = bb_s2[2] - bb_s2[0]

    # Explicit vertical gaps between visual edges
    GAP1 = 18  # 18px gap between bottom edge of HIMESH MEHTA and top edge of BUILDING INTELLIGENT SYSTEMS
    GAP2 = 14  # 14px gap between bottom edge of tagline and top edge of technical line

    total_group_h = name_vis_h + GAP1 + sub1_vis_h + GAP2 + sub2_vis_h
    top_y = (HEIGHT - total_group_h) // 2

    # Exact drawing Y coordinates (accounting for internal font top-bearing offset)
    name_y = top_y - bb_n[1]
    name_bottom = top_y + name_vis_h

    sub1_top = name_bottom + GAP1
    sub1_y = sub1_top - bb_s1[1]
    sub1_bottom = sub1_top + sub1_vis_h

    sub2_top = sub1_bottom + GAP2
    sub2_y = sub2_top - bb_s2[1]

    # Exact horizontal center
    name_x = (WIDTH - name_vis_w) // 2 - bb_n[0]
    sub1_x = (WIDTH - sub1_vis_w) // 2 - bb_s1[0]
    sub2_x = (WIDTH - sub2_vis_w) // 2 - bb_s2[0]

    # --- Line 1: HIMESH MEHTA (Fade in, fixed Y coordinate throughout) ---
    if f_idx >= 16:
        name_prog = min(1.0, (f_idx - 16) / 16.0)
        draw.text((name_x, name_y), name_str, font=NAME_FONT, 
                  fill=(245, 247, 250, int(255 * name_prog)))

    # --- Line 2: BUILDING INTELLIGENT SYSTEMS (Fade in, fixed Y coordinate throughout) ---
    if f_idx >= 30:
        sub1_prog = min(1.0, (f_idx - 30) / 14.0)
        draw.text((sub1_x, sub1_y), sub1_str, font=SUB1_FONT, 
                  fill=(235, 240, 248, int(245 * sub1_prog)))

    # --- Line 3: AI / ML · FULL STACK · AGENTIC SYSTEMS (Fade in, fixed Y coordinate throughout) ---
    if f_idx >= 40:
        sub2_prog = min(1.0, (f_idx - 40) / 14.0)
        draw.text((sub2_x, sub2_y), sub2_str, font=SUB2_FONT, 
                  fill=(135, 175, 210, int(215 * sub2_prog)))

    # 7. Corner Cyber Brackets
    bracket_len = 22
    bracket_alpha = min(110, int(f_idx * 4))
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
    draw.line([(0, HEIGHT - 2), (WIDTH, HEIGHT - 2)], fill=(0, 170, 255, 40), width=2)
    scan_dot_x = int((f_idx / TOTAL_FRAMES) * WIDTH)
    draw.line([(scan_dot_x - 15, HEIGHT - 2), (scan_dot_x + 15, HEIGHT - 2)], fill=(255, 255, 255, 160), width=2)

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

print("Rendering hero GIF with true bounding box spacing...")
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