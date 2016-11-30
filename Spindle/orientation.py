#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import scipy as S
from scipy import stats
from pylab import *
from scipy import io

from spacegeo import *
from pombe import *


dt = 0.5
longueur_moyenne = []
angle_moyen = []
angle_maxi = []
angle_onset = []
ecartype = []
duree2 = []
duree1 = []

for run in range(80):

    cc = CellCycle()
    cc.cycle(dt,fixnuc = 0)
    
    if run % 5 == 0:
        cc.display(dt)

    length_proj = S.array(cc.length_proj)
    trajs_theta = S.array(cc.trajs_theta)
    trans12 = int(cc.temps_1 * 0.5)
    trans23 = int(cc.temps_2 * 0.5)

    if len(length_proj) > trans23:
        longueur_moyenne.append(stats.mean(length_proj[trans12:trans23]))
        angle_moyen.append(stats.mean(trajs_theta[trans12:trans23]))
        angle_maxi.append(reduce(maximum,abs(trajs_theta[trans12:trans23])))
        angle_onset.append(abs(trajs_theta[trans23]))
        ecartype.append(stats.std(trajs_theta[trans12:trans23]))
        duree1.append(cc.temps_1)
        duree2.append(cc.temps_2 - cc.temps_1)
        fname = 'cell'+str(run)
        cc.logging(fname,dt)
        
    else :
        print 'discarded cell # %d ' % run
    del cc



angle_moyen =  S.array(angle_moyen)
longueur_moyenne= S.array(longueur_moyenne)
ecartype =  S.array(ecartype)
duree2 = S.array(duree2)
duree1 = S.array(duree1)
angle_onset = S.array(angle_onset)*180/pi
angle_maxi = S.array(angle_maxi)*180/pi


angle_moyen = fabs(angle_moyen)*180/pi


data = S.column_stack((duree1, duree2, angle_moyen,ecartype,longueur_moyenne))

io.write_array("results.txt", data, separator=' ', linesep='\n')

figure(3)

plot(duree2,angle_moyen,'o')


show()
