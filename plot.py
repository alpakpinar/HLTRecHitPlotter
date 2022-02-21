#!/usr/bin/env python

import os
import re
import sys
import argparse

from helpers.rootfile import RootFile
from helpers.histogram import Histogram, OverlayHistogram

from util import (
    get_job_tag,
    get_pretty_plot_tag
)

from tqdm import tqdm

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('inpath', help='Path to the input ROOT file containing the histograms.')
    parser.add_argument('--dataset', help='The dataset we processed: MET or EGamma.', choices=['MET','EGamma','VBFHinv'])
    parser.add_argument('--distribution', help='Regex specifying the name of distributions we want to plot.', default='.*')
    args = parser.parse_args()
    return args

def get_histograms_for_dataset(dataset):
    '''Get the list of histograms we'll plot for given dataset.'''
    histos = {}
    common_histograms = [
        Histogram('numHFRechits', r'Number of Seed HF RecHits ($E_T > 30 \ GeV$)', 'Counts', ndim=1),
        Histogram('sigmaEtaPhi', r'$\sigma_{\eta \eta}$', r'$\sigma_{\phi \phi}$', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
        Histogram('centralAdjacentStripSize', r'Central $\eta$ Strip Size', r'Adjacent $\eta$ Strip Size', ndim=2),
        Histogram('longFiberEtOverShortFiber', r'Long Fiber $E_{T}$ / Short Fiber $E_{T}$', 'Counts', ndim=1, logscale=True, vmin=1e0, vmax=1e5),
    ]

    vbf_histograms = [
        Histogram('jetPt0', r'Leading Jet $p_T \ (GeV)$', 'Counts', ndim=1),
        Histogram('jetEta0', r'Leading Jet $\eta$', 'Counts', ndim=1),
        Histogram('jetPhi0', r'Leading Jet $\phi$', 'Counts', ndim=1),
        Histogram('jetPt1', r'Trailing Jet $p_T \ (GeV)$', 'Counts', ndim=1),
        Histogram('jetEta1', r'Trailing Jet $\eta$', 'Counts', ndim=1),
        Histogram('jetPhi1', r'Trailing Jet $\phi$', 'Counts', ndim=1),
        Histogram('mjj', r'$m_{jj} \ (GeV)$', 'Counts', ndim=1),
        Histogram('detajj', r'$\Delta \eta_{jj}$', 'Counts', ndim=1),
        Histogram('dphijj', r'$\Delta \phi_{jj}$', 'Counts', ndim=1),
        OverlayHistogram('met', r'$p_T^{miss} \ (GeV)$', 'Counts', root_histo_names=['metPtNotClean', 'metPtClean'], thresh={'distribution': 'MET', 'value': 150}),
    ]
    
    physics_histograms = [
        Histogram('photonPt', r'Photon $p_T \ (GeV)$', 'Counts', ndim=1),
        Histogram('photonEta', r'Photon $\eta$', 'Counts', ndim=1),
        Histogram('photonPhi', r'Photon $\phi$', 'Counts', ndim=1),
        Histogram('dphiJetPho', r'$\Delta\phi(j, \gamma)$', 'Counts', ndim=1),
        Histogram('dptJetPho', r'$\Delta p_T(j, \gamma) \ / \ p_T(j)$', 'Counts', ndim=1),
        Histogram('averageDPhi_centralStripSize', r'Average $\Delta \phi$ From Seed RecHit', r'Central $\eta$ Strip Size', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
    ]

    noise_histograms = [
        Histogram('jetPt', r'Leading Jet $p_T \ (GeV)$', 'Counts', ndim=1),
        Histogram('jetEta', r'Leading Jet $\eta$', 'Counts', ndim=1),
        Histogram('jetPhi', r'Leading Jet $\phi$', 'Counts', ndim=1),
        Histogram('sigmaEtaEta', r'Seed Rechit $\sigma_{\eta \eta}$', 'Counts', ndim=1),
        Histogram('sigmaPhiPhi', r'Seed Rechit $\sigma_{\phi \phi}$', 'Counts', ndim=1),
        Histogram('deltaPhiJetMET', r'$\Delta\phi(jet,MET)$', 'Counts', ndim=1),
        Histogram('averageDPhiFromSeed', r'Average $\Delta \phi$ From Seed RecHit', 'Counts', ndim=1),
        Histogram('deltaEtaRechits', r'$\Delta \eta$ From Seed RecHit', 'Counts', ndim=1),
        Histogram('deltaPhiRechits', r'$\Delta \phi$ From Seed RecHit', 'Counts', ndim=1),
        Histogram('sigmaPhiRechitEnergy', r'$\sigma_{\phi \phi}$', r'Rechit Energy (GeV)', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
        Histogram('sigmaPhiRechitEta', r'$\sigma_{\phi \phi}$', r'Rechit $\eta$', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
        Histogram('sigmaPhiRechitPhi', r'$\sigma_{\phi \phi}$', r'Rechit $\phi$', ndim=2, logscale=True, vmin=1e0, vmax=5e2),
        Histogram('initialRechitEtaPhi', r'Rechit $\eta$', r'Rechit $\phi$', ndim=2, logscale=True, vmin=1e3, vmax=1e7),
        Histogram('mergedRechitEtaPhi', r'Rechit $\eta$', r'Rechit $\phi$', ndim=2, logscale=True, vmin=1e3, vmax=1e7),
        Histogram('initialMergedRechitEnergies', r'Base Rechit Energy (GeV)', r'Merged Rechit Energy (GeV)', ndim=2, logscale=True, vmin=1e0, vmax=1e7),
        OverlayHistogram('met', r'$p_T^{miss} \ (GeV)$', 'Counts', root_histo_names=['metPtNotClean', 'metPtClean'], thresh={'distribution': 'MET', 'value': 100}),
        OverlayHistogram('numRechits', r'Number of Rechits ($E > 1 \ GeV$)', 'Counts', root_histo_names=['numInitialRechits', 'numMergedRechits'], logscale=True, vmin=1e0, vmax=1e6),
        OverlayHistogram('rechitEnergies', r'Rechit Energy (GeV)', 'Counts', root_histo_names=['initialRechitEnergies', 'mergedRechitEnergies'], logscale=True, vmin=1e0, vmax=1e9),
    ]
    
    histos['EGamma'] = common_histograms + physics_histograms
    histos['MET'] = common_histograms + noise_histograms
    histos['VBFHinv'] = common_histograms + vbf_histograms

    return histos[dataset]


def main():
    args = parse_cli()
    inpath = args.inpath
    rf = RootFile(inpath)

    tag = get_job_tag(inpath)
    outdir = f"./output/{tag}"

    assert args.dataset is not None, "Please specify a dataset name: MET or EGamma"

    histograms = get_histograms_for_dataset(args.dataset)

    for hist in tqdm(histograms, desc="Plotting histograms"):
        if not re.match(args.distribution, hist.name):
            continue
        # A single histogram, 1D or 2D
        if isinstance(hist, Histogram):
            try:
                h = rf.get_histogram(hist.name)
            except KeyError:
                continue
            hist.set_histogram_object(h)
            hist.plottag = get_pretty_plot_tag(args.dataset)
            if args.dataset in ['EGamma', 'VBFHinv'] and hist.name in ['sigmaEtaPhi']:
                hist.vmax = 1e2
        
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