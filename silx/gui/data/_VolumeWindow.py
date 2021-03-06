# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2019 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""This module provides a widget to visualize 3D arrays"""

__authors__ = ["T. Vincent"]
__license__ = "MIT"
__date__ = "22/03/2019"


import numpy

from ..plot3d.SceneWindow import SceneWindow
from ..plot3d.items import ScalarField3D, ComplexField3D


class VolumeWindow(SceneWindow):
    """Extends SceneWindow with a convenient API for 3D array

    :param QWidget: parent
    """

    def __init__(self, parent):
        super(VolumeWindow, self).__init__(parent)
        # Hide global parameter dock
        self.getGroupResetWidget().parent().setVisible(False)

    def setAxesLabels(self, xlabel=None, ylabel=None, zlabel=None):
        """Set the text labels of the axes.

        :param Union[str,None] xlabel: Label of the X axis
        :param Union[str,None] ylabel: Label of the Y axis
        :param Union[str,None] zlabel: Label of the Z axis
        """
        sceneWidget = self.getSceneWidget()
        sceneWidget.getSceneGroup().setAxesLabels(
            'X' if xlabel is None else xlabel,
            'Y' if ylabel is None else ylabel,
            'Z' if zlabel is None else zlabel)

    def clear(self):
        """Clear any currently displayed data"""
        sceneWidget = self.getSceneWidget()
        items = sceneWidget.getItems()
        if (len(items) == 1 and
                isinstance(items[0], (ScalarField3D, ComplexField3D))):
            items[0].setData(None)
        else:  # Safety net
            sceneWidget.clearItems()

    @staticmethod
    def __computeIsolevel(data):
        """Returns a suitable isolevel value for data

        :param numpy.ndarray data:
        :rtype: float
        """
        data = data[numpy.isfinite(data)]
        if len(data) == 0:
            return 0
        else:
            return numpy.mean(data) + numpy.std(data)

    def setData(self, data, offset=(0., 0., 0.), scale=(1., 1., 1.)):
        """Set the 3D array data to display.

        :param numpy.ndarray data: 3D array of float or complex
        :param List[float] offset: (tx, ty, tz) coordinates of the origin
        :param List[float] scale: (sx, sy, sz) scale for each dimension
        """
        sceneWidget = self.getSceneWidget()

        previousItems = sceneWidget.getItems()
        if (len(previousItems) == 1 and
                isinstance(previousItems[0], (ScalarField3D, ComplexField3D)) and
                numpy.iscomplexobj(data) == isinstance(previousItems[0], ComplexField3D)):
            # Reuse existing volume item
            volume = sceneWidget.getItems()[0]
            volume.setData(data, copy=False)
        else:
            # Add a new volume
            volume = sceneWidget.addVolume(data, copy=False)
            volume.setLabel('Volume')
            for plane in volume.getCutPlanes():
                plane.setVisible(False)
            volume.addIsosurface(self.__computeIsolevel, '#FF0000FF')

        volume.setTranslation(*offset)
        volume.setScale(*scale)
