from itertools import permutations
from typing import Optional, Sequence, Union

import numpy as np


AxesLike = Union[int, Sequence[int]]
AxesParams = Union[float, Sequence[float]]


def normalize_axes(x: np.ndarray, axes) -> np.ndarray:
    assert x.ndim in [2, 3]
    squeeze = x.ndim == 2
    if squeeze:
        x = x[None]
        if axes is None:
            axes = [1, 2]
        else:
            axes = np.array(np.core.numeric.normalize_axis_tuple(axes, 2)) + 1

    if axes is None:
        raise ValueError('For 3D inputs must pass the `axes` argument.')

    return np.moveaxis(x, axes, [1, 2]), axes, squeeze


def restore_axes(x: np.ndarray, axes, squeeze: bool) -> np.ndarray:
    x = np.moveaxis(x, [1, 2], axes)
    if squeeze:
        (x,) = x
    return x


def get_c_contiguous_permutaion(array: np.ndarray) -> Optional[np.ndarray]:
    for permutation in permutations(range(array.ndim)):
        if np.transpose(array, permutation).data.c_contiguous:
            return np.array(permutation)

    return None


def inverse_permutation(permutation: np.ndarray) -> np.ndarray:
    inverse_permutation = np.arange(permutation.shape[0])
    inverse_permutation[permutation] = inverse_permutation.copy()

    return inverse_permutation


def axis_from_dim(axis: Union[AxesLike, None], dim: int) -> tuple:
    if axis is None:
        return tuple(range(dim))

    left, right = -dim, dim - 1
    if min(axis) < left or max(axis) > right:
        raise ValueError(f'For dim={dim} axis must be within ({left}, {right}): but provided {axis}.')

    return np.core.numeric.normalize_axis_tuple(axis, dim, 'axis')


def broadcast_axis(axis: Union[AxesLike, None], dim: int, *values: Union[AxesLike, AxesParams]):
    axis = axis_from_dim(axis, dim)
    values = [to_axis(axis, x) for x in values]
    sizes = set(map(len, values))
    if not sizes <= {len(axis)}:
        raise ValueError(f"Params sizes don't match with the axes: {axis} vs {sizes}")

    return (axis, *values)


def to_axis(axis, value):
    value = np.atleast_1d(value)
    if len(value) == 1:
        value = np.repeat(value, len(axis), 0)
    return value


def fill_by_indices(target, values, indices):
    target = np.array(target)
    target[list(indices)] = values
    return tuple(target)