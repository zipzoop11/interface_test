from jnius import autoclass
from jnius.jnius import JavaException
from kivy.logger import Logger

import threading
import plyer
from plyer import notification
import json
import time
import random

# Set up the Java stuff
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
CharBuilder = autoclass('java.lang.Character')
UUID = autoclass('java.util.UUID')
autoclass('org.jnius.NativeInvocationHandler')

def rand_sleep():
    time.sleep(round(random.random(), 3))

def get_socket_stream(device):
    #socket = None
    name = device.getName()
    socket = device.createRfcommSocketToServiceRecord(UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
    print("[get_socket_stream] socket: {}".format(socket))
    if socket:
        recv_stream = socket.getInputStream()
        send_stream = socket.getOutputStream()
        try:
            socket.connect()
        except JavaException:
            print("Can't connect!")
            recv_stream, send_stream = None, None
    else:
        print("Can't connect to {}".format(name))
        recv_stream, send_stream = None, None

    if recv_stream and send_stream:
        print("Returning revc_stream and send_stream")
        return recv_stream, send_stream
    else:
        return None, None


class Bluetooth_connection:
    def __init__(self, device_name, out_queue=None, **kwargs):
        self.retry_count = 0
        self.device_name = device_name
        self.out_queue = out_queue
        self.rx_stream, self.tx_stream = None, None
        self.outstanding_commands = dict()
        self.MAX_RETRY = 10
        self.acknowledgements = set()
        self.seq = 0
        self.connected = False
        self.reader = threading.Thread(target=self.rx_thread)
        self.transmitter = threading.Thread(target=self.tx_thread)
        self.tx_queue = dict()
        self.retransmitting = False

    def connect(self):
        self.rx_stream, self.tx_stream = get_socket_stream(self.device_name)

        if self.rx_stream and self.tx_stream:
            self.connected = True
            self.reader.start()
            self.transmitter.start()

            self.send(SYN=True)

            while 0 in self.tx_queue:
                time.sleep(round(random.random(), 3))

            return True

    def disconnect(self):
        self.connected = False
        try:
            self.rx_stream.close()
            self.reader.join()
            self.tx_stream.close()
        except AttributeError as e:
            print(f"Disconnect hit AttributeError: {e}")
        self.rx_stream, self.tx_stream = None, None

        return True

    def rx_thread(self):
        buf = bytearray()
        msg = dict()
        junk = False

        while self.connected:
            try:
                b = self.rx_stream.read()
            except JavaException as e:
                print("RX_THREAD JAVAEXCEPTION: {}".format(e))
                b = None

            if b:
                buf.extend(chr(b).encode('utf-8'))

                # Discard wierd reflected junk
                if buf == b'^[@':
                    junk = True

                if junk and buf[-2:] == b'^J':
                    buf.clear()
                    junk = False

                if chr(b) == '\n' and not junk:

                    #Logger.info("Decoded: {}".format(buf.decode('utf-8')))
                    try:
                        msg = json.loads(buf.decode('utf-8'))
                    except json.JSONDecodeError:
                        msg = None

                    buf.clear()
                    junk = False

            else:
                rand_sleep()

            if msg:
                if msg.get('TYPE') == 'RESPONSE':
                    cmd_id = int(msg['ACK'])

                    while self.retransmitting:
                        rand_sleep()

                    self.acknowledgements.add(cmd_id)
                    print(f"Got an ACK for {cmd_id}")
                    print(msg)

                self.out_queue.put(msg.copy())

                msg.clear()
        print("RX thread exited...")

    def tx_thread(self):
        while self.connected:
            timed_out = []
            time.sleep(random.randint(1, 5))
            self.retransmitting = True

            for p in self.acknowledgements:
                try:
                    self.tx_queue.pop(p)
                except KeyError:
                    pass

            self.acknowledgements.clear()

            for p in self.tx_queue:
                pkt = self.tx_queue[p][0]
                retry_count = self.tx_queue[p][1]
                print("TX_THREAD: self.tx_queue[{}] :: {}".format(p, self.tx_queue[p]))
                if self.tx_queue[p][1] >= self.MAX_RETRY:
                    print(f"TX THREAD {pkt} TIMED OUT!!!")
                    timed_out.append(p)
                else:
                    print("TX THREAD SENDING: {}".format(pkt))
                    self.tx_stream.write(pkt)
                    self.tx_stream.flush()
                    self.tx_queue[p] = pkt, (retry_count + 1)


            for p in timed_out:
                self.tx_queue.pop(p)

            self.retransmitting = False
        print("Tx thread exited...")

    def send(self, msg=None, SYN=False):
        pkt = dict()
        seq = self.seq
        if SYN:
            pkt['TYPE'] = 'SYN'
            seq = 0
            self.seq = 0
            pkt['SEQ'] = seq

        if msg:
            pkt['TYPE'] = 'REQUEST'
            pkt['REQUEST'] = msg
            pkt['SEQ'] = seq

        msg_bytes = json.dumps(pkt).encode('utf-8')

        self.seq += 1
        i = [27, 64]  # ASCII escape integer and at sign integer
        pkt_bytes = bytearray(i)

        pkt_bytes.extend(msg_bytes)
        if chr(pkt_bytes[-1]) != '\n':
            pkt_bytes.extend(b'\n')

        print(f"send() sending: {pkt_bytes}")
        self.tx_stream.write(pkt_bytes)
        self.tx_stream.flush()


        while self.retransmitting:
            rand_sleep()

        self.tx_queue[seq] = pkt_bytes, 0

        return pkt['SEQ']

