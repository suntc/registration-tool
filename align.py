'''
Created on 2016-07-28
@author: Sun Tianchen
'''

from sklearn.neighbors import NearestNeighbors
import numpy as np
from scipy.spatial.distance import pdist
from math import acos
import cv2

def compute_affine(src, dest):
    import numpy as np

    if src.shape[0] < 3 or src.shape[0] != dest.shape[0]:
        return False
    A = []  
    for i in src:
        A.append(np.hstack((i, 1)))
    A = np.array(A, dtype='f')
    xc = np.array(dest[:,0], dtype='f')
    yc = np.array(dest[:,1], dtype='f')
    resx = 0
    resy = 0
    resx = cv2.solve(A.T.dot(A), A.T.dot(xc), flags=1)
    resy = cv2.solve(A.T.dot(A), A.T.dot(yc), flags=1)
    res = np.vstack((np.hstack(resx[1]), np.hstack(resy[1])))
    #print "result is... ", res
    return res

def rigid_transform_2D(A, B):
    assert len(A) == len(B)

    N = A.shape[0]; # total points

    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    
    # centre the points
    AA = A - np.tile(centroid_A, (N, 1))
    BB = B - np.tile(centroid_B, (N, 1))

    # dot is matrix multiplication for array
    H = np.transpose(AA).dot(BB)

    U, S, VT = np.linalg.svd(H)
    
    R = U.dot(VT)
    
    ## reflection case
    if np.linalg.det(R) < 0:
        print "reflection detected"
        R[:,[1]] *= -1

    t = -R.dot(centroid_A.T) + centroid_B.T

    #print R, t

    return R, t

def res(p,src,dst):
    T = np.matrix([[np.cos(p[2]),-np.sin(p[2]),p[0]],
                   [np.sin(p[2]), np.cos(p[2]),p[1]],
                   [0           ,0            ,1   ]])
    n  = np.size(src,0)
    xt = np.ones([n,3])        
    xt[:,:-1] = src
    xt = (xt*T.T).A
    d  = np.zeros(np.shape(src))
    d[:,0] = xt[:,0]-dst[:,0]
    d[:,1] = xt[:,1]-dst[:,1]

    r = np.sum(np.square(d[:,0])+np.square(d[:,1]))
    return r

def basic_icp(data, model, no_iterations = 100):
    
    data = np.hsplit(data, 2)
    model = np.hsplit(model, 2)
    data = np.vstack((np.concatenate(data[0]), np.concatenate(data[1])))
    model = np.vstack((np.concatenate(model[0]), np.concatenate(model[1])))
    
    data = np.array([data.T], copy=True).astype(np.float32)
    model = np.array([model.T], copy=True).astype(np.float32)

    error = 10e10
    trans_h = None

    rl = []
    tl = []

    for i in range(no_iterations):
        nbrs = NearestNeighbors(n_neighbors=1, algorithm='auto').fit(model[0])
        distances, indices = nbrs.kneighbors(data[0])

        prev_error = error
        prev_trans_h = trans_h
        error = res([0,0,0],data[0], model[0, indices.T][0])

        R, T = rigid_transform_2D(data[0], model[0, indices.T][0]) 

        data[0] = data[0].dot(R) + T

        ## store transformation in every round
        rl.append(R)
        tl.append(T)

        ## use homogeneous matrix to keep track of the transformation
        '''
        if i == 0:
            trans_h = np.vstack((np.hstack((R.T,np.array([T]).T)), [0,0,1]))
        else:
            trans_h = np.vstack((np.hstack((R.T,np.array([T]).T)), [0,0,1])).dot(trans_h)
        '''
        ## the transformation is not standard...
        if i == 0:
            trans_h = np.hstack((np.vstack((R,T)),np.array([[0,0,1]]).T))
        else:
            trans_h = trans_h.dot(np.hstack((np.vstack((R,T)),np.array([[0,0,1]]).T)))

        if abs(prev_error - error) / prev_error < 0.0001:
            print "squared error = " + str(error)
            return trans_h, error
            #return rl, tl, error

    ## prevent cases that error goes up and down
    if error > prev_error:
        print "squared error = " + str(prev_error)
        return prev_trans_h, error
    else:   
        print "squared error = " + str(error)
        return trans_h, error
    #return rl, tl, error


def icp_neighbors(data, model, no_iterations = 100):
    p = data
    s = model
    data = np.hsplit(data, 2)
    model = np.hsplit(model, 2)
    data = np.vstack((np.concatenate(data[0]), np.concatenate(data[1])))
    model = np.vstack((np.concatenate(model[0]), np.concatenate(model[1])))
    
    data = np.array([data.T], copy=True).astype(np.float32)
    model = np.array([model.T], copy=True).astype(np.float32)

    error = 10e10
    indices = None

    for i in range(no_iterations):
        prev_error = error
        prev_ind = indices

        nbrs = NearestNeighbors(n_neighbors=1, algorithm='auto').fit(model[0])
        distances, indices = nbrs.kneighbors(data[0])

        error = res([0,0,0],data[0], model[0, indices.T][0])

        R, T = rigid_transform_2D(data[0], model[0, indices.T][0]) 

        data[0] = data[0].dot(R) + T

        if abs(prev_error - error) / prev_error < 0.0001:
            print "squared error = " + str(error)
            return s[np.concatenate(indices)], error

    ## prevent cases that error goes up and down
    if error > prev_error:
        print "squared error = " + str(prev_error)
        return s[np.concatenate(indices)], error
    else:   
        print "squared error = " + str(error)
        return s[np.concatenate(indices)], error



if __name__ == '__main__':
    p = np.array([[139,171],[135,229],[137,303],[163,347],[179,249],[208,209],[201,142],[265,157],[291,226],[209,343]])
    s = np.array([[240,275],[139,561],[93,869],[182,1160],[389,699],[570,495],[596,153],[860,278],[932,719],[373,1211]]) ## sample is reference
    
    p = np.array([[209.27086894169193, 369.4604816555757], [230.9181888874519, 335.90713573964774], [257.97733881965183, 298.02432583456783], [266.6362667979558, 232.0], [259.0597048169398, 158.39911218441617], [191.95301298508397, 162.72857617356817], [130.25815113966812, 227.67053601084802], [160.56439906373203, 319.6716457803278], [212.51796693355593, 295.8595938399919], [150.82310508814007, 277.4593718860959], [204.94140495253993, 227.67053601084802], [224.4239929037239, 175.7169681410241], [184.37645100406797, 285.03593386711185]])
    s = np.array([[32.14932250576658, 422.2489537926695], [107.66762750471798, 521.2039741361232], [224.85120422722912, 635.7834713759119], [599.8386497392644, 557.6610868942378], [808.1650083570617, 573.2855637905725], [844.6221211151762, 213.92259517487224], [482.65507301675325, 107.1553363832511], [105.06354802199553, 284.23274120837885], [206.6226478481717, 479.53870241256385], [272.3210841919597, 139.74271031391834], [540.5412709123736, 335.04867151810333], [808.7614576327878, 413.1710559997773], [155.13750746944856, 389.7343406552751]])  
    
    p = np.array([[129.1757851423801, 131.33996225221622], [204.94140495253993, 109.69264230645626], [300.1896127138837, 129.17523025764024], [342.4018866081156, 168.14040616000813], [338.0724226189636, 212.51741204881603], [306.6838086976117, 268.80044390779193], [234.1652868793159, 293.69486184541586], [160.56439906373203, 262.30624792406394], [141.08181111254808, 201.69375207593606], [249.31841084134783, 184.3758961193281], [203.85903895525195, 210.35268005424007], [268.8009987925318, 244.98839196745598], [168.14096104474802, 134.58706024408022], [270.96573078710776, 157.31674618712816], [327.24876264608366, 242.82365997287997], [183.29408500678, 236.32946398915198], [211.43560093626792, 159.48147818170415], [293.6954167301557, 199.52902008136004], [143.24654310712407, 226.58817001356], [123.76395515594012, 162.72857617356817]])
    s = np.array([[41.49538601113568, 220.51347774961312], [462.09059229599166, 48.61804561580243], [897.315197060321, 96.16359067409053], [1167.9590689305762, 198.5693800304033], [1208.1899147491274, 385.09421064368723], [1047.2665314749217, 823.9761650278848], [794.9094077040083, 926.3819543841977], [304.8245586416542, 908.0952062848561], [132.92912650784342, 589.9057893563128], [714.4477160669055, 377.77951140395066], [513.2934869741482, 597.2204885960494], [857.0843512417694, 721.5703756715722], [246.3069647237612, 224.17082736948146], [787.5947084642714, 271.71637242776956], [1171.6164185504442, 655.7380825139425], [410.88769761783533, 747.1718230106502], [495.0067388748064, 315.6045678661893], [970.4621894576874, 421.6677068423704], [209.73346852507802, 721.5703756715722], [67.09683335021396, 366.80746254434564]])   
    
    p = np.array([[13.412842168802996, 246.52835432527803], [121.79601443213616, 126.5629122513829], [1000.9288685809992, 179.614032760366], [1197.9758876143649, 384.2397832950151], [678.8327797764588, 933.6978171380545], [315.05366771486035, 884.4360623797129], [49.798065169944806, 414.5547093001483], [1232.0801793701396, 937.487182888696]])
    s = np.array([[17.16337361899332, 250.27888577546827], [49.58492448898687, 441.2173534491873], [121.3702538331047, 131.40698470088938], [979.0160307338806, 146.51968561544055], [1194.3720187662339, 388.32290024825835], [706.9874142719605, 932.3801331720986], [340.50441709409574, 894.5983808857209], [1233.5141046631788, 939.7798777979704]]) 
    
    maxd = np.max(pdist(p))
    maxm = np.max(pdist(s))
    guess_scale = maxm / maxd
    print "guess_scale = ", guess_scale
    step = 0.1
    min_error = 10e10
    m_trans_h = None
    m_scale = None
    for i in np.arange(max(guess_scale - 1, 0.1), guess_scale + 1.1, step):
        print "scale = ", i
        trans_h, error = basic_icp(p * i, s)
        if error < min_error:
            min_error = error
            m_trans_h = trans_h
            m_scale = i
    print trans_h
    angle = acos(trans_h[0][0])
    print "min error = ", min_error
    print "scale = ", m_scale
    print "angle = ", angle
    tx = trans_h[0][2]
    ty = trans_h[1][2]
    print tx, ty
    
    #basic_icp(p ,s, 100)