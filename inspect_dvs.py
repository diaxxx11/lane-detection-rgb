import numpy as np
import matplotlib.pyplot as plt

file_path = "data/dvs_data/frame_000005.npz"
dvs = np.load(file_path)

data = dvs["data"]
mask = dvs["mask"]
action = dvs["action"]

plt.figure(figsize=(15,5))

# Channel 0 events
plt.subplot(1,3,1)
plt.imshow(data[:,:,0], cmap="hot")
plt.title("DVS channel 0")

# Lane mask
plt.subplot(1,3,2)
plt.imshow(mask[:,:,0], cmap="gray")
plt.title("Lane mask")

# Channel 1 events
plt.subplot(1,3,3)
plt.imshow(data[:,:,1], cmap="hot")
plt.title("DVS channel 1")

plt.show()

print("Action (steering, throttle, brake):", action)
