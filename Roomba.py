import struct
import serial
import time
import socket
from io import *

PORT = 3141
IP = ''
BREAK = -256
MODE = ''
STATE = 'NULL'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setblocking(1)


#sock.connect(('192.168.1.137', 3141))
sock.connect(('127.0.0.1', 3141))
#datasock.connect(('192.168.1.137', 4444))

'''
This version will be changed to incorporate the new socket techniques used in the DHAM SD smart devices.
Should appear in new branch...
'''

#Must return roomba to passive mode.  Battery can wear.


class Roomba:
    ser = serial.Serial()

    def __init__(self, port, baud):
        self.ser.port = port
        self.ser.baudrate = baud
        self.ser.timeout = 5 #Need timeout?
        print("Initializing serial port.")
        #Serial port initialization
        try:
            self.ser.open()
            print("Serial connected successfully")
        except:
            print 'Error opening serial port'

        self.passive()
        time.sleep(0.5)
        self.safe()  #initialize roomba to safe mode
        #self.full()

        time.sleep(0.5)
        #self.sing_song()

    def write_command(self, command):
        cmd = ""
        for c in command.split():
            cmd += chr(int(c))
        try:
            self.ser.write(cmd)
            print(command)
            print("command written")
        except:
            print("error passing commands")

    def charge(self):
        global STATE
        STATE = 'charge'
        self.write_command("143")
        if MODE != 'P':
            self.passive()
        #wait and signal when the roomba reaches the dock successfully
        while x < 0:
            x = self.get_current()
            print 'waiting'
            time.sleep(.5)




    def sing_song(self):
        #beep
        self.write_command("140 3 1 64 16 141 3")

        #Mary had a little lamb
        #self.write_command("140 3 7 54 16 52 16 50 16 52 16 54 16 54 16 54 16 141 3")

    def passive(self):
        global MODE
        MODE = 'P'
        self.write_command('128')

    def safe(self):
        global MODE
        MODE = 'S'
        self.write_command('131')

    def full(self):
        global MODE
        MODE = 'F'
        self.write_command('132')

    def stop(self):
        global MODE
        MODE = ''
        self.write_command('173')

    def police(self):
        for c in range(0, 10, 1):
            self.write_command("139 8 0 254")
            time.sleep(1)
            self.write_command("139 8 254 254")
            time.sleep(1)

    def clean(self):
        global STATE
        self.write_command("135")
        STATE = 'clean'

    def max(self):
        global STATE
        self.write_command("136")
        STATE = 'max'

    def spot(self):
        global STATE
        self.write_command("134")
        STATE = 'spot'

    #roomba will seek dock but not charge
    def seek_dock(self):
        global STATE
        self.write_command("143")
        STATE = 'delay charge'
        #stream charge
        x = -1
        while x < 0:
            x = self.get_current()
            print 'waiting'
            time.sleep(.5)

        time.sleep(3)

        #back roomba off dock
        if MODE == 'P':
            self.safe()
            time.sleep(.5)

        self.write_command('145 255 56 255 56')
        time.sleep(.5)
        self.write_command('145 0 0 0 0')

        if MODE == 'S':
            self.passive()


# TODO: Need to get max battery charge and convert to percentage.
    def get_charge(self):
        self.write_command("148 1 25")
        print "Reading bytes"
        y = 0
        arr = [0, 0, 0, 0, 0, 0]
        time.sleep(0.007)

        # 2 unsigned byte returned, converted at end of function
        while True:

            x = self.getDecodedBytes(1, "B")

            print x

            if x == 19:
                while True:
                    x = self.getDecodedBytes(1, "B")
                    arr[y] = x
                    y+=1
                    if y == 5:
                        break
                break

        # converting to integer
        high = arr[2]
        low = arr[3]
        n = self.convertUnsigned(high, low)
        print 'charge is: '
        print n
        print 'perctage of charge remaining:  '
        print n/6500
        self.write_command('150 0')
        time.sleep(.5)
        n=int(n)
        return n

    #Current returns 2 signed byte
    def get_current(self):
        print("Fetching current")
        # begin stream for battery information
        y = 0
        arr = [0, 0, 0, 0, 0]
        time.sleep(.5)

        self.write_command("148 1 23")
        print "Reading bytes"
        #time.sleep(0.007)
        #2 byte SIGNED
        #TODO TEST THIS
        while True:

            x = self.getDecodedBytes(1, "b")

            print x

            if x == 19:
                while True:
                    x = self.getDecodedBytes(1, "b")
                    arr[y] = x
                    y+=1
                    if y == 5:
                        break
                break
        #converting to integer
        high = arr[2]
        low = arr[3]
        print 'high is'
        print high
        print 'low is'
        print low

        n = self.convertSigned(high, low)

        print 'current is: '
        print n #contains final converted value as an 64 bit signed int.
        self.write_command('150 0')
        time.sleep(.5)
        return int(n)

    #2 byte unsigned value
    def get_voltage(self):
        self.write_command("142 24")
        print "Reading bytes"
        #gets voltage of roomba battery, returns two bytes
        y = 0
        arr = [0,0,0,0,0]

        while True:

            x = self.getDecodedBytes(1, "B")

            print x

            if x == 19:
                while True:
                    x = self.getDecodedBytes(1, "B")
                    arr[y] = x
                    y+=1
                    if y == 5:
                        break
                break

        z = self.convertUnsigned(arr[2], arr[3])
        print 'Voltage of roomba battery is: '
        print z  #contains final converted value as an 64 bit signed int.
        #end stream?  or convert to regular
        print "Exiting Stream"
        self.write_command('150 0')
        time.sleep(.5)
        return int(z)

    def get_capacity(self):
        self.write_command("148 1 26")

        y = 0
        arr = [0, 0, 0, 0, 0]

        while True:

            x = self.getDecodedBytes(1, "B")

            print x

            if x == 19:
                while True:
                    x = self.getDecodedBytes(1, "B")
                    arr[y] = x
                    y+=1
                    if y == 5:
                        break
                break

        high = arr[3]
        low =  arr[4]

        z = self.convertUnsigned(high, low)
        print 'charge is: '
        print z
        self.write_command('150 0')
        time.sleep(.5)
        return int(z)

    def convertUnsigned(self, high, low):
        print 'high '
        print high
        print 'low '
        print low
        high = high << 8
        low = low | high
        return low

    def convertSigned(self, high, low):
        print 'high '
        print high
        print 'low '
        print low
        high = high << 8

        if low<0:
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

    def getDecodedBytes(self, n, fmt):

        try:
            return struct.unpack(fmt, self.ser.read(n))[0]
        except serial.SerialException:
            print "Lost connection"
            return None
        except struct.error:
            print "Data corrupted, check timing."
            return None





#TODO: send back integer values where necessary
def get_state():
    global STATE
    print "sending state"
    state = ''
    state = STATE + '\n'
    print "State:"+STATE
    sock.send(state)
    return STATE

def clean(*args): #
    global STATE
    STATE = 'clean'
    roomba.clean()

def charge(*args): #
    global STATE
    STATE = 'charge'
    roomba.charge()

def sing(*args): #
    roomba.sing_song()

def exit(*args): #
    roomba.write_command('128')

def current(*args): #
    x = roomba.get_current()
    #need to emit

def safe(*args): #
    roomba.write_command('131')

def reset(*args): #
    roomba.write_command('7')
    time.sleep(5)
    roomba.write_command('128')
    time.sleep(5)
    safe()

def spot(*args): #
    print 'spot activated'
    roomba.write_command('134')

def max(*args): #
    global STATE
    STATE = 'max'
    print 'max activated'
    roomba.write_command('136')

def battery_charge(*args): #
    print 'charge activated'
    x = roomba.get_charge()
    #need to emit x
    x = str(x)
    #socketIO.emit(x)
    socket.send(x)


def battery_capacity(*args):
    print 'capacity' #is this necessary?

def voltage(*args):
    x = roomba.get_voltage()
    x = str(x)
    #socketIO.emit(x)
    socket.send(x)

def seek_dock(*args):
    print 'seek dock activated'
    roomba.seek_dock()

def end_connection():
    datasock.close()
    sock.close()
    print "connection ceased\n"


def readCommand(cmd):
    print "entered read command"

    # cmd_decoded = cmd.decode("utf-8")
    print cmd

    if cmd == "clean":
        clean()
        print 'Sending ack'
        sock.send("clean\n")
    elif cmd == "max":
        max()
        sock.send("max\n")
    elif cmd == "charge":
        charge()
        sock.send("charge\n")#TODO: Need to send ack back AFTER the roomba reaches dock
    elif cmd == 'get_charge':
        #returns current battery charge in a percentage
        #write is done in get_charge function.
        battery_charge()
    elif cmd == "seek_dock":
        seek_dock()
        sock.send("seek dock\n")#TODO: Need to send ack back after roomba reaches dock
    elif cmd == "state":
        get_state()
    elif cmd == 'kill':
        end_connection()


#roomba = Roomba("R1", "/dev/tty.usbserial-DA01NUHC", 115200)

'''
Begin "main"
Declare roomba
create socket instances
begin listening to instructions
'''

roomba = Roomba("/dev/ttyUSB0", 115200)
roomba.sing_song()

while 1:
    cmd = ''

    cmd = sock.recv(56)
    print cmd
    readCommand(cmd)



'''

try:
    socketIO = SocketIO("192.168.1.137", 3141)
    #socketIO = SocketIO("127.0.0.1", 4444)
except:
    print 'issue connecting to server'

Uncomment out to use socket IO instead of direct socket connection

Socket IO goes through the node js server setup in DHam project
while True:
    socketIO.once('clean', clean)
    socketIO.wait(seconds=1)

    socketIO.once('current', current)
    socketIO.wait(seconds=1)

    socketIO.once('charge', charge)
    socketIO.wait(seconds=1)

    socketIO.once('seek_dock', seek_dock)
    socketIO.wait(seconds=1)

    socketIO.once('beep', sing)
    socketIO.wait(seconds=1)

    socketIO.once('exit', exit)
    socketIO.wait(seconds = 1)

    socketIO.once('safe', safe)
    socketIO.wait(seconds=1)

    socketIO.once('reset', reset)
    socketIO.wait(seconds=1)

    socketIO.once('spot', spot)
    socketIO.wait(seconds=1)

    socketIO.once('battery_capacity', battery_capacity)
    socketIO.wait(seconds=1)

    socketIO.once('max', max)
    socketIO.wait(seconds=1)

    socketIO.once('battery_charge', battery_charge)
    socketIO.wait(seconds=1)

    socketIO.once('voltage', voltage)
    socketIO.wait(seconds=1)'''