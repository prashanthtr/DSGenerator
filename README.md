The DSGenerator is data-generation modules in the suit of DSSYnth tools. DSGenerator generates audio and meta-parameter files from custom configuration files.

Within the workflow of data-driven synthesizer design, DSGenerator is used along with DSSYnth collections (e.g., <link to central dssynth collection>). It dynamically loads the DSSynth collection, in context, and through command-line interface  generates audio textures and associated parameter files for a given texture class.

The main aspects of the DSSynth are the *Configuration file*, *Dataset enumerator*, and the *Record generator*.

## Configuration File

The configuration file specifies the DSSynth class, and data labels for sound space (Dataset) generated by DSGenerator.
DSGenerator has a default config file for generating popTextures. The code for popTexutres is available at 
https://github.com/prashanthtr/popTextureDS

### DSSynth class specs

		"soundname": Name of DSSynth class texture (E.g., PopPatternSynth/Engine_0001)
		"samplerate": Sample rate of output audio files (Def. 16000)
		"chunkSecs": Duration of audio files for training (E.g.,2 second)
		"soundDuration": Duration of total sound file (e.g., 4 seconds)
		"recordFormat": Output format for parameter training (e.g., "params", "nsjson", "Tfrecords")

### Datalabels

The different parameters manipulating DSSynth classes provide the labels for sound space.
Interpolation between parameter max and min values specify the granularity of sound space.
The Max and Min values of parameters are described in Normalized(Norm) or Natural(Natural) ranges for interpolation.

**Template for synth parameter(s)**

            "user_pname": User Parameter Name
            "user_minval": Minimum user value for parameter 
            "user_maxval": Maximum user value of parameter
            "user_nvals": Interpolation values
            "user_doc": Freeform mapping expression
            "synth_pname": Synth parameter name
            "synth_minval": Minimum synth value for parameter
            "synth_maxval": Maximum synth value for parameter
            "synth_units": Natural or Normalized units

**Example**

            "user_pname": "Irregularity",
            "user_minval": 0,
            "user_maxval": 1,
            "user_nvals": 4,
            "user_doc": "map to natural synth irregularity param [0, 1]",
            "synth_pname": "irreg_exp",
            "synth_minval": 0,
            "synth_maxval": 1,
            "synth_units": "natural"

## Dataset enumerator 

For each parameter setting, first a "long" signal (of lentgth longDurationSecs) is generated, and then
it is sliced into segments (called variations) of a length desired for training.

Example: If each parameter is sampled at 5 values, the long signal is 10 seconds and variationLength is 2 seconds,
then The the total amount of audio generated is 5*5*5*10= 1250 seconds of sound (about 25 hours; ~3Gb at 16K sr).
If each variation is 2 seconds, then there will be 10/2=5 variations for each parameter setting, and
5*5*5*5 = 625 files.

## Record generator

### ParamManager

### NSJson

### TFRecords


## Installation 

The DSGenerator can be independently installed for development purposes, or installed with DSSynth collections for
dataset generation.

### Independent install 

Clone the github repository:

		> git clone https://github.com/prashanthtr/DSGenerator


### Installation with DSSynth

Add the following line to the requirements of a DSSYnth collection: 

		-e git+https://github.com/prashanthtr/DSGenerator#egg=DSGenerator


## Running DSGenerator

DSGenerator command-line usage for dataset generation 

		> python3 DSGenerator/generate.py --configfile config_file.json --outputpath MyPop

