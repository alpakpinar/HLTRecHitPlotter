import uproot
from dataclasses import dataclass

@dataclass
class RootFile():
    '''
    Object representing a ROOT file.
    Used to read the file and retrieve histograms via get_histogram().
    
    >>> rf = RootFile(<path>)
    >>> hist = rf.get_histogram(<hist_name>)
    '''
    inpath: str
    
    def __post_init__(self) -> None:
        self._index_into_file()
    
    def _index_into_file(self) -> None:
        self.f = uproot.open(self.inpath)
        # Get the directory keys
        self.keys = [k.decode('utf-8').replace(';1','') for k in self.f.keys()]
    
    def get_histogram(self, histname: str):
        '''Retrieve the specified histogram.'''
        for key in self.keys:
            histos_in_dir = [k.decode('utf-8').replace(';1','') for k in self.f[key].keys()]
            if histname in histos_in_dir:
                return self.f[key][histname]
        
        raise KeyError(f'Histogram not found: {histname}')