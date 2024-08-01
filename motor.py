import serial
import time
import re
import serial.tools.list_ports


# Configurar la comunicación serial
bridge = serial.Serial(port="COM11", baudrate=115200)

global data

def crc16(data: bytes):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

def motorcurrent(current, motorid):
    cmd_buf = bytes([0x3E, motorid, 0x08, 0xA1, 0x00, 0x00, 0x00, current & 0xFF, (current >> 8) & 0xFF, 0x00, 0x00])
    crc = crc16(cmd_buf)
    cmd_buf += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    bridge.write(cmd_buf)
    time.sleep(0.01)

def motorposition(angle, max_speed, direction, motorid):
    global data
    cmd_buf = bytes([0x3E, motorid, 0x08, 0xA4, 0x00, max_speed & 0xFF, (max_speed >> 8) & 0xFF,
                     angle  & 0xFF, (angle  >> 8) & 0xFF, (angle >> 16) & 0xFF, (angle >> 24) & 0xFF])
    crc = crc16(cmd_buf)
    cmd_buf += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    bridge.write(cmd_buf)
    angle2 = angle - 5
    angle3 = angle + 5
    while True:
        readPosition()
        if data == str(angle2) or data == str(angle3):
            break

def motorspeed(speed, motorid):
    cmd_buf = bytes([0x3E, motorid, 0x08, 0xA2, 0x00, 0x00, 0x00, speed & 0xFF, (speed >> 8) & 0xFF,
                     (speed >> 16) & 0xFF, (speed >> 24) & 0xFF])
    crc = crc16(cmd_buf)
    cmd_buf += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    bridge.write(cmd_buf)
    time.sleep(0.01)

def positionloop(pos1, pos2, max_speed, max_speed2, motorid):
    global data
    cmd_buf = bytes([0x3E, motorid, 0x08, 0xA4, 0x00, max_speed * 6 & 0xFF, (max_speed * 6 >> 8) & 0xFF,
                     pos1 * 600 & 0xFF, (pos1 * 600 >> 8) & 0xFF, (pos1 * 600 >> 16) & 0xFF, (pos1 * 600 >> 24) & 0xFF])
    cmd_buf1 = bytes([0x3E, motorid, 0x08, 0xA4, 0x00, max_speed2 * 6 & 0xFF, (max_speed2 * 6 >> 8) & 0xFF,
                      pos2 * 600 & 0xFF, (pos2 * 600 >> 8) & 0xFF, (pos2 * 600 >> 16) & 0xFF, (pos2 * 600 >> 24) & 0xFF])
    crc = crc16(cmd_buf)
    crc1 = crc16(cmd_buf1)
    cmd_buf += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    cmd_buf1 += bytes([crc1 & 0xFF, (crc1 >> 8) & 0xFF])
    while True:
        bridge.write(cmd_buf)
        time.sleep(0.01)
        while True:
            readPosition()
            if data == str(pos1):
                break
        bridge.write(cmd_buf1)
        time.sleep(0.01)
        while True:
            readPosition()
            if data == str(pos2):
                break

def positionloop2(pos1, pos2, time1, time2, motorid):
    global data
    max_speed = abs(int(pos1 * 600 / time1))
    max_speed2 = abs(int(pos2 * 600 / time2))
    cmd_buf = bytes([0x3E, motorid, 0x08, 0xA4, 0x00, max_speed * 6 & 0xFF, (max_speed * 6 >> 8) & 0xFF,
                     pos1 * 600 & 0xFF, (pos1 * 600 >> 8) & 0xFF, (pos1 * 600 >> 16) & 0xFF, (pos1 * 600 >> 24) & 0xFF])
    cmd_buf1 = bytes([0x3E, motorid, 0x08, 0xA4, 0x00, max_speed2 * 6 & 0xFF, (max_speed2 * 6 >> 8) & 0xFF,
                      pos2 * 600 & 0xFF, (pos2 * 600 >> 8) & 0xFF, (pos2 * 600 >> 16) & 0xFF, (pos2 * 600 >> 24) & 0xFF])
    crc = crc16(cmd_buf)
    crc1 = crc16(cmd_buf1)
    cmd_buf += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    cmd_buf1 += bytes([crc1 & 0xFF, (crc1 >> 8) & 0xFF])
    while True:
        bridge.write(cmd_buf)
        time.sleep(0.01)
        while True:
            readPosition()
            if data == str(pos1):
                break
        bridge.write(cmd_buf1)
        time.sleep(0.01)
        while True:
            readPosition()
            if data == str(pos2):
                break

def readPosition():
    global data
    cmd_buf = bytes([0x3E, motorid, 0x08, 0x92, 0x00, 0x00, 0x00, 0x00, 0x00])
    crc = crc16(cmd_buf)
    cmd_buf += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    bridge.write(cmd_buf)
    time.sleep(0.01)
    data = bridge.readline()
    data = [int(s) for s in re.findall(r'\b\d+\b', str(data))]
    data = ''.join(filter(str.isdigit, str(data)))

def initmotor():
    cmd_buf = bytes([0x3E, motorid, 0x08, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00])
    crc = crc16(cmd_buf)
    cmd_buf += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    bridge.write(cmd_buf)
    time.sleep(3)

if __name__ == '__main__':
    motorid = int(input("Motorid:"), 16)
    initmotor()
    print("Select control:")
    print("1 ----- Current control")
    print("2 ----- Position control")
    print("3 ----- Speed control")
    print("4 ----- Position Loop")
    print("5 ----- Position Loop 2")
    controltype = input("Control number:")

    if int(controltype) == 1:
        motorid = int(input("Motorid:"), 16)
        while True:
            current = int(input("Current value:"))
            motorcurrent(current, motorid)

    if int(controltype) == 2:
        motorid = int(input("Motorid:"), 16)
        while True:
            angle = int(input("Angle value (degree):"))
            max_speed = int(input("Max speed value(degree per second):"))
            print("0 ----- Clockwise")
            print("1 ----- Anticlockwise")
            direction = int(input("Direction value:"))
            motorposition(angle, max_speed, direction, motorid)

    if int(controltype) == 3:
        motorid = int(input("Motorid:"), 16)
        while True:
            speed = int(input("Speed value(degree per second):"))
            speed = speed
            motorspeed(speed, motorid)

    if int(controltype) == 4:
        motorid = int(input("Motorid:"), 16)
        while True:
            pos1 = int(input("Position 1 value (degree):"))
            max_speed = int(input("Speed(degree per second):"))
            pos2 = int(input("Position 2 value (degree):"))
            max_speed2 = int(input("Speed2 (degree per second):"))
            positionloop(pos1, pos2, max_speed, max_speed2, motorid)

    if int(controltype) == 5:
        motorid = int(input("Motorid:"), 16)
        while True:
            pos1 = int(input("Position 1 value (degree):"))
            time1 = float(input("Time (second):"))
            pos2 = int(input("Position 2 value (degree):"))
            time2 = float(input("Time(second):"))
            positionloop2(pos1, pos2, time1, time2, motorid)