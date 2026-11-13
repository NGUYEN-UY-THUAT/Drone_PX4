"""Cất cánh và đứng yên tại một điểm trên đường, camera nhìn vuông góc với đường (offboard position)."""
import asyncio, sys
from mavsdk import System
from mavsdk.offboard import PositionNedYaw
N, E, ALT, HEAD, DUR = [float(x) for x in sys.argv[1:6]]
async def main():
    d = System(port=50061)
    await d.connect(system_address="udpin://0.0.0.0:14550")
    async for s in d.core.connection_state():
        if s.is_connected: break
    async for h in d.telemetry.health():
        if h.is_global_position_ok and h.is_home_position_ok: break
    print("connected, armed...", flush=True)
    await d.action.arm()
    await d.offboard.set_position_ned(PositionNedYaw(0, 0, 0, HEAD))
    await d.action.takeoff(); await asyncio.sleep(1)
    await d.offboard.set_position_ned(PositionNedYaw(0, 0, -2.0, HEAD))
    await d.offboard.start()
    async def go(n, e, dn, secs):
        for _ in range(int(secs * 10)):
            await d.offboard.set_position_ned(PositionNedYaw(n, e, dn, HEAD)); await asyncio.sleep(0.1)
    await go(0, 0, -ALT, 25)           # lên độ cao
    await go(N, E, -ALT, 40)           # sang điểm quan sát
    print("HOVER_READY", flush=True)
    await go(N, E, -ALT, DUR)
    await d.offboard.stop(); await d.action.land()
    print("landed", flush=True)
asyncio.run(main())
