# Based on a perl script found on https://renenyffenegger.ch/notes/Wissenschaft/Astronomie/Ephemeriden/JPL-Horizons
# Retrieves vector data of Hubble from JPL's HORIZONS system on https://ssd.jpl.nasa.gov/horizons_batch.cgi (see Web interface on https://ssd.jpl.nasa.gov/horizons.cgi)
# Also helpful: https://github.com/kevin218/POET/blob/master/code/doc/spitzer_Horizons_README.txt

import os
import numpy as np
import urllib.request
from astropy.io import ascii
from tqdm import tqdm
from ..lib import manageevent as me


def run01(eventlabel, workdir, meta=None):

	# read in filelist
	filelist_path = meta.workdir + '/filelist.txt'
	if os.path.exists(filelist_path):
		filelist = ascii.read(filelist_path)

	t_mjd = filelist['t_mjd']
	ivisit = filelist['ivisit']

	# Setting for the JPL Horizons interface
	settings = [
		"COMMAND= -48", #Hubble
		"CENTER= 500@0", #Solar System Barycenter (SSB) [500@0]
		"MAKE_EPHEM= YES",
		"TABLE_TYPE= VECTORS",
		#"START_TIME= $ARGV[0]",
		#"STOP_TIME= $ARGV[1]",
		"STEP_SIZE= 5m", # 5 Minute interval
		"OUT_UNITS= KM-S",
		"REF_PLANE= FRAME",
		"REF_SYSTEM= J2000",
		"VECT_CORR= NONE",
		"VEC_LABELS= YES",
		"VEC_DELTA_T= NO",
		"CSV_FORMAT= NO",
		"OBJ_DATA= YES",
		"VEC_TABLE= 3"]

	#Replacing symbols for URL encoding
	for i, setting in enumerate(settings):
		settings[i] = settings[i].replace(" =", "=").replace("= ", "=")
		settings[i] = settings[i].replace(" ", "%20")
		settings[i] = settings[i].replace("&", "%26")
		settings[i] = settings[i].replace(";", "%3B")
		settings[i] = settings[i].replace("?", "%3F")

	settings = '&'.join(settings)
	settings = 'https://ssd.jpl.nasa.gov/horizons_batch.cgi?batch=1&' + settings

	#save it in ./ancil/bjd_conversion/
	if not os.path.exists(meta.workdir + '/ancil/horizons/'):
		os.makedirs(meta.workdir + '/ancil/horizons/')

	# retrieve positions for every individual visit
	for i in tqdm(range(max(ivisit)+1), desc='Retrieving Horizons file for every visit'):
		t_mjd_visit = t_mjd[np.where(ivisit == i)]
		t_start = min(t_mjd_visit) + 2400000.5 - 1/24 #Start of Horizons file one hour before first exposure in visit
		t_end = max(t_mjd_visit) + 2400000.5 + 1/24 #End of Horizons file one hour after last exposure in visit

		set_start = "START_TIME=JD{0}".format(t_start)
		set_end = "STOP_TIME=JD{0}".format(t_end)

		settings_new = settings + '&' + set_start + '&' + set_end

		#t_start = Time(t_start, format='jd', scale='utc')
		#t_end = Time(t_end, format='jd', scale='utc')
		#print(t_start.isot)

		#os.system('perl ./util/horizons.pl JD{0} JD{1} > ./ancil/bjd_conversion/horizons_results_v{2}.txt'.format(t_start, t_end, i))

		urllib.request.urlretrieve(settings_new, meta.workdir + '/ancil/horizons' + '/horizons_results_v{0}.txt'.format(i))

	# Save results
	print('Saving Metadata')
	me.saveevent(meta, meta.workdir + '/WFC3_' + meta.eventlabel + "_Meta_Save", save=[])

	print('Finished s01 \n')

	return meta
