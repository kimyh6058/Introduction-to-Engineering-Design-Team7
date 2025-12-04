#!/usr/bin/env pybricks-micropython
import socket
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Stop

ev3 = EV3Brick()

# [모터 설정]
# A: 손목 / D: 몸통 / B: 집게 
wrist = Motor(Port.A)
base = Motor(Port.D)
claw = Motor(Port.B) 

# [센서 설정 - 4번 포트]
sensor = UltrasonicSensor(Port.S4)

# 초기화
wrist.reset_angle(0)
base.reset_angle(0)
SPEED = 300

# [방향 조절]
# 1이라고 썼는데 반대로 돌면 -1로 바꾸기
DIR = 1 

# [유선 서버 설정]
HOST = '0.0.0.0'
PORT = 9999

print("유선 연결 대기 중...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

conn, addr = server.accept()
print("연결됨!")
ev3.speaker.beep()

while True:
    try:
        data = conn.recv(1024).decode('utf-8')
        if not data: break
        msg = data.strip()
        
        # --- [센서] ---
        if msg == 'READ_SENSOR':
            dist = sensor.distance()
            conn.send(str(dist).encode('utf-8'))

        # --- [집게 명령] ---
        elif msg == 'CLAW_GRAB': # 잡기
            claw.run_time(400, 1500, then=Stop.HOLD) 
            conn.send(b'DONE')
        elif msg == 'CLAW_OPEN': # 풀기
            claw.run_time(-200, 800, then=Stop.BRAKE)
            conn.send(b'DONE')
        elif msg == 'CLAW_SHORT_OPEN':
            claw.run_time(-200, 500)
            conn.send(b'DONE')

        # --- [몸통 회전 (방향 반영)] ---
        elif msg == 'BASE_SINK': # 90도 (DIR 곱해서 방향 조절)
            ev3.speaker.beep()
            base.run_angle(SPEED, 190 * DIR)
            conn.send(b'DONE')
        elif msg == 'BASE_BACK': # 180도
            base.run_angle(SPEED, -380 * DIR)
            conn.send(b'DONE')
        elif msg == 'BASE_BIN': # -90도
            base.run_angle(SPEED, -190 * DIR)
            conn.send(b'DONE')
        elif msg == 'BASE_HOME': # 0도
            base.run_target(SPEED, 0)
            conn.send(b'DONE')

        # --- [손목] ---
        elif msg == 'WRIST_FLIP':
            wrist.run_time(-200, 1100, then=Stop.HOLD)
            conn.send(b'DONE')

        elif msg == 'WRIST_HOME':
            wrist.run_time(200, 1100, then=Stop.BRAKE)
            conn.send(b'DONE')
            
    except Exception as e:
        break
conn.close()
