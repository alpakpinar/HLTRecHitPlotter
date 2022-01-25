#!/usr/bin/env python

import os
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
    args = parser.parse_args()
    return args

def get_histograms_for_dataset(dataset):
    '''Get the list of histograms we'll plot for given dataset.'''
    histos = {}
    common_histograms = [
        Histogram('jetPt', r'Leading Jet $p_T \ (GeV)$', 'Counts', 1),
        Histogram('jetEta', r'Leading Jet $\eta$', 'Counts', 1),
        Histogram('jetPhi', r'Leading Jet $\phi$', 'Counts', 1),
        Histogram('numHFRechits', r'Number of Seed HF RecHits ($E_T > 30 \ GeV$)', 'Counts', 1),
        Histogram('sigmaEtaPhi', r'$\sigma_{i\eta i\eta}$', r'$\sigma_{i\phi i\phi}$', 2, logscale=True, vmin=1e0, vmax=1e2),
        Histogram('centralAdjacentStripSize', r'Central $\eta$ Strip Size', r'Adjacent $\eta$ Strip Size', 2),
    ]

    physics_histograms = [
        Histogram('photonPt', r'Photon $p_T \ (GeV)$', 'Counts', 1),
        Histogram('photonEta', r'Photon $\eta$', 'Counts', 1),
        Histogram('photonPhi', r'Photon $\phi$', 'Counts', 1),
        Histogram('dphiJetPho', r'$\Delta\phi(j, \gamma)$', 'Counts', 1),
    ]

    noise_histograms = [
        Histogram('deltaPhiJetMET', r'$\Delta\phi(jet,MET)$', 'Counts', 1),
        OverlayHistogram('met', ['metPtNotClean', 'metPtClean'], r'$p_T^{miss} \ (GeV)$', 'Counts'),
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
        
        # The histogram object must be either Histogram or OverlayHistogram
        else:
            raise RuntimeError(f'Could not determine data type for histogram: {hist.name}')

        hist.plot(outdir=outdir)

if __name__ == '__main__':
    main()