from PIL import Image
import os

directory = './testoutput'
output_gif = 'output.gif'
duration = 800
loop = 0

# Get only .png files and sort numerically based on filename (e.g., "1.png", "2.png", ...)
image_files = sorted(
    [os.path.join(directory, f) for f in os.listdir(
        directory) if f.lower().endswith('.png')],
    key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
)

# Load images
frames = [Image.open(img).convert('RGB') for img in image_files]

# Save as GIF
frames[0].save(
    output_gif,
    save_all=True,
    append_images=frames[1:],
    duration=duration,
    loop=loop
)
