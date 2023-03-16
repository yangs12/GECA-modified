## Setup
```
conda create --name geca python=3.9
conda activate geca
pip install -r requirements.txt
cd exp
```

Run the config `context=2` to see if it works! :) 
Only two babylm data files "aochildes" and "switchboard" are added in the sh files.
```
sh run_test.sh
```
If it works, there are augmented `.train` files in folder `augment_context2` and output files in folder `context2`. 


Then... try `context=3` and `context=1`... hopefully they will work!!
```
sh run_context1.sh
sh run_context3.sh
```

Notes: 
* I turned off GPU usage in `compose.py` and `flags.py`, can turn GPU back on maybe?
* The output/error files are in  `context1`/`context2`/`context3` folders for debugging and checking errors.
