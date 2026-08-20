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

def get_fonts():
    # Reduced, balanced sans-serif font sizes
    name_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 56)
    sub1_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    sub2_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    mono_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 11)
    return name_font, sub1_font, sub2_font, mono_font

NAME_FONT, SUB1_FONT, SUB2_FONT, MONO_FONT = get_fonts()

# Fixed seed for deterministic particle trajectories & nodes
random.seed(42)

# Generate Neural Network Nodes around left and right edges (framing center)
LEFT_NODES = []
for _ in range(14):
    x = random.randint(30, 240)
    y = random.randint(30, HEIGHT - 30)
    LEFT_NODES.append((x, y))

RIGHT_NODES = []
for _ in range(14):
    x = random.randint(WIDTH - 240, WIDTH - 30)
    y = random.randint(30, HEIGHT - 30)
    RIGHT_NODES.append((x, y))

# Floating Cyber Ambient Particles
PARTICLES = []
for _ in range(35):
    PARTICLES.append({
        'x': random.uniform(0, WIDTH),
        'y': random.uniform(0, HEIGHT),
        'speed': random.uniform(0.3, 1.0),
        'size': random.uniform(1.0, 2.2),
        'angle': random.uniform(0, math.pi * 2),
        'cyan_bias': random.random()
    })

# Circuit / Data Bus lines on top & bottom borders
CIRCUIT_LINES = [
    (50, 25, 200, 25, 220, 45, 360, 45),
    (WIDTH - 50, 25, WIDTH - 200, 25, WIDTH - 220, 45, WIDTH - 360, 45),
    (50, HEIGHT - 25, 180, HEIGHT - 25, 200, HEIGHT - 45, 320, HEIGHT - 45),
    (WIDTH - 50, HEIGHT - 25, WIDTH - 180, HEIGHT - 25, WIDTH - 200, HEIGHT - 45, WIDTH - 320, HEIGHT - 45),
]

def render_frame(f_idx):
    # Deep cosmic dark background
    img = Image.new("RGBA", (WIDTH, HEIGHT), (6, 8, 15, 255))
    draw = ImageDraw.Draw(img)

    t = f_idx / TOTAL_FRAMES

    # 1. Subtle Cyber Grid & Hex Floor / Ceiling depth
    grid_alpha = int(18 + 8 * math.sin(t * math.pi * 2))
    for gx in range(0, WIDTH + 60, 60):
        if gx < 280 or gx > WIDTH - 280:
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(0, 180, 255, int(grid_alpha * 0.5)), width=1)
    
    for gy in [40, 80, HEIGHT - 80, HEIGHT - 40]:
        draw.line([(0, gy), (WIDTH, gy)], fill=(0, 140, 220, int(grid_alpha * 0.3)), width=1)

    # 2. Draw Circuit / Data Bus traces with traveling packets
    for seg in CIRCUIT_LINES:
        x1, y1, x2, y2, x3, y3, x4, y4 = seg
        draw.line([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], fill=(0, 180, 255, 45), width=1)
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
        draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=(180, 240, 255, 200))

    # 3. Neural Network Nodes on left & right flanks (Framing sides, leaving center clean)
    all_nodes = [(LEFT_NODES, (30, 240)), (RIGHT_NODES, (WIDTH - 240, WIDTH - 30))]
    node_activate_prog = min(1.0, max(0.0, (f_idx - 10) / 25.0))
    if node_activate_prog > 0:
        for node_group, _ in all_nodes:
            for i, n1 in enumerate(node_group):
                for j, n2 in enumerate(node_group):
                    if i < j:
                        dist = math.hypot(n1[0] - n2[0], n1[1] - n2[1])
                        if dist < 80:
                            wave = math.sin((n1[0] + n1[1]) * 0.05 - f_idx * 0.15)
                            alpha = int(min(255, max(0, (45 + 35 * wave) * node_activate_prog)))
                            color = (0, 210, 255, alpha) if (i + j) % 3 != 0 else (160, 100, 255, alpha)
                            draw.line([n1, n2], fill=color, width=1)
                
                n_pulse = math.sin(f_idx * 0.2 + i)
                n_rad = 1.8 + 0.8 * n_pulse
                n_alpha = int(min(255, max(0, (130 + 70 * n_pulse) * node_activate_prog)))
                draw.ellipse([n1[0] - n_rad, n1[1] - n_rad, n1[0] + n_rad, n1[1] + n_rad], 
                             fill=(200, 245, 255, n_alpha))

    # 4. Floating Cyber Dust / Particles
    for p in PARTICLES:
        px = (p['x'] + math.cos(p['angle']) * f_idx * p['speed']) % WIDTH
        py = (p['y'] + math.sin(p['angle']) * f_idx * p['speed']) % HEIGHT
        p_alpha = int(100 + 70 * math.sin(f_idx * 0.1 + p['x']))
        p_col = (140, 230, 255, p_alpha) if p['cyan_bias'] > 0.4 else (190, 140, 255, p_alpha)
        draw.ellipse([px - p['size'], py - p['size'], px + p['size'], py + p['size']], fill=p_col)

    # 5. Technical Interface Metadata (Top corners HUD)
    if f_idx >= 5:
        hud_alpha = min(180, int((f_idx - 5) * 15))
        hud_lines_left = [
            "SYS_CORE // 01.AI.NEURAL",
            "STATUS   // ONLINE · OPTIMIZED",
            f"FRAME_SEQ // {f_idx:03d} / 090"
        ]
        for idx, line in enumerate(hud_lines_left):
            draw.text((35, 35 + idx * 14), line, font=MONO_FONT, fill=(0, 220, 255, int(hud_alpha * 0.85)))

        hud_lines_right = [
            "LATENCY // 1.2ms [ZERO_LOSS]",
            "AGENTIC // ACTIVE_THREADS: 16",
            "MODEL   // HYPER_CONVERGENCE"
        ]
        for idx, line in enumerate(hud_lines_right):
            bbox = draw.textbbox((0, 0), line, font=MONO_FONT)
            tw = bbox[2] - bbox[0]
            draw.text((WIDTH - 35 - tw, 35 + idx * 14), line, font=MONO_FONT, fill=(170, 180, 240, int(hud_alpha * 0.85)))

    # 6. TYPOGRAPHY ANIMATION & RENDERING (Clean, centered, no blue oval)
    
    # --- Primary Title: "HIMESH MEHTA" ---
    name_str = "HIMESH MEHTA"
    bbox_name = draw.textbbox((0, 0), name_str, font=NAME_FONT)
    name_w = bbox_name[2] - bbox_name[0]
    name_h = bbox_name[3] - bbox_name[1]
    name_x = (WIDTH - name_w) // 2
    name_y = 80

    if f_idx >= 20:
        name_prog = min(1.0, (f_idx - 20) / 16.0)
        is_glitching = (20 <= f_idx <= 28 and f_idx % 2 == 0)
        disp_x = random.randint(-3, 3) if is_glitching else 0
        disp_y = random.randint(-1, 1) if is_glitching else 0

        # Draw Clean Pure White Title
        draw.text((name_x + disp_x, name_y + disp_y), name_str, font=NAME_FONT, fill=(255, 255, 255, int(255 * name_prog)))

        # Clean light sweep across title
        if 32 <= f_idx <= 55:
            sweep_p = (f_idx - 32) / 23.0
            sweep_x = name_x - 30 + int((name_w + 60) * sweep_p)
            draw.line([(sweep_x - 8, name_y - 4), (sweep_x + 8, name_y + name_h + 8)], 
                      fill=(255, 255, 255, int(150 * math.sin(sweep_p * math.pi))), width=2)

    # --- Subtitle 1: "BUILDING INTELLIGENT SYSTEMS" ---
    sub1_str = "BUILDING INTELLIGENT SYSTEMS"
    bbox_sub1 = draw.textbbox((0, 0), sub1_str, font=SUB1_FONT)
    sub1_w = bbox_sub1[2] - bbox_sub1[0]
    sub1_h = bbox_sub1[3] - bbox_sub1[1]
    sub1_x = (WIDTH - sub1_w) // 2
    sub1_y = name_y + name_h + 24

    if f_idx >= 34:
        sub1_prog = min(1.0, (f_idx - 34) / 14.0)
        y_offset = int((1.0 - sub1_prog) * 10)
        draw.text((sub1_x, sub1_y + y_offset), sub1_str, font=SUB1_FONT, fill=(255, 255, 255, int(255 * sub1_prog)))

    # --- Subtitle 2: "AI / ML · FULL STACK · AGENTIC SYSTEMS" ---
    sub2_str = "AI / ML · FULL STACK · AGENTIC SYSTEMS"
    bbox_sub2 = draw.textbbox((0, 0), sub2_str, font=SUB2_FONT)
    sub2_w = bbox_sub2[2] - bbox_sub2[0]
    sub2_x = (WIDTH - sub2_w) // 2
    sub2_y = sub1_y + sub1_h + 16

    if f_idx >= 44:
        sub2_prog = min(1.0, (f_idx - 44) / 14.0)
        y_offset = int((1.0 - sub2_prog) * 8)
        draw.text((sub2_x, sub2_y + y_offset), sub2_str, font=SUB2_FONT, fill=(255, 255, 255, int(255 * sub2_prog)))

    # 7. Corner Cyber Brackets
    bracket_len = 30
    bracket_alpha = min(180, int(f_idx * 7))
    b_col = (0, 190, 255, bracket_alpha)
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

    # 8. Bottom Progress Line
    draw.line([(0, HEIGHT - 2), (WIDTH, HEIGHT - 2)], fill=(0, 170, 255, 80), width=2)
    scan_dot_x = int((f_idx / TOTAL_FRAMES) * WIDTH)
    draw.line([(scan_dot_x - 25, HEIGHT - 2), (scan_dot_x + 25, HEIGHT - 2)], fill=(255, 255, 255, 240), width=2)

    # 9. Seamless Loop Blend (Fade out/in to seamless dark background)
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

print("Rendering high quality animation sequence without blue oval...")
frames = []
for i in range(TOTAL_FRAMES):
    frames.append(render_frame(i))

print("Exporting optimized GIF...")
frames[0].save(
    OUTPUT_PATH,
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=False
)
print(f"Successfully generated hero animation GIF at {OUTPUT_PATH}")