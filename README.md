## Setup
```
conda create --name geca python=3.9
conda activate geca
cd geca-master
pip install -r requirements.txt
cd exp
```

**Run the `context=2` to see if it works!**
Only two babylm data files "aochildes" and "switchboard" are added in the sh files.
```
sh run_test.sh
```
If it works, there are augmented `.train` in folder `augment_context2` and output files in `context2`. (it takes < 1 min)

Then... try `context=3` and `context=1`... hopefully they will work
```
sh run_context1.sh
sh run_context3.sh
```

Notes: 
* I turned off GPU usage in `compose.py` and `flags.py`, can turn GPU back on maybe?
* The output/error files are in  `context1`/`context2`/`context3` folders for debugging and checking errors.