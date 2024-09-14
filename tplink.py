# mostly deprecated as moonraker now supports this natively
# ~/klipper/klippy/extras/tplink.py
import socket
from struct import pack
import time

class TpLink:
    def __init__(self, config):
        self.ip = '192.168.1.139' # smart switch IP, update to read from config?
        self.port = 9999
        self.timeout = 10 #read from config?

        # Register command
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command("POWER_ON",
                                    self.cmd_TogglePowerOn,
                                    desc=self.cmd_PowerOn_help)
        self.gcode.register_command("POWER_OFF",
                                    self.cmd_TogglePowerOff,
                                    desc=self.cmd_PowerOff_help)
    def sendMessage(self, cmd, timeout=10, quiet=False):
        # Send command and receive reply
        try:
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.settimeout(timeout)
            sock_tcp.connect((self.ip, self.port))
            sock_tcp.settimeout(10)
            sock_tcp.send(self.encrypt(cmd))
            data = sock_tcp.recv(2048)
            sock_tcp.close()

            decrypted = self.decrypt(data[4:])

            if quiet:
                print(decrypted)
            else:
                print("Sent:     ", cmd)
                print("Received: ", decrypted)

        except:
            logging.exception("POWER_TOGGLE Socket failure")
            raise
    # Encryption and Decryption of TP-Link Smart Home Protocol
    # XOR Autokey Cipher with starting key = 171

    def encrypt(self,string):
        key = 171
        result = pack(">I", len(string))
        for i in string:
            a = key ^ ord(i)
            key = a
            #result += bytes([a]) #python3
            result += ''.join(chr(a))
        return result

    def decrypt(self,string):
        key = 171
        result = ""
        for n in string: #for python3 do for i in string
            i = ord(n) #for python3, remove line
            a = key ^ i
            key = i
            result += chr(a)
        return result
    cmd_PowerOn_help = "Toggle on the printer's power"
    def cmd_TogglePowerOn(self, gcmd):
        cmd = '{"system":{"set_relay_state":{"state":1}}}'
        self.sendMessage(cmd)
        #self.gcode.respond_info("Powering on")
        #time.sleep(5)
        #self.gcode.respond_info("Powered on")
    cmd_PowerOff_help = "Toggle off the printer's power"
    def cmd_TogglePowerOff(self, gcmd):
        cmd = '{"system":{"set_relay_state":{"state":0}}}'
        self.sendMessage(cmd)


def load_config(config):
    return TpLink(config)
