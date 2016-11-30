#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

from spacegeo import *
from pylab import *
        
class Cortex(object):

    def __init__(self,cell_width=3.,cell_length=15.):
        self.width = cell_width
        self.length = cell_length

    def isinside(self,particle):
        ''' returns true if the particle (a 3D array) is in the cell '''

        width = self.width
        length = self.length
        right = (length - width)/2
        left = - right
        
        proj = sqrt(particle[1]**2 + particle[2]**2)

        if proj <= width/2 and abs(particle[0]) <= right:
            return True

        elif right < abs(particle[0]) <= length/2:

            p = S.array([abs(particle[0]),particle[1],particle[2]])
            r = S.array([right,0,0])
            c = CartezPos(p-r)
            rho = c.norme()
            
            if rho <= width/2:
                return True
            else:
                return False
        else:
            return False

        
    def shape(self,scale):
        ''' scale is  per pixel  '''

        width = self.width
        length = self.length
        l = int(length*1.2/scale)
        m = int(width*1.2/scale)
        n = m
        
        grid = S.zeros((l,m,n),dtype = int)

        for i in range(l):
            for j in range(m):
                for k in range(n):
                    x = float((i - l/2) * scale)
                    y = float((j - m/2) * scale)
                    z = float((k - n/2) * scale)

                    voxel = S.array([x,y,z])
                    if self.isinside(voxel):
                        grid[i][j][k] = 1
                    else:
                        grid[i][j][k] = 0

        return grid

    def shape2D(self, scale):

        width = self.width
        length = self.length

        xmin = -length/2
        xmax = length/2 + scale 
        right = (length - width)/2
        left = -right
        xaxis = S.arange(xmin, xmax, scale)
        yval1 = []
        for x in xaxis:
            if abs(x) <= right:
                y1 = width/2
            elif xmin <= x < left :
                y1 = sqrt((width / 2)**2 - (x - left)**2)
            elif right < x <= xmax :
                y1 = sqrt((width / 2)**2 - (x - right)**2)

            yval1.append(y1)

        yval1 = S.array(yval1)
        yval2 = -yval1
        return (xaxis, yval1, yval2)
        
class Nucleus(object):

    def __init__(self,radius = 1.5):
        self.radius = radius

    def isinside(self,particle):

        radius = self.radius
        p = CartezPos(particle)
        rho = p.norme()

        if rho < radius:
            return True
        else:
            return False


class Fuseau(CartezPos):

    c  = S.array([0, 1.2, 0])
    
    def __init__(self,length=0.4,center=c,
                 theta=0,phi=pi/2):
        ''' The spindle is defined by its length,
        the position of its center
        and the angles of the SPBs '''
        self.length = length
        self.center = center
        self.theta = theta
        self.phi = phi

    def pos_spbs(self):
        
        ''' returns a tuple of 2 3D arrays giving
        the absolute positions of the SPBs '''

        center = CartezPos(self.center)
        length = self.length
        theta = self.theta
        phi = self.phi

        spb1_rel = S.array([length/2,theta,phi])
        spb1_rel = SpherPos(spb1_rel).cartez()

        spb1 = center.pos + spb1_rel
        spb2 = center.pos - spb1_rel
        
        return (spb1, spb2)

    def projection(self):

        pos_spbs = self.pos_spbs()
        spb1 = pos_spbs[0]
        spb2 = pos_spbs[1]
        spin = [spb1[0] - spb2[0], spb1[1] - spb2[1], 0]
        length_proj = CartezPos(spin).norme()
        return length_proj


## Random motion for a free spindle (no membrane)

    def shake(self, dt, pos_noise = 0.1):
 
        tmp = Fuseau()
        tmp.length = self.length
        ang_noise = 20 * asin(pos_noise / tmp.length)
        tmp.theta = self.theta + dt * random.gauss(0,ang_noise)
        tmp.phi = self.phi + dt * random.gauss(0,ang_noise)
        tmp.center[0] = self.center[0] + dt * random.gauss(0,pos_noise)
        tmp.center[1] = self.center[1] + dt * random.gauss(0,pos_noise)
        tmp.center[2] = self.center[2] + dt * random.gauss(0,pos_noise)
        return tmp
            
    def move(self, txelong, dt, len_noise = 0.2):

        tries = 0
        cortex = Cortex()
        if self.length >= cortex.length :
            return 0
        self.length += dt * random.gauss(txelong,len_noise)  
        if self.length >= cortex.length :
            return 0
        
        tmp = self.shake(dt = dt)
        inside = map(cortex.isinside,tmp.pos_spbs())

        while not S.all(inside) : 
            tmp = self.shake(dt = dt)
            tries += 1 
            inside = map(cortex.isinside,tmp.pos_spbs())
            if tries > 1000:
                return 0
            
        self.theta = tmp.theta
        self.phi = tmp.phi
        self.center = tmp.center
        return 1

## Random motion for a rigid emi-spherical membrane

    def shake_fixnuc(self, dt,  pos_noise = 0.1):
        
        tmp = Fuseau()
        tmp.length = self.length
        nuc = Nucleus()
        radius = nuc.radius

        ang_noise = 20 * asin(pos_noise / tmp.length)
        tmp.theta = self.theta + dt * random.gauss(0,ang_noise)
        tmp.phi = self.phi + dt * random.gauss(0,ang_noise)

        
        tmp.center = CartezPos(self.center).spherical()
        if tmp.length/2 > radius:
            radius = tmp.length / 2
            rho_c = 0
            theta_c = 0
            phi_c = 0
        else:
            rho_c = sqrt(nuc.radius**2 - (tmp.length**2) / 4)                
            ang_noise_center = ( pi / 10 )* pos_noise
            theta_c = tmp.center[1] +  dt * random.gauss(0,ang_noise_center)
            a = cos(self.theta - theta_c) * tan(self.phi)
            if abs(a) <= 1E-6:
                phi_c = tmp.phi + pi/2
                print "a nul!!"
            else:
                phi_c = atan2(1,a)

        tmp.center = array([rho_c, theta_c, phi_c])
        tmp.center = SpherPos(tmp.center).cartez()

        return tmp
    
    def move_fixnuc(self, txelong, dt, len_noise = 0.2):

        tries = 0
        cortex = Cortex()

        if self.length >= cortex.length :
            return 0
        self.length += dt * random.gauss(txelong,len_noise)  
        if self.length >= cortex.length :
            return 0
        tmp = self.shake_fixnuc(dt = dt)
        inside = map(cortex.isinside,tmp.pos_spbs())

        while not S.all(inside) : 
            tmp = self.shake_fixnuc(dt = dt)
            tries += 1 
            inside = map(cortex.isinside,tmp.pos_spbs())
            if tries > 1000:
                print 'out!'
                return 0
             
        self.theta = tmp.theta
        self.phi = tmp.phi
        self.center = tmp.center

        return 1

## Random motion



                
class CellCycle(Fuseau,Nucleus,Cortex):

    f = Fuseau()
    c = Cortex()
    n = Nucleus()
    
    def __init__(self,fuso = f, nuc = n, cortex = c):

        self.fuso = Fuseau()
        self.nuc = Nucleus()
        self.cortex = Cortex()
        self.trajs_spbs = [fuso.pos_spbs()]
        self.trajs_theta = [fuso.theta]
        
    def phase(self,tstart,tstop,dt,txelong, fixnuc = 0):

        cortex = self.cortex
        
        stt = int(round(tstart / dt))
        stp = int(round(tstop / dt))
                
        for i in range(stt, stp):
            if not fixnuc:
                move = self.fuso.move(txelong, dt)
            else:
                move = self.fuso.move_fixnuc(txelong, dt)

            if not move:
                break
            self.trajs_spbs.append(self.fuso.pos_spbs())
            self.trajs_theta.append(self.fuso.theta)

    def cycle(self,dt, fixnuc = 0):

        ## taux d'élongation moyen
   
        self.txelong1 = random.gauss(0.4,0.01)  #um/min
        self.txelong2 = random.gauss(0.2,0.01)
        self.txelong3 = random.gauss(0.8,0.15)
  
        ## timing des phases
   
        self.temps_1 = abs(2 + random.gauss(0,0.1))
        self.temps_2 = self.temps_1 + 6 + abs(random.gauss(3,3))
        self.temps_3 = self.temps_2 + 8 + random.gammavariate(3,1)

        ## initialisation

        l0 = 0.4 + random.gauss(0.4,0.01) # longueur initiale du fuseau
        
        [xc,yc,zc] = [random.gauss(0,0.1),random.gauss(1.2,0.05),
                      random.gauss(0,0.1)]
        center=S.array([xc,yc,zc])
        theta= random.gauss(0,pi/10) # angle initial
        phi = random.gauss(pi/2,pi/10)

        self.fuso = Fuseau(l0,center,theta,phi)
        self.trajs_spbs = [self.fuso.pos_spbs()]
        self.trajs_theta = [self.fuso.theta]


        tps1 = self.temps_1
        tx1 = self.txelong1
        tps2 = self.temps_2
        tx2 = self.txelong2
        tps3 = self.temps_3
        tx3 = self.txelong3

        self.phase(0,tps1,dt,tx1, fixnuc)
        self.phase(tps1,tps2,dt,tx2, fixnuc)
        self.phase(tps2,tps3,dt,tx3, fixnuc)

        trajs_spbs = S.array(self.trajs_spbs)
        self.spb1 = trajs_spbs[:,0,:]
        self.spb2 = trajs_spbs[:,1,:]
        p_spb1 = self.spb1[:,0:2]
        p_spb2 = self.spb2[:,0:2]
        self.length_proj = map(distance, p_spb1, p_spb2)
        


    def display(self,dt):

        cortex = self.cortex.shape2D(0.02)
        trajs_spbs = S.array(self.trajs_spbs)
        trajs_theta = S.array(self.trajs_theta)
        length_proj = S.array(self.length_proj)
 
        p_spb1 = self.spb1[:,0:2]
        p_spb2 = self.spb2[:,0:2]


    
        nb_frames = len(length_proj)
        timelapse = []
        for i in range(nb_frames) :
            timelapse.append(i*dt)
        timelapse = S.array(timelapse)
        timelapse -= self.temps_2
        
        figure(1)
        subplot(211)
        plot(timelapse,length_proj,'-')

        subplot(212)
        plot(timelapse,trajs_theta,'-')
        axis([-15,15,-1,1])
        figure(2)
        plot(self.spb1[:,0],self.spb1[:,1],'bo-',self.spb2[:,0],self.spb2[:,1],'ro-',
             cortex[0], cortex[1], 'k-', cortex[0], cortex[2], 'k-')
       ## axis([-8,8,-2,2])

        
    def logging(self, fname, dt):
        ''' Écrit dans le fichier nommé fname.txt les trajectroires des SPBs, etc.
        '''
        tmp = "data.txt"
        name= fname+".txt"
        
        length_proj = S.array(self.length_proj)
        spindle_angle = S.array(self.trajs_theta)
        posSPB1 = self.spb1[:,0:2]
        posSPB2 = self.spb2[:,0:2]

        nb_frames = len(length_proj)
        timelapse = []
        for i in range(nb_frames) :
            timelapse.append(i*dt)
        timelapse = S.array(timelapse)
        timelapse -= self.temps_2
        

        data = S.column_stack((length_proj, spindle_angle, posSPB1[:,0], posSPB1[:,1],
                             posSPB2[:,0], posSPB2[:,1], timelapse))

        S.io.write_array(tmp, data, separator=' ', linesep='\n')
        f = open(name,'w+')
        g = open(tmp,'r+')
        f.write("spindle_length spindle_angle xspb1 yspb1 xspb2 yspb2 timelapse\n")
        for line in g:
            f.write(line)

        f.close()
        g.close()


