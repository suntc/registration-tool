'''
Created on 2016-08-26
@author: Sun Tianchen
'''
import numpy as np
from matplotlib.delaunay import delaunay
from scipy.spatial.distance import pdist
from math import asin, pi
import align
import cv2
from PIL import Image
from pylab import *
from numpy import *

from PyQt4 import QtCore, QtGui

def triangulate_points(x,y):
    """delaunay triangulation of 2D points"""
    centers,edges,tri,neighbors = delaunay(x,y)
    return tri

def alpha_for_triangle(points,m,n):
    """ creates alpha map of size (m,n) 
        for a triangle with corners defined by points
        (given in normalized homogeneous coordinates)."""
    
    alpha = zeros((m,n))
    points = np.array(points, dtype='i')
    minx = min(points[1])
    miny = min(points[0])
    maxx = max(points[1])
    maxy = max(points[0])
    from matplotlib import path
    tri = path.Path(np.dstack((points[1], points[0]))[0])
    mx, my = np.meshgrid(np.arange(minx, maxx), np.arange(miny, maxy))
    pts = np.dstack((mx, my))
    r = pts.shape[0]
    c = pts.shape[1]
    pts = np.reshape(pts, (1,r*c,2))
    res = tri.contains_points(pts[0])
    res = res.astype(int)
    res = np.reshape(res, (r,c))
    alpha[miny:maxy,minx:maxx] = res
    '''
    for i in range(min(points[0]),max(points[0])):
        for j in range(min(points[1]),max(points[1])):
            x = linalg.solve(points,[i,j,1])
            if min(x) > 0: #all coefficients positive
                alpha[i,j] = 1
    '''     
    return alpha

def pw_affine(fromim,toim,fp,tp,tri):
    """ warp triangular patches from an image.
        fromim = image to warp 
        toim = destination image
        fp = from points in hom. coordinates
        tp = to points in hom.  coordinates
        tri = triangulation
    	corrdinates are in (y, x) form    
    """

    im = toim.copy()

    #check if image is grayscale or color
    is_color = len(fromim.shape) == 3

    #create image to warp to (needed if iterate colors)
    im_t = zeros(im.shape, 'uint8') 

    for t in tri:
        #compute affine transformation
        print "begin affine"
        #H = Haffine_from_points(tp[:,t],fp[:,t])
        dst = np.array(np.dstack((tp[:,t][1],tp[:,t][0]))[0], dtype='f4')
        src = np.array(np.dstack((fp[:,t][1],fp[:,t][0]))[0], dtype='f4')
        H = cv2.getAffineTransform(src,dst)
        print "finish affine" 
        print "begin transform"
        '''
        if is_color:
            for col in range(3):
                im_t[:,:,col] = ndimage.affine_transform(fromim[:,:,col],H[:2,:2],(H[0,2],H[1,2]),im.shape[:2])
        else:
            im_t = ndimage.affine_transform(fromim,H[:2,:2],(H[0,2],H[1,2]),im.shape[:2])
        '''
        im_t = cv2.warpAffine(fromim, H[0:2,:], (im.shape[1], im.shape[0]))
        #cv2.imshow('img', im_t)
        #cv2.waitKey(0)
        print "finish transform"
        #alpha for triangle
        print "begin alpha"
        alpha = alpha_for_triangle(tp[:,t],im_t.shape[0],im_t.shape[1])
        print "finish alpha"
        #add triangle to image
        if is_color:
            for col in range(3):
                im[:,:,col] = (1-alpha)*im[:,:,col] + alpha*im_t[:,:,col]
        else:
            im = (1-alpha)*im + alpha*im_t

    return im

class Registrator(QtCore.QObject):
    sigTransformRequested = QtCore.Signal(object)
    sigAffineRequested = QtCore.Signal(object)
    sigPiecewiseRequested = QtCore.Signal(object)
    """docstring for Registrator"""
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.model = None ## [[],[],...]
        self.data = None
        pass

    def set_points(self, data, model):
        self.data = data
        self.model = model

    def rigid(self):
        data = self.data.reshape([1,self.data.shape[0],self.data.shape[1]])
        model = self.model.reshape([1,self.model.shape[0],self.model.shape[1]])
        rft = cv2.estimateRigidTransform(data, model, False)
        self.sigAffineRequested.emit((rft))

    def affine(self):
        aft = align.compute_affine(self.data, self.model)
        print "affine matrix: ", aft
        self.sigAffineRequested.emit((aft))

    def projective(self):
        pass

    def piecewise(self, d_contour, m_contour):
        ## compute affine / projective first to get bounding box correspondence
        ## contour: N * 2 array
        
        #img = cv2.imread("./photo2.jpg")
        #img2 = cv2.imread("./sample2.tif")
        #img = cv2.imread("./case_11_2_photo.jpg")
        #img2 = cv2.imread("case_11_2.tif")
        
        #brect = [[min(d_contour[:,0]),min(d_contour[:,1]),1], [min(d_contour[:,0]),max(d_contour[:,1]),1], [max(d_contour[:,0]),max(d_contour[:,1]),1], [max(d_contour[:,0]),min(d_contour[:,1]),1]] ##pay attention to the sequence

        aft = align.compute_affine(self.data, self.model)
        '''
        shape = img2.shape
        nphoto = cv2.warpAffine(img, aft, (shape[1], shape[0]))
        
        cv2.imshow('img_0', nphoto)
        cv2.waitKey(0)
        '''
        aft = np.vstack((aft, [0,0,1]))
        #ct =  np.insert(np.dstack((d_contour[:,1],d_contour[:,0]))[0], 2, 1, axis=1)
        ct =  np.insert(d_contour, 2, 1, axis=1)
        ct = aft.dot(ct.T).T
        brect = [[min(ct[:,0]),min(ct[:,1]),1], [min(ct[:,0]),max(ct[:,1]),1], [max(ct[:,0]),max(ct[:,1]),1], [max(ct[:,0]),min(ct[:,1]),1]] ##pay attention to the sequence
        
        #shape = img2.shape
        #nphoto = cv2.warpAffine(img, aft[:2], (shape[1], shape[0]))
        
        data_brect = np.linalg.inv(aft).dot(np.array(brect).T).T
        model_brect =  np.array([[min(m_contour[:,0]),min(m_contour[:,1]),1], [min(m_contour[:,0]),max(m_contour[:,1]),1], [max(m_contour[:,0]),max(m_contour[:,1]),1], [max(m_contour[:,0]),min(m_contour[:,1]),1]]) ##pay attention to the sequence
        #data_brect = np.dstack(( data_brect[:,1], data_brect[:,0] ))[0]
        #model_brect = np.dstack(( model_brect[:,1], model_brect[:,0] ))[0]
        

        model = np.concatenate(( self.model, model_brect[:,0:2] ))
        data = np.concatenate(( self.data, data_brect[:,0:2] ))
        
        x = data[:,0]
        y = data[:,1]
        tri = align.triangulate_points(x, y)
        fp = np.dstack(( data[:,1],data[:,0],np.ones(data.shape[0]) ))[0]
        tp = np.dstack(( model[:,1],model[:,0],np.ones(model.shape[0]) ))[0]
        #nphoto = pw_affine(img,img2,fp.T,tp.T,tri)
        
        '''
        aft = align.compute_affine(data, model)
        
        shape = img2.shape
        nphoto = cv2.warpAffine(img, aft, (shape[1], shape[0]))
        
        cv2.imshow('img', nphoto)
        cv2.waitKey(0)
        '''
        self.sigPiecewiseRequested.emit((fp.T,tp.T,tri))
        

if __name__ == '__main__':
    delaunay()