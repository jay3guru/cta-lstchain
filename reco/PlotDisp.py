#!/usr/bin/env python3
'''
Script for plotting cleaned LST1 images with source position in camera coordinates
'''

import sys
from astropy.io import fits
import matplotlib.pylab as plt
import numpy as np
import math as m
from ctapipe.instrument import CameraGeometry,OpticsDescription
from ctapipe.visualization import CameraDisplay
import astropy.units as u
import ctapipe.coordinates as c
from scipy.optimize import minimize, newton
import Disp

hdu_list = fits.open("/home/queenmab/GitHub/cta-lstchain/reco/results/gamma_events.fits") #File with events
hdu_list[1].data

tel = OpticsDescription.from_name('LST') #Telescope description
focal_length = tel.equivalent_focal_length.value #Telescope focal length
geom = CameraGeometry.from_name("LSTCam") #Camera geometry

nevents = hdu_list[1].data.field(0).size #Total number of events
disp = np.array([]) #Disp quantity

width = np.array([])
length = np.array([])
intensity = np.array([])
energy = np.array([])
psi = np.array([])
ntrain=0;
for i in range(0,nevents):

    ntrain=ntrain+1
    this_size = hdu_list[1].data.field('intensity')[i]
    if this_size < 0:
        continue
    width = np.append(width, hdu_list[1].data.field('width')[i])
    length = np.append(length, hdu_list[1].data.field('length')[i])
    intensity = np.append(intensity, hdu_list[1].data.field('intensity')[i])
    psi = np.append(psi, hdu_list[1].data.field('psi')[i]) 
    energy = np.append(energy, hdu_list[1].data.field('mcEnergy')[i])

    #Calculate source position    
    mcAlt = hdu_list[1].data.field('mcAlt')[i] 
    mcAz = hdu_list[1].data.field('mcAz')[i]
    mcAlttel = hdu_list[1].data.field('mcAlttel')[i]
    mcAztel = hdu_list[1].data.field('mcAztel')[i]
    
    srcpos = Disp.calc_CamSourcePos([mcAlt],[mcAz],[mcAlttel],[mcAztel],focal_length)

    Source_X = srcpos[0]
    Source_Y = srcpos[1]
    
    cen_x = hdu_list[1].data.field('x')[i]
    cen_y = hdu_list[1].data.field('y')[i]
    
    disp = Disp.calc_DISP(Source_X,Source_Y,cen_x,cen_y)

    print(hdu_list[1].data.field('intensity')[i],hdu_list[1].data.field('skewness')[i])
    if (hdu_list[1].data.field('intensity')[i]) > 0:
        display = CameraDisplay(geom)
        display.add_colorbar()
        
        image = hdu_list[2].data[i]
        
        display.image = image
        display.cmap = 'CMRmap'
    
    
        plt.plot([Source_X],[Source_Y],marker='o',markersize=10,color="green")
        plt.plot([cen_x],[cen_y],marker='x',markersize=10,color="blue")
        plt.plot([Source_X,cen_x],[Source_Y,cen_y],'-',color="red")
        posrec = Disp.Disp_to_Pos(disp,cen_x,cen_y,psi[i]) 
        plt.plot(posrec[0],posrec[1],marker='o',color='red')
        plt.show()
    
