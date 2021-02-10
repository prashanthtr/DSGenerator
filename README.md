# DSGenerator independent of sound models

git clone https://github.com/prashanthtr/DSGenerator

cd DSGenerator/

conda create -n DSGenerator python=3.8 ipykernel

conda activate DSGenerator

python3 -m pip install -r requirements.txt --src '.' (use Python3 command before to ensure version compatability)


# Running DSGenerator

>> python3 generate.py --configfile config_file.json


# WRITEUP

'''
This code will generate a dataset of textures consiting of pop or drip textures. 

The files are generated using 3 (or N) different parameters that are sampled over a range of values. The parameters that are 
developed for the sound model are exposed via the config_file.json. The three parameters for a range of sounds
including the pop and drip textures are:
    rate (average events per second),
    irregularity in temporal distribution (using a gaussian distribution around each evenly-spaced time value), and
    the center frequency of bp filter

The generator.py to be independent of any synth, and dependent only on the config file. That is, the same generator.py should work for all DSSynths.
    a) It can get the synth name from the config file, and then import it "dynamically"
    b) It can set any params the user wants to fix (not iterate over)
    c) names in the config file should correspond to names in the synth (right now the generator constructs synth param names from those use in the cofig file by adding "_exp", etc.

There is also a "visualizer" notebook need not generate files at all. The function of the visualizer is to 
interactively explore and create textures using synthinterface and sound models.
It is mostly for understanding the synthesizer, and exploring parameters that you might help you decide how 
you want to specify them in your config file.

The parameter values are each sampled liniearly on an exponential scale, and specified in:
rate = 2^r_exp  (so r_exp in [0,4] means the rate ranges from 2 to 16)
irregularity = .04*10^irreg_exp; sd = irregularity/events per second  (so irreg_exp in [0,1] means irregularity ranges from completely regular, to Poisson process)
cf = 440*2^cf_exp  (so cf_exp in [0,1] means cf ranges from 440 to 880, one octave)

Generator use:
For each parameter setting, first a "long" signal (of lentgth longDurationSecs) is generated, and then
it is sliced into segments (called variations) of a length desired for training.

Example: If each parameter is sampled at 5 values, the long signal is 10 seconds and variationLength is 2 seconds,
then The the total amount of audio generated is 5*5*5*10= 1250 seconds of sound (about 25 hours; ~3Gb at 16K sr).
If each variation is 2 seconds, then there will be 10/2=5 variations for each parameter setting, and
5*5*5*5 = 625 files
'''
