#
#    This file is part of the FractPY project.
#    (C) 2021 Winston Deleon
#    Author(s): Winston Deleon, wdeleon0@gmail.com
#
#    This program is free software: you can redistribute it and/or  modify
#    it under the terms of the GNU Affero General Public License, version 3,
#    as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import time
import numpy
import pycuda.driver as cuda
from pycuda.compiler import SourceModule

# Function to perform ceiling division, instead of floor division:
def ceiling_divide(a, b):
    return -(-a // b)
 
def CUDA_init(CUDA_dev_id):
    cuda.init()
    CUDA_context = cuda.Device(CUDA_dev_id).make_context()
    return CUDA_context
    
def CUDA_create_kernel():
    kernel_code = """
    __device__ unsigned char color_function (unsigned int i,
                                             unsigned int iter_limit)
    {
        if (i == iter_limit) {
            return 0;
        }
        unsigned int color_value = (255 * (i * 4)) / iter_limit;
        if (color_value <= 255) {
            return color_value;
        }
        return 255;
    }
    
    __global__ void render (unsigned char *image_data_gpu,
                            float left_x,
                            float right_x,
                            float top_y,
                            float a,
                            float b,
                            unsigned int iter_limit)
    {
        unsigned int p_x = blockDim.x * blockIdx.x + threadIdx.x;
        unsigned int p_y = blockDim.y * blockIdx.y + threadIdx.y;
        unsigned int p_index = (gridDim.x * blockDim.x * p_y) + p_x;

        float step_size = (right_x - left_x) / (gridDim.x * blockDim.x);
        float x = left_x + (step_size * p_x);
        float y = top_y - (step_size * p_y);
        float tx = x;
        float ty = y;
        unsigned int i = 0;
        
        // Uncomment the following two lines of code to render the Mandelbrot set instead of a Julia set:
        //a = x;
        //b = y;

        // Iterate until iteration limit or escape radius is reached:
        while ((i < iter_limit) && ((x * x + y * y) < 4)) {
            tx = x;
            ty = y;
            x = (tx * tx) - (ty * ty) + a;
            y = (2 * tx * ty) + b;
            i++;
        }
        image_data_gpu[p_index] = color_function(i, iter_limit);
    }
    """
    kernel_module = SourceModule(kernel_code, cache_dir='.')    # Cache compiled CUDA binary to local directory
    return kernel_module.get_function("render")

def render_image_CUDA(img, render_kernel, CUDA_dev_id):
    start_time = time.perf_counter()    # Start time metric

    # Arguments passed by value to a CUDA kernel must be a numpy dtype
    left_x, right_x = numpy.float32(img['left_x']), numpy.float32(img['right_x'])
    top_y = numpy.float32(img['top_y'])
    a, b = numpy.float32(img['a']), numpy.float32(img['b'])
    iter_limit = numpy.uintc(img['iter_limit'])
    p_x, p_y = img['p_x'], img['p_y']
    
    # Configure block and grid sizes by interrogating available CUDA hardware capabilities on specified device
    threads_per_block = cuda.Device(CUDA_dev_id).get_attribute(cuda.device_attribute.MAX_THREADS_PER_BLOCK)
    threads_per_warp = cuda.Device(CUDA_dev_id).get_attribute(cuda.device_attribute.WARP_SIZE)
    
    block_x = threads_per_warp
    block_y = threads_per_block // threads_per_warp
    
    grid_x = ceiling_divide(p_x, block_x)
    grid_y = ceiling_divide(p_y, block_y)
    
    r_x, r_y = (block_x * grid_x), (block_y * grid_y)
    
    # Account for any underlap between original image and a pixel boundary divisible by <block_x>:
    if not (p_x % block_x) == 0:
        step_size = (right_x - left_x) / p_x
        right_x += (r_x - p_x) * step_size
        right_x = numpy.float32(right_x)
    
    # Create a 2-dimensional array of pixels initialized to all zeros:
    image_data = numpy.zeros((r_y, r_x), dtype=numpy.uint8)
    
    # Allocate CUDA device memory to hold the pixel array:
    image_data_gpu = cuda.mem_alloc(image_data.size * image_data.dtype.itemsize)
    
    # Run the rendering kernel on the CUDA device:
    render_kernel(image_data_gpu, left_x, right_x, top_y, a, b, iter_limit, block=(block_x, block_y, 1), grid=(grid_x, grid_y), shared=0)
    
    # Copy the rendering results from CUDA memory back to host memory, then free CUDA device memory:
    cuda.memcpy_dtoh(image_data, image_data_gpu)
    image_data_gpu.free()
    
    # Clip off any overlap:
    if not (p_x % block_x) == 0:
        x_mask = numpy.ones(r_x, dtype=bool)
        x_mask[p_x:r_x] = 0
        image_data = image_data[...,x_mask]   
    if not (p_y % block_y) == 0:
        y_mask = numpy.ones(r_y, dtype=bool)
        y_mask[p_y:r_y] = 0
        image_data = image_data[y_mask]
        
    # Turn the numpy array into a list:
    image_data = image_data.tolist()    
    
    total_time = (time.perf_counter() - start_time) * 1000    # Stop time metric, and convert to milliseconds
    return total_time, image_data

def CUDA_shutdown(CUDA_context):
    CUDA_context.pop()
