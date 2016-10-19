import struct
import serial
import time
from socketIO_client import *

BREAK = -256

ser = serial.Serial()
f = open('roombatest.txt', 'w+')

ser.port = "/dev/ttyUSB0"
ser.baudrate = 115200
ser.open()


def write_command(command):
    cmd = ""
    for c in command.split():
        cmd += chr(int(c))
    try:
        ser.write(cmd)
        print(command)
        print("command written")
    except:
        print("error passing commands")


def read_command(inp):
    # inp = raw_input()
    # inp = self.sock.recv(1024)
    # inp2 = self.sock.recv(4096)
    # print inp2

    # clean done
    if inp == "Clean" or inp == "clean":
        clean()

    # charge done
    elif inp == "Charge" or inp == "charge":
        get_charge()

    elif inp == "Sing" or inp == "sing":
        sing_song()

    elif inp == "Current":
        get_current()


def clean():
    write_command("135")


def max():
    write_command("136")


def spot():
    write_command("134")

#Returning bad values

def get_both():
    write_command('148 2 25 23')
    print 'Reading bytes'
    y = 0
    arr = [0, 0, 0, 0, 0, 0, 0, 0]

    while True:

        x = getDecodedBytes(1, "b")

        print x

        if x == 19:
            while True:
                if y < 3:
                    x = getDecodedBytes(1, "B")
                else:
                    x= getDecodedBytes(1, "b")
                print x
                arr[y] = x
                y += 1
                if y == 7:
                    break
            break

    highCharge = arr[2]
    lowCharge = arr[3]

    highCurrent = arr[4]
    lowCurrent = arr[5]

    charge = convertUnsigned(highCharge, lowCharge)
    current = convertSigned(highCurrent, lowCurrent)

    f.write(str(charge))
    f.write('\t')
    f.write(str(current))
    f.write('\n')



def get_charge():
    write_command("148 1 25")
    print "Reading bytes"
    y = 0
    arr = [0, 0, 0, 0, 0, 0]
    time.sleep(0.007)

    # 2 unsigned byte returned, converted at end of function
    while True:

        x = getDecodedBytes(1, "B")

        print x

        if x == 19:
            while True:
                x = getDecodedBytes(1, "B")
                print x
                arr[y] = x
                y += 1
                if y == 5:
                    break
            break

    # converting to integer
    high = arr[2]
    low = arr[3]
    n = convertUnsigned(high, low)
    print 'charge is: '
    print n
    write_command('150 0')
    time.sleep(.5)
    return int(n)


def get_current():
    print("Fetching current")
    # begin stream for battery information
    y = 0
    arr = [0, 0, 0, 0, 0]
    time.sleep(.5)

    write_command("148 1 23")
    print "Reading bytes"
    # time.sleep(0.007)
    # 2 byte SIGNED
    while True:

        x = getDecodedBytes(1, "b")

        print x

        if x == 19:
            while True:
                x = getDecodedBytes(1, "b")
                print x
                arr[y] = x
                y += 1
                if y == 5:
                    break
            break
    # converting to integer
    high = arr[2]
    low = arr[3]
    print 'high is'
    print high
    print 'low is'
    print low


    n = convertSigned(high, low)

    print 'current is: '
    print n  # contains final converted value as an 64 bit signed int.
    write_command('150 0')
    time.sleep(.5)
    return int(n)


def convertUnsigned(high, low):
    print 'high '
    print high
    print 'low '
    print low
    high = high << 8
    low = low | high
    return low


def convertSigned(high, low):
    print 'high '
    print high
    print 'low '
    print low
    high = high << 8

    if low < 0:
        low = low ^ BREAK

    n = high | low

    return n


'''
Formats needed
b = signed char
B = unsigned char
I = unsigned int
i = signed int
'''


def getDecodedBytes(n, fmt):
    try:
        return struct.unpack(fmt, ser.read(n))[0]
    except serial.SerialException:
        print "Lost connection"
        return None
    except struct.error:
        print "Data corrupted, check timing."
        return None

def reset(*args):  #
    write_command('7')
    time.sleep(5)




write_command("128")
time.sleep(0.5)
#write_command("131")
time.sleep(1)
#clean()

reset()


for i in range(0, 1000, 1):

    #f.write(str(get_current()))
    #f.write('\t')

    time.sleep(1)

    f.write(str(get_charge()))
    f.write('\n')

    #time.sleep(1)



f.close()
ser.close()
