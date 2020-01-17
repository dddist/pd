
# -*- coding: utf-8 -*-

import can
import os
import sys
from threading import Thread
import time
import datetime
import RPi.GPIO as GPIO


from kivy.app import App
from kivy.properties import NumericProperty
from kivy.properties import BoundedNumericProperty
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter
from kivy.uix.stencilview import StencilView
from kivy.animation import Animation


os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['KIVY_WINDOW'] = 'egl_rpi'

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 120) 
p.start(0)


pwm=99

message_commands = {
    'GET_RPM': 0xF40C,
    'GET_SPEED': 0xF40D,
    'GET_DOORS_COMMAND': 0x220D,
    'GET_OIL_TEMPERATURE': 0x202F,
    'GET_OUTDOOR_TEMPERATURE': 0x1014,
    'GET_INDOOR_TEMPERATURE': 0x2613,
    'GET_COOLANT_TEMPERATURE': 0xF405,
    'GET_KM_LEFT': 0x2294,
    'GET_FUEL_LEFT': 0x229A,
    'GET_TIME': 0x2216,
    'GET_DISTANCE': 0x2203,
    'GET_FUEL_CONSUMPTION': 0x2299,
    'GET_FUEL': 0xDA00,
    'GET_AIR_HEATER': 0xDA10,
    'GET_PEREGREV': 0xDA20,
    'GET_BLOCK': 0xDA30,
    'GET_AIR_FILTER': 0xDA40,
    'GET_AKB': 0xDA50,
    'GET_RUCHNIK': 0xDA60,
    'GET_ZASOR_RUL': 0xDA70,
    'GET_ZASOR_KPP': 0xDA80,
    'GET_TEMPER_BOM': 0xDA90,
    'GET_TORMOZ_AIR': 0xDAA0,
    'GET_ENGINE_PRESSURE': 0xDAB0,
    'GET_POVOROT_P': 0xDAC0,
    'GET_POVOROT_L': 0xDAD0,
    'GET_POVOROT_PRICEP': 0xDAE0,
    'GET_OIL_FILTER': 0xDAF0,
    'GET_BOM_TEMP': 0xDB00,
    'GET_CHECK_ENG': 0xDB10,
    'GET_RABOCHIE_FARY_PERED': 0xDB20,
    'GET_RABOCHIE_FARY_ZAD': 0xDB30,
    'GET_AVTOPOEZD': 0xDB40,
    'GET_VODA_V_TOPLIVE': 0xDB50,
    'GET_START': 0xDB60,
    'GET_DALNIY': 0xDB70,
    'GET_BLIZNIY': 0xDB80,
    'GET_GABARITY': 0xDB90,
    'GET_CLOCK': 0xDC00,
    'GET_KM': 0xDC10,
    'GET_MOTO_HOUR': 0xDC20,
    'GET_FUEL_BAR': 0xDD00,
    'GET_TEMP_BAR': 0xDD10,
    'GET_SPEEDOMETER': 0xDD20,
    'GET_TACHOMETER': 0xDD30,
    'GET_PRESSURE_BOM': 0xDD40,
    'GET_VOLTAGE': 0xDD50,
    'GET_TEMPERATURE_NAVES': 0xDD60,
    'GET_AIR_BRAKE_PRESSURE': 0xDD70,
    'GET_AIR_PRESSURE': 0xDD80,
    'GET_TEMPERATURE_BOM': 0xDD90,
    'GET_KPP_PRESSURE': 0xDDA0,
    'GET_COOLANT_BAR': 0xDDB0,
    'GET_GEAR': 0xDDC0,
    'GET_RYAD': 0xDDD0
}

bus = can.interface.Bus(channel='can0', bustype='socketcan')


class PropertyState(object):
    def __init__(self, last, current):
        self.last = last
        self.current = current

    def last_is_not_now(self):
        return self.last is not self.current
    
class CanListener(can.Listener):
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.speed_states = PropertyState(None, None)
        self.rpm_states = PropertyState(None, None)
        self.km_left_states = PropertyState(None, None)
        self.coolant_temperature_states = PropertyState(None, None)
        self.fuel_left_states = PropertyState(None, None)
        self.oil_temperature_states = PropertyState(None, None)
        self.time_states = PropertyState(None, None)
        self.outdoor_temperature_states = PropertyState(None, None)
        self.distance_states = PropertyState(None, None)
        self.fuel_consumption_states = PropertyState(None, None)
        self.doors_states = PropertyState(None, None)
        self.car_minimized = True
        self.gear_states = PropertyState(None, None)
        self.ryad_states = PropertyState(None, None)
        self.fuel_states = PropertyState(None, None)
        self.air_heater_states = PropertyState(None, None)
        self.peregrev_states = PropertyState(None, None)
        self.block_states = PropertyState(None, None)
        self.air_filter_states = PropertyState(None, None)
        self.akb_states = PropertyState(None, None)
        self.ruchnik_states = PropertyState(None, None)
        self.zasor_rul_states = PropertyState(None, None)
        self.zasor_kpp_states = PropertyState(None, None)
        self.temper_bom_states = PropertyState(None, None)
        self.tormoz_air_states = PropertyState(None, None)
        self.engine_pressure_states = PropertyState(None, None)
        self.povorot_p_states = PropertyState(None, None)
        self.povorot_l_states = PropertyState(None, None)
        self.povorot_pricep_states = PropertyState(None, None)
        self.oil_filter_states = PropertyState(None, None)
        self.bom_temp_states = PropertyState(None, None)
        self.check_eng_states = PropertyState(None, None)
        self.rabochie_fary_pered_states = PropertyState(None, None)
        self.rabochie_fary_zad_states = PropertyState(None, None)
        self.avtopoezd_states = PropertyState(None, None)
        self.voda_v_toplive_states = PropertyState(None, None)
        self.start_states = PropertyState(None, None)
        self.dalniy_states = PropertyState(None, None)
        self.blizniy_states = PropertyState(None, None)
        self.gabarity_states = PropertyState(None, None)
        self.km_states = PropertyState(None, None)
        self.moto_hour_states = PropertyState(None, None) 
        self.temp_bar_states = PropertyState(None, None)
        self.fuel_bar_states = PropertyState(None, None)
        self.kpp_pressure_bar_states = PropertyState(None, None)
        self.clock_states = PropertyState(None, None)
        self.voltage_states = PropertyState(None, None)
        self.air_brake_pressure_states = PropertyState(None, None)
        self.pressure_bom_states = PropertyState(None, None)
        self.air_pressure_states = PropertyState(None, None)
        self.pressure_states = PropertyState(None, None)
    
        
        
    def on_message_received(self, message):    
        
        print('get Message!!!!!')
        global pwm 
        #print nowTime
        self.dashboard.clock.text = datetime.datetime.now().strftime("%H:%M               %d/%m/%y")
       
        message_command = message.data[3] | message.data[2] << 8

        # GEAR                
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_GEAR']:
            self.gear_states.current = message.data[5] | message.data[4] << 8         
            if self.gear_states.last_is_not_now():
                gear = int(self.gear_states.current / 21.2 * 100)
                self.dashboard.gear.text = str(gear)
                self.gear_states.last = self.gear_states.current
                
        # RYAD                
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_RYAD']:
            self.ryad_states.current = message.data[5] | message.data[4] << 8     
            if self.ryad_states.last_is_not_now():
                ryad = self.ryad_states.current / 49
                self.dashboard.ryad.text = str(ryad)
                self.ryad_states.last = self.ryad_states.current

        # FUEL        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_FUEL']:
            self.fuel_states.current = message.data[4]
            print('Fuel MSG: ; ' + str(message.data[4]))
            if self.fuel_states.last_is_not_now():
                self.fuel_states.last = self.fuel_states.current
            if (self.fuel_states.current %2) != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.fuel_grey)
                    self.dashboard.add_widget(self.dashboard.fuel_yellow)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.fuel_yellow)
                    self.dashboard.add_widget(self.dashboard.fuel_grey)
                except:
                    pass
        
        # AIR_HEATER        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_AIR_HEATER']:
            self.air_heater_states.current = message.data[4]
            print('AIR_HEATER MSG: ; ' + str(message.data[4]))
            if self.air_heater_states.last_is_not_now():
                self.air_heater_states.last = self.air_heater_states.current
            if self.air_heater_states.current  != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.air_heater_grey)
                    self.dashboard.add_widget(self.dashboard.air_heater_yellow)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.air_heater_yellow)
                    self.dashboard.add_widget(self.dashboard.air_heater_grey)
                except:
                    pass
        # PEREGREV        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_PEREGREV']:
            self.peregrev_states.current = message.data[4]
            print('PEREGREV MSG: ; ' + str(message.data[4]))
            if self.peregrev_states.last_is_not_now():
                self.peregrev_states.last = self.peregrev_states.current
            if self.peregrev_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.peregrev_grey)
                    self.dashboard.add_widget(self.dashboard.peregrev_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.peregrev_red)
                    self.dashboard.add_widget(self.dashboard.peregrev_grey)
                except:
                    pass
        # BLOCK        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_BLOCK']:
            self.block_states.current = message.data[4]
            if self.block_states.last_is_not_now():
                self.block_states.last = self.block_states.current
            if self.block_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.block_grey)
                    self.dashboard.add_widget(self.dashboard.block_yellow)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.block_yellow)
                    self.dashboard.add_widget(self.dashboard.block_grey)
                except:
                    pass
                    
        # AIR_FILTER        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_AIR_FILTER']:
            self.air_filter_states.current = message.data[4]
            if self.air_filter_states.last_is_not_now():
                self.air_filter_states.last = self.air_filter_states.current
            if self.air_filter_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.air_filter_grey)
                    self.dashboard.add_widget(self.dashboard.air_filter_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.air_filter_red)
                    self.dashboard.add_widget(self.dashboard.air_filter_grey)
                except:
                    pass
        
        # AKB        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_AKB']:
            self.akb_states.current = message.data[4]
            if self.akb_states.last_is_not_now():
                self.akb_states.last = self.akb_states.current
            if self.akb_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.akb_grey)
                    self.dashboard.add_widget(self.dashboard.akb_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.akb_red)
                    self.dashboard.add_widget(self.dashboard.akb_grey)
                except:
                    pass                    

        # RUCHNIK        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_RUCHNIK']:
            self.ruchnik_states.current = message.data[4]
            if self.ruchnik_states.last_is_not_now():
                self.ruchnik_states.last = self.ruchnik_states.current
            if self.ruchnik_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.ruchnik_grey)
                    self.dashboard.add_widget(self.dashboard.ruchnik_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.ruchnik_red)
                    self.dashboard.add_widget(self.dashboard.ruchnik_grey)
                except:
                    pass
                    
        # ZASOR_RUL        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_ZASOR_RUL']:
            self.zasor_rul_states.current = message.data[4]
            if self.zasor_rul_states.last_is_not_now():
                self.zasor_rul_states.last = self.zasor_rul_states.current
            if self.zasor_rul_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.zasor_rul_grey)
                    self.dashboard.add_widget(self.dashboard.zasor_rul_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.zasor_rul_red)
                    self.dashboard.add_widget(self.dashboard.zasor_rul_grey)
                except:
                    pass
                    
        # ZASOR_KPP        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_ZASOR_KPP']:
            self.zasor_kpp_states.current = message.data[4]
            if self.zasor_kpp_states.last_is_not_now():
                self.zasor_kpp_states.last = self.zasor_kpp_states.current
            if self.zasor_kpp_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.zasor_kpp_grey)
                    self.dashboard.add_widget(self.dashboard.zasor_kpp_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.zasor_kpp_red)
                    self.dashboard.add_widget(self.dashboard.zasor_kpp_grey)
                except:
                    pass
                    
        # TEMPER_BOM        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_TEMPER_BOM']:
            self.temper_bom_states.current = message.data[4]
            if self.temper_bom_states.last_is_not_now():
                self.temper_bom_states.last = self.temper_bom_states.current
            if self.temper_bom_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.temper_bom_grey)
                    self.dashboard.add_widget(self.dashboard.temper_bom_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.temper_bom_red)
                    self.dashboard.add_widget(self.dashboard.temper_bom_grey)
                except:
                    pass
            
        # TORMOZ_AIR        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_TORMOZ_AIR']:
            self.tormoz_air_states.current = message.data[4]
            if self.tormoz_air_states.last_is_not_now():
                self.tormoz_air_states.last = self.tormoz_air_states.current
            if self.tormoz_air_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.tormoz_air_grey)
                    self.dashboard.add_widget(self.dashboard.tormoz_air_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.tormoz_air_red)
                    self.dashboard.add_widget(self.dashboard.tormoz_air_grey)
                except:
                    pass
                    
        # ENGINE_PRESSURE        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_ENGINE_PRESSURE']:
            self.engine_pressure_states.current = message.data[4]
            if self.engine_pressure_states.last_is_not_now():
                self.engine_pressure_states.last = self.engine_pressure_states.current
            if self.engine_pressure_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.engine_pressure_grey)
                    self.dashboard.add_widget(self.dashboard.engine_pressure_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.engine_pressure_red)
                    self.dashboard.add_widget(self.dashboard.engine_pressure_grey)
                except:
                    pass
                    
        # POVOROT_P        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_POVOROT_P']:
            self.povorot_p_states.current = message.data[4]
            if self.povorot_p_states.last_is_not_now():
                self.povorot_p_states.last = self.povorot_p_states.current
            if self.povorot_p_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.povorot_p_grey)
                    self.dashboard.add_widget(self.dashboard.povorot_p_green)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.povorot_p_green)
                    self.dashboard.add_widget(self.dashboard.povorot_p_grey)
                except:
                    pass
                    
        # POVOROT_L        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_POVOROT_L']:
            self.povorot_l_states.current = message.data[4]
            if self.povorot_l_states.last_is_not_now():
                self.povorot_l_states.last = self.povorot_l_states.current
            if self.povorot_l_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.povorot_l_grey)
                    self.dashboard.add_widget(self.dashboard.povorot_l_green)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.povorot_l_green)
                    self.dashboard.add_widget(self.dashboard.povorot_l_grey)
                except:
                    pass
                    
        # POVOROT_PRICEP       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_POVOROT_PRICEP']:
            self.povorot_pricep_states.current = message.data[4]
            if self.povorot_pricep_states.last_is_not_now():
                self.povorot_pricep_states.last = self.povorot_pricep_states.current
            if self.povorot_pricep_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.povorot_pricep_grey)
                    self.dashboard.add_widget(self.dashboard.povorot_pricep_green)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.povorot_pricep_green)
                    self.dashboard.add_widget(self.dashboard.povorot_pricep_grey)
                except:
                    pass
                    
        # OIL_FILTER       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_OIL_FILTER']:
            self.oil_filter_states.current = message.data[4]
            if self.oil_filter_states.last_is_not_now():
                self.oil_filter_states.last = self.oil_filter_states.current
            if self.oil_filter_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.oil_filter_grey)
                    self.dashboard.add_widget(self.dashboard.oil_filter_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.oil_filter_red)
                    self.dashboard.add_widget(self.dashboard.oil_filter_grey)
                except:
                    pass
                    
        # BOM_TEMP       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_BOM_TEMP']:
            self.bom_temp_states.current = message.data[4]
            if self.bom_temp_states.last_is_not_now():
                self.bom_temp_states.last = self.bom_temp_states.current
            if self.bom_temp_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.bom_temp_grey)
                    self.dashboard.add_widget(self.dashboard.bom_temp_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.bom_temp_red)
                    self.dashboard.add_widget(self.dashboard.bom_temp_grey)
                except:
                    pass
                    
        # CHECK_ENG       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_CHECK_ENG']:
            self.check_eng_states.current = message.data[4]
            if self.check_eng_states.last_is_not_now():
                self.check_eng_states.last = self.check_eng_states.current
            if self.check_eng_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.check_eng_grey)
                    self.dashboard.add_widget(self.dashboard.check_eng_yellow)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.check_eng_yellow)
                    self.dashboard.add_widget(self.dashboard.check_eng_grey)
                except:
                    pass

        # RABOCHIE_FARY_PERED       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_RABOCHIE_FARY_PERED']:
            self.rabochie_fary_pered_states.current = message.data[4]
            if self.rabochie_fary_pered_states.last_is_not_now():
                self.rabochie_fary_pered_states.last = self.rabochie_fary_pered_states.current
            if self.rabochie_fary_pered_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.rabochie_fary_pered_grey)
                    self.dashboard.add_widget(self.dashboard.rabochie_fary_pered_green)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.rabochie_fary_pered_green)
                    self.dashboard.add_widget(self.dashboard.rabochie_fary_pered_grey)
                except:
                    pass
                    
        # RABOCHIE_FARY_ZAD       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_RABOCHIE_FARY_ZAD']:
            self.rabochie_fary_zad_states.current = message.data[4]
            if self.rabochie_fary_zad_states.last_is_not_now():
                self.rabochie_fary_zad_states.last = self.rabochie_fary_zad_states.current
            if self.rabochie_fary_zad_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.rabochie_fary_zad_grey)
                    self.dashboard.add_widget(self.dashboard.rabochie_fary_zad_green)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.rabochie_fary_zad_green)
                    self.dashboard.add_widget(self.dashboard.rabochie_fary_zad_grey)
                except:
                    pass
                    
        # AVTOPOEZD       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_AVTOPOEZD']:
            self.avtopoezd_states.current = message.data[4]
            if self.avtopoezd_states.last_is_not_now():
                self.avtopoezd_states.last = self.avtopoezd_states.current
            if self.avtopoezd_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.avtopoezd_grey)
                    self.dashboard.add_widget(self.dashboard.avtopoezd_yellow)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.avtopoezd_yellow)
                    self.dashboard.add_widget(self.dashboard.avtopoezd_grey)
                except:
                    pass
                    
        # VODA_V_TOPLIVE       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_VODA_V_TOPLIVE']:
            self.voda_v_toplive_states.current = message.data[4]
            if self.voda_v_toplive_states.last_is_not_now():
                self.voda_v_toplive_states.last = self.voda_v_toplive_states.current
            if self.voda_v_toplive_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.voda_v_toplive_grey)
                    self.dashboard.add_widget(self.dashboard.voda_v_toplive_red)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.voda_v_toplive_red)
                    self.dashboard.add_widget(self.dashboard.voda_v_toplive_grey)
                except:
                    pass
                    
                    
        # START                
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_START']:
            self.start_states.current = message.data[4]         
            if self.start_states.last_is_not_now():  
                self.start_states.last = self.start_states.current
            if self.start_states.current != 0:    
                self.dashboard.start.text = 'Stop'
            else:
                self.dashboard.start.text = 'Start'
                
                            
        # DALNIY       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_DALNIY']:
            self.dalniy_states.current = message.data[4]
            if self.dalniy_states.last_is_not_now():
                self.dalniy_states.last = self.dalniy_states.current
            if self.dalniy_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.dalniy_grey)
                    self.dashboard.add_widget(self.dashboard.dalniy_blue)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.dalniy_blue)
                    self.dashboard.add_widget(self.dashboard.dalniy_grey)
                except:
                    pass

        # BLIZNIY       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_BLIZNIY']:
            self.blizniy_states.current = message.data[4]
            if self.blizniy_states.last_is_not_now():
                self.blizniy_states.last = self.blizniy_states.current
            if self.blizniy_states.current != 0:
                try:
                    self.dashboard.remove_widget(self.dashboard.blizniy_grey)
                    self.dashboard.add_widget(self.dashboard.blizniy_green)
                except:
                    pass
            else:
                try:
                    self.dashboard.remove_widget(self.dashboard.blizniy_green)
                    self.dashboard.add_widget(self.dashboard.blizniy_grey)
                except:
                    pass
                    
                    
        # GABARITY       
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_GABARITY']:
            print "+++++ Check GABRITY ++++++"
            self.gabarity_states.current = message.data[4]
            if self.gabarity_states.last_is_not_now():
                self.gabarity_states.last = self.gabarity_states.current
            if self.gabarity_states.current != 0:
                try:
                    pwm=30
                    self.dashboard.remove_widget(self.dashboard.gabarity_grey)
                    self.dashboard.add_widget(self.dashboard.gabarity_green)
                except:
                    pass
            else:
                try:
                    pwm=100
                    self.dashboard.remove_widget(self.dashboard.gabarity_green)
                    self.dashboard.add_widget(self.dashboard.gabarity_grey)
                except:
                    pass
        
        # Tahometer        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_TACHOMETER']:
            self.rpm_states.current = message.data[5] | message.data[4] << 8 
            if self.rpm_states.last_is_not_now():
                self.dashboard.rpm.value = self.rpm_states.current * 11.7
                #print "dashboard.rpm.value", int(self.rpm_states.current * 11.7)
                self.rpm_states.last = self.rpm_states.current

         
        #Speedometer           
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_SPEEDOMETER']:
            self.speed_states.current = message.data[5] | message.data[4] << 8
            if self.speed_states.last_is_not_now():
                self.dashboard.speed.value = self.speed_states.current * 3.51
                self.speed_states.last = self.speed_states.current
                
                
        # KM                
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_KM']:
            self.km_states.current = message.data[4]         
            if self.km_states.last_is_not_now():
                self.dashboard.km.text = str(self.km_states.current)
                self.km_states.last = self.km_states.current
                
        # Moto_Hour                
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_MOTO_HOUR']:
            self.moto_hour_states.current = message.data[4]         
            if self.moto_hour_states.last_is_not_now():
                self.dashboard.moto_hour.text = str(self.moto_hour_states.current)
                self.moto_hour_states.last = self.moto_hour_states.current
        
        #TEMP        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_COOLANT_BAR']:
            self.temp_bar_states.current = message.data[4]
            if self.temp_bar_states.last_is_not_now():
                temperature = self.temp_bar_states.current
                if temperature > 40:
                    self.dashboard.temp_bar.height = temperature
                    self.temp_bar_states.last = self.temp_bar_states.current
                    
        #FUEL_LEFT
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_FUEL_BAR']:
            self.fuel_bar_states.current = message.data[4]
            if self.fuel_bar_states.last_is_not_now():
                # 55L = 256
                # 0L = 0
                # 1L = 4.65 
                self.dashboard.fuel_bar.height = self.fuel_bar_states.current
                self.fuel_bar_states.last = self.fuel_bar_states.current
                
        #KPP_PRESSURE
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_KPP_PRESSURE']:
            self.kpp_pressure_bar_states.current = message.data[4]
            if self.kpp_pressure_bar_states.last_is_not_now():
                # 55L = 256
                # 0L = 0
                # 1L = 4.65 
                self.dashboard.kpp_pressure_bar.height = self.kpp_pressure_bar_states.current
                self.kpp_pressure_bar_states.last = self.kpp_pressure_bar_states.current
        
        #CLOCK        
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_CLOCK']:
            self.clock_states.current = message.data[5] | message.data[4] << 8
            if self.clock_states.last_is_not_now():
                #self.dashboard.clock.text =  RequestsClock.clock.strftime("%H:%M %d/%m/%Y")
                self.clock_states.last = self.clock_states.current
                
        # VOLTAGE                
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_VOLTAGE']:
            self.voltage_states.current = message.data[5] | message.data[4] << 8     
            if self.voltage_states.last_is_not_now():
                volt = self.voltage_states.current /10.0 
                self.dashboard.voltage.text = str(volt)
                self.voltage_states.last = self.voltage_states.current
                
        # GET_AIR_BRAKE_PRESSURE                      
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_AIR_BRAKE_PRESSURE']:
            self.air_brake_pressure_states.current = message.data[5] | message.data[4] << 8     
            if self.air_brake_pressure_states.last_is_not_now():
                a_b_press = self.air_brake_pressure_states.current  / 100
                self.dashboard.air_brake_pressure.text = str(a_b_press)
                self.air_brake_pressure_states.last = self.air_brake_pressure_states.current
        
        #GET_PRESSURE_BOM
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_PRESSURE_BOM']:
            self.pressure_bom_states.current = message.data[5] | message.data[4] << 8      
            if self.pressure_bom_states.last_is_not_now():
                press_b = self.pressure_bom_states.current / 100
                self.dashboard.pressure_BOM.text = str(press_b)
                self.pressure_bom_states.last = self.pressure_bom_states.current
        
        #GET_AIR_PRESSURE 
        if message.arbitration_id == 0x77E and message_command == message_commands['GET_AIR_PRESSURE']:
            self.air_pressure_states.current = message.data[5] | message.data[4] << 8     
            if self.air_pressure_states.last_is_not_now():
                a_press = self.air_pressure_states.current /100
                self.dashboard.air_pressure.text = str(a_press)
                self.air_pressure_states.last = self.air_pressure_states.current
                
        #GET_COOLANT_BAR
        
       
                
                 
                    
class Dashboard(FloatLayout):
    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)

        # Background
        self.background_image = Image(source='img/back.png')
        self.add_widget(self.background_image)

        # BOTTOM BAR
        self.bottom_bar = Image(source='img/bottomBar.png', pos=(0, -209))
        self.add_widget(self.bottom_bar)
        
        # CLOCK
        self.clock = Label(text='--:--               --/--/--', color=[0.41, 0.42, 0.74, 1], font_name='Avenir.ttc', halign="center", font_size=34,
                           pos=(-0, -205))
        #clock1 = datetime.datetime.now()
        #self.clock.text = clock1.strftime("%H:%M               %d/%m/%y")
        self.add_widget(self.clock)
        

        # Fuel BAR
        self.fuel_left_bar_back = Image(source='img/fuel.png', pos=(380, 50))
        self.add_widget(self.fuel_left_bar_back)

        # fuel_grey
        self.fuel_grey = Image(source='icon1/fuel_grey.png', size =(64, 64), pos=(280, 10))
        self.add_widget(self.fuel_grey)
        
        # fuel_yellow
        self.fuel_yellow = Image(source='icon1/fuel_yellow.png', size =(64, 64), pos=(280, 10))
                
        # air_heater_grey
        self.air_heater_grey = Image(source='icon1/air_heater_grey.png', size =(64, 64), pos=(280, 90))
        self.add_widget(self.air_heater_grey)
        
        # air_heater_yellow
        self.air_heater_yellow = Image(source='icon1/air_heater_yellow.png', size =(64, 64), pos=(280, 90))
                
        # TEMP BAR
        self.temp_bar_back = Image(source='img/temp.png', pos=(-380, 50))
        self.add_widget(self.temp_bar_back)

        # peregrev_grey
        self.peregrev_grey = Image(source='icon1/peregev_grey.png', size =(64, 64), pos=(-280, 10))
        self.add_widget(self.peregrev_grey)
        
        # peregrev_red
        self.peregrev_red = Image(source='icon1/peregev_red.png', size =(64, 64), pos=(-280, 10))

        # block_grey
        self.block_grey = Image(source='icon1/block_grey.png', size =(64, 64), pos=(-280, 90))
        self.add_widget(self.block_grey)
        
        # block_yellow
        self.block_yellow = Image(source='icon1/block_yellow.png', size =(64, 64), pos=(-280, 90))
        



        # Center_panel BAR
        self.centre_panel = Image(source='img/centre_panel.png', pos=(0, 50))
        self.add_widget(self.centre_panel)

        

        
        # Speed
        self.speed = Gauge(file_gauge="img/speedometer640.png", do_rotation=False, do_scale=False, do_translation=False, value=0,
                          size_gauge=512, pos=(5, 150))
        self.add_widget(self.speed)
        self.speed.value = 1
        
        # Tachometer
        self.rpm = Gauge(file_gauge="img/tahometer640.png", do_rotation=False, do_scale=False, do_translation=False, value=0,
                         size_gauge=512, pos=(700, 150))
        self.add_widget(self.rpm)
        self.rpm.value = 1
        
        # KM
        self.km= Label(text='---', font_name = 'Idigital-Medium.otf', halign="center", text_size=self.size, font_size=42, pos=(-695,-160))
        self.add_widget(self.km)  
        
        # Moto Hour
        self.moto_hour = Label(text='---', font_name = 'Idigital-Medium.otf', halign="center", text_size=self.size, font_size=42, pos=(690,-160))
        self.add_widget(self.moto_hour)  
        
        # Pressure_BOM
        self.pressure_BOM = Label(text='-', font_size=35, font_name='hemi_head_bd_it.ttf', pos=(95,140))
        #self.pressure_BOM.text='12'
        self.add_widget(self.pressure_BOM)
        
        # Voltage
        self.voltage = Label(text='-', font_size=35, font_name='hemi_head_bd_it.ttf', pos=(95,65))
        #self.voltage.text = '24.0'
        self.add_widget(self.voltage)
        
        # Temperature_Naves
        self.temperature_naves = Label(text='-', font_size=35, font_name='hemi_head_bd_it.ttf', pos=(95,-10))
        #self.temperature_naves.text = '84'
        self.add_widget(self.temperature_naves)
        
        # Air_brake_pressure
        self.air_brake_pressure = Label(text='-', font_size=35, font_name='hemi_head_bd_it.ttf', pos=(0,140))
        #self.air_brake_pressure.text = '5'
        self.add_widget(self.air_brake_pressure)
        
        # Air_pressure
        self.air_pressure = Label(text='-', font_size=35, font_name='hemi_head_bd_it.ttf', pos=(0,65))
        #self.air_pressure.text = '4'
        self.add_widget(self.air_pressure)
        
        # Temperature_BOM
        self.temperature_BOM = Label(text='-', font_size=35, font_name='hemi_head_bd_it.ttf', pos=(0,-10))
        #self.temperature_BOM.text = '93'
        self.add_widget(self.temperature_BOM)

       
        
                
        
        # air_filter_grey
        self.air_filter_grey = Image(source='icon1/air_filter_grey.png', size =(64, 64), pos=(-280, -130))
        self.add_widget(self.air_filter_grey)
        
        # air_filter_red
        self.air_filter_red = Image(source='icon1/air_filter_red.png', size =(64, 64), pos=(-280, -130))
        
        # akb_grey
        self.akb_grey = Image(source='icon1/akb_grey.png', size =(64, 64), pos=(-200, -130))
        self.add_widget(self.akb_grey)
        
        # akb_red
        self.akb_red = Image(source='icon1/akb_red1.png', size =(64, 64), pos=(-200, -130))
        
        # ruchnik_grey
        self.ruchnik_grey = Image(source='icon1/ruchnik_grey.png', size =(64, 64), pos=(-120, -130))
        self.add_widget(self.ruchnik_grey)
        
        # ruchnik_red
        self.ruchnik_red = Image(source='icon1/ruchnik_red.png', size =(64, 64), pos=(-120, -130))
       
        # zasor_rul_grey
        self.zasor_rul_grey = Image(source='icon1/zasor_rul_grey.png', size =(64, 64), pos=(-40, -130))
        self.add_widget(self.zasor_rul_grey)
        
        # zasor_rul_red
        self.zasor_rul_red = Image(source='icon1/zasor_rul_red.png', size =(64, 64), pos=(-40, -130))
          
        # zasor_kpp_grey
        self.zasor_kpp_grey = Image(source='icon1/zasor_kpp_grey.png', size =(64, 64), pos=(40, -130))
        self.add_widget(self.zasor_kpp_grey)
        
        # zasor_kpp_red
        self.zasor_kpp_red = Image(source='icon1/zasor_kpp_red.png', size =(64, 64), pos=(40, -130))
 
        # temper_bom_grey
        self.temper_bom_grey = Image(source='icon1/temper_bom_grey.png', size =(64, 64), pos=(120, -130))
        self.add_widget(self.temper_bom_grey)
        
        # temper_bom_red
        self.temper_bom_red = Image(source='icon1/temper_bom_red.png', size =(64, 64), pos=(120, -130))
       
        # tormoz_air_grey
        self.tormoz_air_grey = Image(source='icon1/tormoz_air_grey.png', size =(64, 64), pos=(200, -130))
        self.add_widget(self.tormoz_air_grey)
        
        # tormoz_air_red
        self.tormoz_air_red = Image(source='icon1/tormoz_air_red.png', size =(64, 64), pos=(200, -130))
        
        # engine_pressure_grey
        self.engine_pressure_grey = Image(source='icon1/engine_pressure_grey.png', size =(64, 64), pos=(280, -130))
        self.add_widget(self.engine_pressure_grey)
        
        # engine_pressure_red
        self.engine_pressure_red = Image(source='icon1/engine_pressure_red.png', size =(64, 64), pos=(280, -130))
   
        # povorot_p_grey
        self.povorot_p_grey = Image(source='icon1/povorot_p_grey.png', size =(64, 64), pos=(300, 170))
        self.add_widget(self.povorot_p_grey)
        
        # povorot_p_green
        self.povorot_p_green = Image(source='icon1/povorot_p_green.png', size =(64, 64), pos=(300, 170))
 
        # povorot_l_grey
        self.povorot_l_grey = Image(source='icon1/povorot_l_grey.png', size =(64, 64), pos=(-300, 170))
        self.add_widget(self.povorot_l_grey)
        
         # povorot_l_green
        self.povorot_l_green = Image(source='icon1/povorot_l_green.png', size =(64, 64), pos=(-300, 170))

        # povorot_pricep_grey
        self.povorot_pricep_grey = Image(source='icon1/povorot_pricep_grey.png', size =(64, 64), pos=(0, 240))
        self.add_widget(self.povorot_pricep_grey)
        
        # povorot_pricep_green
        self.povorot_pricep_green = Image(source='icon1/povorot_pricep_green.png', size =(64, 64), pos=(0, 240))
       
        # oil_filter_grey
        self.oil_filter_grey = Image(source='icon1/oil_filter_grey.png', size =(64, 64), pos=(80, 240))
        self.add_widget(self.oil_filter_grey)
        
        # oil_filter_red
        self.oil_filter_red = Image(source='icon1/oil_filter_red.png', size =(64, 64), pos=(80, 240))
        
        # bom_temp_grey
        self.bom_temp_grey = Image(source='icon1/bom_temp_grey.png', size =(64, 64), pos=(160, 240))
        self.add_widget(self.bom_temp_grey)
        
        # bom_temp_red
        self.bom_temp_red = Image(source='icon1/bom_temp_red.png', size =(64, 64), pos=(160, 240))    
        
        # check_eng_grey
        self.check_eng_grey = Image(source='icon1/check_eng_grey.png', size =(64, 64), pos=(240, 240))
        self.add_widget(self.check_eng_grey)
        
        # check_eng_yellow
        self.check_eng_yellow = Image(source='icon1/check_eng_yellow.png', size =(64, 64), pos=(240, 240))
              
        # rabochie_fary_pered_grey
        self.rabochie_fary_pered_grey = Image(source='icon1/rabochie_fary_pered_grey.png', size =(64, 64), pos=(320, 240))
        self.add_widget(self.rabochie_fary_pered_grey)
        
        # rabochie_fary_pered_green
        self.rabochie_fary_pered_green = Image(source='icon1/rabochie_fary_pered_green.png', size =(64, 64), pos=(320, 240))  
        
        # rabochie_fary_zad_grey
        self.rabochie_fary_zad_grey = Image(source='icon1/rabochie_fary_zad_grey.png', size =(64, 64), pos=(400, 240))
        self.add_widget(self.rabochie_fary_zad_grey)
        
        # rabochie_fary_zad_green
        self.rabochie_fary_zad_green = Image(source='icon1/rabochie_fary_zad_green.png', size =(64, 64), pos=(400, 240))
               
        # avtopoezd_grey
        self.avtopoezd_grey = Image(source='icon1/avtopoezd_grey.png', size =(64, 64), pos=(480, 240))
        self.add_widget(self.avtopoezd_grey)
        
        # avtopoezd_yellow
        self.avtopoezd_yellow = Image(source='icon1/avtopoezd_yellow.png', size =(64, 64), pos=(480, 240))
            
        # voda_v_toplive_grey
        self.voda_v_toplive_grey = Image(source='icon1/voda_v_toplive_grey.png', size =(64, 64), pos=(-80, 240))
        self.add_widget(self.voda_v_toplive_grey)
        
        # voda_v_toplive_red
        self.voda_v_toplive_red = Image(source='icon1/voda_v_toplive_red.png', size =(64, 64), pos=(-80, 240))
   		
	    # Start
        self.start = Label(text="Start", font_name = 'Idigital-Medium.otf', halign="center", text_size=self.size, font_size=32, pos=(-170, 270))
        self.add_widget(self.start) 
                     
        # dalniy_grey
        self.dalniy_grey = Image(source='icon1/dalniy_grey.png', size =(64, 64), pos=(-260, 240))
        self.add_widget(self.dalniy_grey)
        
        # dalniy_blue
        self.dalniy_blue = Image(source='icon1/dalniy_blue.png', size =(64, 64), pos=(-260, 240))
           
        # blizniy_grey
        self.blizniy_grey = Image(source='icon1/blizniy_grey.png', size =(64, 64), pos=(-330, 240))
        self.add_widget(self.blizniy_grey)
        
        # blizniy_green
        self.blizniy_green = Image(source='icon1/blizniy_green.png', size =(64, 64), pos=(-330, 240))
        
        # gabarity_grey
        self.gabarity_grey = Image(source='icon1/gabarity_grey.png', size =(64, 64), pos=(-420, 240))
        self.add_widget(self.gabarity_grey)
        
        # gabarity_green
        self.gabarity_green = Image(source='icon1/gabarity_green.png', size =(64, 64), pos=(-420, 240))

              
       
        # KPP PRESSURE
        self.kpp_pressure_bar = StencilView(size_hint=(None, None), size=(45, 161), pos=(766, 485))
        self.kpp_pressure_image = Image(source='img/kpp_pressure_full.png', size=(45, 161), pos=(766, 485))
        self.kpp_pressure_bar.add_widget(self.kpp_pressure_image)
        self.add_widget(self.kpp_pressure_bar)
        self.kpp_pressure_bar.height = 0

        
        # COOLANT TEMPERATURE
        self.temp_bar = StencilView(size_hint=(None, None), size=(94, 256), pos=(501, 462))
        self.temp_image = Image(source='img/tempScaleFull.png', size=(94, 256), pos=(501, 462))
        self.temp_bar.add_widget(self.temp_image)
        self.add_widget(self.temp_bar)
        self.temp_bar.height = 0

        # FUEL
        self.fuel_bar = StencilView(size_hint=(None, None), size=(94, 256), pos=(1295, 462))
        self.fuel_image = Image(source='img/fuelScaleFull.png', size=(94, 256), pos=(1295, 462))
        self.fuel_bar.add_widget(self.fuel_image)
        self.add_widget(self.fuel_bar)
        self.fuel_bar.height = 0
        
        # Gear
        self.gear = Label(text='0', font_size=64, font_name='FZ_DIGITAL_11.ttf', pos=(700, 20))
        self.add_widget(self.gear)   
        
        # Ryad
        self.ryad = Label(text='0', font_size=120, font_name='FZ_DIGITAL_11.ttf', pos=(-690, 20))
        #self.ryad.text='0'
        self.add_widget(self.ryad)    
        





class Gauge(Scatter):
    value = NumericProperty(10)  # BoundedNumericProperty(0, min=0, max=360, errorvalue=0)
    size_gauge = BoundedNumericProperty(512, min=128, max=512, errorvalue=128)
    size_text = NumericProperty(10)
    file_gauge = StringProperty("")

    def __init__(self, **kwargs):
        super(Gauge, self).__init__(**kwargs)

        self._gauge = Scatter(
            size=(self.size_gauge, self.size_gauge),
            do_rotation=False,
            do_scale=False,
            do_translation=False
        )

        _img_gauge = Image(source=self.file_gauge, size=(self.size_gauge, self.size_gauge))

        self._needle = Scatter(
            size=(self.size_gauge, self.size_gauge),
            do_rotation=False,
            do_scale=False,
            do_translation=False
        )

        _img_needle = Image(source="img/arrow512.png", size=(self.size_gauge, self.size_gauge))

        self._gauge.add_widget(_img_gauge)
        self._needle.add_widget(_img_needle)

        self.add_widget(self._gauge)
        self.add_widget(self._needle)

        self.bind(pos=self._update)
        self.bind(size=self._update)
        self.bind(value=self._turn)

    def _update(self, *args):
        self._gauge.pos = self.pos
        self._needle.pos = (self.x, self.y)
        self._needle.center = self._gauge.center

    def _turn(self, *args):
        self._needle.center_x = self._gauge.center_x
        self._needle.center_y = self._gauge.center_y
        self._needle.rotation = 121-(0.028*self.value)  # 1 rpm = 0.028 gr



class RequestsClock(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while 1:
            print "The current local date time is ",
            clock = datetime.datetime.now()
            nowTime=clock.strftime("%H:%M %d/%m/%Y")
            print nowTime
            time.sleep(1)
      

class RequestsPWM(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while 1:
            p.ChangeDutyCycle(pwm)
            print "PWM is ",str(pwm)
            time.sleep(1)
            
class RequestsLoop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    canCommands = [
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_TACHOMETER'] >> 8,message_commands['GET_TACHOMETER'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_SPEEDOMETER'] >> 8,message_commands['GET_SPEEDOMETER'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_DOORS_COMMAND'] >> 8,message_commands['GET_DOORS_COMMAND'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_KM_LEFT'] >> 8,message_commands['GET_KM_LEFT'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_OIL_TEMPERATURE'] >> 8,message_commands['GET_OIL_TEMPERATURE'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_FUEL_LEFT'] >> 8,message_commands['GET_FUEL_LEFT'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_OUTDOOR_TEMPERATURE'] >> 8,message_commands['GET_OUTDOOR_TEMPERATURE'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_INDOOR_TEMPERATURE'] >> 8,message_commands['GET_INDOOR_TEMPERATURE'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_COOLANT_TEMPERATURE'] >> 8,message_commands['GET_COOLANT_TEMPERATURE'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_TIME'] >> 8,message_commands['GET_TIME'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_TEMP_BAR'] >> 8,message_commands['GET_TEMP_BAR'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False),
        can.Message(arbitration_id=0x714,data=[0x03,0x22,message_commands['GET_VOLTAGE'] >> 8,message_commands['GET_VOLTAGE'] & 0xff, 0x55, 0x55, 0x55, 0x55],extended_id=False)
     ]

    def run(self):
        # poll RPM every 0.01 sec and poll other sensors for every 10 rpm requests (0.1 sec)
        message_number = 0
        rpm_pool_counter = 0
        while True:
            if (rpm_pool_counter >= 10):
                if (message_number == len(self.canCommands)):
                    message_number = 0
                try:
                    bus.send(self.canCommands[message_number])
                except:
                    pass
                message_number = message_number + 1
                rpm_pool_counter = 0

            else:
                try:
                    bus.send(self.canCommands[0])
                    bus.send(self.canCommands[1])
                except:
                    pass
                rpm_pool_counter = rpm_pool_counter + 1
            time.sleep(0.01)

        


class BoxApp(App):
    def build(self):
        dashboard = Dashboard()
        listener = CanListener(dashboard)
        can.Notifier(bus, [listener])
        
        return dashboard


if __name__ == "__main__":
    # Send requests
    RequestsLoop()
    RequestsClock()   
    RequestsPWM()

    _old_excepthook = sys.excepthook

    def myexcepthook(exctype, value, traceback):
        if exctype == KeyboardInterrupt:
            print ("Handler code goes here")
        else:
            _old_excepthook(exctype, value, traceback)
    sys.excepthook = myexcepthook

    # Show dashboard
    BoxApp().run()
