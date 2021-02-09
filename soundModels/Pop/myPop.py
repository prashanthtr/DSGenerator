import numpy as np
#import seaborn as sns
from scipy import signal
import math
#import sys

from genericsynth import synthInterface as SI

class MyPop(SI.MySoundModel) :

	def __init__(self, f0=440, Q=10) :
		SI.MySoundModel.__init__(self)
		#create a dictionary of the parameters this synth will use
		self.__addParam__("cf_exp", 100, 2000, f0)
		self.__addParam__("Q", .1, 50, Q)

	'''
		Override of base model method
	'''
	def generate(self, sigLenSecs) :

		# notation for this method
		f0=self.getParam("cf_exp")
		Q =self.getParam("Q")

		# pop specific parameters
		length = round(sigLenSecs*self.sr) # in samples
		ticksamps = 3  # number of noise samples to use before filtering
		krms = 0.6
		tick=2*np.random.rand(ticksamps)-1    #noise samples in [-1,1]
		tick = np.pad(tick, (0, length-ticksamps), 'constant')

	    # Design peak filter
		b, a = signal.iirpeak(f0, Q, self.sr)
		#use it
		tick=signal.lfilter(b, a, tick)

		if False :
			#print("original rms={}".format(math.sqrt(sum([x*x/ticksamps for x in tick]))))
			c=math.sqrt(ticksamps*krms*krms/sum([(x*x) for x in tick]))
			tick = [c*x for x in tick]
			#print("new rms={}".format(math.sqrt(sum([x*x/ticksamps for x in tick]))))
		else :
			maxfsignal=max(abs(tick))
			tick = tick*.9/maxfsignal

		return tick

	'''Print all the parameters and their ranges from the synth'''
	def printParams(self):
		paramVals = self.paramProps()
		for params in paramVals:
			print( "Name: ", params.name, " Default value : ", params.val, " Max value ", params.max, " Min value ", params.min )
