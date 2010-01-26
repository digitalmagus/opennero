#!/usr/bin/env python
"""Process and display performance of AI algorithms in OpenNERO.

plot_server reads a log file (or receives this file over the network) and 
plots the performance of the AI algorithm which is producing this log file.
"""

import sys
import re
import time
import numpy as np
import matplotlib.pyplot as pl
import matplotlib.mlab as mlab
import socket
import tempfile

__author__ = "Igor Karpov (ikarpov@cs.utexas.edu)"
__copyright__ = "Copyright 2010, The University of Texas at Austin"
__license__ = "LGPL"
__version__ = "0.1.0"

HOST, PORT = "localhost", 9999
ADDR = (HOST, PORT)
BUFSIZE = 4086

ai_tick_pattern = re.compile(r'(?P<date>[^\[]*)\.(?P<msec>[0-9]+) \(m\) \[ai\.tick\]\s+(?P<id>\S+)\s+(?P<episode>\S+)\s+(?P<step>\S+)\s+(?P<reward>\S+)\s+(?P<fitness>\S+)')
timestamp_fmt = r'%Y-%b-%d %H:%M:%S'
file_timestamp_fmt = r'%Y-%m-%d-%H-%M-%S'

def timestamped_filename(prefix = '', postfix = ''):
    return '%s%s%s' % (prefix, time.strftime(file_timestamp_fmt), postfix)

class LearningCurve:
    def __init__(self):
        self.min_time = None
        self.max_time = None
        self.data = []
        self.episodes = []
        self.fig = None

    def save(self):
        if self.fig:
            self.fig.savefig(timestamped_filename('opennero-','-episodes.png'))

    def reset(self):
        self.save()
        self.min_time = None
        self.max_time = None
        self.data = []
        self.episodes = []
        self.fig = pl.figure()
        pl.hold(True)
        pl.xlabel('step')
        pl.ylabel('fitness')
        pl.title('Episodes')
        pl.grid(True)
    
    def plot_episode(self):
        M = np.array(self.data)
        steps = M[:,-3]
        fitness = M[:,-1]
        pl.plot(steps, fitness, linewidth=1.0)

    def append(self, t, msec, episode, step, reward, fitness):
        #only remember the most recent set of episodes
        if episode == 0 and step == 0:
            self.reset()
        elif step == 0:
            # on episode start, append the previous episode's fitness
            self.episodes.append(self.data[-1][-1])
            self.plot_episode()
            self.data = []
        sec = time.mktime(t) * 1000000
        sec += msec
        if not self.min_time:
            self.min_time = sec
        self.max_time = sec
        print sec, episode, step, reward, fitness
        self.data.append( (time, msec, episode, step, reward, fitness) )

def process_line(lc, line):
    """Process a line of the log file and record the information in it in the LearningCurve lc
    """
    line = line.strip().lower()
    m = ai_tick_pattern.search(line)
    if m:
        t = time.strptime(m.group('date'), timestamp_fmt)
        ms = int(m.group('msec'))
        episode = int(m.group('episode'))
        step = int(m.group('step'))
        reward = float(m.group('reward'))
        fitness = float(m.group('fitness'))
        lc.append( t, ms, episode, step, reward, fitness )
        
def server():
    lc = LearningCurve()
    # Create socket and bind to address
    UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    UDPSock.bind(ADDR)
    # Receive messages
    while 1:
        data = UDPSock.recv(BUFSIZE)
        if not data:
            print "Client has exited!"
            break
        else:
            process_line(lc, data)
    # Close socket
    UDPSock.close()
    return lc

def main():
    lc = server()
    lc.save()
    x = np.array(range(0,len(lc.episodes)))
    y = np.array(lc.episodes)
    fig = pl.figure()
    pl.plot(x, y, linewidth=1.0)
    pl.xlabel('episode')
    pl.ylabel('fitness')
    pl.title('By-episode fitness')
    pl.grid(True)
    fig.savefig(timestamped_filename('opennero-','-fitness.png'))
    pl.show()
    print 'done'

if __name__ == "__main__":
    main()