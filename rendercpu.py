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

import os, time
from concurrent.futures import ProcessPoolExecutor

def color_function(i, iter_limit):
    if i == iter_limit:
        return 0
    return min(255, int(255 * ((i * 4) / iter_limit)))

def render_pixel(x, y, a, b, iter_limit):
    # Uncomment the following line of code to render the Mandelbrot set instead of a Julia set:
    #a, b = x, y
    i = 0
    while i < iter_limit and (x * x + y * y) < 4:
        tx, ty = x, y
        x = (tx * tx) - (ty * ty) + a
        y = (2 * tx * ty) + b
        i += 1
    return color_function(i, iter_limit)

def render_chunk_CPU(img):    
    left_x, right_x = img[0], img[1]
    top_y = img[2]
    a, b = img[3], img[4]
    p_x, p_y = img[5], img[6]
    iter_limit = img[7]
    
    step_size = (right_x - left_x) / p_x
    img_data = []
    y = top_y
    
    for j in range(p_y):
        row_data = []                                            # New empty row of pixels
        x = left_x                                               # Start rendering at the leftmost edge
        for i in range(p_x):        
            pixel_data = render_pixel(x, y, a, b, iter_limit)    # Render this pixel
            row_data.append(pixel_data)                          # Add pixel to row
            x += step_size
        img_data.append(row_data)                                # Add row to chunk
        y -= step_size
    return img_data

def render_image_CPU(img):
    start_time = time.perf_counter()    # Start time metric
    
    process_count = os.cpu_count()    # Launch as many processes as there are CPUs present
    image_data = []
    current_y = img['top_y']
    step_size = (img['right_x'] - img['left_x']) / img['p_x']
    chunk_height, chunk_remainder = (img['p_y'] // process_count), (img['p_y'] % process_count)
    
    # Generate chunk parameters for passing to individual processes:
    chunks = []
    for i in range(process_count):
        # Since the number of processes available often won't divide evenly into the number of pixel rows,
        # the first (rows % processors) chunks will each have to pick up one extra row of pixels
        extra = 1 if i < chunk_remainder else 0
        chunk = [img['left_x'], img['right_x'], current_y, img['a'], img['b'], img['p_x'], chunk_height + extra, img['iter_limit']]
        current_y = current_y - (step_size * (chunk_height + extra))
        chunks.append(chunk)
    
    # Map out chunk parameter lists to separate processes for concurrent rendering:
    with ProcessPoolExecutor(process_count) as pool:
        chunk_data = pool.map(render_chunk_CPU, chunks)
    
    # Combine rendered chunk data into a whole image:
    for chunk in chunk_data:
        for line in chunk:
            image_data.append(line)
    
    total_time = (time.perf_counter() - start_time) * 1000    # Stop time metric, and convert to milliseconds
    return total_time, image_data
