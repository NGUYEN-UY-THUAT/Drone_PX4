import sys, time, json, base64, statistics as st
sys.path.insert(0,'/home/uythuat/PX4-ROS2-Gazebo-YOLOv8/detection')
import cv2, numpy as np, torch
from ultralytics import YOLO
from ultralytics.trackers.byte_tracker import BYTETracker
from ultralytics.utils import YAML, IterableSimpleNamespace
from ultralytics.utils.checks import check_yaml
import traffic_counter as tc
W='/home/uythuat/PX4-ROS2-Gazebo-YOLOv8/finetune/runs/yolov8m_sim_50ep_colab/weights/best.pt'
cap=cv2.VideoCapture('/home/uythuat/PX4-ROS2-Gazebo-YOLOv8/demo/video_bay_nhan_dien.mp4')
frames=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frames.append(f)
print('video frames',len(frames), frames[0].shape)
def q(v): v=sorted(v); n=len(v); return dict(mean=round(st.mean(v),2),med=round(v[n//2],2),p95=round(v[int(n*.95)],2),max=round(v[-1],2))
res={}
model=YOLO(W)
def run(name, size, imgsz=640, half=False, device=0, n=150, classes=[0,2,3,5,7]):
    fr=[cv2.resize(f,size) for f in frames[:n+10]]
    for f in fr[:10]: model.predict(f,imgsz=imgsz,half=half,device=device,verbose=False,conf=0.1,classes=classes)
    pre=[];inf=[];post=[];tot=[]
    for f in fr[10:]:
        t=time.perf_counter(); r=model.predict(f,imgsz=imgsz,half=half,device=device,verbose=False,conf=0.1,classes=classes)[0]; tot.append((time.perf_counter()-t)*1e3)
        pre.append(r.speed['preprocess']);inf.append(r.speed['inference']);post.append(r.speed['postprocess'])
    res[name]=dict(pre=q(pre),inf=q(inf),post=q(post),total=q(tot))
    print(name,res[name]['total'],flush=True)
run('1920x1080 imgsz640 fp32 GPU',(1920,1080))
run('1920x1080 imgsz640 fp16 GPU',(1920,1080),half=True)
run('1920x1080 imgsz480 fp32 GPU',(1920,1080),imgsz=480)
run('1280x720 imgsz640 fp32 GPU',(1280,720))
run('1920x1080 imgsz640 fp32 CPU',(1920,1080),device='cpu',n=20)
model=YOLO(W)
for f in frames[:10]: model.predict(f,verbose=False,device=0)
# full pipeline of traffic_counter per stage, on 1920x1080
fr=[cv2.resize(f,(1920,1080)) for f in frames]
tracker=BYTETracker(IterableSimpleNamespace(**YAML.load(check_yaml('bytetrack.yaml'))))
counter=tc.FlowCounter((0.42,0.0,0.58,1.0),60,'/dev/null')
st_det=[];st_trk=[];st_cnt=[];st_conv=[];st_enc=[];st_b64=[];st_all=[]
for i,f in enumerate(fr):
    t0=time.perf_counter()
    # message -> numpy BGR, as in on_image (rgb8 -> bgr)
    raw=np.ascontiguousarray(f[:,:,::-1]).tobytes()
    t1=time.perf_counter()
    a=np.frombuffer(raw,np.uint8).reshape(1080,5760//1)[:, :] if False else np.frombuffer(raw,np.uint8).reshape(1080,1920*3)
    img=a[:, :1920*3].reshape(1080,1920,3); img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    t2=time.perf_counter()
    det=model.predict(img,classes=[0,2,3,5,7],conf=0.1,verbose=False)[0].boxes.cpu().numpy()
    t3=time.perf_counter()
    tr=tracker.update(det,img)
    t4=time.perf_counter()
    boxes=[(int(r[4]),int(r[6]),*det.xyxy[int(r[7])]) for r in tr if r[5]>=0.3]
    counter.update(boxes,1920,1080,i/10.0)
    t5=time.perf_counter()
    ok,jpg=cv2.imencode('.jpg',img,[cv2.IMWRITE_JPEG_QUALITY,80]); t6=time.perf_counter()
    b=base64.b64encode(jpg).decode(); t7=time.perf_counter()
    if i>=10:
        st_conv.append((t2-t1)*1e3);st_det.append((t3-t2)*1e3);st_trk.append((t4-t3)*1e3);st_cnt.append((t5-t4)*1e3);st_enc.append((t6-t5)*1e3);st_b64.append((t7-t6)*1e3)
res['pipeline']=dict(convert=q(st_conv),detect=q(st_det),track=q(st_trk),count=q(st_cnt),jpeg=q(st_enc),b64=q(st_b64),jpeg_kB=round(len(jpg)/1024,1))
print(json.dumps(res['pipeline']))
json.dump(res,open(sys.argv[1],'w'),indent=1)
