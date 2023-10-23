import numpy as np

def r_tree(h_increment, r_decrement, md_init, main_depth, rnd_seed, scaling, s_variance, bd_init, branch_depth, branch_angle, branch_min_size, branch_max_size, tree, x, y, z_value):
    rnd_values = np.random.rand(10) * (rnd_seed % 1000)  # Use modulo to ensure consistency
    
    def z(from_val, to_val, idx):
        return rnd_values[idx] * (to_val - from_val) + from_val
    
    if branch_depth < 1 and tree[int(x), int(y), int(z_value)] == 0:
        tree[int(x), int(y), int(z_value)] = 2  # Mark as leaf node
    else:
        sf = scaling + z(-1, 1, 1) * s_variance
        
        if tree[int(x), int(y), int(z_value)] == 0:
            tree[int(x), int(y), int(z_value)] = 1  # Mark as trunk
        
        if branch_depth > 0 and z(0, 0.8, 2) < ((md_init - main_depth) / md_init):
            r_angle = z(0, 720, 3)
            br_angle = branch_angle / 2 + z(0, 0.5, 4) * branch_angle
            new_increment = h_increment - h_increment / 2.5 * pow(r_decrement, branch_depth)
            branch_ratio = (branch_angle / br_angle) - 1.0
            branch_scaling = branch_min_size * branch_ratio + branch_max_size * (1.0 - branch_ratio)
            main_scaling = sf * branch_ratio + branch_max_size * (1.0 - branch_ratio)
            
            new_x, new_y, new_z = int(x), int(y), int(z_value + h_increment)
            
            for i in range(int(x - branch_scaling), int(x + branch_scaling) + 1):
                for j in range(int(y - branch_scaling), int(y + branch_scaling) + 1):
                    for k in range(int(z_value), int(z_value + h_increment + 1)):
                        if 0 <= i < tree.shape[0] and 0 <= j < tree.shape[1] and 0 <= k < tree.shape[2]:
                            tree[i, j, k] = 3  # Mark as branch
            
            r_tree(new_increment, r_decrement, md_init, md_init, int(z(0, 100, 5)), scaling, s_variance, bd_init, branch_depth - 1, branch_angle, branch_min_size, branch_max_size, tree, new_x, new_y, new_z)
            
            if main_depth > 0:
                new_z = int(z(0, 2, 6))
                r_tree(new_increment, r_decrement, md_init, main_depth - 1 - new_z, int(z(0, 100, 7)), scaling, s_variance, bd_init, branch_depth, branch_angle, branch_min_size, branch_max_size, tree, int(x), int(y), int(z_value + h_increment))
        
        else:
            if main_depth > 0:
                new_z = int(z(0, 2, 0))
                r_tree(h_increment, r_decrement, md_init, main_depth - 1 - new_z, int(z(0, 100, 9)), scaling, s_variance, bd_init, branch_depth, branch_angle, branch_min_size, branch_max_size, tree, int(x), int(y), int(z_value + h_increment))
            
            if branch_depth < 2 and tree[int(x), int(y), int(z_value)] == 0:
                tree[int(x), int(y), int(z_value)] = 4  # Mark as leaf node

# Parameters
tree_shape = (100, 100, 100)  # Define the shape of the tree (x, y, z)
tree = np.zeros(tree_shape, dtype=int)
x, y, z_value = tree_shape[0] // 2, tree_shape[1] // 2, 0

# Call the recursive tree function
r_tree(h_increment=10, r_decrement=0.2, md_init=20, main_depth=25, rnd_seed=41, scaling=0.97, s_variance=0.1, bd_init=4, branch_depth=3, branch_angle=35, branch_min_size=0.3, branch_max_size=0.8, tree=tree, x=x, y=y, z_value=z_value)

# Print the generated tree
print(np.count_nonzero(tree))
