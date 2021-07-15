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
    
def parse_csv(filenames, schema):
    csv_data = []
    for filename in filenames:
        try:
            with open(filename) as f:
                line_number = 1
                for line in f:
                    line_cells = line.strip().split(',')
                    line_data = {}
                    
                    if len(line_cells) < len(schema):
                        sys.exit("Error in " + filename + " at line " + str(line_number) + ": missing values")
    
                    for i in range(len(schema)):
                        keyname = schema[i][0]
                        keytype = schema[i][1]
                        
                        if line_cells[i] == '':
                            sys.exit("Error in " + filename + " at line " + str(line_number) + ": cell " + str(i + 1) + " is null")
                        
                        cell_data = False
                        if keytype == 'i':    # Int
                            try:
                                cell_data = int(line_cells[i])
                            except ValueError:
                                sys.exit("Error in " + filename + " at line " + str(line_number) + ": cell " + str(i + 1) + " is not an int")
                        elif keytype == 'ui':    # Unsigned int
                            try:
                                cell_data = int(line_cells[i])
                            except ValueError:
                                sys.exit("Error in " + filename + " at line " + str(line_number) + ": cell " + str(i + 1) + " is not an int")
                            if cell_data < 0:
                                sys.exit("Error in " + filename + " at line " + str(line_number) + ": cell " + str(i + 1) + " is less than zero")
                        elif keytype == 'f':    # Float
                            try:
                                cell_data = float(line_cells[i])
                            except ValueError:
                                sys.exit("Error in " + filename + " at line " + str(line_number) + ": cell " + str(i + 1) + " is not a float")
                        else:
                            cell_data = line_cells[i]
                            
                        line_data[keyname] = cell_data
    
                    csv_data.append(line_data)
                    line_number += 1
        except IOError:
            sys.exit("Error trying to read " + filename)    
    return csv_data
