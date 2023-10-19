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

##def generate_tree(height_increment, radius_decrement, main_trunk_initial_width, 
##                  num_main_trunk_increments, random_seed, scaling_factor, 
##                  scaling_variance, initial_branch_width, branch_angle, 
##                  min_branch_size, max_branch_size, num_recursive_branchings):
##    random.seed(random_seed)
##
##    colors = []
##    colors.append(Color(0,0,0,0))
##    colors.append(Color(255, 0, 0, 255))  # Red voxel for trunk
##    colors.append(Color(255, 255, 0, 255))  # Yellow voxel for branch
##    tree = np.zeros((100, 100, 100), dtype=int)  # Initialize a 3D array
##    
##    def generate_branch(x, y, z, height, radius, depth):
##        nonlocal tree
##        print(depth, np.count_nonzero(tree))
##        if depth <= 0 or np.count_nonzero(tree) > 50000:
##            return
##        
##        # Draw the current branch
##        for i in range(x - radius, x + radius + 1):
##            for j in range(y - radius, y + radius + 1):
##                for k in range(z, z + height + 1):
##                    if 0 <= i < tree.shape[0] and 0 <= j < tree.shape[1] and 0 <= k < tree.shape[2]:
##                        tree[i, j, k] = depth
##        
##        # Generate recursive branches
##        num_branches = random.randint(min_branch_size, max_branch_size)
##        for _ in range(num_branches):
##            branch_height = int(round(random.uniform(height_increment, height_increment + height)))
##            branch_radius = max(int(round(radius - radius_decrement)), 1)
##            branch_x = x + int(round(random.uniform(-branch_radius, branch_radius)))
##            branch_y = y + int(round(random.uniform(-branch_radius, branch_radius)))
##            branch_z = z + height
##            
##            # Apply scaling factor and variance
##            branch_height = int(round(branch_height * scaling_factor + random.uniform(-scaling_variance, scaling_variance)))
##            branch_radius = int(round(branch_radius * scaling_factor + random.uniform(-scaling_variance, scaling_variance)))
##            
##            # Generate the next branch
##            generate_branch(branch_x, branch_y, branch_z, branch_height, branch_radius, depth - 1)
##    
##    # Generate the main trunk
##    generate_branch(tree.shape[0] // 2, tree.shape[1] // 2, 0, 
##                    height_increment, main_trunk_initial_width, num_main_trunk_increments)
##    
##    return tree, colors
##
##def generate_tree2(h_increment, r_decrement, md_init, main_depth, rnd_seed, scaling, s_variance, bd_init, branch_depth, branch_angle, branch_min_size, branch_max_size, x, y, z, array):
##    if branch_depth < 1 and np.random.rand() > 0.5:
##        array[x][y][z] = 1
##        return
##    
##    sf = scaling + np.random.uniform(-1, 1) * s_variance
##    
##    array[x][y][z:z+h_increment] = 1
##    
##    # Branching logic
##    if branch_depth > 0 and np.random.uniform(0, 0.8) < (md_init - main_depth) / md_init:
##        r_angle = np.random.uniform(0, 720)
##        br_angle = branch_angle / 2 + np.random.uniform(0, 0.5) * branch_angle
##        new_increment = h_increment - h_increment / 2.5 * pow(r_decrement, branch_depth)
##        branch_ratio = (branch_angle / br_angle) - 1.0
##        branch_scaling = branch_min_size * branch_ratio + branch_max_size * (1.0 - branch_ratio)
##        main_scaling = sf * branch_ratio + branch_max_size * (1.0 - branch_ratio)
##        
##        # Recursive call for braches
##        generate_tree(x, y, z + h_increment, new_increment, r_decrement, md_init, md_init, np.random.uniform(0, 100), scaling, s_variance, bd_init, branch_depth - 1, branch_angle, branch_min_size, branch_max_size, array)
##        array[x][y][z] = 0
##        array[x][y][z:z+h_increment] = 1
##        array[x][y][z:z+int(new_increment / 2)] = 1
##        
##        # Recursive call for main path
##        generate_tree(x, y, z + h_increment, new_increment, r_decrement, md_init, main_depth - 1 - np.random.randint(0, 2), np.random.uniform(0, 100), scaling, s_variance, bd_init, branch_depth, branch_angle, branch_min_size, branch_max_size, array)
##        array[x][y][z] = 0
##        array[x][y][z:z+h_increment] = 1
##    
### Parameters
##tree_size = 100
##array_size = 100
##random_seed = 42
##
### Initialize the 3D array
##tree_array = np.zeros((array_size, array_size, tree_size), dtype=int)
##
### Generate the tree structure
##generate_tree2(h_increment=100, r_decrement=0.1, md_init=30, main_depth=15, rnd_seed=random_seed, scaling=0.97, s_variance=0.1, bd_init=4, branch_depth=3, branch_angle=75, branch_min_size=0.3, branch_max_size=0.8, x=array_size // 2, y=array_size // 2, z=0, array=tree_array)
##
### Parameters
##voxel_size = 1
##trunk_height = 20
##branch_height = 20
##num_branches = 5
##voxel_resolution = 64
##
### New Paramenters
##height_increment = 5
##radius_decrement = 0.7
##main_trunk_initial_width = 15
##num_main_trunk_increments = 15
##random_seed = 42
##scaling_factor = 0.97
##scaling_variance = 0.1
##initial_branch_width = 4
##branch_angle = 75
##min_branch_size = 2
##max_branch_size = 4
##num_recursive_branchings = 3

vox_filename = "tree_model_test.vox"

## Most recent attempt

def generate_tree3(tree_height=10, trunk_width=5, branch_density=0.6, 
                  branch_angle=45, min_branch_size=2, max_branch_size=5, 
                  random_seed=None):
    if random_seed is not None:
        random.seed(random_seed)
    
    # Initialize the tree array with zeros
    tree = np.zeros((tree_height, trunk_width * 2, trunk_width * 2), dtype=int)
    
    def generate_branch(x, y, z, height, width):
        nonlocal tree
        
        # Draw the current branch
        for i in range(x - width, x + width + 1):
            for j in range(y - width, y + width + 1):
                for k in range(z, z + height + 1):
                    if 0 <= i < tree.shape[0] and 0 <= j < tree.shape[1] and 0 <= k < tree.shape[2]:
                        tree[i, j, k] = 1
        
        # Generate recursive branches
        num_branches = int((2 * width - 1) * branch_density)
        for _ in range(num_branches):
            branch_height = random.randint(1, height)
            branch_width = random.randint(min_branch_size, max_branch_size)
            branch_x = x + random.randint(-width, width)
            branch_y = y + random.randint(-width, width)
            branch_z = z + height
            
            # Generate the next branch
            generate_branch(branch_x, branch_y, branch_z, branch_height, branch_width)
    
    # Generate the main trunk
    trunk_height = random.randint(tree_height // 2, tree_height)
    trunk_width = random.randint(trunk_width // 2, trunk_width)
    generate_branch(tree.shape[0] // 2, tree.shape[1] // 2, 0, trunk_height, trunk_width)
    
    return tree

# Example usage:
# Set your desired parameters here
tree_height = 7
trunk_width = 6
branch_density = 0.1
branch_angle = 45
min_branch_size = 2
max_branch_size = 3
random_seed = 42

# Generate the tree using the specified parameters
tree_structure = generate_tree3(tree_height, trunk_width, branch_density, 
                               branch_angle, min_branch_size, max_branch_size, 
                               random_seed)

## End most recent attempt

# Old function call
#tree_model_data, colors = generate_tree(voxel_size, trunk_height, branch_height, num_branches, voxel_resolution)

##tree_model_data, colors = generate_tree(height_increment, radius_decrement, main_trunk_initial_width, 
##                  num_main_trunk_increments, random_seed, scaling_factor, 
##                  scaling_variance, initial_branch_width, branch_angle, 
##                  min_branch_size, max_branch_size, num_recursive_branchings)

#voxels = Vox.from_dense(tree_model_data)
voxels = Vox.from_dense(tree_structure)
# Pad out the colors list to include 256 members so VoxEdit doesn't crash
#colors = colors + [Color(0, 0, 0, 0) for _ in range(256 - len(colors))]
#voxels.palette = colors

VoxWriter(vox_filename, voxels).write()

print("Completed creation of tree model")
