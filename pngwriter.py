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

import png
import math

# Find the leading-zero-padded string representing the i-th item out of a set of n items:
def find_padded_name(i, n):
    leading_zeros = int(math.floor(math.log10(n)) - math.floor(math.log10(i)))
    padded_name = str(i)
    for _ in range(leading_zeros):
        padded_name = '0' + padded_name
    return padded_name

def write_png(img_data, img_name):
    try:                                            # Test opening image output file in binary mode
        f = open(img_name + '.png', 'wb')
    except IOError:
        return False
    x, y = len(img_data[0]), len(img_data)          # Find x and y image dimensions
    w = png.Writer(x, y, greyscale=True)            # Create PNG writer
    w.write(f, img_data)                            # Write pixels to file
    f.close()                                       # Close PNG file
    return True
