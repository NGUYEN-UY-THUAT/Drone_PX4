import math, numpy as np
W,H=1920,1080; HFOV=1.204; FX=(W/2)/math.tan(HFOV/2)
SENSOR=np.array([0.01233,-0.03,0.01878])      # pose của sensor trong camera_link
def qmat(x,y,z,w):
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                     [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                     [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def camera_pose(d):
    m=d['x500_depth_0']; Rm=qmat(*m[3:]); tm=np.array(m[:3])
    c=d['camera_link']; Rc=qmat(*c[3:])            # camera_link so với model
    R=Rm@Rc; t=tm+Rm@np.array(c[:3])+R@SENSOR
    return R,t
def project(R,t,P):
    dv=R.T@(np.asarray(P)-t)
    if dv[0]<=0.1: return None
    return W/2-FX*dv[1]/dv[0], H/2-FX*dv[2]/dv[0]
