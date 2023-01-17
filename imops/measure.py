from collections import namedtuple
from typing import NamedTuple, Tuple, Union
from warnings import warn

import numpy as np
from cc3d import connected_components
from fastremap import remap, unique
from skimage.measure import label as skimage_label


# (ndim, skimage_connectivity) -> cc3d_connectivity
skimage2cc3d = {
    (1, 1): 4,
    (2, 1): 4,
    (2, 2): 8,
    (3, 1): 6,
    (3, 2): 18,
    (3, 3): 26,
}


def label(
    label_image: np.ndarray,
    background: int = None,
    return_num: bool = False,
    connectivity: int = None,
    return_sizes: bool = False,
) -> Union[np.ndarray, NamedTuple]:
    """
    Fast version of `skimage.measure.label` which optionally returns sizes of connected components

    See `https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.label`
    """
    ndim = label_image.ndim
    connectivity = connectivity or ndim

    if not 1 <= connectivity <= ndim:
        raise ValueError(f'Connectivity for {ndim}D image should be in [1, ..., {ndim}]. Got {connectivity}.')

    if ndim > 3:
        warn("Fast label is only supported for ndim<=3, Falling back to scikit-image's implementation.")
        labeled_image, num_components = skimage_label(
            label_image, background=background, return_num=True, connectivity=connectivity
        )
    else:
        if ndim == 1:
            label_image = label_image[None]

        if background:
            label_image = remap(
                label_image, {background: 0, 0: background}, preserve_missing_labels=True, in_place=False
            )

        labeled_image, num_components = connected_components(
            label_image,
            connectivity=skimage2cc3d[(ndim, connectivity)],
            return_N=True,
        )

        if ndim == 1:
            labeled_image = labeled_image[0]

    if return_sizes:
        _, sizes = unique(labeled_image, return_counts=True)
        if return_num:
            return namedtuple('Labeling', ['labeled_image', 'num_components', 'sizes'])(
                labeled_image=labeled_image, num_components=num_components, sizes=sizes
            )
        return namedtuple('Labeling', ['labeled_image', 'sizes'])(labeled_image=labeled_image, sizes=sizes)

    if return_num:
        return namedtuple('Labeling', ['labeled_image', 'num_components'])(
            labeled_image=labeled_image, num_components=num_components
        )

    return labeled_image
