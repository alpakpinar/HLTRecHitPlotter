#!/usr/bin/env python

import os
import re
import sys
import argparse

from util import (
    RootFile, 
    Histogram,
    OverlayHistogram,
    get_job_tag,
    get_pretty_plot_tag
)

from tqdm import tqdm

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('inpath', help='Path to the input ROOT file containing the histograms.')
    parser.add_argument('--dataset', help='The dataset we processed: MET or EGamma.', choices=['MET','EGamma'])
    parser.add_argument('--distribution', help='Regex specifying the name of distributions we want to plot.', default='.*')
    args = parser.parse_args()
    return args

def get_histograms_for_dataset(dataset):
    '''Get the list of histograms we'll plot for given dataset.'''
    histos = {}
    common_histograms = [
        Histogram('jetPt', r'Leading Jet $p_T \ (GeV)$', 'Counts', ndim=1),
        Histogram('jetEta', r'Leading Jet $\eta$', 'Counts', ndim=1),
        Histogram('jetPhi', r'Leading Jet $\phi$', 'Counts', ndim=1),
        Histogram('numHFRechits', r'Number of Seed HF RecHits ($E_T > 30 \ GeV$)', 'Counts', ndim=1),
        Histogram('sigmaEtaPhi', r'$\sigma_{i\eta i\eta}$', r'$\sigma_{i\phi i\phi}$', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
        Histogram('centralAdjacentStripSize', r'Central $\eta$ Strip Size', r'Adjacent $\eta$ Strip Size', ndim=2),
    ]

    physics_histograms = [
        Histogram('photonPt', r'Photon $p_T \ (GeV)$', 'Counts', 1),
        Histogram('photonEta', r'Photon $\eta$', 'Counts', 1),
        Histogram('photonPhi', r'Photon $\phi$', 'Counts', 1),
        Histogram('dphiJetPho', r'$\Delta\phi(j, \gamma)$', 'Counts', 1),
    ]

    noise_histograms = [
        Histogram('deltaPhiJetMET', r'$\Delta\phi(jet,MET)$', 'Counts', 1),
        Histogram('sigmaPhiRechitEnergy', r'$\sigma_{i\phi i\phi}$', r'Rechit Energy (GeV)', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
        Histogram('sigmaPhiRechitEta', r'$\sigma_{i\phi i\phi}$', r'Rechit $\eta$', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
        Histogram('sigmaPhiRechitPhi', r'$\sigma_{i\phi i\phi}$', r'Rechit $\phi$', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
        OverlayHistogram('met', r'$p_T^{miss} \ (GeV)$', 'Counts', root_histo_names=['metPtNotClean', 'metPtClean']),
    ]
    
    histos['EGamma'] = common_histograms + physics_histograms
    histos['MET'] = common_histograms + noise_histograms

    return histos[dataset]


def main():
    args = parse_cli()
    inpath = args.inpath
    rf = RootFile(inpath)

    tag = get_job_tag(inpath)
    outdir = f"./output/{tag}"

    histograms = get_histograms_for_dataset(args.dataset)

    for hist in tqdm(histograms, desc="Plotting histograms"):
        if not re.match(args.distribution, hist.name):
            continue
        # A single histogram, 1D or 2D
        if isinstance(hist, Histogram):
            h = rf.get_histogram(hist.name)
            hist.set_histogram_object(h)
            hist.plottag = get_pretty_plot_tag(args.dataset)
        
        # Overlayed histograms in a single plot:
        # e.g. Cleaned vs. uncleaned MET
        elif isinstance(hist, OverlayHistogram):
            histo_map = {}
            for hname in hist.root_histo_names:
                histo_map[hname] = rf.get_histogram(hname)
            hist.set_histogram_objects(histo_map)
            hist.plottag = get_pretty_plot_tag(args.dataset)
        
        # The histogram object must be either Histogram or OverlayHistogram
        else:
            raise RuntimeError(f'Could not determine data type for histogram: {hist.name}')

        hist.plot(outdir=outdir)

if __name__ == '__main__':
    main()