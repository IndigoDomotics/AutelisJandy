# noqa pylint: disable=too-many-lines, invalid-name, unused-argument, redefined-builtin, broad-except, fixme

"""
####################
# Copyright (c) 2011, SSI. All rights reserved.
# Note: This plugin was converted to open source by its author in 2023.

2023-04-29 - Updated to Python 3 and Indigo API 3.0 - DaveL17

"""
from Autelis import Autelis
import logging
try:
    import indigo  # noqa
    # import pydevd
except ImportError:
    pass


class Plugin(indigo.PluginBase):
    """ PLACEHOLDER """

    ######################################################################################
    # class init & del
    def __init__(self, plugin_id, plugin_display_name, plugin_version, plugin_prefs):
        """ PLACEHOLDER """
        indigo.PluginBase.__init__(self, plugin_id, plugin_display_name, plugin_version, plugin_prefs)
        self.autelis = Autelis(self)
        self.debug = self.plugin_prefs.get("showDebugInLog", False)
        self.debug_level = 30
        self.stop_thread = False

        # ================================== Logging ===================================
        log_format = '%(asctime)s.%(msecs)03d\t%(levelname)-10s\t%(name)s.%(funcName)-28s %(message)s'
        self.plugin_file_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt='%Y-%m-%d %H:%M:%S'))
        if self.debug:
            self.debug_level = 10
        self.indigo_log_handler.setLevel(self.debug_level)

        # ============================= Remote Debugging ==============================
        # try:
        #     pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)
        # except NameError:
        #     pass

    def __del__(self):
        """ PLACEHOLDER """
        indigo.PluginBase.__del__(self)

    # =============================== Indigo Methods ===============================
    def device_start_comm(self, dev):
        """ PLACEHOLDER """
        self.autelis.device_start_comm(dev)

    def device_stop_comm(self, dev):
        """ PLACEHOLDER """
        self.autelis.device_stop_comm(dev)

    def run_concurrent_thread(self):
        """ PLACEHOLDER """
        self.logger.debug("Method: run_concurrent_thread")
        self.autelis.run_concurrent_thread()

    def shutdown(self):
        """ PLACEHOLDER """
        self.logger.debug("Method: shutdown")

    def startup(self):
        """ PLACEHOLDER """
        self.logger.debug("Method: startup")
        try:
            if self.plugin_prefs.get("showDebugInfo", False):
                self.debug = True
                self.debug_level = 20
            else:
                self.debug = False
                self.debug_level = 30
        except IndexError:
            pass

    def stop_concurrent_thread(self):
        """ PLACEHOLDER """
        self.logger.debug("Method: stop_concurrent_thread")
        self.stop_thread = True

    def validate_prefs_config_ui(self, values_dict):
        """ PLACEHOLDER """
        return self.autelis.validate_prefs_config_ui(values_dict)

    # =============================== Plugin Methods ===============================
    def action_aqua_pure_boost(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "AquaPureBoost")

    def action_aqua_pure_set(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "AquaPureSet")

    def action_aux(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "AuxDev")

    def action_cleaner(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "Cleaner")

    def action_color_lights_set(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "ColorLightsSet")

    def action_command(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "JandyCommand")

    def action_heat(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "HeatDev")

    def action_keypad_back(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.actionKeypad(plugin_action, "2")

    def action_keypad_pg_dn(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.actionKeypad(plugin_action, "1")

    def action_keypad_pg_up(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.actionKeypad(plugin_action, "3")

    def action_keypad_select(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.actionKeypad(plugin_action, "4")

    def action_keypad_dn(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.actionKeypad(plugin_action, "5")

    def action_keypad_up(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.actionKeypad(plugin_action, "6")

    def action_pump(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "PumpDev")

    def action_setpoints(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "SetpointDev")

    def save_vsp_dev(self, values_dict, type_id, dev_id):  # noqa
        """ PLACEHOLDER """
        return self.autelis.save_vsp_dev(values_dict)

    def action_vsp_speed_set(self, plugin_action):
        """ PLACEHOLDER """
        return self.autelis.action_generic(plugin_action, "VSPSpeedSet")

    ######################################################################################
    # Lists for UI
    def get_aux_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_aux_list()

    def get_pump_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_pump_list()

    def get_heat_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_heat_list()

    def get_setpoint_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_setpoint_list()

    def get_mode_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_mode_list()

    def get_sp_mode_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_sp_mode_list()

    def get_aqua_pure_dev_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_aqua_pure_dev_list()

    def get_aqua_pure_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_aqua_pure_list()

    def get_vsp_dev_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_vsp_dev_list()

    def get_vsp_label_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_vsp_label_list()

    def get_color_lights_list(self, fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ PLACEHOLDER """
        return self.autelis.get_color_lights_list()

    @staticmethod
    def get_aux_devices(fltr="", values_dict=None, type_id="", target_id=0):  # noqa
        """ Generates a list of tuples for config dialogs. """
        return [(f"{n:02}", f"{n}") for n in range(1, 16)]
