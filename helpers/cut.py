import os
import numpy as np

from dataclasses import dataclass

@dataclass
class TwoDimensionalCut():
    '''Implements a two dimensional cut and computes ratio of values falling within a given mask.'''
    xedges: np.ndarray
    yedges: np.ndarray
    values: np.ndarray
    mask_expression: str

    def __post_init__(self) -> None:
        self._get_centers()

    def _get_centers(self) -> None:
        '''Edges to centers.'''
        self.xcenters = 0.5 * (self.xedges[1:] + self.xedges[:-1])
        self.ycenters = 0.5 * (self.yedges[1:] + self.yedges[:-1])

    def return_masked_array(self) -> np.ma.MaskedArray:
        '''Return the masked array.'''
        x, y = np.meshgrid(self.xcenters, self.ycenters)
        mask = eval(self.mask_expression)
        masked_array = np.ma.MaskedArray(self.values, ~mask)
        return masked_array
