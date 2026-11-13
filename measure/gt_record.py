"""Ghi vị trí thật (Gazebo pose/info) của camera và các xe để làm ground truth đếm xe."""
import sys, time, pickle
from gz.transport13 import Node
from gz.msgs10.pose_v_pb2 import Pose_V
DUR=float(sys.argv[1]); OUT=sys.argv[2]
VEH=('hatchback_blue_1','suv_1','pickup_1','bus_1','hatchback_red_1','suv_2','pickup_2','hatchback_red_2',
     'motorbike_red_1','motorbike_blue_1','motorbike_black_1','motorbike_white_1',
     'motorbike_red_2','motorbike_blue_2','motorbike_black_2','motorbike_white_2')
rec=[]; last=[-1.0]
def cb(m):
    t=m.header.stamp.sec+m.header.stamp.nsec*1e-9
    if t-last[0]<0.05: return
    last[0]=t; d={}
    for p in m.pose:
        if p.name in VEH or p.name in ('x500_depth_0','camera_link','gimbal_link'):
            o=p.orientation; d[p.name]=(p.position.x,p.position.y,p.position.z,o.x,o.y,o.z,o.w)
    rec.append((t,d))
n=Node(); assert n.subscribe(Pose_V,'/world/default/pose/info',cb)
t0=time.time()
while time.time()-t0<DUR: time.sleep(0.5)
pickle.dump(rec,open(OUT,'wb')); print(len(rec),'samples', rec[0][0], rec[-1][0])
