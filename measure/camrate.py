import time
from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image
st=[]
def ci(m): st.append((time.time(), m.header.stamp.sec+m.header.stamp.nsec*1e-9))
n=Node(); n.subscribe(Image,'/world/default/model/x500_depth_0/link/camera_link/sensor/IMX214/image',ci)
time.sleep(15)
print(len(st),'frames; real',round(st[-1][0]-st[0][0],1),'s; sim',round(st[-1][1]-st[0][1],2),'s')
print('fps real',round((len(st)-1)/(st[-1][0]-st[0][0]),2),'fps sim',round((len(st)-1)/(st[-1][1]-st[0][1]),2),'RTF',round((st[-1][1]-st[0][1])/(st[-1][0]-st[0][0]),2))
