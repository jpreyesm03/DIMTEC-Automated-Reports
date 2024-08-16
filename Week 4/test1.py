import matplotlib.pyplot as plt
import numpy as np

# Example data (replace with your actual data)
dates = np.linspace(1, 31, 31)  # Days of the month
edge = np.random.normal(300, 100, 31)  # Replace with actual edge data
midgress = np.random.normal(100, 50, 31)  # Replace with actual midgress data
origin = np.random.normal(10, 5, 31)  # Replace with actual origin data
offload = np.random.normal(80, 20, 31)  # Replace with actual offload data

fig, ax1 = plt.subplots(figsize=(14, 6))

# Plot Edge, Midgress, and Origin on the left y-axis
ax1.plot(dates, edge, label='Edge', color='blue')
ax1.plot(dates, midgress, label='Midgress', color='green')
ax1.plot(dates, origin, label='Origin', color='orange')
ax1.set_xlabel('Date (July)')
ax1.set_ylabel('Bits/sec')
ax1.legend(loc='upper left')

# Create a second y-axis for Offload
ax2 = ax1.twinx()
ax2.plot(dates, offload, label='Offload', color='red')
ax2.set_ylabel('Offload')
ax2.legend(loc='upper right')

# Add title and grid
plt.title('Edge, Midgress, and Origin bits/sec with Offload')
ax1.grid(True)

# Show the plot
plt.show()
