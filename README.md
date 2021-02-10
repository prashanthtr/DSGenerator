# DSGenerator independent of sound models

git clone https://github.com/prashanthtr/DSGenerator

cd DSGenerator/

conda create -n DSGenerator python=3.8 ipykernel

conda activate DSGenerator

python3 -m pip install -r requirements.txt --src '.' (use Python3 command before to ensure version compatability)


# Running DSGenerator

>> python3 generate.py --configfile config_file.json