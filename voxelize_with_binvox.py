import numpy as np
from stl import mesh
from pyvox.models import Vox
from pyvox.writer import VoxWriter
import subprocess
import os

class Voxels(object):
    #Holds a binvox model.
    def __init__(self, data, dims, translate, scale, axis_order):
        self.data = data
        self.dims = dims
        self.translate = translate
        self.scale = scale
        assert (axis_order in ('xzy', 'xyz'))
        self.axis_order = axis_order

    def clone(self):
        data = self.data.copy()
        dims = self.dims[:]
        translate = self.translate[:]
        return Voxels(data, dims, translate, self.scale, self.axis_order)

    def write(self, fp):
        write(self, fp)

def read_header(fp):
    """ Read binvox header. Mostly meant for internal use.
    """
    line = fp.readline().strip()
    if not line.startswith(b'#binvox'):
        raise IOError('Not a binvox file')
    dims = list(map(int, fp.readline().strip().split(b' ')[1:]))
    translate = list(map(float, fp.readline().strip().split(b' ')[1:]))
    scale = list(map(float, fp.readline().strip().split(b' ')[1:]))[0]
    line = fp.readline()
    return dims, translate, scale

def read_as_3d_array(fp, fix_coords=True):
    """ Read binary binvox format as array.

    Returns the model with accompanying metadata.

    Voxels are stored in a three-dimensional numpy array, which is simple and
    direct, but may use a lot of memory for large models. (Storage requirements
    are 8*(d^3) bytes, where d is the dimensions of the binvox model. Numpy
    boolean arrays use a byte per element).

    Doesn't do any checks on input except for the '#binvox' line.
    """
    dims, translate, scale = read_header(fp)
    raw_data = np.frombuffer(fp.read(), dtype=np.uint8)

    values, counts = raw_data[::2], raw_data[1::2]
    data = np.repeat(values, counts).astype(np.bool_)
    data = data.reshape(dims)
    if fix_coords:
        # xzy to xyz TODO the right thing
        data = np.transpose(data, (0, 2, 1))
        axis_order = 'xyz'
    else:
        axis_order = 'xzy'
    return Voxels(data, dims, translate, scale, axis_order)

def read_binvox(binvox_filename):
    with open(binvox_filename, 'rb') as binvox_file:
        voxel_model = read_as_3d_array(binvox_file, fix_coords=False)
    return voxel_model.data

def voxelize_stl(stl_filename, binvox_filename, voxel_resolution):
    # Voxelize STL file using binvox
    binvox_cmd = ['c:\\voxedit\python\models\pangolin\\binvox.exe', '-d', str(voxel_resolution), '-c', '-e', stl_filename]
    #subprocess.Popen(["start", "cmd", "/k", binvox_cmd], shell=True)
    print(binvox_cmd)
    result = subprocess.run(binvox_cmd, check=True, capture_output=True, text=True)
    print(result.stdout)
    # Convert binvox file to numpy array
    voxel_model = read_binvox(binvox_filename)
    
    return np.array(voxel_model.data)

def get_stl_files(directory):
    stl_files = []
    for file in os.listdir(directory):
        if file.lower().endswith('.stl') and os.path.isfile(os.path.join(directory, file)):
            stl_files.append(os.path.join(directory, file))
    return stl_files

if __name__ == "__main__":
    model_path = r'./models/'
    output_path = r'./output/'
    voxel_resolution = 255
    
    stl_files = get_stl_files(model_path)
    for stl in stl_files:
        filename = stl.split(r'/')[-1].split('.')[0]
        print("Processing: " + filename)
        binvox_filename = model_path + filename + '.binvox'
        stl_filename = model_path + filename + '.stl'
        vox_filename = output_path + filename + '.vox'
        voxels = voxelize_stl(stl_filename, binvox_filename, voxel_resolution)
        # Convert numpy array to PyVox Vox object
        vox = Vox.from_dense(voxels)

        # Save voxel data to a VOX file
        VoxWriter(vox_filename, vox).write()

        # Delete the .binvox file
        os.remove(binvox_filename)

    print("Conversion complete. Voxel data saved to output.vox.")
