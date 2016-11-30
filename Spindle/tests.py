from eval import *

dt = 0.5
basename = 'cell'
sep = ' '
degrees = None

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
        all_spb1.append([all_datas['xspb1'], all_datas['yspb1']])
        all_spb2.append([all_datas['xspb2'], all_datas['yspb2']])

    except IOError:
        print 'file '+filename+' not found'
        i+=1
        continue



distA = angle_evaluation(sep, degrees)[0]
xdistA = angle_evaluation(sep, degrees)[1]

distDA = angle_speed_eval(dt, basename, sep, degrees)[0]
xdistDA = angle_speed_eval(dt, basename, sep, degrees)[1]

distDR = deltaR_eval(dt, basename, sep, degrees)[0]
xdistDR = deltaR_eval(dt, basename, sep, degrees)[1]        


data = S.column_stack((distaA, xdistA, distDA, xdistDA,  distDR, xdistDR))

tmp = 'temp.txt'
name = 'distros.txt'

S.io.write_array(tmp, data, separator=' ', linesep='\n')
f = open(name,'w+')
g = open(tmp,'r+')
f.write("Ang, XAng DeltaAng XDeltaAng DeltaR XDeltaR\n")
for line in g:
    f.write(line)

f.close()
g.close()
