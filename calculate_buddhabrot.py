import numpy as np
import matplotlib.pyplot as plt
from numba import jit
import time

# Basic parameters
IMAGE_SIZE = 4000    # Image resolution
MAX_ITER = 1000      # Maximum iterations
SAMPLES = 10**7      # Number of samples
X_MIN, X_MAX = -2.0, 2.0
Y_MIN, Y_MAX = -2.0, 2.0

@jit(nopython=True)
def calculate_buddhabrot():
    hist = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint32)
    scale_x = (X_MAX - X_MIN) / IMAGE_SIZE
    scale_y = (Y_MAX - Y_MIN) / IMAGE_SIZE

    for sample in range(SAMPLES):
        # Generate random complex number c
        cx = np.random.uniform(X_MIN, X_MAX)
        cy = np.random.uniform(Y_MIN, Y_MAX)

        x = 0.0
        y = 0.0
        trajectory_x = []
        trajectory_y = []
        escape = False

        # Track trajectory
        for i in range(MAX_ITER):
            # Calculate z = z^2 + c
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
            # Record trajectory in histogram
            for j in range(len(trajectory_x)):
                px = int((trajectory_x[j] - X_MIN) / scale_x)
                py = int((trajectory_y[j] - Y_MIN) / scale_y)
                if 0 <= px < IMAGE_SIZE and 0 <= py < IMAGE_SIZE:
                    hist[px, py] += 1

    return hist

def normalize_and_save(histogram, filename='buddhabrot.png'):
    # Visualize using log scaling
    log_hist = np.log1p(histogram)

    # Normalize
    normalized = (log_hist - log_hist.min()) / (log_hist.max() - log_hist.min())

    # Generate image
    plt.figure(figsize=(20, 20), dpi=300)
    plt.imshow(normalized.T,
               cmap='hot',
               extent=[X_MIN, X_MAX, Y_MIN, Y_MAX])
    plt.axis('off')
    plt.tight_layout()

    # Save image
    plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()

if __name__ == "__main__":
    print("Starting Buddhabrot calculation...")
    start_time = time.time()

    # Main calculation
    histogram = calculate_buddhabrot()

    calc_time = time.time() - start_time
    print("Calculation time: %.2f seconds" % calc_time)

    # Save image
    print("Generating image...")
    normalize_and_save(histogram)
    print("Image saved as buddhabrot.png")
