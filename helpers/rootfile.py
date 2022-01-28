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
        self._get_directory()
    
    def _get_directory(self) -> None:
        f = uproot.open(self.inpath)
        # Get the directory key
        keys = [k.decode('utf-8').replace(';1','') for k in f.keys()]
        # There should be exactly one key (representing the EDAnalyzer we ran)
        assert len(keys) == 1, f"Input ROOT file {self.inpath} has more than one directory!"
        self.directory = f[keys[0]]
    
    def get_histogram(self, histname: str):
        '''Retrieve the specified histogram.'''
        return self.directory[histname]