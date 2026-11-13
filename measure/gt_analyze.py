import sys, pickle, csv, json, collections, numpy as np
sys.path.insert(0,sys.argv[1])
from proj import *
PKL, CSV, T0, TOL = sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
ZONE=(0.42,0.0,0.58,1.0)
CLS={'hatchback':'Ô tô','suv':'Ô tô','motorbike':'Xe máy','bus':'Xe buýt','pickup':'Xe tải'}
def cls_of(n):
    for k,v in CLS.items():
        if n.startswith(k): return v
rec=pickle.load(open(PKL,'rb'))
rec=[r for r in rec if r[0]>=T0]; t_end=rec[-1][0]
prev={}; gt=[]
for t,d in rec:
    if 'camera_link' not in d: continue
    R,tc=camera_pose(d)
    for n,v in d.items():
        if n in ('x500_depth_0','camera_link','gimbal_link'): continue
        p=project(R,tc,np.array(v[:3])+[0,0,0.8])
        if p is None: prev.pop(n,None); continue
        u,vv=p; inimg=0<=u<W and 0<=vv<H
        inz=ZONE[0]*W<=u<=ZONE[2]*W and ZONE[1]*H<=vv<=ZONE[3]*H
        if n in prev:
            pt,pu,pin,pinz,pw=prev[n]
            jump=np.hypot(v[0]-pw[0],v[1]-pw[1])>3.0     # xe quay lại đầu đường
            if not jump and pin and not pinz and inz:
                gt.append(dict(t=t,name=n,cls=cls_of(n),dir='→' if u>pu else '←'))
        prev[n]=(t,u,inimg,inz,v)
ev=[]
for r in csv.DictReader(open(CSV,encoding='utf-8')):
    if float(r['time_s'])>=T0: ev.append(dict(t=float(r['time_s']),cls=r['class'],dir=r['direction'],id=r['track_id']))
ev=[e for e in ev if e['t']<=t_end]
# ghép cặp tối ưu (Hungarian) chỉ theo thời gian + cùng chiều; KHÔNG dùng lớp để ghép nên phân loại được đánh giá độc lập
from scipy.optimize import linear_sum_assignment
cost=np.full((len(gt),len(ev)),1e6)
for i,g in enumerate(gt):
    for j,e in enumerate(ev):
        if e['dir']==g['dir'] and abs(e['t']-g['t'])<=TOL: cost[i,j]=abs(e['t']-g['t'])
ri,ci=linear_sum_assignment(cost)
tp=[(gt[i],ev[j]) for i,j in zip(ri,ci) if cost[i,j]<1e5]
used={j for i,j in zip(ri,ci) if cost[i,j]<1e5}; mg={i for i,j in zip(ri,ci) if cost[i,j]<1e5}
fn=[g for i,g in enumerate(gt) if i not in mg]
fp=[e for i,e in enumerate(ev) if i not in used]
dur=t_end-T0
print(f'cửa sổ: {T0:.1f}→{t_end:.1f} s mô phỏng ({dur:.1f} s)')
print(f'GT={len(gt)}  đếm được={len(ev)}  khớp(TP)={len(tp)}  bỏ sót(FN)={len(fn)}  đếm thừa(FP)={len(fp)}')
P=len(tp)/max(1,len(ev)); Rc=len(tp)/max(1,len(gt)); F1=2*P*Rc/max(1e-9,P+Rc)
print(f'precision={P:.3f} recall={Rc:.3f} F1={F1:.3f}  sai số tổng |N-GT|/GT={abs(len(ev)-len(gt))/max(1,len(gt))*100:.1f}%')
print(f'q_GT={len(gt)*60/dur:.1f} xe/phút  q_đếm={len(ev)*60/dur:.1f} xe/phút')
cc=sum(1 for g,e in tp if g['cls']==e['cls']); print(f'phân loại đúng trong số khớp: {cc}/{len(tp)} = {cc/max(1,len(tp)):.3f}')
conf=collections.Counter((g['cls'],e['cls']) for g,e in tp)
perc={}
for c in ('Ô tô','Xe máy','Xe buýt','Xe tải'):
    ng=sum(1 for g in gt if g['cls']==c); ne=sum(1 for e in ev if e['cls']==c); nt=sum(1 for g,e in tp if g['cls']==c and e['cls']==c)
    perc[c]=(ng,ne,nt); print(f'  {c:8s} GT={ng:3d} đếm={ne:3d} đúng lớp+khớp={nt:3d}')
dt=[e['t']-g['t'] for g,e in tp]
print(f'lệch thời gian đếm so với GT: mean={np.mean(dt):.2f}s std={np.std(dt):.2f}s')
print('FN theo lớp',collections.Counter(g['cls'] for g in fn),'FP theo lớp',collections.Counter(e['cls'] for e in fp))
json.dump(dict(window=[T0,t_end],gt=len(gt),counted=len(ev),tp=len(tp),fn=len(fn),fp=len(fp),precision=P,recall=Rc,f1=F1,
   q_gt=len(gt)*60/dur,q_cnt=len(ev)*60/dur,cls_ok=cc,per_class=perc,dt_mean=float(np.mean(dt)),dt_std=float(np.std(dt)),
   fn_list=[(g['t'],g['name'],g['dir']) for g in fn],fp_list=[(e['t'],e['cls'],e['dir']) for e in fp],
   conf={f'{a}->{b}':n for (a,b),n in conf.items()}),open(sys.argv[6],'w'),ensure_ascii=False,indent=1)
