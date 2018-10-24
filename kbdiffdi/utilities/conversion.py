import numpy as np


""" converting temperature values """
def celsius_to_fahrenheit(feature):
    feature.data = feature.data * (9./5.) + 32.


def fahrenheit_to_celsius(feature):
    feature.data = (feature.data - 32.) * 5./9.


""" converting precipitation values """    
def millimeters_to_inches(feature):
    feature.data = feature.data/25.4


def inches_to_millimeters(feature):
    feature.data = feature.data*25.4


""" converting windspeed from m/s to km/h """
def mpers_to_kmperh(feature):
    feature.data = feature.data*3.6


""" converting the KBDI values """
def KBDI_index_to_millimeters(feature):
    feature.data = (feature.data/100) * 25.4


def KBDI_index_to_inches(feature):
    feature.data = (feature.data/25.4) * 100