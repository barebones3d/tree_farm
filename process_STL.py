from stl import mesh
import numpy as np
from pyvox.models import Vox, Color
from pyvox.writer import VoxWriter

def process_stl(file_path, num_slices):
    # Load STL file
    mesh_data = mesh.Mesh.from_file(file_path)
    
    # Determine the bounding box of the STL model
    min_coords = np.min(mesh_data.v0, axis=0)
    max_coords = np.max(mesh_data.v0, axis=0)
    
    # Calculate scaling factors for each dimension
    x_scale = 254 / (max_coords[0] - min_coords[0] + 1)
    y_scale = 254 / (max_coords[1] - min_coords[1] + 1)
    z_scale = num_slices / (max_coords[2] - min_coords[2] + 1)
    
    # Apply scaling to vertices
    scaled_vertices = ((mesh_data.v0 - min_coords) * [x_scale, y_scale, z_scale]).astype(int)
    
    # Initialize 3D grid
    grid = np.zeros((num_slices, 255, 255), dtype=int)
    
    # Iterate through scaled vertices and fill the grid
    for vertex in scaled_vertices:
        x, y, z = vertex
        if 0 <= z < num_slices:
            grid[z, y, x] = 1
    
##    # Iterate through slices and fill the grid
##    for i in range(num_slices):
##        z_min = min_coords[2] + i * slice_height
##        z_max = z_min + slice_height
##        
##        # Get vertices within the current slice
##        vertices_in_slice = mesh_data.v0[
##            (mesh_data.v0[:, 2] >= z_min) & (mesh_data.v0[:, 2] < z_max)
##        ]
##        
##        # Fill the 2D grid for the current slice
##        for vertex in vertices_in_slice:
##            x, y, z = vertex
##            grid[i, int(y - min_coords[1]), int(x - min_coords[0])] = 1
    
    # Identify connected regions using Flood Fill algorithm
    def flood_fill(x, y, z, region_num):
        if 0 <= z < num_slices and 0 <= y < grid.shape[1] and 0 <= x < grid.shape[2] and grid[z, y, x] == 1:
            grid[z, y, x] = region_num
            flood_fill(x + 1, y, z, region_num)
            flood_fill(x - 1, y, z, region_num)
            flood_fill(x, y + 1, z, region_num)
            flood_fill(x, y - 1, z, region_num)
            flood_fill(x, y, z + 1, region_num)
            flood_fill(x, y, z - 1, region_num)
    
    region_num = 2
    
    # Apply Flood Fill to identify connected regions
    for z in range(num_slices):
        for y in range(grid.shape[1]):
            for x in range(grid.shape[2]):
                if grid[z, y, x] == 1:
                    if region_num >= 256:
                        region_num = 255
                    flood_fill(x, y, z, region_num)
                    region_num += 1
    
    return grid

# Example usage
file_path = 'models/young_maple.stl'  # Replace with the path to your STL file
num_slices = 255  # Number of slices
tree = process_stl(file_path, num_slices)
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

# Print the generated tree
print(tree)
##for i in range(0,257):
##    print(i, np.count_nonzero(tree==i))
print(np.max(tree))
print(tree.shape)  # Print the shape of the resulting 3D grid


# Save the Vox file
vox_filename = "treeSTL.vox"
VoxWriter(vox_filename, voxels).write()

print(file_path + " rendering complete.")
