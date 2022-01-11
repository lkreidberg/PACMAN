import numpy as np
from astropy.io import ascii, fits
import math
import numpy as np
from importlib import reload
import multiprocessing as mp
import os
from tqdm import tqdm
import numpy.ma as ma
from astropy.io import ascii


#s00
def readfiles(meta):
    """
    Reads in the files saved in topdir + datadir and saves them into a list

    Parameters
    -----------
    meta
        metadata object

    Returns
    ----------
    meta
        metadata object but adds segment_list to metadata containing the sorted data fits files

    Revisions
    ----------
    Written by Sebastian Zieba      December 2021

    """
    meta.segment_list = []
    for fname in os.listdir(str(meta.path)):
        if fname.endswith(meta.suffix + '.fits'):
            meta.segment_list.append(str(meta.path) +'/'+ fname)
    return meta



#s02

def ancil(meta, s10=False, s20=False):
    """
    This function loads in a lot of useful arrays and values into meta

    The following additional information are being loading into meta:

    - **norbit:**   number of orbits
    - **nvisit:**   number of visits
    - **files_sp:** all spectra files
    - **files_di:** all direct image files
    - **ra:** RA of the target in radians (from the header) (Note: this data is taken from the first spectrum file)
    - **dec:** DEC of the target in radians (from the header) (Note: this data is taken from the first spectrum file)
    - **coordtable:** a list of files containing the vector information of HST downloaded in s01


    Parameters
    -----------
    meta
        metadata object
    s10: bool
        Is set to True when s10 is being performed
    s20: bool
        Is set to True when s20 is being performed

    Returns
    ----------
    meta
        metadata object

    Revisions
    ----------
    Written by Sebastian Zieba      December 2021
    """

    filelist = ascii.read(meta.workdir + '/filelist.txt')

    aa = filelist['iorbit'].data
    bb = np.diff(aa)
    meta.norbit, meta.nvisit = len(np.insert(aa[1:][np.where(bb != 0)], 0, aa[0])), len(set(filelist['ivisit'].data))

    meta.mask_sp = np.array([i[0] for i in filelist['filter/grism']]) == 'G'
    meta.mask_di = np.array([i[0] for i in filelist['filter/grism']]) == 'F'
    meta.files_sp = [meta.path + '/' + i for i in filelist['filenames'][meta.mask_sp].data]
    meta.files_di = [meta.path + '/' + i for i in filelist['filenames'][meta.mask_di].data]

    f = fits.open(meta.files_sp[0])

    meta.ra = f[0].header['ra_targ'] * math.pi / 180.0  # stores right ascension
    meta.dec = f[0].header['dec_targ'] * math.pi / 180.0  # stores declination

    meta.coordtable = []  # table of spacecraft coordinates
    for i in range(max(filelist['ivisit']) + 1): meta.coordtable.append(
        meta.workdir + '/ancil/horizons/' + "/horizons_results_v" + str(i) + ".txt")

    ###
    # 03
    # FIXME SZ Should make sure all visits use the same grism. Not only the very first observation
    meta.filter = filelist['filter/grism'][meta.mask_di][0]
    meta.grism = filelist['filter/grism'][meta.mask_sp][0]

    meta.scans_sp = filelist['scan'][meta.mask_sp].data
    meta.iorbit_sp = filelist['iorbit'][meta.mask_sp].data
    meta.ivisit_sp = filelist['ivisit'][meta.mask_sp].data

    # the following lists store the indices of spectral files where the orbit/visit increases
    meta.new_orbit_idx_sp = np.concatenate(([0], np.where(np.diff(meta.iorbit_sp)!=0)[0]+1))
    meta.new_visit_idx_sp = np.concatenate(([0], np.where(np.diff(meta.ivisit_sp)!=0)[0]+1))

    # the following list stores the cumulative orbit number
    meta.iorbit_sp_cumulative = np.zeros(len(meta.iorbit_sp), dtype=int)
    c = 0
    for i in range(len(meta.iorbit_sp) - 1):
        if meta.iorbit_sp[i + 1] != meta.iorbit_sp[i]:
            c = c + 1
        meta.iorbit_sp_cumulative[i + 1] = c

    meta.iorbit_di = filelist['iorbit'][meta.mask_di].data
    meta.ivisit_di = filelist['ivisit'][meta.mask_di].data
    meta.t_mjd_sp = filelist['t_mjd'][meta.mask_sp].data

    meta.t_orbit_sp = filelist['t_orbit'][meta.mask_sp].data
    meta.t_visit_sp = filelist['t_visit'][meta.mask_sp].data

    meta.platescale = 0.13  # IR detector has plate scale of 0.13 arcsec/pixel

    meta.POSTARG1 = f[0].header['POSTARG1']  # x-coordinate of the observer requested target offset
    meta.POSTARG2 = f[0].header['POSTARG2']  # y-coordinate of the observer requested target offset
    meta.LTV1 = int(f[1].header['LTV1'])     # X offset to get into physical pixels
    meta.LTV2 = int(f[1].header['LTV2'])     # Y offset to get into physical pixels

    meta.subarray_size = f[1].header['SIZAXIS1']  # size of subarray

    if meta.grism == 'G102':
        meta.BEAMA_i = 41
        meta.BEAMA_f = 248
    elif meta.grism == 'G141':
        meta.BEAMA_i = 15
        meta.BEAMA_f = 196


    if s10:
        if 't_bjd' in filelist.keys():
            meta.t_bjd_sp = filelist['t_bjd'][meta.mask_sp].data
        if 't_bjd' in filelist.keys():
            meta.t_bjd_di = filelist['t_bjd'][meta.mask_di].data

    if s20:
        meta.refpix = np.genfromtxt(meta.workdir + "/xrefyref.txt")
        # meta.refpix = ascii.read(meta.workdir + "/xrefyref.txt") # reads in reference pixels
        # # TODO Fix the possibility of two DIs in an orbit or only one DI per visit
        # meta.refpix = ascii.read(meta.workdir + "/xrefyref.txt")
        # refpix_orbit_rows = np.zeros(meta.norbit)
        # refpix_orbit_cols = np.zeros(meta.norbit)
        # for i in range(meta.norbit):
        #     refpix_orbit_rows[i] = meta.refpix['x_pos'][i]
        #     refpix_orbit_cols[i] = meta.refpix['y_pos'][i]


        #idx = np.argsort(refpix[:, 0])  # sort by time
        #meta.refpix = refpix[idx]  # reference pixels from direct image

    return meta










def computeRMS(data, maxnbins=None, binstep=1, isrmserr=False):
    # bin data into multiple bin sizes
    npts    = data.size
    if maxnbins == None:
            maxnbins = npts/10.
    binsz   = np.arange(1, maxnbins+binstep, step=binstep)
    nbins   = np.zeros(binsz.size)
    rms     = np.zeros(binsz.size)
    rmserr  = np.zeros(binsz.size)
    for i in range(binsz.size):
            nbins[i] = int(np.floor(data.size/binsz[i]))
            bindata   = np.zeros(nbins[i], dtype=float)
# bin data
# ADDED INTEGER CONVERSION, mh 01/21/12
            for j in range(int(nbins[i])):
                    bindata[j] = data[j*binsz[i]:(j+1)*binsz[i]].mean()
            # get rms
            rms[i]    = np.sqrt(np.mean(bindata**2))
            rmserr[i] = rms[i]/np.sqrt(2.*int(nbins[i]))
    # expected for white noise (WINN 2008, PONT 2006)
    stderr = (data.std()/np.sqrt(binsz))*np.sqrt(nbins/(nbins - 1.))
    if isrmserr == True:
            return rms, stderr, binsz, rmserr
    else:
            return rms, stderr, binsz


def quantile(x, q):
    return np.percentile(x, [100. * qi for qi in q])

def weighted_mean(data, err):            #calculates the weighted mean for data points data with std devs. err
    ind = err != 0.0
    weights = 1.0/err[ind]**2
    mu = np.sum(data[ind]*weights)/np.sum(weights)
    var = 1.0/np.sum(weights)
    return [mu, np.sqrt(var)]                







def get_wave_grid(meta):

    if meta.grism == 'G102':
        from ..lib import geometry102 as geo
    elif meta.grism == 'G141':
        from ..lib import geometry as geo
    else:
        print('Error: GRISM in obs_par.cf is neither G102 nor G141!')

    wave_grid = np.empty((meta.norbit*meta.nvisit, meta.subarray_size, meta.subarray_size))

    #calculates wavelength solution row by row for each orbit
    for i in range(meta.norbit):
        for j in range(meta.subarray_size):
            disp_solution = geo.dispersion(meta.refpix[i,1], -meta.LTV2+j)
            delx = 0.5 + np.arange(meta.subarray_size) - (meta.refpix[i,2] + meta.LTV1 + meta.POSTARG1/meta.platescale)
            wave_grid[i, j, :] = disp_solution[0] + delx*disp_solution[1]

    return wave_grid


def get_flatfield(meta):                    #function that flatfields a data array D, which starts at [minr, cmin] of hdu[1].data
    flat = fits.open(meta.flat)                #reads in flatfield cube
    WMIN = flat[0].header['WMIN']                #constants for computing flatfield coefficients
    WMAX = flat[0].header['WMAX']

    a0 = flat[0].data[-meta.LTV1:-meta.LTV1+meta.subarray_size, -meta.LTV2:-meta.LTV2+meta.subarray_size]
    a1 = flat[1].data[-meta.LTV1:-meta.LTV1+meta.subarray_size, -meta.LTV2:-meta.LTV2+meta.subarray_size]
    a2 = flat[2].data[-meta.LTV1:-meta.LTV1+meta.subarray_size, -meta.LTV2:-meta.LTV2+meta.subarray_size]

    flatfield = []
    for i in range(meta.norbit*meta.nvisit):
        wave = meta.wave_grid[i, :]
        x = (wave - WMIN)/(WMAX-WMIN)
        flatfield.append(a0+a1*x+a2*x**2)
        flatfield[i][flatfield[i] < 0.5] = -1.        #sets flatfield pixels below 0.5 to -1 so they can be masked
    return flatfield







def median_abs_dev(vec):
    med = ma.median(vec)
    return ma.median(abs(vec - med))















def residuals(params, template_waves, template, spectrum, error):
    shift, scale = params
    fit = scale*np.interp(template_waves, template_waves-shift, spectrum)
    x = (template-fit)/error
    return (template-fit)/error

from scipy.interpolate import interp1d

def residuals2(params, x1, y1, x2, y2):
    a, b, c = params
    x1=np.array(x1)
    x2=np.array(x2)
    y1=np.array(y1)
    y2=np.array(y2)

    f = interp1d(x1, y1, kind='cubic')
    fit = f(a+b*x2)*c

    return fit - y2

def interpolate_spectrum(spectrum, error, template, template_waves):
    p0 = [1., 1.0]                                        #initial guess for parameters shift and scale
    plsq, success  = leastsq(residuals, p0, args=(template_waves, template, spectrum, error))
    shift, scale = plsq
    interp_spectrum = np.interp(template_waves, template_waves-shift, spectrum)
    interp_error = np.interp(template_waves, template_waves-shift, error)
    return [interp_spectrum, interp_error, shift]

# def read_dict(filename):
#     #with open(filename,"r") as text:
#     #    return dict(line.strip().split() for line in text)
#     dict = {}
#     with open(filename,"r") as text:
#         for line in text:
#             key, value = line.split()
#             value = str_to_num(value)
#             if value == 'True': value = True
#             if value == 'False': value = False
#             dict[key] = value
#     return dict



#def getphase(t):
#    phase = (t - t0)/period
#    return phase - int(phase)








