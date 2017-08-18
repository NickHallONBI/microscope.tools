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
import time
import scipy.stats as stats
from skimage import io
import matplotlib.pyplot as plt
from ZernikeDecomposition import PhaseUnwrap
from microscope import clients

def getImage(pokeSteps):
    camera = clients.DataClient('PYRO:XimeaCamera@192.168.1.20:8008')
    AO = clients.DataClient('PYRO:AlpaoDeformableMirror@192.168.1.20:8007')

    camera.enable()
    camera.set_exposure_time(0.01)

    data = []

    numActuators = AO.get_n_actuators()
    pokeRange = np.linspace(-1.0,1.0,pokeSteps)
    values = np.full(((numActuators*pokeSteps),numActuators),0.0)

    for poke in range(pokeSteps):
        for actuator in range(numActuators):
            index = (pokeSteps * actuator) + poke
            values[index, actuator] = pokeRange[poke]

    index = 1
    for value in values:
        AO.send(value)
#        time.sleep(0.5)
        image = camera.trigger_and_wait()[0]
        data.append(image)
        print("Frame %d of %d captured." %(index,len(values)))
        index += 1
    data = np.asarray(data)

    print(np.shape(data))
    data = data.flatten()
    print(np.shape(data))
    data.tofile("pokeStack.txt")

    AO.reset()
    camera.disable()


def CreateControlMatrix():
    AO = clients.DataClient('PYRO:AlpaoDeformableMirror@192.168.1.20:8007')

    # Read in the parameters needed for the phase mask
    try:
        parameters = np.loadtxt("circleParameters.txt", int)
    except IOError:
        print("Error: Masking parameters do not exist. Create by running select_circle.py")
        return

    centre = [0, 0]
    centre[0] = parameters[0]
    centre[1] = parameters[1]
    diameter = parameters[2]

    numActuators = AO.get_n_actuators()

    # The number of Zernike modes decomposed should always be the same as the number of actuators available
    noZernikeModes = numActuators
    slopes = np.zeros(noZernikeModes)
    intercepts = np.zeros(noZernikeModes)
    r_values = np.zeros(noZernikeModes)
    p_values = np.zeros(noZernikeModes)
    std_errs = np.zeros(noZernikeModes)

    # Read in the image stack.
    imageStack = np.fromfile("pokeStack.txt", dtype='uint8')
    imageStack = np.reshape(imageStack, (-1, 2048, 2048))
    print("Image stack read in.")

    noSteps = np.shape(imageStack)[0] / numActuators
    pokeSteps = np.linspace(-1, 1, noSteps)
    zernikeModeAmp = np.zeros((noSteps, noZernikeModes))
    controlMatrix = np.zeros((noZernikeModes, noZernikeModes))

    # Here the each image in the image stack (read in as np.array), centre and diameter should be passed to the unwrap
    # function to obtain the Zernike modes for each one.
    for ii in range(numActuators):
        # Get the amplitudes of each Zernike mode for the poke range of one actuator
        for jj in range(len(pokeSteps)):
            print("Decomposing Zernike modes")
            [zernikeModeAmp[jj, :], unwrappedPhase] = PhaseUnwrap(imageStack[ii + jj, :, :],
                                                                  noZernikeModes=numActuators - 1,
                                                                  MIDDLE=centre, DIAMETER=diameter)

        # Fit a linear regression to get the relationship between actuator position and Zernike mode amplitude
        for kk in range(numActuators):
            slopes[kk], intercepts[kk], r_values[kk], p_values[kk], std_errs[kk] = stats.linregress(pokeSteps,
                                                                                                    zernikeModeAmp[:,
                                                                                                    kk])

        # Input obtained slopes as the entries in the control matrix
        controlMatrix[ii, :] = slopes[:]
        print("Control values for actuator %d calculated" % ii)
    controlMatrix = np.transpose(controlMatrix)
    np.savetxt('controlMatrix.txt', controlMatrix)

def FlattenMirror():
    camera = clients.DataClient('PYRO:XimeaCamera@192.168.1.20:8008')
    AO = clients.DataClient('PYRO:AlpaoDeformableMirror@192.168.1.20:8007')

    camera.enable()
    camera.set_exposure_time(0.01)

    data = []

    try:
        controlMatrix = np.loadtxt("controlMatrix.txt")
    except IOError:
        print("Error: Control Matrix do not exist.")
        return
    numActuators = AO.get_n_actuators()

    numZernikeModes = np.shape(controlMatrix)[0] - 1
    zernikeAmp = np.zeros(np.shape(controlMatrix)[0])
    actuatorValues = np.zeros(np.shape(controlMatrix)[0])

    # Read in the parameters needed for the phase mask
    try:
        parameters = np.loadtxt("circleParameters.txt", int)
    except IOError:
        print("Error: Masking parameters do not exist. Create by running select_circle.py")
        return
    centre = [0, 0]
    centre[0] = parameters[0]
    centre[1] = parameters[1]
    diameter = parameters[2]
    # Iterative loop
    for ii in range(10):
        #Here an image needs to be taken and read in in order to be decomposed into Zernike modes.
        time.sleep(0.5)
        image = np.asarray(camera.trigger_and_wait()[0])

        #Decompose image into zernike modes
        [zernikeAmp, unwrappedPhase] = PhaseUnwrap(image[:, :], noZernikeModes=numZernikeModes,
                                                    MIDDLE=centre, DIAMETER=diameter)

        #Solve for actuator values
        actuatorValues = actuatorValues - np.linalg.solve(controlMatrix, zernikeAmp)

        #Send the actuator values to the DM
        AO.send(actuatorValues)
    np.savetxt('dmFlatValues.txt', actuatorValues)



#CreateControlMatrix('DeepSIM_interference_test.png')
FlattenMirror()
