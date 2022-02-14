#!/usr/bin/env python

import os
import sys
import argparse
import uproot
import numpy as np
import mplhep as hep

from typing import Dict
from tqdm import tqdm
from matplotlib import pyplot as plt

pjoin = os.path.join

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('path1', help='Path to the first file.')
    parser.add_argument('path2', help='Path to the second file.')
    parser.add_argument('--tag', help='Tag for this job.')
    args = parser.parse_args()
    return args

def compare_across_datasets(histos: Dict, outfile: str, normed: bool=True, log_yscale: bool=False):
    fig, ax = plt.subplots()
    for label, h in histos.items():
        if normed:
            values = h.values / np.sum(h.values)
        else:
            values = h.values 
        hep.histplot(values, bins=h.edges, ax=ax, label=label)
    
    ax.set_xlabel(r'Long Fiber $E_{T}$ / Short Fiber $E_{T}$ (per HF cluster)')

    ylabel = 'Normalized Counts' if normed else 'Counts'
    ax.set_ylabel(ylabel)
    ax.legend()

    if log_yscale:
        ax.set_yscale('log')
        ax.set_ylim(1e-5,1e0)

    fig.savefig(outfile)

def main():
    args = parse_cli()
    infiles = args.path1, args.path2
    distributions = ['longFiberEtOverShortFiber', 'longFiberEtOverShortFiberEtaRestricted']

    assert args.tag is not None, "Please specify a tag!"

    outdir = f'./output/comparisons/{args.tag}'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for distribution in tqdm(distributions, desc='Plotting distributions'):
        outpath = pjoin(outdir, f'{distribution}.pdf')
        
        histos = {}
        for fpath in infiles:
            f = uproot.open(fpath)
            label = r'$\gamma$ + jet' if 'EGamma' in fpath else 'Noise Enriched'
            file_keys = f.keys()
            histos[label] = f[file_keys[0]][distribution]

        compare_across_datasets(histos, outfile=outpath, normed=True, log_yscale=False)

if __name__ == '__main__':
    main()