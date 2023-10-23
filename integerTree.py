from stl import mesh
import numpy as np
import math
from pyvox.models import Vox, Color
from pyvox.writer import VoxWriter
from scipy.spatial import Delaunay

debug = False
seed_value = 42


vox_filename = "treeFromScratch.vox"

def createVoxEditGradientPalette(initialColor, gradientIncrement, num_shades=255):
    """
    createVoxEditGradientPalette - Creates a palette to attach to a voxel model with 255
        members which is the required size for VoxEdit. It fills the gradient starting at
        the initial color by incrementing the RGB values. It continues making colors until
        the gradient turns to white. Then it pads the palette with white.

        Parameters: intialColor - PyVox Color model for the starting color.
                    gradientIncrement - PyVox Color Model of RGB values to change the color by.
                    num_shade - The number of shades to produce before padding the palette.
                                The default value is 255 if not specified

        Returns: a palette object that can be used to set the palette on a Vox model with
                 voxModelName.palette = the returned value
    """
    # Create a color palette with gradients of natural browns.
    palette = [
        Color(
            min(initialColor.r + i * gradientIncrement.r, 255),  # Increment red component
            min(initialColor.g + i * gradientIncrement.g, 255),  # Increment green component
            min(initialColor.b + i * gradientIncrement.b, 255),  # Increment blue component
            min(initialColor.a + i * gradientIncrement.a, 255)   # Increment Alpha channel
        ) for i in range(num_shades)
    ]

    # Create a single list comprehension for the palette
    palette = [palette[min(value, num_shades - 1)] for value in range(256)]

    return palette

def setCornersToMaintainArraySize(array):
    """
    This function sets the corners of the given array to 1. This prevents Vox edit from changing the size of the array if it is partially empty
    """
    depth, height, width = array.shape
    corners = [(x, y, z) for x in range(depth) for y in range(height) for z in range(width) if x in [0, depth - 1] and y in [0, height - 1] and z in [0, width - 1]]
    for x, y, z in corners:
        array[x, y, z] = 1
    return array

def draw_line_3d(array, x1, y1, z1, x2, y2, z2, value=1):
    """
    This function uses the bresenham algorithm to create a line in a 3d array

    """
    array[x1, y1, z1]= value
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    dz = abs(z2 - z1)
    if (x2 > x1):
            xs = 1
    else:
            xs = -1
    if (y2 > y1):
            ys = 1
    else:
            ys = -1
    if (z2 > z1):
            zs = 1
    else:
            zs = -1

    # Driving axis is X-axis"
    if (dx >= dy and dx >= dz):	 
            p1 = 2 * dy - dx
            p2 = 2 * dz - dx
            while (x1 != x2):
                    x1 += xs
                    if (p1 >= 0):
                            y1 += ys
                            p1 -= 2 * dx
                    if (p2 >= 0):
                            z1 += zs
                            p2 -= 2 * dx
                    p1 += 2 * dy
                    p2 += 2 * dz
                    array[x1, y1, z1]= value

    # Driving axis is Y-axis"
    elif (dy >= dx and dy >= dz):	 
            p1 = 2 * dx - dy
            p2 = 2 * dz - dy
            while (y1 != y2):
                    y1 += ys
                    if (p1 >= 0):
                            x1 += xs
                            p1 -= 2 * dy
                    if (p2 >= 0):
                            z1 += zs
                            p2 -= 2 * dy
                    p1 += 2 * dx
                    p2 += 2 * dz
                    array[x1, y1, z1]= value

    # Driving axis is Z-axis"
    else:	 
            p1 = 2 * dy - dz
            p2 = 2 * dx - dz
            while (z1 != z2):
                    z1 += zs
                    if (p1 >= 0):
                            y1 += ys
                            p1 -= 2 * dz
                    if (p2 >= 0):
                            x1 += xs
                            p2 -= 2 * dz
                    p1 += 2 * dy
                    p2 += 2 * dx
                    array[x1, y1, z1]= value
    return array

def create_3d_filled_ellipse(radius, irregularity_scaler, center, altitude, azimuth, color_value):
    # Test Values: (10, 2, (10,10,10), 3, 0, 2)

    np.random.seed(seed_value) if debug else None
    
    # Generate theta values for the ellipse
    theta = np.linspace(0, 2*np.pi, 1000)
    
    # Calculate ellipse points in 2D space with irregularity
    ellipse_points = np.array([radius * np.cos(theta) + np.random.uniform(-irregularity_scaler, irregularity_scaler, len(theta)),
                               radius * np.sin(theta) + np.random.uniform(-irregularity_scaler, irregularity_scaler, len(theta)),
                               np.zeros(len(theta))])

##    y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
##    mask = x**2 + y**2 <= radius**2
##    array[center_y-radius:center_y+radius+1, center_x-radius:center_x+radius+1][mask] = fill_value
    
    # Rotate ellipse based on altitude and azimuth angles
    rotation_matrix_altitude = np.array([[np.cos(altitude), 0, -np.sin(altitude)],
                                        [0, 1, 0],
                                        [np.sin(altitude), 0, np.cos(altitude)]])
    
    #this rotation isn't used since it only rotates around the central axis
    rotation_matrix_azimuth = np.array([[np.cos(azimuth), -np.sin(azimuth), 0],
                                        [np.sin(azimuth), np.cos(azimuth), 0],
                                        [0, 0, 1]])
    
    rotation_matrix_x_axis = np.array([[1, 0, 0],
                                       [0, np.cos(azimuth), -np.sin(azimuth)],
                                       [0, np.sin(azimuth), np.cos(azimuth)]])
    
    rotated_ellipse = np.dot(rotation_matrix_altitude, np.dot(rotation_matrix_x_axis, ellipse_points))
    
    # Translate ellipse to the specified center point
    translated_ellipse = rotated_ellipse + np.array(center)[:, np.newaxis]
    print(np.shape(translated_ellipse)) if debug else None
    # Convert ellipse points to integer coordinates
    integer_coordinates = np.round(translated_ellipse).astype(int)
    
    # Create a 3D array to represent the filled ellipse
    max_coords = np.max(integer_coordinates, axis=1)
    min_coords = np.min(integer_coordinates, axis=1)
    shape = tuple(max_coords - min_coords + 1)
    print("shape", shape) if debug else None
    filled_ellipse = np.zeros(shape, dtype=int)
    
    # Fill the ellipse in the 3D array with the specified color value
    print("len(integer_coordinates[0])", len(integer_coordinates[0])) if debug else None
    for i in range(len(integer_coordinates[0])):
        x, y, z = integer_coordinates[:, i] - min_coords
        filled_ellipse[x, y, z] = color_value
        ##### FIX ME DURING REFACTORING - this needs to be fixed since the middle of the ellipse is hallow
        #filled_ellipse += draw_line_3d(filled_ellipse, center[0], center[1], center[2], x, y, z, value=color_value)
        
    return np.swapaxes(filled_ellipse, 1, 2)

def create_tree(array_shape, trunk_length, trunk_angle, branch_angle, depth, branches):
    np.random.seed(seed_value) if debug else None
    # Create an empty 3D array for the tree structure
    tree_array = np.zeros(array_shape, dtype=int)
    
    # Function to recursively draw branches
    def draw_branch(x, y, z, length, angle, branches, depth, color):
        nonlocal tree_array
        if length <= 0 or depth <= 0:
            return
        
        # Calculate direction vector from parent to child node
        dx = int(length * math.sin(angle))
        dz = int(length * math.cos(angle))
        dy = 3  # Fixed vertical growth
        
        # Calculate new branch endpoint
        x2 = x + dx
        y2 = y + dy
        z2 = z + dz
        
        # Draw the branch
        tree_array = draw_line_3d(tree_array, x, y, z, x2, y2, z2, value=color)
        
        # Recursively draw branches
        for _ in range(branches):
            # Calculate a new angle based on the direction vector and add some randomness
            new_angle = math.atan2(dx, dz) + np.random.uniform(-branch_angle, branch_angle)
            # Recursive call with reduced length and depth
            draw_branch(x2, y2, z2, length * 0.8, new_angle, branches, depth - 1, color)
    
    # Start drawing the tree from the bottom center
    start_x = array_shape[0] // 2
    start_y = 0
    start_z = array_shape[2] // 2
    
    # Initial trunk length and angle
    trunk_length = trunk_length #np.random.randint(5, 10)
    trunk_angle = math.radians(trunk_angle)
    delta_x = int(trunk_length * math.tan(trunk_angle))
    tree_array = draw_line_3d(tree_array, start_x, start_y, start_z, start_x + delta_x, trunk_length, start_z, 40)
    
    # Number of branches at each node
    branches = np.random.randint(1, num_branches + 1)
    branch_angle = math.radians(branch_angle)
    
    # Draw the trunk
    print(start_x + delta_x, trunk_length, start_z, trunk_length, branch_angle, branches, 40)
    #draw_branch(start_x + delta_x, trunk_length, start_z, trunk_length, branch_angle, branches, 40)
    draw_branch(start_x + delta_x, trunk_length, start_z, trunk_length, trunk_angle, branches, depth, 40)
    
    return tree_array

def calculate_3d_angle(x1, y1, z1, x2, y2, z2):
    dot_product = x1*x2 + y1*y2 + z1*z2
    magnitude1 = math.sqrt(x1**2 + y1**2 + z1**2)
    magnitude2 = math.sqrt(x2**2 + y2**2 + z2**2)
    
    # Ensure denominators are not zero to avoid division by zero error
    if magnitude1 != 0 and magnitude2 != 0:
        cos_theta = dot_product / (magnitude1 * magnitude2)
        angle_radians = math.acos(cos_theta)
        return angle_radians
    else:
        # Handle the case where one or both vectors have zero magnitude
        return 0.0



def test (array, value=1):
    start_x = array_shape[0] // 2
    start_y = array_shape[1] // 2
    start_z = array_shape[2] // 2
    end_x = start_x
    end_y = 10
    end_z = start_z
    return draw_line_3d(array, start_x, start_y, start_z, end_x, end_y, end_z, value=1)

if __name__ == "__main__":
    # Code that you want to run when the script is executed directly goes here
    debug = True
    array_shape = (100, 100, 100)  # Numpy array shape
    branch_angle = 90  # Branch angle in degrees
    num_branches = 3  # Number of branches at each node
    trunk_length = 20
    trunk_angle = 15
    recursion_depth = 3
    # Test the function with initial length of 20, initial spacing of 5, and reduction factor of 2
    tree = create_tree(array_shape, trunk_length, trunk_angle, branch_angle, recursion_depth, num_branches)
    #tree = test(np.zeros(array_shape, dtype=int),value=1)
    #tree = draw_line_3d(np.zeros(array_shape, dtype=int), 0, 0, 0, 9, 9, 9, value=1)
    #tree = create_3d_filled_ellipse(10, 2, (21,21,21), 0.785, 0.785, 2)
    print("tree.shape", tree.shape)  if debug else None # Print the shape of the resulting 3D grid

    tree = setCornersToMaintainArraySize(tree)
    if(np.max(tree) > 255):
        print("Color values can not be > 255 for VoxEdit import.\nColors will be clipped") if debug else None
        # Clip the values to ensure the maximum value is 255
        tree = np.clip(tree, 0, 255)


    # Save the Vox file
    voxels = Vox.from_dense(tree)
    voxels.palette = createVoxEditGradientPalette(Color(22,11,3,255), Color(1,1,1,0))
    #print(tree)
    VoxWriter(vox_filename, voxels).write()

    print(vox_filename + " rendering complete.")

