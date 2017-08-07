# Copyright (C) 2017 Josh Edwards <Josh.Edwards222@gmail.com>
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this.  If not, see <http://www.gnu.org/licenses/>.

#import required packs
import scipy
import numpy
import PIL
import matplotlib.pyplot as plt
import scipy.fftpack
import math
import numpy.ma as ma
from unwrap import unwrap
import cv2

#Please note: numpy array indexing is done [y,x] hence there are some oddities in this code to overcome missmatches
#that this causes

def PhaseUnwrap(image, MIDDLE, DIAMETER, REGION=30):

    #convert image to array and float
    data = numpy.asarray(image)
    datafloat=numpy.zeros((data.shape),dtype=float)
    datafloat=data*1.0

    #create the mask to cut out unwanted image areas
    mask = numpy.ones(data.shape)
    mask=cv2.circle(mask,center=tuple(MIDDLE),radius=int(round(DIAMETER/2)),color=0, thickness=-1)
    mask=mask-1
    mask=abs(mask)

    #mask image to remove extraneous data from edges
    datafloat = datafloat*mask

    #perform fourier transform and plot
    fftarray = numpy.fft.fft2(datafloat, norm='ortho')
    fftarray = numpy.fft.fftshift(fftarray)

    #remove center section to allow finding of 1st order point
    centre=[int(fftarray.shape[1]/2),int(fftarray.shape[0]/ 2)]
    order0 = numpy.log((fftarray[centre[1]-REGION:centre[1]+REGION,centre[0]-REGION:centre[0]+REGION]))
    fftarray[centre[1]-REGION:centre[1]+REGION,centre[0]-REGION:centre[0]+REGION]=0.00001+0j

    #find first order point
    maxpoint = numpy.argmax(fftarray)
    maxpoint = [int(maxpoint%fftarray.shape[1]),int(maxpoint/fftarray.shape[1])]
    order1 = ((fftarray[maxpoint[1]-REGION:maxpoint[1]+REGION,maxpoint[0]-REGION:maxpoint[0]+REGION]))

    #pad the fftarray back to original size
    order1pad=numpy.zeros((data.shape),dtype=complex)
    index = numpy.zeros(4,dtype=int)
    index[0] = int((order1pad.shape[1]/2)-(order1.shape[1]/2))
    index[1] = int((order1pad.shape[1]/2)+(order1.shape[1]/2))
    index[2] = int((order1pad.shape[0]/2)-(order1.shape[0]/2))
    index[3] = int((order1pad.shape[0]/2)+(order1.shape[0]/2))
    order1pad[index[0]:index[1],index[2]:index[3]] = order1

    #shift the quadrants back to format for ifft use
    order1pad = numpy.fft.ifftshift(order1pad)

    #inverse fourier transform
    ifftorder1 = numpy.fft.ifft2(order1pad, norm='ortho')

    #mask ifftarray to remove extraneous data from edges
    ifftorder1=ifftorder1*mask

    #find phase data by taking 2d arctan of imaginary and real parts
    phaseorder1 = numpy.zeros(ifftorder1.shape)
    phaseorder1 = numpy.arctan2(ifftorder1.imag,ifftorder1.real)

    #mask out edge region to allow unwrap to only use correct region
    phasesave = phaseorder1
    phaseorder1mask = ma.masked_where(mask == 0,phaseorder1)

    #perform unwrap
    phaseunwrap = unwrap(phaseorder1mask)

    #crop to fill array to improve performance of zernike decomposition
    out = numpy.zeros((DIAMETER,DIAMETER), dtype=float)
    out = phaseunwrap[MIDDLE[1]-int(round(DIAMETER/2)):MIDDLE[1]+int(round(DIAMETER/2)),MIDDLE[0]-int(round(DIAMETER/2)):MIDDLE[0]+int(round(DIAMETER/2))]
    return out

# setting parameters and defining functions for padding and masking
MIDDLE = [900,975]
DIAMETER = 1200

#collect image from file
im = PIL.Image.open('DeepSIM_interference_test.png')
out = PhaseUnwrap(im, MIDDLE, DIAMETER)
plt.imshow(out)
plt.show()