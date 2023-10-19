from pyvox.models import Vox, Model, Voxel, Size, Color
from pyvox.writer import VoxWriter
import numpy as np
import random
import math

from matplotlib.cm import inferno

##def generate_tree(voxel_size, trunk_height, branch_height, num_branches, voxel_resolution):
##    colors = []
##    colors.append(Color(0,0,0,0))
##    # Create an empty Vox model
##    voxels = np.zeros((voxel_resolution, voxel_resolution, voxel_resolution), dtype=np.uint8)  # Initialize with transparent voxels
##
##    # Trunk
##    colors.append(Color(255, 0, 0, 255))  # Red voxel for trunk
##    for z in range(trunk_height):
##        voxels[15][15][z] = 1
##
##    # Branches
##    colors.append(Color(0, 0, 255, 255))  # Blue voxel for trunk
##    
##    
##    for _ in range(num_branches):
##        x, y, z = 15, 15, trunk_height + random.randint(1, branch_height)
##        for _ in range(random.randint(3, 7)):
##            # Ensure branch position is within grid boundaries
##            if 0 <= x < voxel_resolution and 0 <= y < voxel_resolution and 0 <= z < voxel_resolution:
##                voxels[x][y][z] = 2  # Blue voxel for branches
##                x += random.choice([-1, 0, 1])
##                y += random.choice([-1, 0, 1])
##                z += random.choice([0, 1])
##
##    return voxels, colors

def generate_tree(height_increment, radius_decrement, main_trunk_initial_width, 
                  num_main_trunk_increments, random_seed, scaling_factor, 
                  scaling_variance, initial_branch_width, branch_angle, 
                  min_branch_size, max_branch_size, num_recursive_branchings):
    random.seed(random_seed)

    colors = []
    colors.append(Color(0,0,0,0))
    colors.append(Color(255, 0, 0, 255))  # Red voxel for trunk
    colors.append(Color(255, 255, 0, 255))  # Yellow voxel for branch
    tree = np.zeros((100, 100, 100), dtype=int)  # Initialize a 3D array
    
    def generate_branch(x, y, z, height, radius, depth):
        nonlocal tree
        print(depth, np.count_nonzero(tree))
        if depth <= 0 or np.count_nonzero(tree) > 50000:
            return
        
        # Draw the current branch
        for i in range(x - radius, x + radius + 1):
            for j in range(y - radius, y + radius + 1):
                for k in range(z, z + height + 1):
                    if 0 <= i < tree.shape[0] and 0 <= j < tree.shape[1] and 0 <= k < tree.shape[2]:
                        tree[i, j, k] = depth
        
        # Generate recursive branches
        num_branches = random.randint(min_branch_size, max_branch_size)
        for _ in range(num_branches):
            branch_height = int(round(random.uniform(height_increment, height_increment + height)))
            branch_radius = max(int(round(radius - radius_decrement)), 1)
            branch_x = x + int(round(random.uniform(-branch_radius, branch_radius)))
            branch_y = y + int(round(random.uniform(-branch_radius, branch_radius)))
            branch_z = z + height
            
            # Apply scaling factor and variance
            branch_height = int(round(branch_height * scaling_factor + random.uniform(-scaling_variance, scaling_variance)))
            branch_radius = int(round(branch_radius * scaling_factor + random.uniform(-scaling_variance, scaling_variance)))
            
            # Generate the next branch
            generate_branch(branch_x, branch_y, branch_z, branch_height, branch_radius, depth - 1)
    
    # Generate the main trunk
    generate_branch(tree.shape[0] // 2, tree.shape[1] // 2, 0, 
                    height_increment, main_trunk_initial_width, num_main_trunk_increments)
    
    return tree, colors

# Example usage:
# tree = generate_tree(height_increment=5, radius_decrement=1, main_trunk_initial_width=8, 
#                     num_main_trunk_increments=5, random_seed=42, scaling_factor=0.7, 
#                     scaling_variance=0.1, initial_branch_width=5, branch_angle=45, 
#                     min_branch_size=3, max_branch_size=7, num_recursive_branchings=3)



# Parameters
voxel_size = 1
trunk_height = 20
branch_height = 20
num_branches = 5
voxel_resolution = 64

# New Paramenters
height_increment = 5
radius_decrement = 0.7
main_trunk_initial_width = 15
num_main_trunk_increments = 15
random_seed = 42
scaling_factor = 0.97
scaling_variance = 0.1
initial_branch_width = 4
branch_angle = 75
min_branch_size = 2
max_branch_size = 4
num_recursive_branchings = 3

vox_filename = "tree_model_test.vox"

# Old function call
#tree_model_data, colors = generate_tree(voxel_size, trunk_height, branch_height, num_branches, voxel_resolution)

tree_model_data, colors = generate_tree(height_increment, radius_decrement, main_trunk_initial_width, 
                  num_main_trunk_increments, random_seed, scaling_factor, 
                  scaling_variance, initial_branch_width, branch_angle, 
                  min_branch_size, max_branch_size, num_recursive_branchings)

voxels = Vox.from_dense(tree_model_data)
# Pad out the colors list to include 256 members so VoxEdit doesn't crash
colors = colors + [Color(0, 0, 0, 0) for _ in range(256 - len(colors))]
voxels.palette = colors

VoxWriter(vox_filename, voxels).write()

print("Completed creation of tree model")
