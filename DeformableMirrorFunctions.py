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
import scipy.stats as stats
from skimage import io
import matplotlib.pyplot as plt
from ZernikeDecomposition import PhaseUnwrap

def CreateControlMatrix(image_stack_file_name, numActuators=69, pokeSteps = np.linspace(-1,1,5)):
    try:
        parameters = np.loadtxt("circleParameters.txt", int)
    except IOError:
        print("Error: Masking parameters do not exist. Create by running select_circle.py")
        return

    centre = [0,0]
    centre[0] = parameters[0]
    centre[1] = parameters[1]
    diameter = parameters[2]

    #The number of Zernike modes decomposed should always be the same as the number of actuators available
    noZernikeModes = numActuators
    slopes = np.zeros(noZernikeModes)
    intercepts = np.zeros(noZernikeModes)
    r_values = np.zeros(noZernikeModes)
    p_values = np.zeros(noZernikeModes)
    std_errs = np.zeros(noZernikeModes)

    # Read in the image stack. Must be tiff
    imageStack = io.imread('%s' %image_stack_file_name)
    zernikeModeAmp = np.zeros((len(pokeSteps),noZernikeModes))
    controlMatrix = np.zeros((noZernikeModes,noZernikeModes))

    # Here the each image in the image stack (read in as np.array), centre and diameter should be passed to the unwrap
    # function to obtain the Zernike modes for each one. For the moment a set of random Zernike modes are generated.
    for ii in range(numActuators):

        #Get the amplitudes of each Zernike mode for the poke range of one actuator
        for jj in range(len(pokeSteps)):
            #[zernikeModeAmp[jj,:], unwrappedPhase] = PhaseUnwrap(imageStack[ii+jj,:,:], noZernikeModes=numActuators-1,
            #                                                   MIDDLE=centre, DIAMETER=diameter)
            zernikeModeAmp[jj, :] = np.random.rand(1, numActuators)

        #Fit a linear regression to get the relationship between actuator position and Zernike mode amplitude
        for kk in range(numActuators):
            slopes[kk], intercepts[kk], r_values[kk], p_values[kk], std_errs[kk] = stats.linregress(pokeSteps,zernikeModeAmp[:,kk])

        #Input obtained slopes as the entries in the control matrix
        controlMatrix[ii,:] = slopes[:]
    np.savetxt('controlMatrix.txt', controlMatrix)

def FlattenMirror(interference_image, numActuators = 69):
    try:
        controlMatrix = np.loadtxt("controlMatrix.txt")
        print np.shape(controlMatrix)
    except IOError:
        print("Error: Control Matrix do not exist.")
        return

#CreateControlMatrix('DeepSIM_interference_test.png')
FlattenMirror(1)
