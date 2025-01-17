import numpy as np
import pickle
from datetime import datetime
from scipy.stats import norm
import dynesty
import inspect
from dynesty import plotting as dyplot
import matplotlib.pyplot as plt
import corner


def name_and_args():
    caller = inspect.stack()[1][0]
    args, _, _, values = inspect.getargvalues(caller)
    return [(i, values[i]) for i in args]

def quantile(x, q):                                                             
        return np.percentile(x, [100. * qi for qi in q]) 

def transform_uniform(x,a,b):
    return a + (b-a)*x

def transform_normal(x,mu,sigma):
    return norm.ppf(x,loc=mu,scale=sigma)

def format_params_for_mcmc(params, meta, fit_par):	#FIXME: make sure this works for cases when nvisit>1
    nvisit = int(meta.nvisit)
    theta = []

    if meta.fit_par_new == False:
        for i in range(len(fit_par)):
                if fit_par['fixed'][i].lower() == "false":
                        if fit_par['tied'][i].lower() == "true": theta.append(params[i*nvisit])
                        else:
                                for j in range(nvisit): theta.append(params[i*nvisit+j])
    else:
        ii = 0
        for i in range(int(len(params)/nvisit)):
                if fit_par['fixed'][ii].lower() == "false":
                        if str(fit_par['tied'][ii]) == "-1":
                            theta.append(params[i*nvisit])
                            ii = ii + 1
                        else:
                            for j in range(nvisit):
                                theta.append(params[i*nvisit+j])
                                ii = ii + 1
                else:
                    ii = ii + 1

    return np.array(theta)



def labels_gen(params, meta, fit_par):
    nvisit = int(meta.nvisit)
    labels = []

    if meta.fit_par_new == False:
        for i in range(len(fit_par)):
                if fit_par['fixed'][i].lower() == "false":
                        if fit_par['tied'][i].lower() == "true": labels.append(fit_par['parameter'][i])
                        else:
                                for j in range(nvisit): labels.append(fit_par['parameter'][i]+str(j))
    else:
        ii = 0
        for i in range(int(len(params)/nvisit)):
                if fit_par['fixed'][ii].lower() == "false":
                        if str(fit_par['tied'][ii]) == "-1":
                            labels.append(fit_par['parameter'][ii])
                            ii = ii + 1
                        else:
                            for j in range(nvisit):
                                labels.append(fit_par['parameter'][ii]+str(j))
                                ii = ii + 1
                else:
                    ii = ii + 1

    #print('labels', labels)
    return labels





def mcmc_output(samples, params, meta, fit_par, data):	#FIXME: make sure this works for cases when nvisit>1
    nvisit = int(meta.nvisit)
    labels = labels_gen(params, meta, fit_par)

    fig = corner.corner(samples, labels=labels, show_titles=True)
    current_time = datetime.now().time()
    figname = "pairs_"+current_time.isoformat()+".png"
    fig.savefig(figname)


def format_params_for_Model(theta, params, meta, fit_par):
    nvisit = int(meta.nvisit)
    params_updated = []
    iter = 0									#this should be a more informative name FIXME
    if meta.fit_par_new == False:
        for i in range(len(fit_par)):
                if fit_par['fixed'][i].lower() == "true":
                        for j in range(nvisit):
                                params_updated.append(params[i*nvisit+j])
                else:
                        if fit_par['tied'][i].lower() == "true":
                                for j in range(nvisit): params_updated.append(theta[iter])
                                iter += 1
                        else:
                                for j in range(nvisit):
                                        params_updated.append(theta[iter])
                                        iter += 1
    else:
        ii = 0
        for i in range(int(len(params)/nvisit)):
                if fit_par['fixed'][ii].lower() == "true":
                        for j in range(nvisit):
                                params_updated.append(params[i*nvisit+j])
                        ii = ii + 1
                else:
                        if str(fit_par['tied'][ii]) == "-1":
                                for j in range(nvisit): params_updated.append(theta[iter])
                                iter += 1
                                ii = ii + 1
                        else:
                                for j in range(nvisit):
                                        params_updated.append(theta[iter])
                                        iter += 1
                                        ii = ii + 1

    return np.array(params_updated)

def nested_sample(data, model, params, file_name, meta, fit_par):
    x = format_params_for_mcmc(params, meta, fit_par)

    ndim = len(x) 

    l_args = [params, data, model, meta, fit_par]
    p_args = [data]
    
    #dsampler = dynesty.DynamicNestedSampler(loglike, ptform, ndim,
    #                                        logl_args = l_args,
    #                                       ptform_args = p_args,
    #                                        update_interval=float(ndim))
    #dsampler.run_nested(wt_kwargs={'pfrac': 1.0})#, maxiter = 20000)
    #results = dsampler.results

    sampler = dynesty.NestedSampler(loglike, ptform, ndim, logl_args = l_args,ptform_args = p_args,update_interval=float(ndim), nlive=meta.run_nlive)
    sampler.run_nested(dlogz=meta.run_dlogz)
    results = sampler.results

    pickle.dump(results, open( "nested_results.p", "wb" ) )
    results.summary()

    labels = labels_gen(params, meta, fit_par)


    # Plot a summary of the run.
    #rfig, raxes = dyplot.runplot(results)
    #plt.savefig(meta.workdir + meta.fitdir + '/nested_runplot_' + meta.fittime + '.png')
    # Plot traces and 1-D marginalized posteriors.
    #tfig, taxes = dyplot.traceplot(results)
    #plt.savefig(meta.workdir + meta.fitdir + '/nested_traceplot_' + meta.fittime + '.png')
    # Plot the 2-D marginalized posteriors.
    cfig, caxes = dyplot.cornerplot(results, show_titles=True, title_fmt='.4',labels=labels, color='blue', hist_kwargs=dict(facecolor='blue', edgecolor='blue'))
    plt.savefig(meta.workdir + meta.fitdir + '/nested_cornerplot_' + meta.fittime + '.png')
    #plt.show()


    return 0.


def ptform(u, data):
    p = np.zeros_like(u) 
    n = len(data.prior)
    for i in range(n):
        if data.prior[i][0] == 'U':  p[i] = transform_uniform(u[i], 
                                            data.prior[i][1],data.prior[i][2])
        if data.prior[i][0] == 'N':  p[i] = transform_normal(u[i], 
                                            data.prior[i][1],data.prior[i][2])
    return p
    


def loglike(x, params, data, model, meta, fit_par):
    updated_params = format_params_for_Model(x, params, meta, fit_par)
    fit = model.fit(data, updated_params)
    return fit.ln_like 
