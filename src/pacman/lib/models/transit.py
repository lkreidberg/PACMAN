import batman

def transit(t, data, params, visit = 0):
    p = batman.TransitParams()

    t0, per, rp, a, inc, ecc, w, u1, u2, limb_dark = params
    if limb_dark[visit] == 2: p.limb_dark = "quadratic"
    else: 
        print("unsupported limb darkening parameter")
        return 0

    p.t0 = t0[visit] + data.toffset
    p.per = per[visit]
    p.rp = rp[visit]
    p.a = a[visit]
    p.inc = inc[visit]
    p.ecc = ecc[visit]
    p.w = w[visit]
    p.u = [u1[visit], u2[visit]]

    m = batman.TransitModel(
    p, t, supersample_factor=3, exp_time = data.exp_time/24./60./60.
    )
    return m.light_curve(p)
