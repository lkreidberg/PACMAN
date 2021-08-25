import sys, os, time
#sys.path.append('../..')
sys.path.append('/home/zieba/Desktop/Projects/Open_source/wfc-pipeline/')
from importlib import reload

import wfc3_reduction.reduction.s30_run as s30

from wfc3_reduction.lib.reload_meta import reload_meta

eventlabel = 'L-98-59_Hubble15856'

#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-03_12-22-13_L-98-59_Hubble15856/' #[0]
#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-04_03-19-10_L-98-59_Hubble15856/' #[0,2]
#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-04_04-00-53_L-98-59_Hubble15856/' #[all]

#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-09_05-19-56_L-98-59_Hubble15856/' #[0]
#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-09_10-37-26_L-98-59_Hubble15856/' #[0,2]
#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-09_10-57-17_L-98-59_Hubble15856/' #[all]

#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-16_22-31-42_L-98-59_Hubble15856/' #[all] window=10
#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-17_20-54-55_L-98-59_Hubble15856/' #[all] window=5

#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-18_16-35-23_L-98-59_Hubble15856/' #[all], window=10, correct_shift=True
#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-18_16-55-59_L-98-59_Hubble15856/' #[all], window=10, correct_shift=False
#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-18_17-17-28_L-98-59_Hubble15856/' #[3], window=10, correct_shift=False

#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-19_04-31-43_L-98-59_Hubble15856/' #[3], window=10, correct_shift=False, corrected refpix
#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-19_17-10-45_L-98-59_Hubble15856/' #[3], window=10, correct_shift=False, corrected refpix

#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-19_19-22-39_L-98-59_Hubble15856/' #[all], window=10, correct_shift=False, corrected refpix

#workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-21_02-00-29_L-98-59_Hubble15856/' #[all], window=10, correct_shift=True, corrected refpix
workdir = '/home/zieba/Desktop/Projects/Open_source/wfc3-pipeline/run/run_2021-08-21_02-00-29_L-98-59_Hubble15856_spec/' #[all], window=10, correct_shift=True, corrected refpix

reload_meta(eventlabel, workdir)

reload(s30)
s30.run30(eventlabel, workdir)


# 1. run_wfc_3.py
# 2. s30_run.py
# 3. read_data.py
# 4. s30_run.py
# 5. model.py
# 6. functions.py
# 7. s30_run.py
# 8. least_squares.py
# 9. plot_data.py
# 10. mpfit.py 997
# models.py
# constant.py ...
#least_squares.py
#formatter
#plots
## 8. least_squares.py
# 7. s30_run.py