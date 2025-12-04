#!/usr/bin/env pybricks-micropython
import socket
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch

ev3 = EV3Brick()

# [모터 설정]
# 리프트 모터(미디엄)
lift_A = Motor(Port.A)
lift_D = Motor(Port.D)

# [유선 연결 설정]
TARGET_HOST = '169.254.187.149' # 아래 ev3브릭 IP
TARGET_PORT = 9999

print("유선 연결 대기 중...") # 연결중 확인
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True: # 연결 대기
    try:
        client.connect((TARGET_HOST, TARGET_PORT))
        break
    except:
        wait(1000)
print("연결됨!") # 연결 완료 확인
ev3.speaker.beep() # 연결 완료 음성 알림

LIFT_SPEED = 200 # 리프트 속도 설정

# [함수] 리프트 제어
def run_lift(angle):
    if angle > 0:
        # [올리기] (Stop.HOLD로 버티기)
        lift_A.run_time(-200, 1000, then=Stop.HOLD, wait=False)
        lift_D.run_time(300, 1000, then=Stop.HOLD, wait=True)
    else:
        # [내리기] (Stop.COAST로 힘 풀기)
        lift_A.run_time(200, 700, then=Stop.COAST, wait=False)
        lift_D.run_time(-200, 700, then=Stop.COAST, wait=True)

# [함수] 명령 보내기
def send_cmd(cmd):
    print("Send:", cmd)
    client.send(cmd.encode('utf-8'))
    
    watch = StopWatch()
    watch.reset()
    
    while watch.time() < 3000:
        try:
            client.settimeout(0.1) 
            data = client.recv(1024).decode('utf-8')
            if 'DONE' in data:
                break 
        except:
            pass
            
    client.settimeout(None)

# [함수] 센서 값 물어보기
def get_remote_dist():
    try:
        client.send(b'READ_SENSOR')
        return int(client.recv(1024).decode('utf-8'))
    except: return 9999

# --- 메인 로직 ---
while True:
    dist = get_remote_dist()
    
    if dist < 100: 
        ev3.speaker.beep()
        wait(2000)
        print("Detect:", dist)
        
        # [PHASE 1] 잔여물 비우기 
        send_cmd('CLAW_GRAB')     
        wait(500)
        run_lift(1)
        send_cmd('BASE_BACK')
        send_cmd('WRIST_FLIP')
        wait(1500)
        send_cmd('WRIST_HOME')
        wait(500)
        lift_A.run_time(200, 400, then=Stop.HOLD, wait=False)
        lift_D.run_time(-200, 400, then=Stop.HOLD, wait=True)
        sned_cmd('BASE_HOME')
        wait(500)
        send_cmd('BASE_BIN')
        wait(1000)
        send_cmd('CLAW_OPEN')    
        wait(500)
        send_cmd('BASE_HOME')
        wait(500)
        run_lift(-1)
        ev3.speaker.beep()
        wait(2000)

    wait(100)
