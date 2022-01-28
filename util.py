import os

def get_job_tag(inpath: str):
    '''Get the job tag from the input path to the ROOT file.'''
    return os.path.basename(os.path.dirname(inpath))

def get_pretty_plot_tag(dataset: str):
    '''Given the dataset name (short), get the pretty tag to print in the plot.'''
    mapping = {
        'MET' : 'MET 2018A, Run: 315264',
        'EGamma' : 'EGamma 2018D, Run: 324500-324999',
    }
    try:
        return mapping[dataset]
    except KeyError:
        raise ValueError(f'Cannot identify tag for dataset: {dataset}')