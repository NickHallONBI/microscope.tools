#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (C) 2017 Nicholas Hall <nicholas.hall@dtc.ox.ac.uk>
##
## This is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import scipy.stats
from skimage import io
import joshs_function

def CreateControlMatrix(image_stack_file_name, centre, diameter, numActuators=69, pokeSteps = np.linspace(-1,1,5)):
    # Read in the image stack. Must be tiff
    imageStack = io.imread('%s.tif' %image_stack_file_name)
    zernikeModeAmp = np.zeros(np.shape(range(pokeSteps),numActuators))

    # Here the each image in the image stack (read in as np.array), centre and diameter should be passed to Josh's
    # function to obtain the Zernike modes for each one. For the moment a set of random Zernike modes are generated.
    for ii in range(numActuators):
        for jj in range(pokeSteps):
            zernikeModeAmp[jj,:] = joshs_function(imageStack[ii+jj,:,:], centre, diameter)
