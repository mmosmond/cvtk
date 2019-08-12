import numpy as np

def reshape_matrix(matrix, R):
    """
    Take a S x L frequency or depth matrix (where S = R x T is the number of
    samples), and the number of replicates, and reshape the frequency matrix
    such that it's a R x T x L tensor.
    """
    # find the indices where the replicate switches -- as evident from checks
    # this relies on replicates and freqs in same order, sorted by replicates!
    return np.stack(np.vsplit(matrix, R))

def flatten_matrix(matrix, R, T, L):
    """
    Flatten a 3D array of shape R x T x L into an (R x T) x L matrix.  This
    relies on the specific way numpy reshapes arrays, specifically that
    *timepoints are nested within replicates*. This makes the process of
    calculating covariances easier, since the temporal covariance sub block
    matrices are all around the diagonal.

    Below is an example demonstrating this is the default np.reshape() behavior.
    If this were to ever change, this could would break.

    TODO: unit test.

    R = 2; T = 3; L = 5
    M = np.stack([np.array([[f"R={r},T={t},L={l}" for l in range(L)] for
                        t in range(T)]) for r in range(R)])

    M.shape
        (2, 3, 5)

    M  # this is the form of the tensor:
    array(
    [[['R=0,T=0,L=0', 'R=0,T=0,L=1', 'R=0,T=0,L=2', 'R=0,T=0,L=3', 'R=0,T=0,L=4'],
        ['R=0,T=1,L=0', 'R=0,T=1,L=1', 'R=0,T=1,L=2', 'R=0,T=1,L=3', 'R=0,T=1,L=4'],
        ['R=0,T=2,L=0', 'R=0,T=2,L=1', 'R=0,T=2,L=2', 'R=0,T=2,L=3', 'R=0,T=2,L=4']],

    [['R=1,T=0,L=0', 'R=1,T=0,L=1', 'R=1,T=0,L=2', 'R=1,T=0,L=3', 'R=1,T=0,L=4'],
        ['R=1,T=1,L=0', 'R=1,T=1,L=1', 'R=1,T=1,L=2', 'R=1,T=1,L=3', 'R=1,T=1,L=4'],
        ['R=1,T=2,L=0', 'R=1,T=2,L=1', 'R=1,T=2,L=2', 'R=1,T=2,L=3', 'R=1,T=2,L=4']]],
        dtype='<U11')

    M.reshape((R*T, L))  # this is the flattened version; note the structure
    # where the timepoints are grouped inside a replicate. This is the
    # appropriate structure for blocked covariance matrix.

    array(
    [['R=0,T=0,L=0', 'R=0,T=0,L=1', 'R=0,T=0,L=2', 'R=0,T=0,L=3', 'R=0,T=0,L=4'],
        ['R=0,T=1,L=0', 'R=0,T=1,L=1', 'R=0,T=1,L=2', 'R=0,T=1,L=3', 'R=0,T=1,L=4'],
        ['R=0,T=2,L=0', 'R=0,T=2,L=1', 'R=0,T=2,L=2', 'R=0,T=2,L=3', 'R=0,T=2,L=4'],

        ['R=1,T=0,L=0', 'R=1,T=0,L=1', 'R=1,T=0,L=2', 'R=1,T=0,L=3', 'R=1,T=0,L=4'],
        ['R=1,T=1,L=0', 'R=1,T=1,L=1', 'R=1,T=1,L=2', 'R=1,T=1,L=3', 'R=1,T=1,L=4'],
        ['R=1,T=2,L=0', 'R=1,T=2,L=1', 'R=1,T=2,L=2', 'R=1,T=2,L=3', 'R=1,T=2,L=4']],
        dtype='<U11')


    """
    assert(matrix.ndim == 3)
    return matrix.reshape((R * T, L))

def swap_alleles(freqs):
    # assumes ngens x nloci
    if freqs.ndim == 3:
        _, ngens, L = freqs.shape
    elif freqs.ndim == 2:
        ngens, L = freqs.shape
    else:
        raise ValueError("frequency matrix must be 2D or 3D")
    flips = np.broadcast_to(np.random.binomial(1, 0.5, L), (ngens, L))
    # flips is broadcast to all timepoints; we just return the loci's
    # flips for the same timepoint since all are identical.
    swap_alleles = flips[0]
    return np.abs(flips - freqs), flips


def sort_samples(samples):
    """
    Sort the samples, ordering and grouping by replicate, then timepoint.
    This returns a tuple, of the ordered samples and then an indexing array
    to rearrange the columns of the input frequency matrix.
    """
    sorted_i = sorted(range(len(samples)),
                      key=lambda i: (samples[i][0], samples[i][1]))
    return [samples[i] for i in sorted_i], sorted_i

