import asyncio, json, time, pathlib, sys
import websockets
tok=pathlib.Path.home().joinpath('.config/uav_bridge_token').read_text().strip()
DUR=float(sys.argv[1]); OUT=sys.argv[2]
async def main():
    rows=[]
    async with websockets.connect('ws://127.0.0.1:8765', max_size=2**24) as ws:
        await ws.send(json.dumps({"type":"auth","protocol":1,"token":tok}))
        t_end=time.time()+DUR
        while time.time()<t_end:
            raw=await asyncio.wait_for(ws.recv(),20); tr=time.time()
            p=json.loads(raw)
            if p.get('type')!='frame': continue
            rows.append(dict(seq=p['seq'],tr=tr,t_rx=p['t_rx'],ts=p['timestamp'],n=len(raw),ndet=len(p['detections']),**p['timing']))
    json.dump(rows,open(OUT,'w')); print(len(rows),'frames')
asyncio.run(main())
