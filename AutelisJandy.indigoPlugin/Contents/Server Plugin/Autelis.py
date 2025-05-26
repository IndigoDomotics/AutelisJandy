# noqa pylint: disable=too-many-lines, invalid-name, unused-argument, redefined-builtin, broad-except, fixme

"""
####################
# Copyright (c) 2011, SSI. All rights reserved.
# Note: This plugin was converted to open source by its author in 2023.
"""

import binascii
import logging
import re
# from socket import *
from socket import AF_INET, SOCK_STREAM, socket
try:
    import indigo  # noqa
except ImportError:
    pass

HLL = None
JANDY_EOM = "0D"
JANDY_EOL = "0A"
KP = {}
KP_HL = ""
KPS = None
SECONDS_BETWEEN_SENDING = 0.25
SOCKET_TIMEOUT = 0.25
NOT_HANDLED_BY_PLUGIN = "\tMessage not handled by plugin"
MAX_NUMBER_OF_AUX = 15
VSPDev = None

ColorLights = [
    'Alpine White',
    'Sky Blue',
    'Cobalt Blue',
    'Caribbean Blu',
    'Spring Green',
    'Emerald Green',
    'Magenta',
    'Violet',
    'Slow Splash',
    'Fast Splash',
    'USA!!!',
    'Fat Tuesday',
    'Disco Tech'
]

my_logger = logging.getLogger("Plugin")


# class Autelis(object):  # FIXME: delete if working.  DaveL17
class Autelis:
    """ PLACEHOLDER """

    # class init & del
    def __init__(self, plugin):
        """ PLACEHOLDER """
        self.aqua_pure = False
        self.aux_list = []
        self.cl_dev = None
        self.color_lights = False
        self.connected = False
        self.device_list = []
        self.enable_udp = False
        self.keypad_updates = False
        self.need_to_get_plugin_prefs = True
        self.number_of_aux = 1
        self.plugin = plugin
        self.socket_ip = None
        self.socket_port = None
        self.udp_port = None
        self.vsp1 = False
        self.vsp1_list = []
        self.vsp2 = False
        self.vsp2_list = []
        self.vsp3 = False
        self.vsp3_list = []
        self.vsp4 = False
        self.vsp4_list = []
        self.sock = None

    def __del__(self):
        """ PLACEHOLDER """
        pass

    def device_start_comm(self, device):
        """ PLACEHOLDER """
        my_logger.debug("Starting device: " + device.name)
        if device.id not in self.device_list:
            self.device_list.append(device.id)
            device.stateListOrDisplayStateIdChanged()

    def device_stop_comm(self, device):
        """ PLACEHOLDER """
        my_logger.debug("Stopping device: " + device.name)
        if device.id in self.device_list:
            self.device_list.remove(device.id)

    # Concurrent Thread Start
    def run_concurrent_thread(self):
        """ PLACEHOLDER """

        my_logger.debug("Running Concurrent Thread")

        # time_start = time.time()

        while not self.plugin.stop_thread:

            if self.need_to_get_plugin_prefs:
                self.connected = False

                if self.get_plugin_prefs():
                    self.close_connection()
                    self.open_connection()

            if self.connected:
                self.check_for_messages()

            self.plugin.sleep(0.01)

        # TODO: This bit was commented out when I got the plugin and can go maybe?  DaveL17
        # if (time.time() - time_start) >= 2:
        # 	self.parseKeypad()
        # 		self.send_message("#OPMODE?")
        # 	time_start = time.time()

        if self.connected:
            self.close_connection()

    # Open connections
    def open_connection(self):
        """ PLACEHOLDER """
        my_logger.debug("Opening connection....")
        self.sock = socket(AF_INET, SOCK_STREAM)
        try:
            self.sock.settimeout(SOCKET_TIMEOUT)
            self.sock.connect((self.socket_ip, int(self.socket_port)))
            indigo.server.log(f"Socket: {self.socket_ip}:{self.socket_port} connected successfully")

        except Exception as err:
            my_logger.error(
                f"Socket: {self.socket_ip}:{self.socket_port} failed to connect. Please check the plugin configuration."
            )
            my_logger.error(f"open_connection error: {err}")
            return

        self.connected = True
        self.poll_jandy()

    # Close connections
    def close_connection(self):
        """ PLACEHOLDER """
        try:
            self.sock.close()
            indigo.server.log(f"Socket: {self.socket_ip}:{self.socket_port} closed successfully.")

        except Exception as err:
            my_logger.error(f"Socket: {self.socket_ip}:{self.socket_port} not open to close.")
            my_logger.error(f"open_connection error: {err}")

    # Sending and Receiving
    def send_message(self, msg):
        """ PLACEHOLDER """
        my_logger.debug(f"TX: {msg}")
        msg += chr(self.hex2dec(JANDY_EOM))
        try:
            self.sock.send(msg.encode('utf-8'))

        except Exception as err:
            my_logger.error(f"send_message Error: {err}")
            self.close_connection()
            self.open_connection()

        self.plugin.sleep(SECONDS_BETWEEN_SENDING)

        if msg.find("KEYPAD") != -1:
            self.plugin.sleep(0.5)

    def read_socket(self):
        """ PLACEHOLDER """
        msg = []
        try:
            while True:
                data = self.sock.recv(1)

                if data == binascii.unhexlify(JANDY_EOL):
                    break

                msg.append(data.decode('utf-8'))
            my_logger.debug(f"RX: {msg}")
            return msg

        except Exception:  # noqa
            # The only errors we're seeing here are timeouts which we ignore.  DaveL17
            # my_logger.error(f"read_socket error: {err}")
            pass

    def check_for_messages(self):
        """ PLACEHOLDER

        Messages that start with '!00' are successful messages
        "!00 POOLTMP=80 F\r\n"
        "!00 AUX1=0\r\n"
        "!00 POOLSP=84 F\r\n"

        An invalid command results in a '?01 INVALID COMMAND' response.
        """
        # Check for messages
        while True:
            msg = self.read_socket()

            if msg is None:
                break

            my_logger.debug(f"{''.join(msg)}")
            self.process_jandy("".join(msg))

    def action_generic(self, plugin_action, action):
        """ PLACEHOLDER """
        # Actions
        global KP_HL
        global HLL
        global KP
        global KPS
        out_msg = ""

        # FIXME: not sure what this is for, but it doesn't do anything meaningful at the moment. DaveL17
        for dev in indigo.devices.iter("self.AutelisController"):
            device_id = dev
            break

        match action:
            case "AuxDev":
                aux_dev = str(int(plugin_action.props.get("AuxDev")) + 1)
                setting = plugin_action.props.get("setting")
                match setting:
                    case "Off":
                        out_msg = f"#AUX{aux_dev}=FALSE"

                    case "On":
                        out_msg = f"#AUX{aux_dev}=TRUE"

                    case "Toggle":
                        out_msg = f"#AUX{aux_dev}"

                self.send_message(out_msg)

            case "PumpDev":
                pump_dev = plugin_action.props.get("PumpDev")
                setting = plugin_action.props.get("setting")

                match pump_dev:
                    case "Pool":
                        out_msg = "#PUMP"

                    case "Low Speed  - Pool":
                        out_msg = "#PUMPLO"

                    case"Spa":
                        out_msg = "#SPA"

                match setting:
                    case "Off":
                        out_msg += "=FALSE"

                    case "On":
                        out_msg += "=TRUE"

                self.send_message(out_msg)

            case "HeatDev":
                heat_dev = plugin_action.props.get("HeatDev")
                setting = plugin_action.props.get("setting")

                match heat_dev:
                    case "Pool":
                        out_msg = "#POOLHT"

                    case "Pool 2":
                        out_msg = "#POOLHT2"

                    case "Spa":
                        out_msg = "#SPAHT"

                    case "Solar":
                        out_msg = "#SOLHT"

                match setting:
                    case "Off":
                        out_msg += "=FALSE"

                    case "On":
                        out_msg += "=TRUE"

                self.send_message(out_msg)

            case "SetpointDev":
                setpoint_dev = plugin_action.props.get("SetpointDev")
                setting = plugin_action.props.get("setting")

                match setpoint_dev:
                    case "Pool":
                        out_msg = "#POOLSP"

                    case "Pool 2":
                        out_msg = "#POOLSP2"

                    case "Spa":
                        out_msg = "#SPASP"

                match setting:
                    case "Down":
                        out_msg += "-"

                    case "Up":
                        out_msg += "+"

                    case "Set":
                        out_msg = out_msg + "=" + plugin_action.props.get("temp")

                self.send_message(out_msg)

            case "Cleaner":
                setting = plugin_action.props.get("setting")

                match setting:
                    case "Off":
                        out_msg = "#CLEANR=FALSE"

                    case "On":
                        out_msg = "#CLEANR=TRUE"

                    case "Toggle":
                        out_msg = "#CLEANR"

                self.send_message(out_msg)

            case "JandyCommand":
                setting = plugin_action.props.get("setting")
                self.send_message(setting)

            case "AquaPureSet":
                setting = int(plugin_action.props.get("setting")[:-1])
                self.nav_kp_menu()

                while KP_HL.find("SET aqua_pure") == -1:
                    self.send_message("#KEYPAD=5")

                self.send_message("#KEYPAD=4")
                if plugin_action.props.get("AquaPureDev") == "Pool":
                    while KP_HL.find("SET POOL TO:") == -1:
                        self.send_message("#KEYPAD=5")

                else:
                    while KP_HL.find("SET SPA TO:") == -1:
                        self.send_message("#KEYPAD=5")

                in_row = HLL
                self.send_message("#KEYPAD=4")
                cur = int(str.strip(KP[in_row].split(":")[1])[:-1])
                # FIXME: Commented out in original file.  Leaving for now. DaveL17
                # cur = int(str.strip(KP_HL.split(":")[1])[:-1])

                if cur < setting:
                    while cur < setting:
                        self.send_message("#KEYPAD=6")
                        cur = int(str.strip(KP[in_row].split(":")[1])[:-1])
                        my_logger.debug(f"aqua_pure up:{cur}:{setting}")

                elif cur > setting:
                    while cur > setting:
                        self.send_message("#KEYPAD=5")
                        cur = int(str.strip(KP[in_row].split(":")[1])[:-1])
                        my_logger.debug(f"aqua_pure dn:{cur}:{setting}")

                # Send message 4-2-2
                for _ in ["#KEYPAD=4", "#KEYPAD=2", "#KEYPAD=2"]:
                    self.send_message(_)

            case "AquaPureBoost":
                self.nav_kp_menu()

                while KP_HL.find("BOOST POOL") == -1:
                    self.send_message("#KEYPAD=5")

                # Send message 4-4-2-2
                for _ in ["#KEYPAD=4", "#KEYPAD=4", "#KEYPAD=2", "#KEYPAD=2"]:
                    self.send_message(_)

            case "VSPSpeedSet":
                self.nav_kp_equip()

                while KP_HL.find(plugin_action.props.get("VSPDev") + " SPD ADJ") == -1:
                    self.send_message("#KEYPAD=5")

                self.send_message("#KEYPAD=4")

                if KP_HL[-2:-1] == 'X':
                    vps_hl = str.strip(KP_HL[1:-2])

                else:
                    vps_hl = str.strip(KP_HL[1:-1])

                while str.strip(vps_hl) != plugin_action.props.get("setting"):
                    self.send_message("#KEYPAD=5")

                    if KP_HL[-2:-1] == 'X':
                        vps_hl = str.strip(KP_HL[1:-2])

                    else:
                        vps_hl = str.strip(KP_HL[1:-1])

                # Send message 4-4-4-4-4-2-2
                for _ in ["#KEYPAD=4", "#KEYPAD=4", "#KEYPAD=4", "#KEYPAD=4", "#KEYPAD=4", "#KEYPAD=2", "#KEYPAD=2"]:
                    self.send_message(_)

            case "ColorLightsSet":
                self.nav_kp_equip()

                cl_dev_name = self.aux_list[int(self.cl_dev) - 1][1]
                cl_dev_state = str.upper(str(dev.states["AUX" + str(int(self.cl_dev))]))

                # while KP_HL.find(CLDevName + " " + CLDevState) == -1:
                while KP_HL.find(cl_dev_name) == -1 or KP_HL.find(cl_dev_state) == -1:
                    my_logger.debug(f"Dev:{cl_dev_name}, State:{cl_dev_state}")
                    self.send_message("#KEYPAD=5")

                self.send_message("#KEYPAD=4")

                if cl_dev_state == "ON":
                    # FIXME: Commented out in original file.  Leaving for now. DaveL17
                    # while KPS.find("LIGHT WILL TURN") == -1:
                    # 	self.plugin.sleep (0.1)
                    # self.plugin.sleep (1)
                    # self.send_message("#KEYPAD=4")
                    out_msg = "#AUX" + self.cl_dev + "=0"
                    self.send_message(out_msg)

                while KP_HL is not None:
                    self.plugin.sleep(0.1)

                while KP_HL.find(plugin_action.props.get("setting")) == -1:
                    self.send_message("#KEYPAD=5")

                self.send_message("#KEYPAD=4")

            case _:
                return

    def actionKeypad(self, plugin_action, action):  # noqa
        """ PLACEHOLDER """
        self.send_message("#KEYPAD=" + action)

    def nav_kp_home(self):
        """ PLACEHOLDER """
        global KP_HL
        global KPS
        global HLL

        # DaveL17 Users were encountering a None Type error when trying to set pump speed. I've added a simple way to
        # avoid evaluating the variable if the value is None, and some logging to see if the variable is ever populated.
        # It'll have to come from somewhere else because nothing is passed to this method.
        if KP_HL is not None:
            my_logger.debug(KP_HL)
            KP_HL = str(KP_HL)
            while KP_HL.find("EQUIPMENT ON/OFF") == -1 and \
                    KP_HL.find("ONETOUCH  ON/OFF") == -1 and \
                    KP_HL.find("MENU / HELP") == -1 and \
                    KP_HL.find("MORE ONETOUCH") == -1 and \
                    KP_HL.find("SYSTEM") == -1:
                self.send_message("#KEYPAD=2")

            if KP_HL.find("MORE ONETOUCH") != -1:
                for _ in ["#KEYPAD=5", "#KEYPAD=4"]:
                    self.send_message(_)

            elif KP_HL.find("SYSTEM") != -1:
                self.send_message("#KEYPAD=4")

    def nav_kp_equip(self):
        """ PLACEHOLDER """
        global KP_HL
        global KPS
        global HLL

        KP_HL = str(KP_HL)
        self.nav_kp_home()
        self.send_message("#KEYPAD=4")

    def nav_kp_menu(self):
        """ PLACEHOLDER """
        global KP_HL
        global KPS
        global HLL

        KP_HL = str(KP_HL)
        while KP_HL.find("EQUIPMENT ON/OFF") == -1 and \
                KP_HL.find("ONETOUCH  ON/OFF") == -1 and \
                KP_HL.find("MENU / HELP") == -1 and \
                KP_HL.find("MORE ONETOUCH") == -1 and \
                KP_HL.find("SYSTEM") == -1:
            self.send_message("#KEYPAD=2")

        if KP_HL.find("EQUIPMENT ON/OFF") != -1:
            for _ in ["#KEYPAD=5", "#KEYPAD=5"]:
                self.send_message(_)

        elif KP_HL.find("ONETOUCH   ON/OFF") != -1:
            self.send_message("#KEYPAD=5")

        elif KP_HL.find("MORE ONETOUCH") != -1:
            for _ in ["#KEYPAD=5", "#KEYPAD=4", "#KEYPAD=5", "#KEYPAD=5"]:
                self.send_message(_)

        elif KP_HL.find("SYSTEM") != -1:
            for _ in ["#KEYPAD=4", "#KEYPAD=5", "#KEYPAD=5"]:
                self.send_message(_)

        self.send_message("#KEYPAD=4")

    def process_jandy(self, msg):
        """ PLACEHOLDER """
        global KP_HL
        global KPS
        global HLL
        global KP
        device_id = None

        for dev in indigo.devices.iter("self.AutelisController"):
            device_id = dev
            break

        # msg = msg[-(len(msg)-4):]
        msg = msg[4:]
        state = msg.split("=")

        if state[0][:3] == "AUX":
            try:
                if int(state[1]) == 0:
                    state[1] = "off"

                else:
                    state[1] = "on"

                self.update_state_on_server(device_id, state[0], state[1])

            except Exception as err:
                my_logger.debug("Error reading Jandy")
                my_logger.error(f"state[0]:[3] - process_jandy error: {err}")

        match state[0]:
            case ("POOLSP" | "POOLSP2" | "ORPLVL1" | "PHLVL1" | "SWCPOOL" | "SALTPOOL" | "ORPFEED1" | "POOLTMP" |
                  "POOLTMP2" | "SPASP" | "SPATMP" | "AIRTMP" | "SOLTMP" | "OPMODE" | "VBAT" | "OPTIONS" | "MODEL" |
                  "UNITS"):
                self.update_state_on_server(device_id, state[0], state[1])

            case ("SPA" | "PUMP" | "PUMPLO" | "WFALL" | "CLEAN"):
                try:
                    if int(state[1]) == 0:
                        state[1] = "off"

                    else:
                        state[1] = "on"

                    self.update_state_on_server(device_id, state[0], state[1])

                except Exception as err:
                    my_logger.debug("Error reading Jandy")
                    my_logger.error(f"state[0] SPA - process_jandy error: {err}")

            case ("POOLHT" | "POOLHT2" | "SPAHT" | "SOLHT"):
                try:
                    match int(state[1]):
                        case 0:
                            state[1] = "off"

                        case 1:
                            state[1] = "enabled"

                        case _:
                            state[1] = "on"

                    self.update_state_on_server(device_id, state[0], state[1])

                except Exception as err:
                    my_logger.debug("Error reading Jandy")
                    my_logger.error(f"state[0] POOLHT - process_jandy error: {err}")

            case ("SWCSPA" | "SALTSPA" | "HTPMP" | "VSP1"):
                self.update_state_on_server(device_id, state[0], state[1])

            case "KEYPAD":
                KP = state[1].split(",")
                kpt = state[1].split(",")
                HLL = int(KP[12])
                e0 = int(KP[13])
                e1 = int(KP[14])
                e2 = int(KP[15])
                e3 = int(KP[16])
                o0 = int(KP[17])
                o1 = int(KP[18])
                o2 = int(KP[19])

                for i in range(0, 12):
                    line = i
                    if o0 > 0 and o1 <= i <= o2:
                        line += o0

                        if line > o2:
                            line -= o2 - o1 + 1

                    kpt[i] = self.get_format(KP[line], i, e0, e1, e2, e3)

                self.update_state_on_server(device_id, "KP_00", kpt[0])
                self.update_state_on_server(device_id, "KP_01", kpt[1])
                self.update_state_on_server(device_id, "KP_02", kpt[2])
                self.update_state_on_server(device_id, "KP_03", kpt[3])
                self.update_state_on_server(device_id, "KP_04", kpt[4])
                self.update_state_on_server(device_id, "KP_05", kpt[5])
                self.update_state_on_server(device_id, "KP_06", kpt[6])
                self.update_state_on_server(device_id, "KP_07", kpt[7])
                self.update_state_on_server(device_id, "KP_08", kpt[8])
                self.update_state_on_server(device_id, "KP_09", kpt[9])
                self.update_state_on_server(device_id, "KP_10", kpt[10])
                self.update_state_on_server(device_id, "KP_11", kpt[11])

                if int(KP[12]) <= 11:
                    KP_HL = str.strip(kpt[HLL])
                    my_logger.debug(f"KP_HL: {KP_HL}")

                else:
                    KP_HL = None

                KPS = "\n".join(KP)
                if KP[0].find("EQUIPMENT STATUS") != -1:
                    if dev.states["PUMP"]:
                        if KPS.find("FILTER PUMP") != -1:
                            if self.aqua_pure:
                                if KPS.find("aqua_pure") != -1:
                                    if KPS.find("CHECK aqua_pure") != -1:
                                        self.update_state_on_server(device_id, "AP_STATUS", "CHECK aqua_pure")

                                    else:
                                        self.update_state_on_server(device_id, "AP_STATUS", "on")

                                    for kpl in KP:
                                        if kpl.find("aqua_pure") != -1 and kpl.find("CHECK") == -1:
                                            self.update_state_on_server(device_id, "AP_SET", str.strip(kpl)[9:])

                                        elif kpl.find("SALT") != -1:
                                            self.update_state_on_server(device_id, "AP_SALT", str.strip(kpl)[5:])

                                elif KPS.find("BOOST POOL") != -1:
                                    self.update_state_on_server(device_id, "AP_STATUS", "boost")

                                    for kpl in KP:
                                        if kpl.find("SALT") != -1:
                                            self.update_state_on_server(device_id, "AP_SALT", str.strip(kpl)[5:])

                                else:
                                    self.update_state_on_server(device_id, "AP_STATUS", "off")
                                    self.update_state_on_server(device_id, "AP_SET", "0%")
                                    self.update_state_on_server(device_id, "AP_SALT", "N/A")

                        if KPS.find("JANDY ePUMP") != -1:
                            for kpl in KP:
                                pump_no = str.strip(kpl)[-1]

                                if kpl.find("JANDY ePUMP") != -1:
                                    self.update_state_on_server(device_id, "P" + pump_no + "_NAME", "JANDY ePUMP")
                                    self.update_state_on_server(device_id, "P" + pump_no + "_STATUS", "online")

                                if kpl.find("RPM") != -1:
                                    self.update_state_on_server(device_id, "P" + pump_no + "_RPM", str.strip(kpl)[5:])

                                elif kpl.find("PRIMING") != -1:
                                    self.update_state_on_server(device_id, "P" + pump_no + "_RPM", "PRIMING")

                                if kpl.find("WATTS") != -1:
                                    self.update_state_on_server(
                                        device_id, "P" + pump_no + "_WATTS", str.strip(str.strip(kpl)[6:])
                                    )

        # Note that this can result in a lot of messages; best to leave off until needed.
        # TODO: Unknown messages caught so far: VSP1=1, SWCSPA=75, SALTSPA=62, HTPMP=1, KPEN=1
        # else:
        #     my_logger.error(f"process_jandy unk msg: {msg}")

    def get_format(self, in_text, line, e0, e1, e2, e3):
        """ PLACEHOLDER """
        # global HLL  # FIXME - using global without assignment.  DaveL17

        if HLL == line:
            in_text = self.reverse(in_text)

        if e0 != '' and e0 == line:
            if e1 < 16 and e2 < 16:
                sub1 = self.get_special_chars(in_text[0:e1])
                sub2 = self.get_special_chars(in_text[e1:e2 + 1])
                sub3 = self.get_special_chars(in_text[e2 + 1:])

                match e3:
                    case 1:
                        # background:#ddd
                        in_text = f"{sub1}{sub2}{sub3}"

                    case 4:
                        in_text = f"{sub1}{self.underline(sub2)}{sub3}"

                return str.strip(in_text)

        return str.strip(self.get_special_chars(in_text))

    @staticmethod
    def get_special_chars(in_text):
        """ PLACEHOLDER """
        in_text = re.sub('`', '\u00b0', in_text)
        in_text = re.sub('_', '\u2193', in_text)
        in_text = re.sub('\\^', '\u2191', in_text)
        in_text = re.sub('>', '\u2192', in_text)
        in_text = re.sub('}', '\u2192', in_text)
        in_text = re.sub('{', '\u2190', in_text)
        return in_text

    @staticmethod
    def underline(in_text):
        """ TODO: Found this method commented out; fixed the Unicode reference.  DaveL17 """
        # for x in in_text:
        # 	in_text = re.sub(x, x + '\u0332', in_text)
        return in_text

    @staticmethod
    def reverse(in_text):
        """ TODO: This method never did anything but return a string wrapped in brackets. DaveL17 """
        return f'[{in_text}]'

    def poll_jandy(self):
        """ PLACEHOLDER

        A question mark (?) designates a query for the state of the equipment or setting specified by the command word.

        An equals sign (=) requires a value to which the equipment specified by the command word will be set. Equipment
        supported values: 1,0,TRUE,FALSE,T,F (case-insensitive) Setpoint supported values: valid integer temperature
        value.

        A plus sign (+) causes a step-up in the value of the equipment or setting specified by the command word. This
        can be a dimmer or a temperature setpoint.

        A minus sign (-) causes a step-down in the value of the equipment or setting specified by the command word. This
        can be a dimmer or a temperature setpoint.

        Example Commands:
        "#POOLTMP?\r"
        "#AUX1=0\r"
        "#POOLSP+\r"
        """
        for i in range(1, int(self.number_of_aux)):
            self.send_message(f"#AUX{i}?")

        for _ in ["#AIRTMP?", "#POOLHT?", "#POOLHT2?", "#POOLSP?", "#POOLSP2?", "#POOLTMP?", "#ORPLVL1", "#SWCPOOL",
                  "#SALTPOOL", "#ORPFEED1", "#PHLVL1", "#PUMP?", "#PUMPLO?", "#SPA?", "#SPAHT?", "#SPASP?", "#SPATMP?",
                  "#SOLHT?", "#SOLTMP?", "#OPMODE?", "#WFALL?", "#CLEANR?", "#VBAT?", "#OPTIONS?", "#MODEL?", "#UNITS?"
                  ]:
            self.send_message(_)

        if self.keypad_updates:
            self.send_message("#KPEN=1")

        else:
            self.send_message("#KPEN=0")

    # TODO: This method is only called in one spot and that call is commented out. No longer needed? I've
    # def parseKeypad(self):
    #     """ PLACEHOLDER """
    #      attempted to update it just in case.  DaveL17
    #     device_id = None
    #     for dev in indigo.devices.iter("self.AutelisController"):
    #         device_id = dev
    #         break
    #     the_url = f"http://{self.socket_ip}/keypad.xml"
    #
    #     # request = urllib2.Request(the_url)
    #     # base64string = base64.encodestring(f'{"admin"}:{self.adminPW}')[:-1]
    #     # request.add_header("Authorization", f"Basic {base64string}")
    #
    #     # TODO: This is the only reference to `self.adminPW`. Not sure how this can work.
    #     base64string = base64.encodestring(f'{"admin"}:{self.adminPW}')[:-1]
    #     headers = "Authorization", f"Basic {base64string}"
    #
    #     try:
    #         # f = urllib2.urlopen(request)
    #         f = requests.get(the_url, headers=headers)
    #     except Exception as err:
    #         my_logger.error(f"Error reading AquaLink status: {the_url}")
    #         return
    #
    #     the_xml = f.read()
    #     # KP = Etree.parse(urllib2.urlopen(request))
    #     k_p = Etree.parse(the_xml)
    #     b0 = k_p.findtext('b0')
    #     b1 = k_p.findtext('b1')
    #     b2 = k_p.findtext('b2')
    #     b3 = k_p.findtext('b3')
    #     b4 = k_p.findtext('b4')
    #     b5 = k_p.findtext('b5')
    #     b6 = k_p.findtext('b6')
    #     b7 = k_p.findtext('b7')
    #     b8 = k_p.findtext('b8')
    #     b9 = k_p.findtext('b9')
    #     b10 = k_p.findtext('b10')
    #     b11 = k_p.findtext('b11')
    #     if b0 is not None:
    #         self.update_state_on_server(device_id, "KP_00", b0)
    #     if b1 is not None:
    #         self.update_state_on_server(device_id, "KP_01", b1)
    #     if b2 is not None:
    #         self.update_state_on_server(device_id, "KP_02", b2)
    #     if b3 is not None:
    #         self.update_state_on_server(device_id, "KP_03", b3)
    #     if b4 is not None:
    #         self.update_state_on_server(device_id, "KP_04", b4)
    #     if b5 is not None:
    #         self.update_state_on_server(device_id, "KP_05", b5)
    #     if b6 is not None:
    #         self.update_state_on_server(device_id, "KP_06", b6)
    #     if b7 is not None:
    #         self.update_state_on_server(device_id, "KP_07", b7)
    #     if b8 is not None:
    #         self.update_state_on_server(device_id, "KP_08", b8)
    #     if b9 is not None:
    #         self.update_state_on_server(device_id, "KP_09", b9)
    #     if b10 is not None:
    #         self.update_state_on_server(device_id, "KP_10", b10)
    #     if b11 is not None:
    #         self.update_state_on_server(device_id, "KP_11", b11)

    # Plugin Preferences
    def get_plugin_prefs(self):
        """ PLACEHOLDER """
        try:
            self.plugin.debug = self.plugin.pluginPrefs.get('showDebugInLog', False)
            self.enable_udp = self.plugin.pluginPrefs.get('enableUDP', False)
            self.keypad_updates = self.plugin.pluginPrefs.get('KeypadUpdates', False)
            self.aqua_pure = self.plugin.pluginPrefs.get('AquaPure', False)
            self.vsp1 = self.plugin.pluginPrefs['VSP1']
            self.vsp2 = self.plugin.pluginPrefs['VSP2']
            self.vsp3 = self.plugin.pluginPrefs['VSP3']
            self.vsp4 = self.plugin.pluginPrefs['VSP4']
            self.color_lights = self.plugin.pluginPrefs['ColorLights']

            my_logger.debug("Getting Plugin Configuration Settings")
            self.socket_ip = self.plugin.pluginPrefs["socketIP"]
            self.socket_port = self.plugin.pluginPrefs.get("socketPort", 6000)
            self.udp_port = self.plugin.pluginPrefs.get("UDPPort", 7890)
            my_logger.debug("\tConnection Type: Socket")
            my_logger.debug(f"\t{'Socket IP:':<20}{self.socket_ip}")
            my_logger.debug(f"\t{'Socket Port:':<20}{self.socket_port}")
            my_logger.debug(f"\t{'Enable UDP:':<20}{self.enable_udp}")
            my_logger.debug(f"\t{'UDP Port:':<20}{self.udp_port}")
            my_logger.debug(f"\t{'Keypad Updates:':<20}{self.keypad_updates}")
            my_logger.debug(f"\t{'aqua_pure:':<20}{self.aqua_pure}")

            my_logger.debug(f"\t{'VSP 1:':<20}{self.vsp1}")
            if self.vsp1:
                self.vsp1_list = []

                for i in range(1, 9):
                    self.vsp1_list.append(self.plugin.pluginPrefs[f"VSP1_S{i}"])
                    my_logger.debug(f"\t\t VPS1 Speed Label {i}:{self.plugin.pluginPrefs[f'VSP1_S{i}']}")

            my_logger.debug(f"\t{'VSP 2:':<20}{self.vsp2}")
            if self.vsp2:
                self.vsp2_list = []

                for i in range(1, 9):
                    self.vsp2_list.append(self.plugin.pluginPrefs[f"VSP2_S{i}"])
                    my_logger.debug(f"\t\t VPS2 Speed Label {i}:{self.plugin.pluginPrefs[f'VSP2_S{i}']}")

            my_logger.debug(f"\t{'VSP 3:':20}{self.vsp3}")
            if self.vsp3:
                self.vsp3_list = []

                for i in range(1, 9):
                    self.vsp3_list.append(self.plugin.pluginPrefs[f"VSP3_S{i}"])
                    my_logger.debug(f"\t\t VPS3 Speed Label {i}:{self.plugin.pluginPrefs[f'VSP3_S{i}']}")

            my_logger.debug(f"\t{'VSP 4:':<20}{self.vsp4}")
            if self.vsp4:
                self.vsp4_list = []

                for i in range(1, 9):
                    self.vsp4_list.append(self.plugin.pluginPrefs[f"VSP4_S{i}"])
                    my_logger.debug(f"\t\t VPS4 Speed Label {i}:{self.plugin.pluginPrefs[f'VSP4_S{i}']}")

            my_logger.debug(f"\tcolor_lights:\t{self.color_lights}")
            if self.color_lights:
                self.cl_dev = self.plugin.pluginPrefs["cl_dev"]
                my_logger.debug(f"\t\t Color Lights Aux Device: {self.cl_dev}")

            self.number_of_aux = self.plugin.pluginPrefs.get("numberOfAux", 6)
            my_logger.debug(f"\t{'Aux Devices:':<20}{self.number_of_aux}")
            self.aux_list = []

            for i in range(1, MAX_NUMBER_OF_AUX + 1):
                if self.plugin.pluginPrefs[f"nameOfAux{i}"] == "":
                    self.plugin.pluginPrefs[f"nameOfAux{i}"] = f"Aux {i}"

                self.aux_list.append((str(i - 1).zfill(2), self.plugin.pluginPrefs[f"nameOfAux{i}"]))

            for i in range(1, int(self.number_of_aux) + 1):
                my_logger.debug(f"\t\tAux {str(i).zfill(2)}:\t\t{self.aux_list[i - 1][1]}")

            indigo.server.log("Saved Plugin Configuration")
            self.need_to_get_plugin_prefs = False
            return True

        except Exception as err:
            my_logger.debug("There was an error reading the plugin preferences. Please check your configuration.")
            my_logger.error(f"get_plugin_prefs error: {err}")
            self.plugin.sleep(3)
            return False

    def validate_prefs_config_ui(self, values_dict):
        """ PLACEHOLDER """
        # UI Validation
        my_logger.debug("Validating Plugin Configuration")
        errors_dict = indigo.Dict()
        if values_dict["socketIP"] == "":
            errors_dict["socketIP"] = "Please enter a socket IP."

        if values_dict["socketPort"] == "":
            errors_dict["socketPort"] = "Please enter a socket port."

        if len(errors_dict) > 0:
            my_logger.debug("\t Validation Errors")
            return False, values_dict, errors_dict

        else:
            my_logger.debug("\t Validation Successful")
            self.need_to_get_plugin_prefs = True
            return True, values_dict

    def get_aux_list(self, fltr=""):  # noqa
        """ PLACEHOLDER """
        # Plug in UI stuff
        my_array = []
        # FIXME: I don't know what 'ANY' is referring to here; it's the only reference. Since there is apparently no
        #  call to this method with a filter expressed, it's probably safe to get rid of it.  DaveL17
        # if fltr == "withAny":
        #     my_array.append((ANY, "Any Device"))
        for i in range(1, int(self.number_of_aux) + 1):
            my_array.append((self.aux_list[i - 1][0], self.aux_list[i - 1][1]))

        return my_array

    @staticmethod
    def get_mode_list():
        """ PLACEHOLDER """
        return ["Off", "On", "Toggle"]

    @staticmethod
    def get_sp_mode_list():
        """ PLACEHOLDER """
        return ["Down", "Up", "Set"]

    @staticmethod
    def get_pump_list():
        """ PLACEHOLDER """
        return ["Pool", "Pool - Low Speed", "Spa"]

    @staticmethod
    def get_heat_list():
        """ PLACEHOLDER """
        return ["Pool", "Pool 2", "Spa", "Solar"]

    @staticmethod
    def get_setpoint_list():
        """ PLACEHOLDER """
        return ["Pool", "Pool 2", "Spa"]

    @staticmethod
    def get_aqua_pure_dev_list():
        """ PLACEHOLDER """
        return ["Pool", "Spa"]

    @staticmethod
    def get_aqua_pure_list():
        """ PLACEHOLDER """
        return [f"{x}%" for x in range(0, 105, 5)]

    def get_vsp_dev_list(self):
        """ PLACEHOLDER """
        my_array = []
        if self.vsp1:
            my_array.append("vsp1")

        if self.vsp2:
            my_array.append("vsp2")

        if self.vsp3:
            my_array.append("vsp3")

        if self.vsp4:
            my_array.append("vsp4")

        return my_array

    @staticmethod
    def save_vsp_dev(values_dict):
        """ PLACEHOLDER """
        global VSPDev
        VSPDev = values_dict["VSPDev"]

    def get_vsp_label_list(self):
        """ PLACEHOLDER """
        # global VSPDev  FIXME: This is unneeded since no assignment is done. DaveL17
        my_array = []
        match VSPDev:
            case "vsp1":
                my_array = self.vsp1_list

            case "vsp2":
                my_array = self.vsp2_list

            case "vsp3":
                my_array = self.vsp3_list

            case "vsp4":
                my_array = self.vsp4_list

        return my_array

    @staticmethod
    def get_color_lights_list():
        """ PLACEHOLDER """
        return ColorLights

    # Utilities
    @staticmethod
    def hexify_and_upper(i):
        """ PLACEHOLDER """
        return binascii.hexlify(i).upper()

    def ascii2hex(self, str_val):
        """ PLACEHOLDER """
        r_str = ord(str_val)
        if 20 <= r_str <= 126:
            r_str = self.dec2hex(r_str)

        else:
            r_str = 20

        return str(r_str)

    @staticmethod
    def hex2dec(str_val):
        """ PLACEHOLDER """
        return int(str_val, 16)

    @staticmethod
    def dec2hex(num):
        """ PLACEHOLDER """
        return f"{num:X}".zfill(2)

    @staticmethod
    def update_state_on_server(dev, state, value):
        """ PLACEHOLDER """
        my_logger.debug(f"\t Updating Device: {dev.name}, State: {state}, Value: {value}")
        dev.updateStateOnServer(state, value=value)
