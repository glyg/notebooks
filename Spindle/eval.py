#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import *
from pylab import *
from scipy import *

def ouvrir(data, filename, sep):

    f = open(filename, 'r+')

    WaveList = f.readline()
    WaveList = WaveList.split()

    index = 0
    for name in WaveList:
        if data in name:
            break
        else:
            index+=1
    if index + 1 > len(WaveList):
        print 'data not in found !!'
        return 0
    
    wave = io.array_import.read_array(f , separator = sep,columns = (index, )) 

    return wave
    



def distribution(data, filename, sep, do_plot = 1, bins = 10, range = None):
    '''
    data and filename must be strings
    displays the histogram if do_plot = 1
    same output as the histogram function
    '''
    wave = ouvrir(data, filename, sep)
    if do_plot :
        dist = histogram(wave, bins = bins, normed = True)[0]
        xdist = histogram(wave, bins = bins, normed = True)[1]
        figure(1)
        plot(xdist, dist, 'ro')
        show()
        
    return histogram(wave, bins = bins, normed = False)

def variations(data, filename,  sep, xwave = None, dt = None ):

    wave = ouvrir(data, filename, sep)
    wave_dif = diff(wave)

    if xwave is not None:
        if len(xwave) != len(wave):
            print 'Both waves must be of same length !!!'
            return 0

        xwave_dif = diff(xwave)
        wave_dif = wave_dif / xwave_dif
        return wave_dif
    elif dt is not None:
        wave_dif /= dt
        return wave_dif
    else:
        return wave_dif

def angle_evaluation(basename, sep, degrees = None):

    angbins = 100.
    angmax = pi
    angmin = - pi
    angstep = (angmax - angmin) / angbins
    angdist = zeros(angbins)
    xangdist = arange(angmin, angmax, angstep)

    for i in range(70):
        filename = basename+str(i)+'.txt'
        try:
            spindle_angle = ouvrir('spindle_angle', filename, sep)
            if degrees is not None:
                spindle_angle *= pi/180

            tmp_adist = histogram(spindle_angle, angbins,
                                  range = (angmin, angmax), normed = False)[0]
            angdist += tmp_adist
        except IOError:
            print 'file '+filename+' not found'
            i+=1
            continue

    sigma = sum(angdist)               
    angdist /= sigma

    figure(1)
    plot(xangdist, angdist)
    xlabel('Angle (radians)')
    ylabel('Frequency')
        
    return (angdist, xangdist)
    
 
def angle_speed_eval(dt, basename, sep, degrees = None):

    difangbins = 100.
    difangmax = pi / 4
    difangmin = - pi / 4
    difangstep = (difangmax - difangmin) / difangbins

    difangdist = zeros(difangbins)
    xdifangdist = arange(difangmin, difangmax, difangstep)

    for i in range(70):
        filename = basename+str(i)+'.txt'
        try:
            angle_dif = variations('spindle_angle', filename,  sep, xwave = None, dt = dt)

            if degrees is not None:
                angle_dif *= pi/180

            tmp_adist = histogram(angle_dif, difangbins,
                                  range = (difangmin, difangmax), normed = False)[0]
            difangdist += tmp_adist
        except IOError:
            i += 1

    sigma = sum(difangdist)               
    difangdist /= sigma

    figure(2)
    plot(xdifangdist, difangdist)
    xlabel(r'$\Delta \theta (rad.min^{-1})$')
    ylabel('Frequency')

    return (difangdist, xdifangdist)
    
    
def deltaR_eval(dt, basename, sep, degrees = None):

    
    bin = 100.
    mini = -2.5
    maxi= 2.5
    step = (maxi - mini)/bin

    Rdist = zeros(bin)
    xRdist = arange(mini+step/2, maxi+step/2, step)
    
    for i in range(70):
        filename = basename+str(i)+'.txt'
        
        try:
            spindle_angle = ouvrir('spindle_angle', filename, sep)
            if degrees is not None:
                spindle_angle *= pi/180
            spindle_length = ouvrir('spindle_length', filename, sep)
            
            angle_dif = diff(spindle_angle) / dt
            deltaR = spindle_length[1:] * sin(angle_dif)

            tmp_Rdist = histogram(deltaR, bin,
                                  range = (mini, maxi), normed = False)[0]
            Rdist += tmp_Rdist

        except IOError:
            print 'file '+filename+' not found'
            i+=1
            continue

    sigma = sum(Rdist)               
    Rdist /= sigma

    figure(3)
    plot(xRdist, Rdist)
    xlabel(r'$\Delta r (\mu m.min^{-1})$')
    ylabel('Frequency')

    return (Rdist, xRdist)

def agregation(dt, basename, sep, degrees = None):

    all_angles = []
    all_lengths = []
    all_spb1 = []
    all_spb2 = []

    for i in range(70):
        
        filename = basename+str(i)+'.txt'
        try:
            f = open(filename, 'r+')

            wavelist = f.readline()
            wavelist = wavelist.split()
            numcol = len(wavelist)

            wave = io.array_import.read_array(f , separator = sep,columns = (0, -1))
            
            index = 0
            reflist = []
            # On écrit une liste de paires contenant le nom de la wave lu sur la 1° ligne
            # et les valeurs de la colonne correspondante
            for name in wavelist:
                reflist.append((name, wave[:, index]))
                index+=1
            # Comme ça on a le dictionnaire:
            all_datas = dict(reflist)
            
            all_angles.append(all_datas['spindle_angle'])
            all_lengths.append(all_datas['spindle_length'])
            try:
                all_spb1.append([all_datas['xspb1'], all_datas['yspb1']])
                all_spb2.append([all_datas['xspb2'], all_datas['yspb2']])
            except KeyError:
                all_spb1.append([all_datas['xSPB1'], all_datas['ySPB1']])
                all_spb2.append([all_datas['xSPB2'], all_datas['ySPB2']])
        except IOError:
            print 'file '+filename+' not found'
            i+=1
            continue



    distA = angle_evaluation(basename, sep, degrees)[0]
    xdistA = angle_evaluation(basename, sep, degrees)[1]

    distDA = angle_speed_eval(dt, basename, sep, degrees)[0]
    xdistDA = angle_speed_eval(dt, basename, sep, degrees)[1]

    distDR = deltaR_eval(dt, basename, sep, degrees)[0]
    xdistDR = deltaR_eval(dt, basename, sep, degrees)[1]        


    data = column_stack((distA, xdistA, distDA, xdistDA,  distDR, xdistDR))

    tmp = 'temp.txt'
    name = 'distros.txt'
    
    io.write_array(tmp, data, separator=' ', linesep='\n')
    f = open(name,'w+')
    g = open(tmp,'r+')
    f.write("Ang, XAng DeltaAng XDeltaAng DeltaR XDeltaR\n")
    for line in g:
        f.write(line)

    f.close()
    g.close()

    
        

        

