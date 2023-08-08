[![codecov](https://codecov.io/gh/neuro-ml/imops/branch/master/graph/badge.svg)](https://codecov.io/gh/neuro-ml/imops)
[![pypi](https://img.shields.io/pypi/v/imops?logo=pypi&label=PyPi)](https://pypi.org/project/imops/)
![License](https://img.shields.io/github/license/neuro-ml/imops)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/imops)](https://pypi.org/project/imops/)

# Imops

Efficient parallelizable algorithms for multidimensional arrays to speed up your data pipelines. Docs are [here](https://neuro-ml.github.io/imops/). Benchmarks are [here](WAITING FOR BENCHMARKS).

# Install

```shell
pip install imops  # default install with Cython backend
pip install imops[numba]  # additionally install Numba backend
```

# Features

### Fast Radon transform

```python
from imops import radon, inverse_radon
```

### Fast 0/1-order zoom

```python
from imops import zoom, zoom_to_shape

# fast zoom with optional fallback to scipy's implementation
y = zoom(x, 2, axis=[0, 1])
# a handy function to zoom the array to a given shape 
# without the need to compute the scale factor
z = zoom_to_shape(x, (4, 120, 67))
```
Works faster only for `ndim<=4, dtype=float32 or float64 (and bool-int16-32-64 if order == 0), output=None, order=0 or 1, mode='constant', grid_mode=False`
### Fast 1d linear interpolation

```python
from imops import interp1d  # same as `scipy.interpolate.interp1d`
```
Works faster only for `ndim<=3, dtype=float32 or float64, order=1`
### Fast binary morphology

```python
from imops import binary_dilation, binary_erosion, binary_opening, binary_closing
```
These functions mimic `scikit-image` counterparts
### Padding

```python
from imops import pad, pad_to_shape

y = pad(x, 10, axis=[0, 1])
# `ratio` controls how much padding is applied to left side:
# 0 - pad from right
# 1 - pad from left
# 0.5 - distribute the padding equally
z = pad_to_shape(x, (4, 120, 67), ratio=0.25)
```

### Cropping

```python
from imops import crop_to_shape

# `ratio` controls the position of the crop
# 0 - crop from right
# 1 - crop from left
# 0.5 - crop from the middle
z = crop_to_shape(x, (4, 120, 67), ratio=0.25)
```

### Labeling

```python
from imops import label

# same as `skimage.measure.label`
labeled, num_components = label(x, background=1, return_num=True)
```

# Backends
For all heavy image routines except `label` you can specify which backend to use. Backend can be specified by a string or by an instance of `Backend` class. The latter allows you to customize some backend options:
```python
from imops import Cython, Numba, Scipy, zoom

y = zoom(x, 2, backend='Cython')
y = zoom(x, 2, backend=Cython(fast=False))  # same as previous
y = zoom(x, 2, backend=Cython(fast=True))  # -ffast-math compiled cython backend
y = zoom(x, 2, backend=Scipy())  # use scipy original implementation
y = zoom(x, 2, backend='Numba')
y = zoom(x, 2, backend=Numba(parallel=True, nogil=True, cache=True))  # same as previous
```
Also backend can be specified globally or locally:
```python
from imops import imops_backend, set_backend, zoom

set_backend('Numba')  # sets Numba as default backend
with imops_backend('Cython'):  # sets Cython backend via context manager
    zoom(x, 2)
```
Note that for `Numba` backend setting `num_threads` argument has no effect for now and you should use `NUMBA_NUM_THREADS` environment variable.
Available backends:
|                   | Scipy   | Cython  | Numba   |
|-------------------|---------|---------|---------|
| `zoom`            | &check; | &check; | &check; |
| `zoom_to_shape`   | &check; | &check; | &check; |
| `interp1d`        | &check; | &check; | &check; |
| `radon`           | &cross; | &check; | &cross; |
| `inverse_radon`   | &cross; | &check; | &cross; |
| `binary_dilation` | &check; | &check; | &cross; |
| `binary_erosion`  | &check; | &check; | &cross; |
| `binary_closing`  | &check; | &check; | &cross; |
| `binary_opening`  | &check; | &check; | &cross; |
| `center_of_mass`  | &check; | &check; | &cross; |

# How fast is it?

We use [`airspeed velocity`](https://asv.readthedocs.io/en/stable/) to benchmark our code. All results are available [here](WAITING FOR BENCHMARKS).

# Acknowledgements

Some parts of our code for radon/inverse radon transform as well as the code for linear interpolation are inspired by
the implementations from [`scikit-image`](https://github.com/scikit-image/scikit-image) and [`scipy`](https://github.com/scipy/scipy).
Also we used [`fastremap`](https://github.com/seung-lab/fastremap) and [`cc3d`](https://github.com/seung-lab/connected-components-3d) out of the box.
