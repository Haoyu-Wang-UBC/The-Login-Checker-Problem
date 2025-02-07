import matplotlib.pyplot as plt

# Data from the table
x = [1, 2, 3, 4, 5]  # User counts in millions
# y_linear = [0.00856, 0.021851, 0.02855, 0.033668, 0.042824]
# y_binary = [0.0000137, 0.0000152, 0.0000151, 0.0000162, 0.0000168]
# y_hash = [0.0000031, 0.0000033, 0.0000033, 0.0000039, 0.0000032]
# y_bloom = [0.0000189, 0.000021, 0.0000159, 0.0000214, 0.0000199]
# y_cuckoo = [0.0000072, 0.0000079, 0.0000069, 0.0000073, 0.0000082]


# Data extracted from the image
y_linear = [0.00855600, 0.01825000, 0.02765700, 0.03502000, 0.04378300]
y_binary = [0.00001400, 0.00001560, 0.00001520, 0.00001760, 0.00001510]
y_hash = [0.00000300, 0.00000350, 0.00000270, 0.00000270, 0.00000350]
y_bloom = [0.00001590, 0.00001840, 0.00001580, 0.00001900, 0.00001980]
y_cuckoo = [0.00000670, 0.00000720, 0.00000720, 0.00000700, 0.00000680]

# Plotting the data with logarithmic scale for the y-axis
plt.figure(figsize=(10, 6))
plt.plot(x, y_linear, marker='o', label='Linear Search')
plt.plot(x, y_binary, marker='o', label='Binary Search')
plt.plot(x, y_hash, marker='o', label='Hash Search')
plt.plot(x, y_bloom, marker='o', label='BloomFilter Search')
plt.plot(x, y_cuckoo, marker='o', label='CuckooFilter Search')

# Adding labels, title, and setting log scale
plt.xlabel('Number of Users (in Millions)')
plt.ylabel('Search Time (in Seconds)')
plt.yscale('log')  # Set y-axis to logarithmic scale
plt.title('Search Time for Different Data Structures (Log Scale)')
plt.xticks(x, labels=[f"{i}M" for i in x])
plt.legend()
plt.grid(True, which="both", linestyle="--")
plt.tight_layout()

# Show the plot
plt.show()
