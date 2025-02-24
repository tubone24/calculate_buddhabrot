import numpy as np
import matplotlib.pyplot as plt
from numba import jit
import time

# Basic parameters
IMAGE_SIZE = 4000    # Image resolution
SAMPLES = 10**7      # Number of samples
X_MIN, X_MAX = -2.0, 2.0
Y_MIN, Y_MAX = -2.0, 2.0

# Different iteration limits for RGB channels
MAX_ITER_R = 1000    # Red channel - short trajectories
MAX_ITER_G = 10000   # Green channel - medium trajectories
MAX_ITER_B = 100000  # Blue channel - long trajectories

@jit(nopython=True)
def calculate_nebulabrot(max_iter):
    hist = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint32)
    scale_x = (X_MAX - X_MIN) / IMAGE_SIZE
    scale_y = (Y_MAX - Y_MIN) / IMAGE_SIZE

    for sample in range(SAMPLES):
        cx = np.random.uniform(X_MIN, X_MAX)
        cy = np.random.uniform(Y_MIN, Y_MAX)

        x = 0.0
        y = 0.0
        trajectory_x = []
        trajectory_y = []
        escape = False

        for i in range(max_iter):
            x_new = x*x - y*y + cx
            y_new = 2*x*y + cy
            x = x_new
            y = y_new

            trajectory_x.append(x)
            trajectory_y.append(y)

            if x*x + y*y > 4:
                escape = True
                break

        if escape:
            for j in range(len(trajectory_x)):
                px = int((trajectory_x[j] - X_MIN) / scale_x)
                py = int((trajectory_y[j] - Y_MIN) / scale_y)
                if 0 <= px < IMAGE_SIZE and 0 <= py < IMAGE_SIZE:
                    hist[px, py] += 1

    return hist

def normalize_channel(histogram):
    log_hist = np.log1p(histogram)
    normalized = (log_hist - log_hist.min()) / (log_hist.max() - log_hist.min())
    return normalized

def create_nebulabrot():
    print("Calculating Red channel...")
    red = calculate_nebulabrot(MAX_ITER_R)

    print("Calculating Green channel...")
    green = calculate_nebulabrot(MAX_ITER_G)

    print("Calculating Blue channel...")
    blue = calculate_nebulabrot(MAX_ITER_B)

    # Normalize each channel
    red_norm = normalize_channel(red)
    green_norm = normalize_channel(green)
    blue_norm = normalize_channel(blue)

    # Combine channels - shape should be (height, width, 3)
    rgb_image = np.zeros((IMAGE_SIZE, IMAGE_SIZE, 3))
    rgb_image[:,:,0] = red_norm
    rgb_image[:,:,1] = green_norm
    rgb_image[:,:,2] = blue_norm

    return rgb_image

def save_nebulabrot(rgb_image, filename='nebulabrot.png'):
    plt.figure(figsize=(20, 20), dpi=300)
    plt.imshow(rgb_image,  # Remove .T here
               extent=[X_MIN, X_MAX, Y_MIN, Y_MAX])
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()

if __name__ == "__main__":
    print("Starting Nebulabrot calculation...")
    start_time = time.time()

    # Calculate all channels and combine
    rgb_image = create_nebulabrot()

    calc_time = time.time() - start_time
    print("Total calculation time: %.2f seconds" % calc_time)

    # Save image
    print("Generating final image...")
    save_nebulabrot(rgb_image)
    print("Image saved as nebulabrot.png")
