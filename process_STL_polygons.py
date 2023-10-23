from stl import mesh
import numpy as np
from pyvox.models import Vox, Color
from pyvox.writer import VoxWriter
from scipy.spatial import Delaunay

import numpy as np
from stl import mesh
from scipy.spatial import Delaunay

def process_stl(file_path, num_slices, max_distance=1.0):
    # Load STL file
    mesh_data = mesh.Mesh.from_file(file_path)
    
    # Determine the bounding box of the STL model
    min_coords = np.min(mesh_data.v0, axis=0)
    max_coords = np.max(mesh_data.v0, axis=0)
    
    # Calculate scaling factors for each dimension to fit within 255x255x255 grid
    x_scale = 255 / (max_coords[0] - min_coords[0])
    y_scale = 255 / (max_coords[1] - min_coords[1])
    z_scale = 255 / (max_coords[2] - min_coords[2])
    
    # Apply scaling to the vertices of the mesh
    scaled_vertices = (mesh_data.v0 - min_coords) * np.array([x_scale, y_scale, z_scale])
    
    # Calculate slice heights
    slice_height = 255 / num_slices
    
    # Initialize 2D grids for each slice
    grids = []
    for i in range(num_slices):
        z_min = i * slice_height
        z_max = (i + 1) * slice_height
        
        # Get vertices within the current slice
        vertices_in_slice = scaled_vertices[
            (scaled_vertices[:, 2] >= z_min) & (scaled_vertices[:, 2] < z_max)
        ]
        
        # Create a Delaunay triangulation for the vertices within the slice
        tri = Delaunay(vertices_in_slice[:, :2])
        
        # Create an empty 2D grid for the current slice
        grid = np.zeros((256, 256), dtype=int)
        
        # Connect points within a certain distance using Delaunay triangulation
        for simplex in tri.simplices:
            for i in range(3):
                pt1 = vertices_in_slice[simplex[i], :2]
                pt2 = vertices_in_slice[simplex[(i + 1) % 3], :2]
                
                # Calculate the Euclidean distance between points
                distance = np.linalg.norm(pt2 - pt1)
                
                # Draw a line between points if the distance is within the specified limit
                if distance <= max_distance:
                    x1, y1 = int(pt1[0]), int(pt1[1])
                    x2, y2 = int(pt2[0]), int(pt2[1])
                    
                    # Check bounds before setting the point in the grid
                    if 0 <= x1 < 256 and 0 <= y1 < 256 and 0 <= x2 < 256 and 0 <= y2 < 256:
                        # Bresenham's line drawing algorithm
                        dx = abs(x2 - x1)
                        dy = abs(y2 - y1)
                        sx = -1 if x1 > x2 else 1
                        sy = -1 if y1 > y2 else 1
                        err = dx - dy
                        
                        while x1 != x2 or y1 != y2:
                            # Set the point in the grid
                            grid[y1, x1] = 1
                            
                            e2 = 2 * err
                            if e2 > -dy:
                                err -= dy
                                x1 += sx
                            if e2 < dx:
                                err += dx
                                y1 += sy
                    
        grids.append(grid)
    
    # Convert the list of 2D grids to a 3D numpy array
    return np.array(grids)

# Example usage
file_path = 'models/young_maple.stl'  # Replace with the path to your STL file
num_slices = 25  # Number of slices
max_distance = 10.0  # Maximum distance between connected points
tree = process_stl(file_path, num_slices, max_distance)

# Clip the values to ensure the maximum value is 255
tree = np.clip(tree, 0, 255)




# Create a Vox object with colors assigned to voxels
print(tree.shape)  # Print the shape of the resulting 3D grid
if(np.max(tree) > 255):
    print("Color values can not be > 255 for VoxEdit import.")

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

# Save the Vox file
vox_filename = "treeSTL.vox"
voxels = Vox.from_dense(tree)
voxels.palette = palette
VoxWriter(vox_filename, voxels).write()

print(file_path + " rendering complete.")
