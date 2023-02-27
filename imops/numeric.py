from warnings import warn

import numpy as np

from .backend import BackendLike, resolve_backend
from .src._fast_numeric import (
    _parallel_pointwise_mul as cython_fast_parallel_pointwise_mul,
    _parallel_sum as cython_fast_parallel_sum,
)
from .src._numeric import _parallel_pointwise_mul as cython_parallel_pointwise_mul, _parallel_sum as cython_parallel_sum
from .utils import FAST_MATH_WARNING, normalize_num_threads


def parallel_sum(nums: np.ndarray, num_threads: int = -1, backend: BackendLike = None) -> float:
    """
    Parallel sum of flat numpy array

    Parameters
    ----------
    nums: np.ndarray
        1-dimensional array
    num_threads: int
        the number of threads to use for computation. Default = the cpu count. If negative value passed
        cpu count + num_threads + 1 threads will be used
    backend: BackendLike
        which backend to use. Only `cython` is available

    Returns
    -------
    sum: float

    Examples
    --------
    >>> s = parallel_sum(x, num_threads=1)
    >>> s = parallel_sum(x, num_threads=8, backend=Cython(fast=True))  # ffast-math compiled version
    """
    backend = resolve_backend(backend)
    if backend.name not in ('Cython',):
        raise ValueError(f'Unsupported backend "{backend.name}"')

    num_threads = normalize_num_threads(num_threads, backend)

    if backend.name == 'Cython':
        if backend.fast:
            warn(FAST_MATH_WARNING)
            src_parallel_sum = cython_fast_parallel_sum
        else:
            src_parallel_sum = cython_parallel_sum

    return src_parallel_sum(nums, num_threads)


def parallel_pointwise_mul(
    nums1: np.ndarray, nums2: np.ndarray, num_threads: int = -1, backend: BackendLike = None
) -> np.ndarray:
    """
    Parallel pointwise multiplication of 2 numpy arrays (aka x * y). Works faster only for ndim <= 3.

    Parameters
    ----------
    nums1: np.ndarray
    nums2: np.ndarray
    num_threads: int
        the number of threads to use for computation. Default = the cpu count. If negative value passed
        cpu count + num_threads + 1 threads will be used
    backend: BackendLike
        which backend to use. Only `cython` is available

    Returns
    -------
    multiplied: np.ndarray
        result of nums1 * nums2

    Examples
    --------
    >>> mul = parallel_pointwise_mul(nums1, nums2, num_threads=8)
    >>> mul = parallel_pointwise_mul(np.ones((2, 3)), np.ones((1, 3)))  # broadcasting, mul.shape == (2, 3)
    >>> mul = parallel_pointwise_mul(nums1, nums2, backend=Cython(fast=True))  # ffast-math compiled version
    """
    if not nums1.size and not nums2.size:
        return np.array([], dtype=nums1.dtype)
    if bool(nums1.size) ^ bool(nums2.size):
        raise ValueError('One of the arrays is empty, hence pointwise multiplication cannot be performed.')
    if len(nums1.shape) != len(nums2.shape):
        raise ValueError('Both arrays must have the same number of dimensions for pointwise multiplication.')
    for dim1, dim2 in zip(nums1.shape, nums2.shape):
        if dim1 != dim2 and dim1 != 1 and dim2 != 1:
            raise ValueError(f'Arrays of shapes {nums1.shape} and {nums2.shape} are not broadcastable.')

    if nums1.ndim > 3:
        return nums1 * nums2

    backend = resolve_backend(backend)
    if backend.name not in ('Cython',):
        raise ValueError(f'Unsupported backend "{backend.name}"')

    num_threads = normalize_num_threads(num_threads, backend)

    if backend.name == 'Cython':
        if backend.fast:
            warn(FAST_MATH_WARNING)
            src_parallel_pointwise_mul = cython_fast_parallel_pointwise_mul
        else:
            src_parallel_pointwise_mul = cython_parallel_pointwise_mul

    n_dummy = 3 - nums1.ndim

    if n_dummy:
        nums1 = nums1[(None,) * n_dummy]
        nums2 = nums2[(None,) * n_dummy]

    out = src_parallel_pointwise_mul(nums1, nums2, np.maximum(nums1.shape, nums2.shape), num_threads)

    if n_dummy:
        out = out[(0,) * n_dummy]

    return out
