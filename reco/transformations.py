#!/usr/bin/env python3
'''
Module with auxiliar functions:
Transform AltAz coordinates into Camera coordinates (This should be implemented already in ctapipe but I haven't managed to find how to do it)
Calculate source position from Disp distance.
Calculate Disp distance from source position.

Usage:

"import transformations"

'''

import numpy as np
import ctapipe.coordinates as c
import astropy.units as u

def alt_to_theta(alt):
    """
    transforms altitude (angle from the horizon upwards) to theta (angle from z-axis)                                                         
    for simtel array coordinate systems                                  
    """
    return (90 * u.deg - alt).to(alt.unit)


def az_to_phi(az):
    """
    transforms azimuth (angle from north towards east)                
    to phi (angle from x-axis towards y-axis)                            
    for simtel array coordinate systems                                  
    """
    return -az

        
def calc_CamSourcePos(mcAlt,mcAz,mcAlttel,mcAztel,focal_length):
    """
    Transform Alt-Az source position into Camera(x,y) coordinates source position. 

    """
    mcAlt = alt_to_theta(mcAlt*u.rad).value
    mcAz = az_to_phi(mcAz*u.rad).value
    mcAlttel = alt_to_theta(mcAlttel*u.rad).value
    mcAztel = az_to_phi(mcAztel*u.rad).value
        
    #Sines and cosines of direction angles
    cp = np.cos(mcAz)
    sp = np.sin(mcAz)
    ct = np.cos(mcAlt)
    st = np.sin(mcAlt)
    
     #Shower direction coordinates

    sourcex = st*cp
    sourcey = st*sp
    sourcez = ct

    #print(sourcex)

    source = np.array([sourcex,sourcey,sourcez])
    source=source.T
    
    #Rotation matrices towars the camera frame
    
    rot_Matrix = np.empty((0,3,3))
    #    for (alttel,aztel) in zip(mcAlttel,mcAztel):
        
    alttel = mcAlttel
    aztel = mcAztel
    mat_Y = np.array([[np.cos(alttel),0,np.sin(alttel)],
                      [0,1,0], 
                      [-np.sin(alttel),0,np.cos(alttel)]]).T
        
        
    mat_Z = np.array([[np.cos(aztel),-np.sin(aztel),0],
                      [np.sin(aztel),np.cos(aztel),0],
                      [0,0,1]]).T
    
        
    #rot_Matrix = np.append(rot_Matrix,[np.matmul(mat_Y,mat_Z)],axis=0)
    rot_Matrix = np.matmul(mat_Y,mat_Z)
    
    res = np.einsum("...ji,...i",rot_Matrix,source)
    res = res.T
    
    Source_X = -focal_length*res[0]/res[2]
    Source_Y = -focal_length*res[1]/res[2]
    return Source_X, Source_Y

def calc_DISP(Source_X,Source_Y,cen_x,cen_y):
    """
    Calculates "Disp" distance from source position in camera coordinates
    """
    disp = np.sqrt((Source_X-cen_x)**2+(Source_Y-cen_y)**2)
    return disp

def Disp_to_Pos(Disp,cen_x,cen_y,psi):
    """
    Calculates source position in camera coordinates(x,y) from "Disp" distance.
    For now, it only works for POINT GAMMAS, it doesn't take into account the duplicity of the 
    disp method. 
    """
    
    Source_X1 = cen_x - Disp*np.cos(psi)
    Source_Y1 = cen_y - Disp*np.sin(psi)
   
    return Source_X1,Source_Y1
        
       
