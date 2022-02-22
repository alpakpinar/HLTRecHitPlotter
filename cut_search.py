#!/usr/bin/env python

import os
import argparse
import uproot
import numpy as np

from matplotlib import pyplot as plt
from tqdm import tqdm

from helpers.cut import TwoDimensionalCut

pjoin = os.path.join

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', help='Path to the two ROOT files we are going to compare.', nargs=2)
    parser.add_argument('--hname', default='sigmaEtaPhi', help='Name of the histogram to look at, default is sigmaEtaPhi.')
    args = parser.parse_args()
    return args

def get_histos(args):
    '''Retrieve the histogram objects.'''
    histos = {}
    for fname in args.files:
        if "MET" in fname:
            tag = 'Noise Enriched'
            analyzer = 'noisyRechitAnalyzer'
        elif "EGamma" in fname:
            tag = 'Physics Enriched'
            analyzer = 'rechitAnalyzer'

        t = uproot.open(fname)[analyzer]
        histos[tag] = t[args.hname]

    return histos

def compute_s_over_b(histos, mask_expression: str):
    '''
    For the given (two) histograms compute S/B after masks are applied.
    Masks are computed from the given "mask_expression"
    S/B = # of Physics Enriched / # of Noise Enriched
    '''
    number_of_events = {}
    eff = {}
    for tag, h in histos.items():
        xedges, yedges = h.edges
        values = h.values.T
        cut = TwoDimensionalCut(
            xedges, yedges, values, mask_expression=mask_expression
        )

        masked_array = cut.return_masked_array()
        number_of_events[tag] = np.sum(masked_array)
        eff[tag] = np.sum(masked_array) / np.sum(values)

    s_over_b = number_of_events['Physics Enriched'] / number_of_events['Noise Enriched']
    return s_over_b, eff['Physics Enriched'], eff['Noise Enriched']

def plot_s_over_b(histos, outdir):
    '''Makes a plot of S/B for different cuts.'''
    s_over_b, noise_rejection, physics_rejection = [], [], []

    exp_base = 'x<'
    thresholds = np.linspace(0.1,0.3,40)

    for thresh in tqdm(thresholds, desc='Computing S/B'):
        exp = f'{exp_base}{thresh}'
        s_over_b_val, physics_eff_val, noise_eff_val = compute_s_over_b(histos, exp)
        s_over_b.append(s_over_b_val)
        noise_rejection.append(1-noise_eff_val)
        physics_rejection.append(1-physics_eff_val)

    fig, ax = plt.subplots()
    ax.scatter(thresholds, s_over_b, label='# Physics / # Noise')
    ax.scatter(thresholds, noise_rejection, label='Noise Rejection')
    ax.scatter(thresholds, physics_rejection, label='Physics Rejection')
    ax.legend(title='Quantity')
    
    xlabel = exp_base.replace('x', r'$\sigma_{\eta\eta}$ ').replace('y', r' $\sigma_{\phi\phi}$ ')
    xlabel += ' X'

    # ax.set_xlabel(r'$\sigma_{\eta\eta} - \sigma_{\phi\phi}$ Threshold', fontsize=14)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel('Quantity', fontsize=14)
    ax.set_ylim(0,1)
    ax.grid(True)

    outpath = pjoin(outdir, 'cut_search.pdf')
    fig.savefig(outpath)
    plt.close(fig)

def main():
    args = parse_cli()
    histos = get_histos(args)

    outdir = './output/cut_search'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    plot_s_over_b(histos, outdir=outdir)

if __name__ == '__main__':
    main()