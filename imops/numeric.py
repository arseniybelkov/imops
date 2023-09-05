from typing import Callable, Union

import numpy as np

from .backend import BackendLike, resolve_backend
from .src._fast_numeric import (
    _pointwise_add_array_3d as cython_fast_pointwise_add_array_3d,
    _pointwise_add_array_3d_fp16 as cython_fast_pointwise_add_array_3d_fp16,
    _pointwise_add_array_4d as cython_fast_pointwise_add_array_4d,
    _pointwise_add_array_4d_fp16 as cython_fast_pointwise_add_array_4d_fp16,
    _pointwise_add_value_3d as cython_fast_pointwise_add_value_3d,
    _pointwise_add_value_3d_fp16 as cython_fast_pointwise_add_value_3d_fp16,
    _pointwise_add_value_4d as cython_fast_pointwise_add_value_4d,
    _pointwise_add_value_4d_fp16 as cython_fast_pointwise_add_value_4d_fp16,
)
from .src._numeric import (
    _pointwise_add_array_3d as cython_pointwise_add_array_3d,
    _pointwise_add_array_3d_fp16 as cython_pointwise_add_array_3d_fp16,
    _pointwise_add_array_4d as cython_pointwise_add_array_4d,
    _pointwise_add_array_4d_fp16 as cython_pointwise_add_array_4d_fp16,
    _pointwise_add_value_3d as cython_pointwise_add_value_3d,
    _pointwise_add_value_3d_fp16 as cython_pointwise_add_value_3d_fp16,
    _pointwise_add_value_4d as cython_pointwise_add_value_4d,
    _pointwise_add_value_4d_fp16 as cython_pointwise_add_value_4d_fp16,
)
from .utils import normalize_num_threads


TYPES = (np.int16, np.int32, np.int64, np.float16, np.float32, np.float64)
STR_TYPES = ('int16', 'int32', 'int64', 'float16', 'float32', 'float64')


# TODO: maybe dict is better?
def _choose_cython_pointwise_add(ndim: int, summand_is_array: bool, is_fp16: bool, fast: bool) -> Callable:
    assert ndim <= 4, ndim

    if ndim <= 3:
        if summand_is_array:
            if is_fp16:
                return cython_fast_pointwise_add_array_3d_fp16 if fast else cython_pointwise_add_array_3d_fp16

            return cython_fast_pointwise_add_array_3d if fast else cython_pointwise_add_array_3d

        if is_fp16:
            return cython_fast_pointwise_add_value_3d_fp16 if fast else cython_pointwise_add_value_3d_fp16

        return cython_fast_pointwise_add_value_3d if fast else cython_pointwise_add_value_3d

    if summand_is_array:
        if is_fp16:
            return cython_fast_pointwise_add_array_4d_fp16 if fast else cython_pointwise_add_array_4d_fp16

        return cython_fast_pointwise_add_array_4d if fast else cython_pointwise_add_array_4d

    if is_fp16:
        return cython_fast_pointwise_add_value_4d_fp16 if fast else cython_pointwise_add_value_4d_fp16

    return cython_fast_pointwise_add_value_4d if fast else cython_pointwise_add_value_4d


def pointwise_add(
    nums: np.ndarray,
    summand: Union[np.array, float],
    output: np.ndarray = None,
    num_threads: int = -1,
    backend: BackendLike = None,
) -> np.ndarray:
    backend = resolve_backend(backend)
    if backend.name not in ('Scipy', 'Cython'):
        raise ValueError(f'Unsupported backend "{backend.name}".')

    ndim = nums.ndim
    dtype = nums.dtype
    is_fp16 = dtype == np.float16

    if dtype not in TYPES:
        raise ValueError(f'Input array dtype must be one of {", ".join(STR_TYPES)}, got {dtype}.')

    if output is None:
        output = np.empty_like(nums, dtype=dtype)
    elif output.shape != nums.shape:
        raise ValueError('Input array and output array shapes must be the same.')
    elif dtype != output.dtype:
        raise ValueError('Input array and output array dtypes must be the same.')

    summand_is_array = isinstance(summand, np.ndarray)
    if summand_is_array:
        if dtype != summand.dtype:
            raise ValueError(f'Input and summand arrays must have same dtypes, got {dtype} vs {summand.dtype}.')
    elif not isinstance(summand, (*TYPES, *(int, float))):
        raise ValueError(f'Summand dtype must be one of {", ".join(STR_TYPES)}, got {type(summand)}.')
    else:
        summand = nums.dtype.type(summand)

    if backend.name == 'Scipy' or ndim > 4:
        np.add(nums, summand, out=output)
        return output

    num_threads = normalize_num_threads(num_threads, backend)
    src_pointwise_add = _choose_cython_pointwise_add(ndim, summand_is_array, is_fp16, backend.fast)

    n_dummy = 3 - ndim if ndim <= 3 else 0

    if n_dummy:
        nums = nums[(None,) * n_dummy]
        output = output[(None,) * n_dummy]
        if summand_is_array:
            summand = summand[(None,) * n_dummy]

    if is_fp16:
        output = src_pointwise_add(
            nums.view(np.uint16), summand.view(np.uint16), output.view(np.uint16), num_threads
        ).view(np.float16)
    else:
        output = src_pointwise_add(nums, summand, output, num_threads)

    if n_dummy:
        output = output[(0,) * n_dummy]

    return output
