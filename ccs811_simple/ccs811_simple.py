"""
s-Sense CCS811 by itbrainpower.net I2C sensor breakout example - v1.0/20200218. 

Compatible with:
		s-Sense CCS811 I2C sensor breakout [PN: SS-CCS811#I2C, SKU: ITBP-6004], info https://itbrainpower.net/sensors/CCS811-CO2-TVOC-I2C-sensor-breakout 
		s-Sense CCS811 + HDC2010 I2C sensor breakout [PN: SS-HDC2010+CCS811#I2C, SKU: ITBP-6006], info https://itbrainpower.net/sensors/CCS811-HDC2010-CO2-TVOC-TEMPERATURE-HUMIDITY-I2C-sensor-breakout
		all Raspberry PI, using Python 2.7

Reading CO2 and tVOC values example (pulling at 2sec) - based on test software (Beerware license) written by Nathan Seidle from SparkFun Electronics. 
Thank you Nathan! Great job! 
 
We've ported Nathan's functions into python, add some variables, functions and functionalities.                


Mandatory wiring [bellow for RPi B/B+/II/3B/3B+/4/Zero/Zero W]:
        - sensor Vin            <------> RPI pin 1 [3V3 power] *
        - sensor I2C SDA        <------> RPI pin 3 [i2c-1 SDA]
        - sensor I2C SCL        <------> RPI pin 5 [i2c-1 SCL]
        - sensor GND            <------> RPI pin 9 [GND]
        - sensor PAD6 [!WAKE]   <------> RPI pin 6 [GND] ** or RPI pin 22 [GPIO25] ***

Optional wiring:
        - sensor PAD7 [!RESET]  <------> RPI pin 7 [GPIO4] ****

Wiring notes:
        *    to spare 3V3 power - read about RPI I2C sensors 5V powering
        **   if connected to GND, CCS811 will be always WAKE
        ***  if connected to RPI pin 22, CCS811 can be switched in WAKE/SLEEP mode - handled inside library 
        **** if RESET is not conneted, only CCS811 software reset will be available in application. 
        common ==> check ccs811_param.py file for WAKE and RESET options! 

WIRING WARNING:
        Wrong wiring may damage your RaspberryPI or your sensor! Double check what you've done.


IMPORTANT INFO:       
        New CCS811 sensors requires 48 hours burn in. After that readings should be considered good after 20 minutes of running.


CCS811 definitions are placed in ccs811_param.py


Bellow, how to set-up i2c on RPi and install requiered python packages and other utilities.

Enable I2C channel 1
        a. sudo raspi-config
                menu F5		=> 	enable I2C
                save, exit and reboot.
        
        
        b. edit /boot/config.txt and add/enable following directives:
               dtparam=i2c_arm=on
               dtparam=i2c_arm_baudrate=10000

           save and reboot.

Check i2c is loaded:
        run: ls /dev/*i2c*
        should return: /dev/i2c-1

Add i2c-tools packages:
        sudo apt-get install -y i2c-tools

Check sensor I2C connection:
        run: i2cdetect -y 1
        you should see listed the s-Sense CCS811 I2C address [0x5A]

Install additional python packages:
        a. sudo apt-get install python-setuptools
        b. wget https://files.pythonhosted.org/packages/6a/06/80a6928e5cbfd40c77c08e06ae9975c2a50109586ce66435bd8166ce6bb3/smbus2-0.3.0.tar.gz
        c. expand archive
        d. chdir smbus2-0.3.0
        e. sudo python setup.py install


You are legaly entitled to use this SOFTWARE ONLY IN CONJUNCTION WITH s-Sense CCS811 I2C sensors DEVICES USAGE. Modifications, derivates and redistribution 
of this software must include unmodified this COPYRIGHT NOTICE. You can redistribute this SOFTWARE and/or modify it under the terms 
of this COPYRIGHT NOTICE. Any other usage may be permited only after written notice of Dragos Iosub / R&D Software Solutions srl.

This SOFTWARE is distributed is provide "AS IS" in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
or FITNESS FOR A PARTICULAR PURPOSE.


itbrainpower.net invests significant time in design phase of our IoT products and in associated software and support resources.
Support us by purchasing our environmental and air quality sensors from here https://itbrainpower.net/order#s-Sense


Dragos Iosub, Bucharest 2020.
https://itbrainpower.net
"""

from time import sleep
from ccs811 import *
import paho.mqtt.client as mqtt
import statistics
import shlex,subprocess


cli = "sudo chmod a+rw /dev/i2c-1"
args = shlex.split(cli)
subprocess.Popen(args)

# def on_connect(client, userdata, flags, rc):
# # For paho-mqtt 2.0.0, you need to add the properties parameter.
# # def on_connect(client, userdata, flags, rc, properties):
    # if rc == 0:
        # print("Connected to MQTT Broker!")
    # else:
        # print("Failed to connect, return code %d\n", rc)

# paho_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,client_id="ccs811")
# paho_client.username_pw_set(username="ubuntu", password="srinivas")
# paho_client.on_connect = on_connect
# paho_client.connect("localhost", 1883, 60)

co2_ppm = []
tvoc_mmg = []
avg_co2_ppm = 0
avg_tvoc_mmg = 0
  
#start CCS811, data update rate at 1sec                    
ccs811Begin(CCS811_driveMode_1sec)                                     
for i in range(10):
    #replace with temperature and humidity values from HDC2010 sensor
    try:
        ccs811SetEnvironmentalData(22.78, 57.73) 
    except Exception as e:
        continue
    try:
        if ccs811CheckDataAndUpdate():
            CO2 = ccs811GetCO2()
            tVOC = ccs811GetTVOC()
            co2_ppm.append(CO2)
            tvoc_mmg.append(tVOC)
        elif ccs811CheckForError():
            ccs811PrintError()
    except Exception as e:
        print(e)
        continue
    sleep(2)
avg_co2_ppm = int(statistics.mean(co2_ppm))
avg_tvoc_mmg = int(statistics.mean(tvoc_mmg))
#print(avg_co2_ppm,avg_tvoc_mmg)

#paho_client.loop_forever()

# msg1 = paho_client.publish("ccs811/air_quality/co2",avg_co2_ppm, qos=0)
# msg2 = paho_client.publish("ccs811/air_quality/tvoc",avg_tvoc_mmg, qos=0)

cli2 = "mosquitto_pub -h localhost -u ubuntu -P srinivas -t 'ccs811/air_quality/co2' -m %d"%avg_co2_ppm
args = shlex.split(cli2)
subprocess.Popen(args)
cli3 = "mosquitto_pub -h localhost -u ubuntu -P srinivas -t 'ccs811/air_quality/tvoc' -m %d"%avg_tvoc_mmg
args = shlex.split(cli3)
subprocess.Popen(args)