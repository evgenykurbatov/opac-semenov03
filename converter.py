# -*- coding: utf-8 -*-

import subprocess
import numpy as np
from numpy import log10
import h5py
import matplotlib as mpl
import matplotlib.pyplot as plt



##
## Parameters
##

raw_inp = \
"""\
%s                      !'model': 'nrm'/'ips'/'irs' silicate types
%s                        !'top': 'c'/'p'/'h' dust topologies,
%s                        !'shape': 's'/'a'/'5' dust shapes,
%s                  !'.true.'/'.false.' - Rosseland/Planck mean op., cm^2/g
   1.000E%0.2d             !'rho': gas density, g/cm^3
 201                     !'N_T': amount of temperature points,
   5.000E+00             !'T_0': initial temperature, K,
   9.999E+03             !'T_1': last temperature, K
"""

model = 'nrm'
#model = 'ips'
#model = 'irs'

#top = 'c'
#top = 'p'
top = 'h'

shape = 's'
#shape = 'a'
# shape = '5'



##
## Run
##

log10rho = np.arange(-18, -6)
num_T = 201

## Rosseland mean
kind, fname = '.true. ', 'kR.out'  ## Rosseland mean
log10kappaR = np.empty((len(log10rho), num_T))
for i in range(len(log10rho)):
    ## Make input file
    with open('opacity.inp', 'w') as f:
        inp = raw_inp % (model, top, shape, kind, log10rho[i])
        f.write(inp)
    ## Run
    print('log10rho =', log10rho[i])
    subprocess.run('./opacity')
    print()
    ## Read opacities
    T, kap = np.loadtxt(fname, unpack=True)
    ## Convert data to 2-D array
    log10T = log10(T)
    log10kappaR[i] = log10(kap)

## Planck mean
kind, fname = '.false.', 'kP.out'  ## Planck mean
log10kappaP = np.empty((len(log10rho), num_T))
for i in range(len(log10rho)):
    ## Make input file
    with open('opacity.inp', 'w') as f:
        inp = raw_inp % (model, top, shape, kind, log10rho[i])
        f.write(inp)
    ## Run
    print('log10rho =', log10rho[i])
    subprocess.run('./opacity')
    print()
    ## Read opacities
    T, kap = np.loadtxt(fname, unpack=True)
    ## Convert data to 2-D array
    log10T = log10(T)
    log10kappaP[i] = log10(kap)

## Write
with h5py.File('semenov03.h5', 'w') as f:
    f.create_dataset('model',    data=model)
    f.create_dataset('top',      data=top)
    f.create_dataset('shape',    data=shape)
    f.create_dataset('log10rho', data=log10rho)
    f.create_dataset('log10T',   data=log10T)
    f.create_dataset('log10kappaR', data=log10kappaR)
    f.create_dataset('log10kappaP', data=log10kappaP)



##
## Plot
##

import matplotlib as mpl
import matplotlib.pyplot as plt

fig, ax = plt.subplots(nrows=1, ncols=2)

ax_ = ax[0]
ax_.set_title("Rosseland mean opacity")
for i in range(len(log10rho)):
    ax_.loglog(10**log10T, 10**log10kappaR[i], label=(r"$10^{%g}$ cm$^{-3}$" % log10rho[i]))
ax_.legend()
ax_.set_xlabel(r"$T$ [K]")
ax_.set_ylabel(r"$\kappa_\mathrm{R}$ [cm$^2/$g]")

ax_ = ax[1]
ax_.set_title("Planck mean opacity")
for i in range(len(log10rho)):
    ax_.loglog(10**log10T, 10**log10kappaP[i], label=(r"$10^{%g}$ cm$^{-3}$" % log10rho[i]))
ax_.legend()
ax_.set_xlabel(r"$T$ [K]")
ax_.set_ylabel(r"$\kappa_\mathrm{P}$ [cm$^2/$g]")

plt.tight_layout()
plt.show()
