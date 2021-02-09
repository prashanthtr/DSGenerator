# dependencies for file reading
import json
import sys
import itertools
import numpy as np
import os
import soundfile as sf

import librosa # conda install -c conda-forge librosa

from parammanager import paramManager
# from sonyganformat import sonyGanJson

from genericsynth import synthInterface as SI
# from myDripPatternSynth import MyDripPatternSynth
from filewrite import fileHandler

import importlib


#from Tf_record import tfrecordManager

'''
This code will generate a dataset of textures consiting of drip. A 'pop' is a frequency sweep with an amplitude envelope.

The files are generated using 3 different parameters that are sampled over a range of values. The three parameters affect:
    rate (average events per second),
    irregularity in temporal distribution (using a gaussian distribution around each evenly-spaced time value), and
    the center frequency of bp filter

The parameter values are each sampled liniearly on an exponential scale:

rate = 2^r_exp  (so r_exp in [0,4] means the rate ranges from 2 to 16)
irregularity = .04*10^irreg_exp; sd = irregularity/events per second  (so irreg_exp in [0,1] means irregularity ranges from completely regular, to Poisson process)
cf = 440*2^cf_exp  (so cf_exp in [0,1] means cf ranges from 440 to 880, one octave)

For each parameter setting, first a "long" signal (of lentgth longDurationSecs) is generated, and then
it is sliced into segments (called variations) of a length desired for training.

Example: If each parameter is sampled at 5 values, the long signal is 10 seconds and variationLength is 2 seconds,
then The the total amount of audio generated is 5*5*5*10= 1250 seconds of sound (about 25 hours; ~3Gb at 16K sr).
If each variation is 2 seconds, then there will be 10/2=5 variations for each parameter setting, and
5*5*5*5 = 625 files
'''

import argparse

myConfig = {}
soundModels = {}

def get_arguments():
    parser = argparse.ArgumentParser(description="myParser")
    parser.add_argument("--configfile", required=True)
    return parser.parse_args()

def main():

    loadSoundModels()

    args = get_arguments()
    module_name = args.configfile # here, the result is the file name, e.g. config or config-special

    # Not use __import__, use import_module instead according to @bruno desthuilliers's suggestion
    # __import__(module_name) # here, dynamic load the config module
    # MyConfig = sys.modules[module_name].MyConfig # here, get the MyConfig class
    # MyConfig = importlib.import_module(module_name)

    with open(module_name) as json_file:
        MyConfig = json.load(json_file)
        print("Reading parameters for generating ", MyConfig['soundname'], " texture.. ")
        for p in MyConfig['params']:
            p['formula'] = eval("lambda *args: " + p['formula'])

    # from args.configfile import MyConfig # <-- how is that possible?
    generate(MyConfig)

    print(MyConfig["params"])

def loadSoundModels():
    print("loading")
    dirpath = "soundModels/"
    modules = [f for f in os.listdir(os.path.dirname(dirpath)) if f[0] != "." and f[0] != "_"]
    for module in modules:
        spec = importlib.util.spec_from_file_location(module, os.path.join(dirpath,module +"/my" + module + "PatternSynth.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        soundModels[module] = mod
        # mod_name = file[:-3]   # strip .py at the end
        # exec('from soundModels' + ' import ' + os.path.abspath(mod_name))

        # files = [f for f in os.listdir(os.path.dirname(dirpath+module+"/")) if f[0] != "." and f[0] != "_"]
        #for file in files:
        #    spec = importlib.util.spec_from_file_location(module, os.path.join(dirpath,module +"/" + file))
        #    mod = importlib.util.module_from_spec(spec)
        #    spec.loader.exec_module(mod)
        # importlib.import_module(dirpath + directory)

def generate(MyConfig):
    
    '''Initializes file through a filemanager'''
    fileHandle = fileHandler()


    print("Enumerating parameter combinations..")

    '''
        for every combination of cartesian parameter
        for every variation
            Create variation wav files
            Create variation parameter files
    '''

    '''2 arrays for normalised and naturalised ranges'''
    userRange = []
    synthRange = []
    paramArr = MyConfig["params"]

    if MyConfig["paramRange"] == "Norm":
        for p in MyConfig["params"]:
            userRange.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))    
        for p in MyConfig["params"]:
            synthRange.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))
    else:
        for p in MyConfig["params"]:
            userRange.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))    
        for p in MyConfig["params"]:
            synthRange.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))

    userParam = list(itertools.product(*userRange))
    synthParam = list(itertools.product(*synthRange))

    # sg = sonyGanJson.SonyGanJson(MyConfig['soundname'],1, 16000, MyConfig['soundname'])

    for index in range(len(userParam)): # caretesian product of lists

            userP = userParam[index]
            synthP = synthParam[index]

            #set parameters
            print(soundModels[MyConfig["soundname"]].PatternSynth)
            barsynth=soundModels[MyConfig["soundname"]].PatternSynth()

            if MyConfig["paramRange"] == "Norm":
                barsynth.setParamNorm("rate_exp", synthP[0]) # will make 2^1 events per second
                barsynth.setParamNorm("irreg_exp", synthP[1])
                barsynth.setParamNorm("cf_exp", synthP[2])
            else:
                barsynth.setParam("rate_exp", synthP[0]) # will make 2^1 events per second
                barsynth.setParam("irreg_exp", synthP[1])
                barsynth.setParam("cf_exp", synthP[2])

            barsig=barsynth.generate(MyConfig["soundDuration"])
            varDurationSecs=MyConfig["soundDuration"]/MyConfig["numVariations"]  #No need to floor this?

            for v in range(MyConfig["numVariations"]):

                    '''Write wav'''
                    wavName = fileHandle.makeName(MyConfig["soundname"], paramArr, userP, v)
                    wavPath = fileHandle.makeFullPath(MyConfig["outPath"],wavName,".wav")
                    chunkedAudio = SI.selectVariation(barsig, MyConfig["samplerate"], v, varDurationSecs)
                    sf.write(wavPath, chunkedAudio, MyConfig["samplerate"])

                    '''Write params'''
                    paramName = fileHandle.makeName(MyConfig["soundname"], paramArr, userP, v)
                    pfName = fileHandle.makeFullPath(MyConfig["outPath"], paramName,".params")

                    if MyConfig["recordFormat"] == "params" or MyConfig["recordFormat"]==0:
                        pm=paramManager.paramManager(pfName, fileHandle.getFullPath())
                        pm.initParamFiles(overwrite=True)
                        for pnum in range(len(paramArr)):
                                pm.addParam(pfName, paramArr[pnum]['pname'], [0,MyConfig["soundDuration"]], [userP[pnum], userP[pnum]], units=paramArr[pnum]['units'], nvals=paramArr[pnum]['nvals'], minval=paramArr[pnum]['minval'], maxval=paramArr[pnum]['maxval'], origUnits=None, origMinval=barsynth.getParam(paramArr[pnum]['pname']+"_exp", "min"), origMaxval=barsynth.getParam(paramArr[pnum]['pname']+"_exp", "max"))
                                if MyConfig["paramRange"] == "Norm":
                                    synthmin = barsynth.getParam(paramArr[pnum]['pname']+"_exp", "min")
                                    synthmax = barsynth.getParam(paramArr[pnum]['pname']+"_exp", "max")
                                    pm.addMetaParam(pfName, paramArr[pnum]['pname'], 
                                        {
                                        "user": "User maps parameters in Normalized units from 0-1 to " + str(paramArr[pnum]['minval']) + "-" + str(paramArr[pnum]['maxval']), 
                                        "synth": "Synth maps parameters from " + str(paramArr[pnum]['minval']) + "-" + str(paramArr[pnum]['maxval']) + " to " + str(synthmin + paramArr[pnum]['minval']*(synthmax-synthmin)) + "-" + str(synthmin + paramArr[pnum]['maxval']*(synthmax-synthmin))
                                        })
                                    # pm.addMetaParam(pfName, paramArr[pnum]['pname']+"_synth", "Synth parameters in Normalized units from " + str(paramArr[pnum]['minval']) + " to " + str(paramArr[pnum]['maxval']))
                                else:
                                    pm.addMetaParam(pfName, paramArr[pnum]['pname'], {"user": "User maps " + MyConfig["paramRange"] + " units from " + str(paramArr[pnum]['minval']) + "->" + str(paramArr[pnum]['maxval']), "synth": "Synth maps in " + MyConfig["paramRange"] + " units from " + str(paramArr[pnum]['minval']) + "->" + str(paramArr[pnum]['maxval'])})
                                    # pm.addMetaParam(pfName, paramArr[pnum]['pname']+"_user", "User parameters in " + paramRange + " units from " + paramArr[pnum]['minval'] + " to " + paramArr[pnum]['maxval'])
                                    # pm.addMetaParam(pfName, paramArr[pnum]['pname']+"_synth", "Synth parameters in " + paramRange + " units from " + barsynth.getParam(paramArr[pnum]['pname']+"_exp", "min") + " to " + barsynth.getParam(paramArr[pnum]['pname']+"_exp", "max"))

                    elif MyConfig["recordFormat"] == "sonyGan" or MyConfig["recordFormat"] == 1:

                        sg.storeSingleRecord(wavName)
                        for pnum in range(len(paramArr)):
                            sg.addParams(wavName, paramArr[pnum]['pname'], userP[pnum], barsynth.getParam(paramArr[pnum]['pname']+"_exp"))
                        sg.write2File("sonyGan.json")
                    else:
                        print("Tfrecords")
                    '''write TF record'''

            #tfm=tfrecordManager.tfrecordManager(vFilesParam[v], outPath)
            #data,sr = librosa.core.load(outPath + fname + '--v-'+'{:03}'.format(v)+'.wav',sr=16000)
            #print(len(data))
            #tfm.addFeature(vFilesParam[v], 'audio', [0,len(data)], data, units='samples', nvals=len(data), minval=0, maxval=0)
            #for pnum in range(len(paramArr)):
            #   print(pnum)
            #   tfm.addFeature(vFilesParam[v], paramArr[pnum]['pname'], [0,data['soundDuration']], [enumP[pnum], enumP[pnum]], units=paramArr[pnum]['units'], nvals=paramArr[pnum]['nvals'], minval=paramArr[pnum]['minval'], maxval=paramArr[pnum]['maxval'])
            #tfm.writeRecordstoFile()

if __name__ == '__main__':
    main()