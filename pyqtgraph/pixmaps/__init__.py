"""
Allows easy loading of pixmaps used in UI elements. 
Provides support for frozen environments as well.
"""

import os, sys, pickle
from ..functions import makeQImage
from ..Qt import QtGui
if sys.version_info[0] == 2:
    from . import pixmapData_2 as pixmapData
else:
    from . import pixmapData_3 as pixmapData


def getPixmap(name):
    """
    Return a QPixmap corresponding to the image file with the given name.
    (eg. getPixmap('auto') loads pyqtgraph/pixmaps/auto.png)
    """
    key = name+'.png'
    if key in ['del.png', 'curve.png', 'color.png']:
        from PIL import Image
        import numpy as np
        arr = pixmapData.pixmapData['lock.png']
        brr = np.array(arr, copy=True)
        imarr = np.asarray(Image.open(key), dtype='i')
        if imarr.shape[2] == 3:
            imarr = np.insert(imarr, 3, 255, axis=2)
        for i in range(brr.shape[0]):
            for j in range(brr.shape[1]):
                brr[i][j] = np.array(imarr[i][j], copy=True)
        arr = brr
    else:
        data = pixmapData.pixmapData[key]
        if isinstance(data, basestring) or isinstance(data, bytes):
            pixmapData.pixmapData[key] = pickle.loads(data)
        arr = pixmapData.pixmapData[key]
    return QtGui.QPixmap(makeQImage(arr))

    
def addPixmap(path):
    from PIL import Image
    import numpy as np
    arr = np.ones([16,16,4])
    arr = arr * 255
    pixmapData.pixmapData['del.png'] = pixmapData.pixmapData['default.png']