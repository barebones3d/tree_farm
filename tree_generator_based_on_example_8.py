import numpy as np
from pyvox.models import Vox, Color
from pyvox.writer import VoxWriter


def r_tree(tree_shape, h_increment, r_decrement, md_init, main_depth, rnd_seed, scaling, s_variance, bd_init, branch_depth, branch_angle, branch_min_size, branch_max_size):
    tree = np.zeros(tree_shape, dtype=int)  # Initialize the tree array with zeros
    
    def random(seed, mod_val):
        # Custom random function using integer operations only
        seed = (seed * 1103515245 + 12345) & 0x7fffffff
        return (seed // 65536) % mod_val
    
    def z(from_val, to_val, idx):
        return random(rnd_seed + idx, to_val - from_val + 1) + from_val
    
    def generate_branch(x, y, z_value, h_increment, branch_depth):
        nonlocal tree
        if branch_depth < 1 or tree[x, y, z_value] != 0:
            return
        
        tree[x, y, z_value] = 1  # Mark as trunk
        
        sf = scaling + (z(-1, 1, 1) * s_variance) // 100
        
        if branch_depth > 0 and z(0, 100, 2) < ((md_init - main_depth) // md_init):
            r_angle = z(0, 720, 3)
            br_angle = branch_angle // 2 + (z(0, 50, 4) * branch_angle) // 100
            new_increment = (h_increment - (h_increment * 5 // 10 * pow(r_decrement, branch_depth) // 100))
            branch_ratio = (branch_angle * 100 // br_angle) - 100
            branch_scaling = ((branch_min_size * branch_ratio + branch_max_size * (100 - branch_ratio)) // 100)
            main_scaling = ((sf * branch_ratio + branch_max_size * (100 - branch_ratio)) // 100)
            
            for i in range(x - branch_scaling, x + branch_scaling + 1):
                for j in range(y - branch_scaling, y + branch_scaling + 1):
                    for k in range(z_value, z_value + h_increment + 1):
                        if 0 <= i < tree.shape[0] and 0 <= j < tree.shape[1] and 0 <= k < tree.shape[2]:
                            tree[i, j, k] = 3  # Mark as branch
            
            generate_branch(x, y, z_value + h_increment, new_increment, branch_depth - 1)
            if main_depth > 0:
                new_z = z(0, 2, 6)
                generate_branch(x, y, z_value + h_increment, new_increment, main_depth - 1 - new_z)
            new_z = z(0, 2, 0)
            generate_branch(x, y, z_value + h_increment, h_increment, main_depth - 1 - new_z)
            
            if branch_depth < 2 and z(0, 100, 9) < 50:
                tree[x, y, z_value] = 4  # Mark as leaf node

    rnd_seed = random(rnd_seed, 10000)  # Initialize random seed
    x, y, z_value = tree_shape[0] // 2, tree_shape[1] // 2, 0  # Starting position
    
    generate_branch(x, y, z_value, h_increment, branch_depth)
    
    return tree

# Example usage:
tree_shape = (100, 100, 100)  # Define the shape of the tree (x, y, z)
h_increment = 10
r_decrement = 1
md_init = 30
main_depth = 25
rnd_seed = 41
scaling = 100
s_variance = 10
bd_init = 4
branch_depth = 3
branch_angle = 35
branch_min_size = 40
branch_max_size = 120




# Parameters
tree_shape = (100, 100, 100)  # Define the shape of the tree (x, y, z)
tree = np.zeros(tree_shape, dtype=int)
x, y, z_value = tree_shape[0] // 2, tree_shape[1] // 2, 0

# Call the recursive tree function
#r_tree(h_increment=10, r_decrement=2, md_init=20, main_depth=25, rnd_seed=41, scaling=97, s_variance=10, bd_init=4, branch_depth=3, branch_angle=35, branch_min_size=30, branch_max_size=80, tree=tree, x=x, y=y, z_value=z_value)

tree = r_tree(tree_shape, h_increment, r_decrement, md_init, main_depth, rnd_seed, scaling, s_variance, bd_init, branch_depth, branch_angle, branch_min_size, branch_max_size)
# Colors
trunk_color = Color(139, 69, 19, 255)  # Brown
branch_color = Color(0, 128, 0, 255)  # Green
leaf_color = Color(0, 255, 0, 255)  # Bright Green

# Assign colors to the voxels in the tree based on their values
colors = {
    1: trunk_color,  # Trunk
    3: branch_color,  # Branches
    4: leaf_color  # Leaves
}

# Create a list of RGBA tuples for the palette
palette = [colors.get(value, Color(0, 0, 0, 0)) for value in range(256)]

# Create a Vox object with colors assigned to voxels
voxels = Vox.from_dense(tree)
voxels.palette = palette

# Save the Vox file
vox_filename = "tree.vox"
VoxWriter(vox_filename, voxels).write()

# Print the generated tree
print(tree)
for i in range(0,5):
    print(i, np.count_nonzero(tree==i))
