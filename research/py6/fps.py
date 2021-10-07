import time

T_FPS = 100

def main():
    FPS = 1
    target_fps = 1.0 / T_FPS
    fps_l = ()
    AVG = 100

    while 1:
        f_sl = fps_l[-AVG::]
        start_time = time.time() # start time of the loop
        avg_fps = round(sum(f_sl)/AVG)

        run_all(target_fps, FPS, avg_fps)
        diff = (time.time() - start_time)
        # FPS = 1 / time to process loop
        try:
            nFPS = round(1.0 / diff)
        except ZeroDivisionError:
            continue

        # if FPS != nFPS:
        #     dv = round(T_FPS / FPS, 5)
        #     print("FPS: ", nFPS, round(diff, 5), dv, target_fps)

        # target_fps = 1.0 / (T_FPS * dv)
        # if nFPS > (nFPS * .1):
        #     target_fps = dv
        fps_l = f_sl + (nFPS,)
        FPS = nFPS

data = { 'count': 100_000}

def run_all(delay, c_fps, avg_fps):
    v = 0 if avg_fps == T_FPS else -20
    if avg_fps > T_FPS:
        v = 20


    data['count'] += v
    d = [x for x in range(data['count'])]
    print(f"FPS: {c_fps:<3}, {avg_fps:<3} - count: {data['count']:,}")

    # time.sleep(delay)

if __name__ == '__main__':
    main()
