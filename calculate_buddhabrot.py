import numpy as np
import matplotlib.pyplot as plt
from numba import jit
import time
from multiprocessing import Pool
import os

# Basic parameters
IMAGE_SIZE = 4000    # Image resolution
SAMPLES = 10**7      # Number of samples
X_MIN, X_MAX = -2.0, 2.0
Y_MIN, Y_MAX = -2.0, 2.0

# Different iteration limits for RGB channels
MAX_ITER_R = 10000    # Red channel - short trajectories
MAX_ITER_G = 100000   # Green channel - medium trajectories
MAX_ITER_B = 1000000  # Blue channel - long trajectories

# Number of processes to use (typically number of CPU cores)
NUM_PROCESSES = os.cpu_count()
CHUNK_SIZE = SAMPLES // NUM_PROCESSES

@jit(nopython=True)
def calculate_nebulabrot_chunk(max_iter, start_sample, num_samples):
    hist = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint32)
    scale_x = (X_MAX - X_MIN) / IMAGE_SIZE
    scale_y = (Y_MAX - Y_MIN) / IMAGE_SIZE

    for sample in range(num_samples):
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

def process_channel(args):
    max_iter, start_sample, chunk_size = args
    return calculate_nebulabrot_chunk(max_iter, start_sample, chunk_size)

def parallel_nebulabrot(max_iter):
    # Create chunks for parallel processing
    chunks = [(max_iter, i * CHUNK_SIZE, CHUNK_SIZE)
              for i in range(NUM_PROCESSES)]

    # Process chunks in parallel
    with Pool() as pool:
        results = pool.map(process_channel, chunks)

    # Combine results
    return sum(results)

def normalize_channel(histogram):
    log_hist = np.log1p(histogram)
    normalized = (log_hist - log_hist.min()) / (log_hist.max() - log_hist.min())
    return normalized

def create_nebulabrot():
    print(f"Using {NUM_PROCESSES} processes")

    print("Calculating Red channel...")
    start_time = time.time()
    red = parallel_nebulabrot(MAX_ITER_R)
    print(f"Red channel completed in {time.time() - start_time:.2f} seconds")

    print("Calculating Green channel...")
    start_time = time.time()
    green = parallel_nebulabrot(MAX_ITER_G)
    print(f"Green channel completed in {time.time() - start_time:.2f} seconds")

    print("Calculating Blue channel...")
    start_time = time.time()
    blue = parallel_nebulabrot(MAX_ITER_B)
    print(f"Blue channel completed in {time.time() - start_time:.2f} seconds")

    # Normalize each channel
    red_norm = normalize_channel(red)
    green_norm = normalize_channel(green)
    blue_norm = normalize_channel(blue)

    # Combine channels
    rgb_image = np.zeros((IMAGE_SIZE, IMAGE_SIZE, 3))
    rgb_image[:,:,0] = red_norm
    rgb_image[:,:,1] = green_norm
    rgb_image[:,:,2] = blue_norm

    return rgb_image

def save_nebulabrot(rgb_image, filename='nebulabrot.png'):
    plt.figure(figsize=(20, 20), dpi=300)
    plt.imshow(rgb_image,
               extent=[X_MIN, X_MAX, Y_MIN, Y_MAX])
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()

if __name__ == "__main__":
    print("Starting Nebulabrot calculation...")
    total_start_time = time.time()

    # Calculate all channels and combine
    rgb_image = create_nebulabrot()

    total_calc_time = time.time() - total_start_time
    print(f"Total calculation time: {total_calc_time:.2f} seconds")

    # Save image
    print("Generating final image...")
    save_nebulabrot(rgb_image)
    print("Image saved as nebulabrot.png")
