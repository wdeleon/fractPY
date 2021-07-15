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

import sys
import listfileparser as lfp
    
if __name__ == '__main__':
    csv_files = []
    render_CPU_multi, render_GPU = False, False
    enable_image_output = False
    for arg in sys.argv[1:]:
        if arg == '-i':
            enable_image_output = True
            import pngwriter
        elif arg == '-m':
            render_CPU_multi = True
            import rendercpu as rcpu
        elif arg == '-g':
            render_GPU = True
            import rendercuda as rcuda
            CUDA_dev_id = 0    # Change this device ID to use different CUDA devices
            CUDA_context = rcuda.CUDA_init(CUDA_dev_id)
            kernel = rcuda.CUDA_create_kernel()
        else:
            csv_files.append(arg)
    
    # Display help and exit if no csv sources are specified:
    if len(csv_files) <= 0 or ((not render_CPU_multi) and (not render_GPU)):
        print("\nUsage: fract.py [-i] [-g] [-m] <CSV filename 1> <CSV filename 2> ... <CSV filename n>")
        print("  Arguments:")
        print("    -i:              Enable outputting image files.")
        print("                     Image files will be written to the current directory.")
        print("                     WARNING: this can use a large amount of disk space.")
        print("                     WARNING: previously generated images will be overwritten without prompting.\n")
        print("    -g:              Use CUDA GPU rendering.\n")
        print("    -m:              Use multi-core CPU rendering.\n")
        print("    <CSV filename>:  Name of a CSV file to generate images from. At least one file is required.")
        print("                     There is no limit to how many files may be specified.\n")
        print("    At least one of either -g or -m is required. Both may be used at the same time.")
        sys.exit()
    
    # Load and parse all supplied csv file names into a single list of images to generate:
    schema = [('left_x', 'f'),
              ('right_x', 'f'),
              ('top_y', 'f'),
              ('p_x', 'i'),
              ('p_y', 'i'),
              ('a', 'f'),
              ('b', 'f'),
              ('iter_limit', 'ui')]
    image_list = lfp.parse_csv(csv_files, schema)
    
    # Test opening an output file before starting the image rendering run:
    try:
        if render_CPU_multi:
            CPU_multi_out_file = open('cpu_times.txt', 'w')
        if render_GPU:
            GPU_out_file = open('gpu_times.txt', 'w')
    except IOError:
        sys.exit("Error trying to open output file")
    
    # Run all images through the chosen renderer(s):
    for i in range(len(image_list)):
        if render_CPU_multi:
            print("Rendering image " + str(i + 1) + " with CPU...")
            image_time, image_data = rcpu.render_image_CPU(image_list[i])
            CPU_multi_out_file.write(str(image_time) + '\n')
            if enable_image_output:
                img_name = pngwriter.find_padded_name(i+ 1, len(image_list)) + '_multi'
                if not pngwriter.write_png(image_data, img_name):
                    sys.exit("Error trying to write image file")
        if render_GPU:
            print("Rendering image " + str(i + 1) + " with CUDA...")
            image_time, image_data = rcuda.render_image_CUDA(image_list[i], kernel, CUDA_dev_id)
            GPU_out_file.write(str(image_time) + '\n')
            if enable_image_output:
                img_name = pngwriter.find_padded_name(i+ 1, len(image_list)) + '_gpu'
                if not pngwriter.write_png(image_data, img_name):
                    sys.exit("Error trying to write image file")
    
    # Close output files and clean up:
    if render_CPU_multi:
        CPU_multi_out_file.close()
    if render_GPU:
        GPU_out_file.close()
        rcuda.CUDA_shutdown(CUDA_context)
