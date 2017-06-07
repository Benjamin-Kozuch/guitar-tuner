import pyaudio
import struct
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal
from sets import Set

def cancel_low_powered_freq(X,min):
    index = 0
    for i in abs(X):
        if i < min:
           X[index] = 0; 
        index+=1
    return X  

def get_peak(X):
    return np.argmax(abs(X))

E_LOW =Set([10, 16, 1013])
A=Set([14, 21, 1017, 1010, 1003])
D=Set([19, 1005])
G=Set([25, 999])
B=Set([16, 1008])
E_HIGH=Set([21,1003])

#strings = [E, A, D, G, B, E]
strings = {'E_LOW': E_LOW, 'A': A, 'D': D,'G': G, 'B': B, 'E_HIGH': E_HIGH};

plt.ion()           # Turn on interactive mode so plot gets updated

WIDTH = 2           # bytes per sample
CHANNELS = 1        # mono
RATE = 16000      	# Sampling rate (samples/second)
BLOCKSIZE = 1024
DURATION = 120       # Duration in seconds

num_blocks = int( DURATION * RATE / BLOCKSIZE )

print 'BLOCKSIZE =', BLOCKSIZE
print 'num_blocks =', num_blocks
print 'Running for ', DURATION, 'seconds...'

# Initialize plot window:
plt.figure(1)
plt.ylim(0, 10*RATE)

#Time axis in units of milliseconds:
plt.xlim(0, RATE/2.0)         # set x-axis limits
plt.xlabel('Frequency (Hz)')
f = [n*float(RATE/BLOCKSIZE) for n in range(BLOCKSIZE)]

line, = plt.plot([], [], color = 'blue')  # Create empty line
line.set_xdata(f)                         # x-data of plot (frequency)

# Open audio device:
p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(format = PA_FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                output = False)

all_peaks = Set([ ])

for i in range(0, num_blocks):
    try:
        input_string = stream.read(BLOCKSIZE) 
    except IOError as ex:
        if ex[1] != pyaudio.paInputOverflowed:
            raise
        data = '\x00' * BLOCKSIZE 


    input_tuple = struct.unpack('h'*BLOCKSIZE, input_string)  # Convert
    X = np.fft.fft(input_tuple)


    #Take out Low powered frequencies
    X = cancel_low_powered_freq(X,50000)


    #Get peaks
    peak = get_peak(X)
    if peak == 0:
        is_note = False # there is currently no note being played
    else:
        is_note = True 


    if is_note:
        all_peaks.add(peak)  	
    else:
        if len(all_peaks)!=0:
            just_min = min(all_peaks)
            if just_min == 10: print 'Low E'
            elif just_min == 14: print 'A'
            elif just_min == 19: print 'D'
            elif just_min == 25: print 'G'
            elif just_min == 16: print 'B'
            elif just_min == 21: print 'High E'
            else:
                print 'XXXXXXXXXXX'*3 + ' '+ str(just_min)
                print "\nE-->10\nA-->14\nD-->19\nG-->25\nB-->16\nE->21\n"	

        all_peaks.clear()

    line.set_ydata(abs(X))                               
    plt.draw()

stream.stop_stream()
stream.close()
p.terminate()

print '* Done *'
