from PIL import Image, ImageDraw, ImageFont
import random

# Settings
width, height = 1200, 350
frames = 30
fps = 10  # frames per second
output_path = "assets/himesh-hero.gif"

# Colors
bg_color = (0, 0, 0)  # black
grid_color = (0, 150, 255)  # electric blue
particle_color = (150, 200, 255)  # light cyan
text_color = (255, 255, 255)  # white

# Create base image
base_image = Image.new("RGB", (width, height), bg_color)
draw = ImageDraw.Draw(base_image)

# Font (default PIL font)
try:
    font = ImageFont.truetype("arial.ttf", 80)
    small_font = ImageFont.truetype("arial.ttf", 40)
except:
    font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Text to display
main_text = "HIMESH MEHTA"
secondary_text = "BUILDING INTELLIGENT SYSTEMS"
tertiary_text = "AI / ML · FULL STACK · AGENTIC SYSTEMS"

# Precompute grid positions
grid_spacing = 150
grid_lines = []
for i in range(0, width + grid_spacing, grid_spacing):
    grid_lines.append((i, 0, i, height))
for i in range(0, height + grid_spacing, grid_spacing):
    grid_lines.append((0, i, width, i))

# Particle positions
particles = []
for _ in range(30):
    x = random.randint(0, width)
    y = random.randint(0, height)
    dx = random.uniform(-0.5, 0.5)
    dy = random.uniform(-0.5, 0.5)
    particles.append([x, y, dx, dy])

def draw_frame(frame_idx):
    img = Image.new("RGB", (width, height), bg_color)
    d = ImageDraw.Draw(img)
    # Draw grid lines
    for x1, y1, x2, y2 in grid_lines:
        d.line([x1, y1, x2, y2], fill=grid_color, width=1)
    # Update particle positions
    for p in particles:
        p[0] += p[2]
        p[1] += p[3]
        # Bounce off edges
        if p[0] <= 0 or p[0] >= width:
            p[2] = -p[2]
        if p[1] <= 0 or p[1] >= height:
            p[3] = -p[3]
        d.ellipse([p[0]-3, p[1]-3, p[0]+3, p[1]+3], fill=particle_color)
    # Text animation: main text positioning
    bbox_main = d.textbbox((0, 0), main_text, font=font)
    w_main, h_main = bbox_main[2] - bbox_main[0], bbox_main[3] - bbox_main[1]
    
    bbox_sec = d.textbbox((0, 0), secondary_text, font=small_font)
    w_sec, h_sec = bbox_sec[2] - bbox_sec[0], bbox_sec[3] - bbox_sec[1]
    
    bbox_ter = d.textbbox((0, 0), tertiary_text, font=small_font)
    w_ter, h_ter = bbox_ter[2] - bbox_ter[0], bbox_ter[3] - bbox_ter[1]

    # Center and smooth entry animation
    target_main_y = (height - (h_main + h_sec + h_ter + 40)) // 2
    progress = min(1.0, (frame_idx + 1) / (frames * 0.4))
    main_y = int(target_main_y + (1.0 - progress) * 60)
    main_x = (width - w_main) // 2
    d.text((main_x, main_y), main_text, font=font, fill=text_color)
    
    # Secondary text
    sec_y = main_y + h_main + 20
    sec_x = (width - w_sec) // 2
    d.text((sec_x, sec_y), secondary_text, font=small_font, fill=text_color)
    
    # Tertiary text
    ter_y = sec_y + h_sec + 10
    ter_x = (width - w_ter) // 2
    d.text((ter_x, ter_y), tertiary_text, font=small_font, fill=text_color)
    return img

frames_list = []
for i in range(frames):
    frames_list.append(draw_frame(i))

# Save as GIF
frames_list[0].save(
    output_path,
    save_all=True,
    append_images=frames_list[1:],
    duration=1000 // fps,
    loop=0,
    optimize=True,
    disposal=2
)
print(f"GIF saved to {output_path}")