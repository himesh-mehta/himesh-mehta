import math
import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Canvas Dimensions
WIDTH, HEIGHT = 1200, 350
FPS = 15
TOTAL_FRAMES = 90  # 6 seconds loop at 15 fps
OUTPUT_PATH = "assets/hero-animated.gif"

# Ensure output directory
os.makedirs("assets", exist_ok=True)

# Try loading premium fonts, fallback to clean system fonts
def get_fonts():
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    # Name Font (Heavy / Bold)
    name_font = None
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if os.path.exists(p):
            try:
                name_font = ImageFont.truetype(p, 52)
                break
            except: pass
    if not name_font: name_font = ImageFont.load_default()

    # Subtitle Font
    sub_font = None
    for p in ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(p):
            try:
                sub_font = ImageFont.truetype(p, 18)
                break
            except: pass
    if not sub_font: sub_font = ImageFont.load_default()

    # Mono Technical Font
    mono_font = None
    for p in ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/cour.ttf"]:
        if os.path.exists(p):
            try:
                mono_font = ImageFont.truetype(p, 12)
                break
            except: pass
    if not mono_font: mono_font = ImageFont.load_default()

    # Tagline Font
    tag_font = None
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if os.path.exists(p):
            try:
                tag_font = ImageFont.truetype(p, 14)
                break
            except: pass
    if not tag_font: tag_font = ImageFont.load_default()

    return name_font, sub_font, mono_font, tag_font

NAME_FONT, SUB_FONT, MONO_FONT, TAG_FONT = get_fonts()

# Fixed seed for deterministic particle trajectories & nodes
random.seed(42)

# Generate Neural Network Nodes around left and right edges (framing center)
LEFT_NODES = []
for _ in range(16):
    x = random.randint(30, 280)
    y = random.randint(30, HEIGHT - 30)
    LEFT_NODES.append((x, y))

RIGHT_NODES = []
for _ in range(16):
    x = random.randint(WIDTH - 280, WIDTH - 30)
    y = random.randint(30, HEIGHT - 30)
    RIGHT_NODES.append((x, y))

# Floating Cyber Ambient Particles
PARTICLES = []
for _ in range(45):
    PARTICLES.append({
        'x': random.uniform(0, WIDTH),
        'y': random.uniform(0, HEIGHT),
        'speed': random.uniform(0.3, 1.2),
        'size': random.uniform(1.0, 2.5),
        'angle': random.uniform(0, math.pi * 2),
        'cyan_bias': random.random()
    })

# Circuit / Data Bus lines on top & bottom borders
CIRCUIT_LINES = [
    # (x1, y1, x2, y2, angle_x, angle_y, end_x, end_y)
    (50, 25, 200, 25, 220, 45, 380, 45),
    (WIDTH - 50, 25, WIDTH - 200, 25, WIDTH - 220, 45, WIDTH - 380, 45),
    (50, HEIGHT - 25, 180, HEIGHT - 25, 200, HEIGHT - 45, 340, HEIGHT - 45),
    (WIDTH - 50, HEIGHT - 25, WIDTH - 180, HEIGHT - 25, WIDTH - 200, HEIGHT - 45, WIDTH - 340, HEIGHT - 45),
]

def render_frame(f_idx):
    # Base background: Deep cosmic cyberpunk dark navy / near black
    img = Image.new("RGBA", (WIDTH, HEIGHT), (6, 8, 15, 255))
    draw = ImageDraw.Draw(img)

    # Master timeline normalized progress (0.0 to 1.0)
    t = f_idx / TOTAL_FRAMES

    # Scene timings:
    # Scene 1: 0 - 18 frames (0 - 1.2s): Initialization, HUD diagnostics, circuit sparks
    # Scene 2: 18 - 36 frames (1.2 - 2.4s): Neural grids, ambient node activation, sweep
    # Scene 3: 32 - 48 frames (2.1 - 3.2s): Glitch-assisted reveal of HIMESH MEHTA
    # Scene 4: 45 - 60 frames (3.0 - 4.0s): Reveal of Subtitles & Tags
    # Scene 5 & 6: 60 - 80 frames (4.0 - 5.3s): Full hold with ambient pulsing, data stream pulses
    # Loop fadeout: 80 - 90 frames (5.3 - 6.0s): Seamless blend out to frame 0

    # 1. Subtle Cyber Grid & Hex Floor / Ceiling depth
    grid_alpha = int(22 + 12 * math.sin(t * math.pi * 2))
    grid_color = (0, 160, 230, grid_alpha)
    # Perspective ground lines
    for gx in range(0, WIDTH + 60, 60):
        # Draw faint vertical grid lines with fade near center
        if gx < 320 or gx > WIDTH - 320:
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(0, 180, 255, int(grid_alpha * 0.6)), width=1)
    
    # Horizontal scanning guidelines
    for gy in [40, 80, HEIGHT - 80, HEIGHT - 40]:
        draw.line([(0, gy), (WIDTH, gy)], fill=(0, 140, 220, int(grid_alpha * 0.4)), width=1)

    # 2. Draw Circuit / Data Bus traces with traveling packets
    for seg in CIRCUIT_LINES:
        x1, y1, x2, y2, x3, y3, x4, y4 = seg
        draw.line([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], fill=(0, 180, 255, 60), width=1)
        # Pulse along the segment
        pulse_pos = ((f_idx * 3.5) % 300) / 300.0
        # draw a traveling glowing packet
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
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(180, 240, 255, 220))

    # 3. Neural Network Nodes on left & right flanks
    all_nodes = [(LEFT_NODES, (30, 280)), (RIGHT_NODES, (WIDTH - 280, WIDTH - 30))]
    node_activate_prog = min(1.0, max(0.0, (f_idx - 10) / 25.0))
    if node_activate_prog > 0:
        for node_group, (min_x, max_x) in all_nodes:
            # Draw connections
            for i, n1 in enumerate(node_group):
                for j, n2 in enumerate(node_group):
                    if i < j:
                        dist = math.hypot(n1[0] - n2[0], n1[1] - n2[1])
                        if dist < 85:
                            # Dynamic wave pulse across connections
                            wave = math.sin((n1[0] + n1[1]) * 0.05 - f_idx * 0.15)
                            alpha = int(min(255, max(0, (50 + 40 * wave) * node_activate_prog)))
                            color = (0, 210, 255, alpha) if (i + j) % 3 != 0 else (160, 100, 255, alpha)
                            draw.line([n1, n2], fill=color, width=1)
                
                # Draw node circles
                n_pulse = math.sin(f_idx * 0.2 + i)
                n_rad = 2.0 + 1.0 * n_pulse
                n_alpha = int(min(255, max(0, (140 + 80 * n_pulse) * node_activate_prog)))
                draw.ellipse([n1[0] - n_rad, n1[1] - n_rad, n1[0] + n_rad, n1[1] + n_rad], 
                             fill=(200, 245, 255, n_alpha))
                # subtle glow halo
                draw.ellipse([n1[0] - n_rad - 3, n1[1] - n_rad - 3, n1[0] + n_rad + 3, n1[1] + n_rad + 3], 
                             outline=(0, 200, 255, int(n_alpha * 0.3)), width=1)

    # 4. Floating Cyber Dust / Particles
    for p in PARTICLES:
        px = (p['x'] + math.cos(p['angle']) * f_idx * p['speed']) % WIDTH
        py = (p['y'] + math.sin(p['angle']) * f_idx * p['speed']) % HEIGHT
        p_alpha = int(120 + 80 * math.sin(f_idx * 0.1 + p['x']))
        if p['cyan_bias'] > 0.4:
            p_col = (140, 230, 255, p_alpha)
        else:
            p_col = (190, 140, 255, p_alpha)
        draw.ellipse([px - p['size'], py - p['size'], px + p['size'], py + p['size']], fill=p_col)

    # 5. Technical Interface Metadata (Top corners & HUD)
    if f_idx >= 5:
        hud_alpha = min(200, int((f_idx - 5) * 15))
        # Top Left Diagnostic HUD
        hud_lines_left = [
            "SYS_CORE // 01.AI.NEURAL",
            "STATUS   // ONLINE · OPTIMIZED",
            f"FRAME_SEQ // {f_idx:03d} / 090"
        ]
        for idx, line in enumerate(hud_lines_left):
            draw.text((35, 38 + idx * 15), line, font=MONO_FONT, fill=(0, 220, 255, int(hud_alpha * 0.85)))

        # Top Right Diagnostics
        hud_lines_right = [
            "LATENCY // 1.2ms [ZERO_LOSS]",
            "AGENTIC // ACTIVE_THREADS: 16",
            "MODEL   // HYPER_CONVERGENCE"
        ]
        for idx, line in enumerate(hud_lines_right):
            bbox = draw.textbbox((0, 0), line, font=MONO_FONT)
            tw = bbox[2] - bbox[0]
            draw.text((WIDTH - 35 - tw, 38 + idx * 15), line, font=MONO_FONT, fill=(170, 180, 240, int(hud_alpha * 0.85)))

    # 6. Central Cyber Glow Halo behind Typography
    # Center position calculations
    center_x = WIDTH // 2
    center_y = HEIGHT // 2 - 10

    glow_prog = min(1.0, max(0.0, (f_idx - 25) / 25.0))
    if glow_prog > 0:
        glow_radius_x = 320
        glow_radius_y = 90
        glow_alpha = int(35 * glow_prog * (1.0 + 0.15 * math.sin(f_idx * 0.2)))
        # Layered subtle radial gradient
        for r in range(4):
            rx = glow_radius_x - r * 50
            ry = glow_radius_y - r * 15
            draw.ellipse([center_x - rx, center_y - ry, center_x + rx, center_y + ry],
                         fill=(0, 140, 255, glow_alpha // (r + 1)))

    # 7. TYPOGRAPHY ANIMATION & RENDERING
    
    # --- Primary Title: "HIMESH MEHTA" ---
    name_str = "HIMESH MEHTA"
    bbox_name = draw.textbbox((0, 0), name_str, font=NAME_FONT)
    name_w = bbox_name[2] - bbox_name[0]
    name_h = bbox_name[3] - bbox_name[1]
    name_x = (WIDTH - name_w) // 2
    name_y = center_y - 45

    # Reveal timeline for name: Frame 28 to 50
    if f_idx >= 28:
        name_prog = min(1.0, (f_idx - 28) / 18.0)
        
        # Subtle chromatic aberration / glitch displacement during entry
        is_glitching = (28 <= f_idx <= 38 and f_idx % 2 == 0) or (f_idx == 44)
        disp_x = random.randint(-4, 4) if is_glitching else 0
        disp_y = random.randint(-2, 2) if is_glitching else 0

        # Letter by letter / wave unveil effect
        chars_to_show = int(len(name_str) * min(1.0, (f_idx - 28) / 14.0)) if f_idx < 42 else len(name_str)
        curr_text = name_str[:chars_to_show]

        # Draw Chromatic Shadow (Cyan & Magenta)
        if name_prog > 0.3:
            draw.text((name_x + disp_x - 2, name_y + disp_y), curr_text, font=NAME_FONT, fill=(0, 220, 255, int(160 * name_prog)))
            draw.text((name_x + disp_x + 2, name_y + disp_y), curr_text, font=NAME_FONT, fill=(255, 40, 140, int(110 * name_prog)))
        
        # Draw Crisp Pure White Main Title
        draw.text((name_x + disp_x, name_y + disp_y), curr_text, font=NAME_FONT, fill=(255, 255, 255, int(255 * name_prog)))

        # Light sweep shine across title
        if 40 <= f_idx <= 65:
            sweep_p = (f_idx - 40) / 25.0
            sweep_x = name_x - 50 + int((name_w + 100) * sweep_p)
            # draw high-intensity beam sweep
            draw.line([(sweep_x - 15, name_y - 5), (sweep_x + 15, name_y + name_h + 10)], 
                      fill=(255, 255, 255, int(180 * math.sin(sweep_p * math.pi))), width=3)

    # --- Subtitle 1: "BUILDING INTELLIGENT SYSTEMS" ---
    sub1_str = "BUILDING INTELLIGENT SYSTEMS"
    bbox_sub1 = draw.textbbox((0, 0), sub1_str, font=SUB_FONT)
    sub1_w = bbox_sub1[2] - bbox_sub1[0]
    sub1_x = (WIDTH - sub1_w) // 2
    sub1_y = name_y + name_h + 18

    if f_idx >= 44:
        sub1_prog = min(1.0, (f_idx - 44) / 15.0)
        # Smooth sliding up motion
        y_offset = int((1.0 - sub1_prog) * 12)
        draw.text((sub1_x, sub1_y + y_offset), sub1_str, font=SUB_FONT, fill=(0, 225, 255, int(235 * sub1_prog)))
        
        # Framing horizontal micro tech dashes
        dash_len = int(50 * sub1_prog)
        draw.line([(sub1_x - 20 - dash_len, sub1_y + 11), (sub1_x - 20, sub1_y + 11)], fill=(0, 200, 255, int(180 * sub1_prog)), width=1)
        draw.line([(sub1_x + sub1_w + 20, sub1_y + 11), (sub1_x + sub1_w + 20 + dash_len, sub1_y + 11)], fill=(0, 200, 255, int(180 * sub1_prog)), width=1)

    # --- Subtitle 2: "AI / ML · FULL STACK · AGENTIC SYSTEMS" ---
    sub2_str = "AI / ML  ·  FULL STACK  ·  AGENTIC SYSTEMS"
    bbox_sub2 = draw.textbbox((0, 0), sub2_str, font=TAG_FONT)
    sub2_w = bbox_sub2[2] - bbox_sub2[0]
    sub2_x = (WIDTH - sub2_w) // 2
    sub2_y = sub1_y + 32

    if f_idx >= 52:
        sub2_prog = min(1.0, (f_idx - 52) / 14.0)
        y_offset = int((1.0 - sub2_prog) * 10)
        draw.text((sub2_x, sub2_y + y_offset), sub2_str, font=TAG_FONT, fill=(185, 200, 230, int(220 * sub2_prog)))

    # 8. Framing Corner Cyber Brackets
    bracket_len = 35
    bracket_alpha = min(200, int(f_idx * 8))
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

    # 9. Bottom Scanline & Status Bar
    draw.line([(0, HEIGHT - 2), (WIDTH, HEIGHT - 2)], fill=(0, 170, 255, 90), width=2)
    scan_dot_x = int((f_idx / TOTAL_FRAMES) * WIDTH)
    draw.line([(scan_dot_x - 30, HEIGHT - 2), (scan_dot_x + 30, HEIGHT - 2)], fill=(255, 255, 255, 255), width=2)

    # 10. Seamless Loop Blend (Fade to/from Black in last 10 frames)
    if f_idx >= 80:
        fade_prog = (f_idx - 80) / 10.0
        # Overlay darkening layer for perfectly smooth looping
        dark_alpha = int(255 * fade_prog)
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (6, 8, 15, dark_alpha))
        img = Image.alpha_composite(img, overlay)
    elif f_idx <= 6:
        # Fade in from black on start
        fade_prog = 1.0 - (f_idx / 6.0)
        dark_alpha = int(255 * fade_prog)
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (6, 8, 15, dark_alpha))
        img = Image.alpha_composite(img, overlay)

    return img.convert("RGB")

print("Rendering high quality animation sequence...")
frames = []
for i in range(TOTAL_FRAMES):
    if i % 15 == 0:
        print(f"Rendering frame {i}/{TOTAL_FRAMES}...")
    frames.append(render_frame(i))

# Quantize and save GIF with custom palette optimization
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