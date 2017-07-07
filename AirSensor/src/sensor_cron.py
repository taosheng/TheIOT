#!/usr/bin/env python

import time
import sqlite3

air_sensor = 2 # port A2 Air Quality
hcho_sensor = 1 # port A1 HCHO


def general_air_sensor():
    import grovepi
    grovepi.pinMode(air_sensor,"INPUT")
    sensor_name = "Air Quality"
    sensor_value = grovepi.analogRead(air_sensor)
    ts = time.time()
    print("{}, {}, {}".format(sensor_name, ts, sensor_value))
    conn = sqlite3.connect('air.db')
    c = conn.cursor()

    c.execute("INSERT INTO sensor VALUES ('{}',{},{})".format(sensor_name, ts, sensor_value))

    conn.commit()

    conn.close()    


def hcho_sensor():
    import grovepi
    grovepi.pinMode(hcho_sensor,"INPUT")

    grove_vcc = 5
    sensor_value = grovepi.analogRead(hcho_sensor)

    voltage = (float)(sensor_value * grove_vcc / 1024)
    ts = time.time()

    print("{}, sensor_value ={} voltage={}".format(ts, sensor_value, voltage))


if __name__ == '__main__':
    general_air_sensor()
