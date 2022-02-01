import os
import re
import matplotlib.colors
import numpy as np
import mplhep as hep

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from matplotlib import pyplot as plt

@dataclass
class HistogramBase():
    '''
    Base object for a histogram.
    '''
    name: str
    xlabel: str
    ylabel: str
    fontsize: int=14
    plottag: Optional[str]=None

    def _save_fig(self, fig: plt.figure, path: str) -> None:
        outdir = os.path.dirname(path)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        fig.savefig(path)

    def _decorate_plot(self, ax: plt.axis) -> None:
        dataset, run = self.plottag.split(', ')
        ax.text(0,1,dataset,
            fontsize=self.fontsize,
            ha='left',
            va='bottom',
            transform=ax.transAxes
        )
        ax.text(1,1,run,
            fontsize=self.fontsize,
            ha='right',
            va='bottom',
            transform=ax.transAxes
        )


@dataclass
class Histogram(HistogramBase):
    '''
    Simple 1D or 2D histogram class.
    Initialize the instance with name and labels, attach it to an uproot histogram and plot.
    >>> h = Histogram(<name>, <xlabel>, <ylabel>, <ndim>)
    >>> h.set_histogram_object(<uproot_histo>)
    >>> h.plot(outdir=<output_path>)
    '''
    ndim: int=1
    logscale: bool=False
    vmin: Optional[float]=None
    vmax: Optional[float]=None

    def __post_init__(self) -> None:
        assert self.ndim in (1,2), f"Number of dimensions not accepted: {self.ndim}"

    def set_histogram_object(self, h_obj) -> None:
        '''Matches the uproot histogram object with the instance of the Histogram class.'''
        self.h_obj = h_obj
        
    def _plot1d(self, outdir: str) -> None:
        '''Plot 1-dimensional histogram object.'''
        fig, ax = plt.subplots()
        hep.histplot(self.h_obj.values, self.h_obj.edges, ax=ax)
        ax.set_xlabel(self.xlabel, fontsize=self.fontsize)
        ax.set_ylabel(self.ylabel, fontsize=self.fontsize)
        
        if self.plottag:
            self._decorate_plot(ax)
        
        self._save_fig(fig=fig, path=os.path.join(outdir, f"{self.name}.pdf"))

    def _plot2d(self, outdir: str, normed: bool=False) -> None:
        '''Plot 2-dimensional histogram object.'''
        fig, ax = plt.subplots()
        vals = self.h_obj.values.T
        if normed:
            vals /= np.sum(vals)
        
        patch_opts = {}
        if self.logscale:
            patch_opts['norm'] = matplotlib.colors.LogNorm(self.vmin,self.vmax)

        pc = ax.pcolormesh(self.h_obj.edges[0], self.h_obj.edges[1], vals, **patch_opts)
        cb = fig.colorbar(pc)
        cb.set_label("Counts")

        if self.name in ['centralAdjacentStripSize']:
            xedges = self.h_obj.edges[0]
            xcenters = 0.5 * (xedges[:-1] + xedges[1:])
            yedges = self.h_obj.edges[1]
            ycenters = 0.5 * (yedges[:-1] + yedges[1:])
            for ix, xcenter in enumerate(xcenters):
                for iy, ycenter in enumerate(ycenters):
                    opts = {
                        "horizontalalignment": "center",
                        "verticalalignment": "center",
                    }
                    opts["color"] = (
                        "black" if pc.norm(vals[iy, ix]) > 0.5 else "lightgrey"
                    )
                    txtformat = opts.pop("format", r"%.2f")
                    ax.text(xcenter, ycenter, txtformat % vals[iy, ix], **opts)

        # Sigma eta-phi plot: Plot the diagonal cut that we apply
        elif re.match('.*sigmaEtaPhi.*', self.name):
            xs = ax.get_xlim()
            ys = (xs[0]-0.05, xs[1]-0.05)
            ax.plot(xs, ys, color='red', lw=3)
            ax.set_ylim(0,0.2)
        
        ax.set_xlabel(self.xlabel, fontsize=self.fontsize)
        ax.set_ylabel(self.ylabel, fontsize=self.fontsize)
        
        if self.plottag:
            self._decorate_plot(ax)

        self._save_fig(fig=fig, path=os.path.join(outdir, f"{self.name}.pdf"))

    def plot(self, outdir: str) -> None:
        if self.ndim == 1:
            return self._plot1d(outdir=outdir)
        return self._plot2d(outdir=outdir, 
            normed='StripSize' in self.name
            )

@dataclass
class OverlayHistogram(HistogramBase):
    '''Object to store and plot overlayed 1D histograms on a single plot.'''
    root_histo_names: List[str] = field(default_factory=list)
    
    # thresh: Dictionary specifying a distribution and threshold value
    # e.g.
    # thresh: {
    #   "distribution" : "met",
    #   "value" : 100
    # }
    thresh: Optional[Dict] = None

    def set_histogram_objects(self, histo_map) -> None:
        self.histo_map = histo_map

    def compute_ratio(self, histo, thresh: float) -> float:
        vals = histo.values
        centers = 0.5 * (histo.edges[1:] + histo.edges[:-1])
        mask = centers < thresh
        
        ratio = np.sum(vals[mask]) / np.sum(vals) * 100
        return ratio

    def plot(self, outdir: str) -> None:
        fig, ax = plt.subplots()
        ratios = []
        for label, h in self.histo_map.items():
            hep.histplot(h.values, h.edges, ax=ax, label=label)
            if self.thresh is not None:
                r = self.compute_ratio(h, thresh=self.thresh['value'])
                if r > 0:
                    ratios.append( r )
        
        ax.set_xlabel(self.xlabel, fontsize=self.fontsize)
        ax.set_ylabel(self.ylabel, fontsize=self.fontsize)
        ax.legend()

        if len(ratios) > 0 and self.thresh is not None:
            r = ratios[0]
            ax.text(0.99, 0.7,f'% of events with \n ${self.thresh["distribution"]} < {self.thresh["value"]} \\ GeV: {r:.2f}\\%$', 
                fontsize=self.fontsize,
                ha='right',
                va='bottom',
                transform=ax.transAxes
                )

        if self.plottag:
            self._decorate_plot(ax)
        
        self._save_fig(fig=fig, path=os.path.join(outdir, f"{self.name}.pdf"))