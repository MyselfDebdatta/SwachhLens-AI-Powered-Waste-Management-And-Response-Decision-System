"""
Data Generator — Smart Waste Management Platform (Hyderabad, India)
Generates 365 days of realistic synthetic fill-level history for 100 smart bins
distributed across Hyderabad's wards and landmarks.

Bin count: 100
City: Bhubaneswar, Odisha, India
Data points: 100 bins × 365 days × 24 hrs = 876,000 records
Trucks: 5 municipal collection trucks

Hardware Note:
    These bins mirror the data schema that an actual ESP32+Ultrasonic Sensor
    would transmit. Each record = one hourly IoT reading.

Run:
    python -m ml.data_generator.generator
"""
import os
import sys
import datetime
import random
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from database.db import engine, init_db, SessionLocal
from database.models import Bin, FillHistory, Truck, Driver

# ──────────────────────────────────────────────────────────────
#  100 BHUBANESWAR BINS — Real GPS Coordinates
#  Spread across wards, landmarks, and neighbourhoods
# ──────────────────────────────────────────────────────────────

BHUBANESWAR_BINS = [
    # ── Saheed Nagar (Ward 10) ──
    {"bin_id":"BIN001","lat":20.2956,"lon":85.8186,"street":"Road No.12, Saheed Nagar","area":"Saheed Nagar","ward":"Ward-10","ward_num":10,"area_type":"Residential","cap":240},
    {"bin_id":"BIN002","lat":20.2938,"lon":85.8193,"street":"Road No.2, Saheed Nagar","area":"Saheed Nagar","ward":"Ward-10","ward_num":10,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN003","lat":20.2979,"lon":85.8151,"street":"Peddamma Temple Road","area":"Saheed Nagar","ward":"Ward-10","ward_num":10,"area_type":"Park","cap":180},
    {"bin_id":"BIN004","lat":20.2925,"lon":85.8212,"street":"Care Hospital Junction","area":"Saheed Nagar","ward":"Ward-10","ward_num":10,"area_type":"Hospital","cap":480},
    {"bin_id":"BIN005","lat":20.3001,"lon":85.8168,"street":"GVK One Mall Entrance","area":"Saheed Nagar","ward":"Ward-10","ward_num":10,"area_type":"Mall","cap":500},
    # ── Nayapalli (Ward 9) ──
    {"bin_id":"BIN006","lat":20.3129,"lon":85.7773,"street":"Road No.36, Nayapalli","area":"Nayapalli","ward":"Ward-9","ward_num":9,"area_type":"Residential","cap":240},
    {"bin_id":"BIN007","lat":20.3112,"lon":85.7789,"street":"Nayapalli Check Post","area":"Nayapalli","ward":"Ward-9","ward_num":9,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN008","lat":20.3150,"lon":85.7758,"street":"People's Plaza Road","area":"Nayapalli","ward":"Ward-9","ward_num":9,"area_type":"Market","cap":420},
    {"bin_id":"BIN009","lat":20.3174,"lon":85.7721,"street":"Film Nagar Road","area":"Nayapalli","ward":"Ward-9","ward_num":9,"area_type":"Residential","cap":240},
    {"bin_id":"BIN010","lat":20.3098,"lon":85.7802,"street":"KBR National Park Gate","area":"Nayapalli","ward":"Ward-9","ward_num":9,"area_type":"Park","cap":180},
    # ── Hitech City / Patia (Ward 13) ──
    {"bin_id":"BIN011","lat":20.3284,"lon":85.7604,"street":"Hitech City Main Road","area":"Patia","ward":"Ward-13","ward_num":13,"area_type":"Commercial","cap":480},
    {"bin_id":"BIN012","lat":20.3301,"lon":85.7573,"street":"Cyber Towers Junction","area":"Patia","ward":"Ward-13","ward_num":13,"area_type":"Commercial","cap":480},
    {"bin_id":"BIN013","lat":20.3260,"lon":85.7646,"street":"Inorbit Mall Road","area":"Patia","ward":"Ward-13","ward_num":13,"area_type":"Mall","cap":500},
    {"bin_id":"BIN014","lat":20.3322,"lon":85.7551,"street":"DLF Cybercity Gate 1","area":"Patia","ward":"Ward-13","ward_num":13,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN015","lat":20.3275,"lon":85.7617,"street":"Patia Circle","area":"Patia","ward":"Ward-13","ward_num":13,"area_type":"Restaurant","cap":300},
    # ── Khandagiri (Ward 14) ──
    {"bin_id":"BIN016","lat":20.3443,"lon":85.7306,"street":"Khandagiri Main Road","area":"Khandagiri","ward":"Ward-14","ward_num":14,"area_type":"Residential","cap":240},
    {"bin_id":"BIN017","lat":20.3422,"lon":85.7325,"street":"Ashoka Metro Pillar","area":"Khandagiri","ward":"Ward-14","ward_num":14,"area_type":"Residential","cap":240},
    {"bin_id":"BIN018","lat":20.3460,"lon":85.7291,"street":"Khandagiri KPHB Road","area":"Khandagiri","ward":"Ward-14","ward_num":14,"area_type":"Market","cap":420},
    {"bin_id":"BIN019","lat":20.3405,"lon":85.7343,"street":"Oasis Centre Road","area":"Khandagiri","ward":"Ward-14","ward_num":14,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN020","lat":20.3480,"lon":85.7270,"street":"Khandagiri Bus Depot","area":"Khandagiri","ward":"Ward-14","ward_num":14,"area_type":"Bus Stand","cap":420},
    # ── Chandrasekharpur (Ward 15) ──
    {"bin_id":"BIN021","lat":20.3201,"lon":85.7189,"street":"Chandrasekharpur Stadium Road","area":"Chandrasekharpur","ward":"Ward-15","ward_num":15,"area_type":"Park","cap":300},
    {"bin_id":"BIN022","lat":20.3180,"lon":85.7211,"street":"Financial District Road","area":"Chandrasekharpur","ward":"Ward-15","ward_num":15,"area_type":"Commercial","cap":480},
    {"bin_id":"BIN023","lat":20.3225,"lon":85.7167,"street":"ISB Campus Gate","area":"Chandrasekharpur","ward":"Ward-15","ward_num":15,"area_type":"School","cap":360},
    {"bin_id":"BIN024","lat":20.3165,"lon":85.7230,"street":"Mind Space Junction","area":"Chandrasekharpur","ward":"Ward-15","ward_num":15,"area_type":"Commercial","cap":480},
    {"bin_id":"BIN025","lat":20.3244,"lon":85.7145,"street":"University of Hyderabad Gate","area":"Chandrasekharpur","ward":"Ward-15","ward_num":15,"area_type":"School","cap":300},
    # ── Jayadev Vihar / Bapuji Nagar (Ward 5) ──
    {"bin_id":"BIN026","lat":20.3241,"lon":85.8314,"street":"Jayadev Vihar Airport Road","area":"Jayadev Vihar","ward":"Ward-5","ward_num":5,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN027","lat":20.3263,"lon":85.8293,"street":"Sarojini Devi Hospital","area":"Jayadev Vihar","ward":"Ward-5","ward_num":5,"area_type":"Hospital","cap":480},
    {"bin_id":"BIN028","lat":20.3220,"lon":85.8335,"street":"Paradise Circle","area":"Jayadev Vihar","ward":"Ward-5","ward_num":5,"area_type":"Restaurant","cap":300},
    {"bin_id":"BIN029","lat":20.3287,"lon":85.8272,"street":"Bapuji Nagar Clock Tower","area":"Bapuji Nagar","ward":"Ward-5","ward_num":5,"area_type":"Market","cap":420},
    {"bin_id":"BIN030","lat":20.3302,"lon":85.8256,"street":"Bapuji Nagar Railway Station","area":"Bapuji Nagar","ward":"Ward-5","ward_num":5,"area_type":"Railway Station","cap":500},
    # ── Old City / Old Town (Lingaraj) (Ward 1) ──
    {"bin_id":"BIN031","lat":20.2416,"lon":85.8447,"street":"Old Town (Lingaraj) Road","area":"Old Town (Lingaraj)","ward":"Ward-1","ward_num":1,"area_type":"Market","cap":500},
    {"bin_id":"BIN032","lat":20.2398,"lon":85.8463,"street":"Laad Bazaar","area":"Old Town (Lingaraj)","ward":"Ward-1","ward_num":1,"area_type":"Market","cap":480},
    {"bin_id":"BIN033","lat":20.2441,"lon":85.8431,"street":"Mecca Masjid Road","area":"Old Town (Lingaraj)","ward":"Ward-1","ward_num":1,"area_type":"Market","cap":420},
    {"bin_id":"BIN034","lat":20.2375,"lon":85.8482,"street":"Shalibanda Road","area":"Old Town (Lingaraj)","ward":"Ward-1","ward_num":1,"area_type":"Residential","cap":240},
    {"bin_id":"BIN035","lat":20.2460,"lon":85.8414,"street":"Purani Haveli Road","area":"Old Town (Lingaraj)","ward":"Ward-1","ward_num":1,"area_type":"Market","cap":420},
    # ── Acharya Vihar (Ward 7) ──
    {"bin_id":"BIN036","lat":20.3174,"lon":85.8194,"street":"Acharya Vihar Metro Station","area":"Acharya Vihar","ward":"Ward-7","ward_num":7,"area_type":"Commercial","cap":480},
    {"bin_id":"BIN037","lat":20.3155,"lon":85.8212,"street":"SR Nagar Road","area":"Acharya Vihar","ward":"Ward-7","ward_num":7,"area_type":"Residential","cap":240},
    {"bin_id":"BIN038","lat":20.3192,"lon":85.8176,"street":"Acharya Vihar Bus Stand","area":"Acharya Vihar","ward":"Ward-7","ward_num":7,"area_type":"Bus Stand","cap":420},
    {"bin_id":"BIN039","lat":20.3215,"lon":85.8155,"street":"ESI Hospital Gate","area":"Acharya Vihar","ward":"Ward-7","ward_num":7,"area_type":"Hospital","cap":480},
    {"bin_id":"BIN040","lat":20.3138,"lon":85.8231,"street":"Panjagutta Junction","area":"Acharya Vihar","ward":"Ward-7","ward_num":7,"area_type":"Commercial","cap":360},
    # ── Mancheswar (Ward 16) ──
    {"bin_id":"BIN041","lat":20.3748,"lon":85.7696,"street":"KPHB Colony Phase 1","area":"Mancheswar","ward":"Ward-16","ward_num":16,"area_type":"Residential","cap":240},
    {"bin_id":"BIN042","lat":20.3772,"lon":85.7675,"street":"Mancheswar Metro Station","area":"Mancheswar","ward":"Ward-16","ward_num":16,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN043","lat":20.3725,"lon":85.7718,"street":"BDL Junction","area":"Mancheswar","ward":"Ward-16","ward_num":16,"area_type":"Industrial","cap":300},
    {"bin_id":"BIN044","lat":20.3791,"lon":85.7654,"street":"JNTU Hyderabad Gate","area":"Mancheswar","ward":"Ward-16","ward_num":16,"area_type":"School","cap":360},
    {"bin_id":"BIN045","lat":20.3704,"lon":85.7740,"street":"Moosapet Main Road","area":"Mancheswar","ward":"Ward-16","ward_num":16,"area_type":"Market","cap":420},
    # ── Rasulgarh / Kalpana Square (Ward 2) ──
    {"bin_id":"BIN046","lat":20.2290,"lon":85.9246,"street":"Rasulgarh Circle","area":"Rasulgarh","ward":"Ward-2","ward_num":2,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN047","lat":20.2312,"lon":85.9225,"street":"Rasulgarh Metro Station","area":"Rasulgarh","ward":"Ward-2","ward_num":2,"area_type":"Bus Stand","cap":420},
    {"bin_id":"BIN048","lat":20.2482,"lon":85.9018,"street":"Kalpana Square Main Road","area":"Kalpana Square","ward":"Ward-2","ward_num":2,"area_type":"Market","cap":480},
    {"bin_id":"BIN049","lat":20.2460,"lon":85.9040,"street":"Kalpana Square Bus Stand","area":"Kalpana Square","ward":"Ward-2","ward_num":2,"area_type":"Bus Stand","cap":420},
    {"bin_id":"BIN050","lat":20.2500,"lon":85.8995,"street":"Moula Ali Industrial Area","area":"Kalpana Square","ward":"Ward-2","ward_num":2,"area_type":"Industrial","cap":300},
    # ── Vani Vihar (Ward 3) ──
    {"bin_id":"BIN051","lat":20.2862,"lon":85.9296,"street":"Vani Vihar Ring Road","area":"Vani Vihar","ward":"Ward-3","ward_num":3,"area_type":"Industrial","cap":300},
    {"bin_id":"BIN052","lat":20.2840,"lon":85.9318,"street":"Vani Vihar Bus Stand","area":"Vani Vihar","ward":"Ward-3","ward_num":3,"area_type":"Bus Stand","cap":420},
    {"bin_id":"BIN053","lat":20.2883,"lon":85.9274,"street":"NGRI Colony Road","area":"Vani Vihar","ward":"Ward-3","ward_num":3,"area_type":"Residential","cap":240},
    {"bin_id":"BIN054","lat":20.2905,"lon":85.9251,"street":"Ramanthapur Market","area":"Vani Vihar","ward":"Ward-3","ward_num":3,"area_type":"Market","cap":420},
    {"bin_id":"BIN055","lat":20.2820,"lon":85.9343,"street":"Mallapur Industrial","area":"Vani Vihar","ward":"Ward-3","ward_num":3,"area_type":"Industrial","cap":300},
    # ── Barmunda (Ward 8) ──
    {"bin_id":"BIN056","lat":20.2748,"lon":85.8076,"street":"Barmunda Circle","area":"Barmunda","ward":"Ward-8","ward_num":8,"area_type":"Commercial","cap":480},
    {"bin_id":"BIN057","lat":20.2726,"lon":85.8098,"street":"Rethibowli Market","area":"Barmunda","ward":"Ward-8","ward_num":8,"area_type":"Market","cap":420},
    {"bin_id":"BIN058","lat":20.2770,"lon":85.8054,"street":"Shamsabad Road Junction","area":"Barmunda","ward":"Ward-8","ward_num":8,"area_type":"Residential","cap":240},
    {"bin_id":"BIN059","lat":20.2705,"lon":85.8121,"street":"Tolichowki Main Road","area":"Barmunda","ward":"Ward-8","ward_num":8,"area_type":"Restaurant","cap":300},
    {"bin_id":"BIN060","lat":20.2789,"lon":85.8031,"street":"Santosh Nagar Colony","area":"Barmunda","ward":"Ward-8","ward_num":8,"area_type":"Residential","cap":240},
    # ── Unit-1 Market / Unit-2 Market (Ward 4) ──
    {"bin_id":"BIN061","lat":20.2630,"lon":85.8487,"street":"Unit-1 Market Sultan Bazaar","area":"Unit-1 Market","ward":"Ward-4","ward_num":4,"area_type":"Market","cap":500},
    {"bin_id":"BIN062","lat":20.2651,"lon":85.8465,"street":"Unit-2 Market Circle","area":"Unit-2 Market","ward":"Ward-4","ward_num":4,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN063","lat":20.2609,"lon":85.8510,"street":"Master Canteen Station Road","area":"Master Canteen","ward":"Ward-4","ward_num":4,"area_type":"Railway Station","cap":500},
    {"bin_id":"BIN064","lat":20.2674,"lon":85.8440,"street":"Public Gardens Entrance","area":"Unit-2 Market","ward":"Ward-4","ward_num":4,"area_type":"Park","cap":180},
    {"bin_id":"BIN065","lat":20.2588,"lon":85.8534,"street":"Gandhi Bhavan Road","area":"Master Canteen","ward":"Ward-4","ward_num":4,"area_type":"Commercial","cap":360},
    # ── Infocity (Ward 17) ──
    {"bin_id":"BIN066","lat":20.3773,"lon":85.7164,"street":"Infocity Metro Station","area":"Infocity","ward":"Ward-17","ward_num":17,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN067","lat":20.3751,"lon":85.7186,"street":"Infocity Main Road","area":"Infocity","ward":"Ward-17","ward_num":17,"area_type":"Residential","cap":240},
    {"bin_id":"BIN068","lat":20.3798,"lon":85.7141,"street":"Kollur Road Junction","area":"Infocity","ward":"Ward-17","ward_num":17,"area_type":"Residential","cap":240},
    {"bin_id":"BIN069","lat":20.3820,"lon":85.7118,"street":"Chandanagar Market","area":"Infocity","ward":"Ward-17","ward_num":17,"area_type":"Market","cap":420},
    {"bin_id":"BIN070","lat":20.3730,"lon":85.7210,"street":"BHEL Township","area":"Infocity","ward":"Ward-17","ward_num":17,"area_type":"Residential","cap":240},
    # ── Jharpada / Laxmisagar (Ward 6) ──
    {"bin_id":"BIN071","lat":20.2320,"lon":85.8752,"street":"Laxmisagar Bus Depot","area":"Laxmisagar","ward":"Ward-6","ward_num":6,"area_type":"Bus Stand","cap":420},
    {"bin_id":"BIN072","lat":20.2343,"lon":85.8731,"street":"Chaderghat Bridge","area":"Laxmisagar","ward":"Ward-6","ward_num":6,"area_type":"Residential","cap":240},
    {"bin_id":"BIN073","lat":20.2296,"lon":85.8773,"street":"Jharpada Colony","area":"Jharpada","ward":"Ward-6","ward_num":6,"area_type":"Residential","cap":240},
    {"bin_id":"BIN074","lat":20.2270,"lon":85.8796,"street":"Karan Shah Market","area":"Jharpada","ward":"Ward-6","ward_num":6,"area_type":"Market","cap":420},
    {"bin_id":"BIN075","lat":20.2366,"lon":85.8710,"street":"Champapet Road","area":"Jharpada","ward":"Ward-6","ward_num":6,"area_type":"Residential","cap":240},
    # ── Kalarahanga (Ward 18) ──
    {"bin_id":"BIN076","lat":20.4203,"lon":85.8423,"street":"Kalarahanga Main Road","area":"Kalarahanga","ward":"Ward-18","ward_num":18,"area_type":"Residential","cap":240},
    {"bin_id":"BIN077","lat":20.4227,"lon":85.8399,"street":"Kalarahanga Market Area","area":"Kalarahanga","ward":"Ward-18","ward_num":18,"area_type":"Market","cap":420},
    {"bin_id":"BIN078","lat":20.4180,"lon":85.8448,"street":"Bowrampet Road","area":"Kalarahanga","ward":"Ward-18","ward_num":18,"area_type":"Residential","cap":240},
    {"bin_id":"BIN079","lat":20.4250,"lon":85.8374,"street":"Alwal Bus Stand","area":"Kalarahanga","ward":"Ward-18","ward_num":18,"area_type":"Bus Stand","cap":360},
    {"bin_id":"BIN080","lat":20.4158,"lon":85.8470,"street":"Suraram Industrial Area","area":"Kalarahanga","ward":"Ward-18","ward_num":18,"area_type":"Industrial","cap":300},
    # ── Mancheswar Industrial / Palasuni (Ward 3B) ──
    {"bin_id":"BIN081","lat":20.3014,"lon":85.8984,"street":"Mancheswar Industrial Industrial","area":"Mancheswar Industrial","ward":"Ward-3B","ward_num":19,"area_type":"Industrial","cap":300},
    {"bin_id":"BIN082","lat":20.3036,"lon":85.8961,"street":"Palasuni Main Road","area":"Palasuni","ward":"Ward-3B","ward_num":19,"area_type":"Residential","cap":240},
    {"bin_id":"BIN083","lat":20.2992,"lon":85.9008,"street":"Satsang Vihar Junction","area":"Satsang Vihar","ward":"Ward-3B","ward_num":19,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN084","lat":20.3060,"lon":85.8937,"street":"Stadium Road","area":"Palasuni","ward":"Ward-3B","ward_num":19,"area_type":"Park","cap":180},
    {"bin_id":"BIN085","lat":20.2970,"lon":85.9032,"street":"VSS Nagar Circle","area":"VSS Nagar","ward":"Ward-3B","ward_num":19,"area_type":"Commercial","cap":360},
    # ── Biju Patnaik Airport Area / Airport Zone (Ward 20) ──
    {"bin_id":"BIN086","lat":20.1203,"lon":85.7994,"street":"Rajiv Gandhi Int. Airport","area":"Biju Patnaik Airport Area","ward":"Ward-20","ward_num":20,"area_type":"Commercial","cap":500},
    {"bin_id":"BIN087","lat":20.1227,"lon":85.7971,"street":"Airport Road Toll Plaza","area":"Biju Patnaik Airport Area","ward":"Ward-20","ward_num":20,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN088","lat":20.1178,"lon":85.8018,"street":"Biju Patnaik Airport Area Market","area":"Biju Patnaik Airport Area","ward":"Ward-20","ward_num":20,"area_type":"Market","cap":420},
    {"bin_id":"BIN089","lat":20.1250,"lon":85.7948,"street":"Outer Ring Road Junction","area":"Biju Patnaik Airport Area","ward":"Ward-20","ward_num":20,"area_type":"Residential","cap":240},
    {"bin_id":"BIN090","lat":20.1155,"lon":85.8042,"street":"Biju Patnaik Airport Area Bus Stand","area":"Biju Patnaik Airport Area","ward":"Ward-20","ward_num":20,"area_type":"Bus Stand","cap":360},
    # ── Unit-8 (Ward 11) ──
    {"bin_id":"BIN091","lat":20.3010,"lon":85.8278,"street":"Unit-8 Metro","area":"Unit-8","ward":"Ward-11","ward_num":11,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN092","lat":20.3032,"lon":85.8256,"street":"Unit-8 Market","area":"Unit-8","ward":"Ward-11","ward_num":11,"area_type":"Market","cap":480},
    {"bin_id":"BIN093","lat":20.2989,"lon":85.8300,"street":"Hussain Sagar Lake Path","area":"Unit-8","ward":"Ward-11","ward_num":11,"area_type":"Park","cap":180},
    {"bin_id":"BIN094","lat":20.3055,"lon":85.8233,"street":"Indira Park Road","area":"Unit-8","ward":"Ward-11","ward_num":11,"area_type":"Park","cap":180},
    {"bin_id":"BIN095","lat":20.2970,"lon":85.8323,"street":"Siripur Circle","area":"Siripur","ward":"Ward-11","ward_num":11,"area_type":"Commercial","cap":480},
    # ── Kalinga Nagar / Unit-4 (Ward 5B) ──
    {"bin_id":"BIN096","lat":20.3620,"lon":85.8895,"street":"Kalinga Nagar Main Road","area":"Kalinga Nagar","ward":"Ward-5B","ward_num":21,"area_type":"Residential","cap":240},
    {"bin_id":"BIN097","lat":20.3642,"lon":85.8873,"street":"Unit-4 Market","area":"Unit-4","ward":"Ward-5B","ward_num":21,"area_type":"Market","cap":420},
    {"bin_id":"BIN098","lat":20.3598,"lon":85.8918,"street":"Unit-6 Road","area":"Unit-6","ward":"Ward-5B","ward_num":21,"area_type":"Residential","cap":240},
    {"bin_id":"BIN099","lat":20.3664,"lon":85.8850,"street":"Lothukunta Circle","area":"Kalinga Nagar","ward":"Ward-5B","ward_num":21,"area_type":"Commercial","cap":360},
    {"bin_id":"BIN100","lat":20.3576,"lon":85.8941,"street":"Dammaiguda Road","area":"Kalinga Nagar","ward":"Ward-5B","ward_num":21,"area_type":"Residential","cap":240},
]

# ─────────────────────────────────────────────────────────────
#  TRUCK FLEET (Bhubaneswar Municipal Corporation)
# ─────────────────────────────────────────────────────────────

TRUCK_FLEET = [
    {"truck_id": "TRK-BBS-01", "plate": "OD02BA0001", "capacity": 5000, "driver": "Ramesh Kumar", "driver_id": "DRV001"},
    {"truck_id": "TRK-BBS-02", "plate": "OD02BA0002", "capacity": 5000, "driver": "Suresh Reddy",  "driver_id": "DRV002"},
    {"truck_id": "TRK-BBS-03", "plate": "OD02BA0003", "capacity": 5000, "driver": "Vijay Babu",    "driver_id": "DRV003"},
    {"truck_id": "TRK-BBS-04", "plate": "OD02BA0004", "capacity": 5000, "driver": "Naresh Yadav",  "driver_id": "DRV004"},
    {"truck_id": "TRK-BBS-05", "plate": "OD02BA0005", "capacity": 4000, "driver": "Prasad Goud",   "driver_id": "DRV005"},
]

DRIVER_DETAILS = [
    {"driver_id":"DRV001","name":"Ramesh Kumar","phone":"9876543210","license":"OD123456"},
    {"driver_id":"DRV002","name":"Suresh Reddy","phone":"9876543211","license":"OD123457"},
    {"driver_id":"DRV003","name":"Vijay Babu",  "phone":"9876543212","license":"OD123458"},
    {"driver_id":"DRV004","name":"Naresh Yadav","phone":"9876543213","license":"OD123459"},
    {"driver_id":"DRV005","name":"Prasad Goud", "phone":"9876543214","license":"TS123460"},
]

# ─────────────────────────────────────────────────────────────
#  AREA PARAMETERS
# ─────────────────────────────────────────────────────────────

AREA_PARAMS = {
    "Residential":      {"base_fill_rate": 1.8,  "peak_hours": [7, 8, 12, 18, 19, 20], "pop_density": 4500, "holiday_boost": 1.2},
    "Commercial":       {"base_fill_rate": 2.5,  "peak_hours": [9, 10, 11, 12, 13, 14, 15, 16], "pop_density": 8000, "holiday_boost": 0.4},
    "Market":           {"base_fill_rate": 3.8,  "peak_hours": [8, 9, 10, 11, 12, 16, 17, 18, 19], "pop_density": 12000, "holiday_boost": 1.6},
    "Hospital":         {"base_fill_rate": 2.2,  "peak_hours": [8, 9, 10, 11, 14, 15, 16], "pop_density": 5000, "holiday_boost": 0.8},
    "School":           {"base_fill_rate": 2.0,  "peak_hours": [7, 8, 12, 13, 16, 17], "pop_density": 3500, "holiday_boost": 0.1},
    "Restaurant":       {"base_fill_rate": 3.2,  "peak_hours": [11, 12, 13, 19, 20, 21], "pop_density": 6000, "holiday_boost": 1.5},
    "Mall":             {"base_fill_rate": 3.5,  "peak_hours": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "pop_density": 10000, "holiday_boost": 1.8},
    "Bus Stand":        {"base_fill_rate": 2.8,  "peak_hours": [7, 8, 9, 17, 18, 19], "pop_density": 7000, "holiday_boost": 1.1},
    "Railway Station":  {"base_fill_rate": 3.0,  "peak_hours": [6, 7, 8, 16, 17, 18, 19], "pop_density": 9000, "holiday_boost": 1.3},
    "Park":             {"base_fill_rate": 0.9,  "peak_hours": [6, 7, 17, 18, 19], "pop_density": 2000, "holiday_boost": 1.7},
    "Industrial":       {"base_fill_rate": 2.0,  "peak_hours": [8, 9, 10, 14, 15, 16], "pop_density": 3000, "holiday_boost": 0.2},
}

from ml.preprocessing.calendar_features import BHUBANESWAR_HOLIDAYS

# Monsoon months in Bhubaneswar: June–October (higher rainfall, affects bin usage)
MONSOON_MONTHS = {6, 7, 8, 9, 10}


def generate_hourly_fill(bin_data, timestamp, current_fill, is_holiday, temperature, rainfall):
    """
    Simulates fill percentage increase for one hour, given bin context.
    Returns (new_fill, waste_generated).
    """
    params = AREA_PARAMS[bin_data["area_type"]]
    hour = timestamp.hour
    
    base_rate = params["base_fill_rate"]
    
    # Peak hour multiplier
    hour_multiplier = 1.8 if hour in params["peak_hours"] else 0.6
    
    # Holiday/weekend multiplier
    is_weekend = timestamp.weekday() >= 5
    if is_holiday:
        day_multiplier = params["holiday_boost"]
    elif is_weekend:
        day_multiplier = 1.1
    else:
        day_multiplier = 1.0
    
    # Temperature effect (higher temp = more waste/spoilage)
    temp_effect = 1.0 + max(0, (temperature - 28) * 0.02)
    
    # Rainfall effect (heavy rain suppresses outdoor activity)
    rain_effect = 1.0 - min(0.4, rainfall * 0.05)
    
    # Random natural variability (±15%)
    noise = np.random.normal(1.0, 0.15)
    
    # Final waste rate as percentage of capacity per hour
    capacity_liters = bin_data["cap"]
    fill_rate = (base_rate * hour_multiplier * day_multiplier * temp_effect * rain_effect * noise)
    waste_liters = fill_rate * (capacity_liters / 100.0)
    waste_liters = max(0, waste_liters)
    
    # Add waste to fill
    new_fill_liters = (current_fill / 100.0) * capacity_liters + waste_liters
    new_fill_pct = min(100.0, (new_fill_liters / capacity_liters) * 100.0)
    
    return new_fill_pct, waste_liters


def run_generation():
    """
    Main data generation pipeline.
    Creates 100 bins × 365 days × 24 hours of synthetic hourly readings.
    """
    print("=" * 60)
    print("  SMART WASTE MANAGEMENT - DATA GENERATOR")
    print("  City: Bhubaneswar, Odisha, India")
    print(f"  Bins: {len(BHUBANESWAR_BINS)}")
    print("  Period: 365 days")
    print(f"  Total records: {len(BHUBANESWAR_BINS) * 365 * 24:,}")
    print("=" * 60)
    
    init_db()
    db: Session = SessionLocal()
    
    try:
        # ── Clear existing data ──
        print("\n[1/5] Clearing existing data...")
        db.query(FillHistory).delete()
        db.query(Bin).delete()
        db.query(Truck).delete()
        db.query(Driver).delete()
        db.commit()
        
        # ── Insert Drivers ──
        print("[2/5] Inserting driver records...")
        for d in DRIVER_DETAILS:
            driver = Driver(
                driver_id=d["driver_id"],
                name=d["name"],
                phone=d["phone"],
                license_number=d["license"],
                status="Available"
            )
            db.add(driver)
        db.commit()
        
        # ── Insert Bins ──
        print("[3/5] Inserting 100 Hyderabad bin records...")
        installation_base = datetime.date(2022, 1, 1)
        for i, b in enumerate(BHUBANESWAR_BINS):
            install_date = installation_base + datetime.timedelta(days=random.randint(0, 180))
            bin_obj = Bin(
                bin_id=b["bin_id"],
                latitude=b["lat"],
                longitude=b["lon"],
                street_name=b["street"],
                area_name=b["area"],
                ward=b["ward"],
                ward_number=b["ward_num"],
                area_type=b["area_type"],
                capacity=b["cap"],
                current_fill_percentage=random.uniform(10, 60),
                battery_level=random.uniform(75, 100),
                signal_strength=random.randint(65, 98),
                temperature=None,
                status="Active",
                last_updated=None,
                last_collection_time=None,
                installation_date=install_date
            )
            db.add(bin_obj)
        db.commit()
        print(f"  [OK] Inserted {len(BHUBANESWAR_BINS)} bins")

        # ── Insert Trucks ──
        print("[4/5] Inserting truck fleet...")
        for t in TRUCK_FLEET:
            truck = Truck(
                truck_id=t["truck_id"],
                plate_number=t["plate"],
                capacity=t["capacity"],
                driver=t["driver"],
                driver_id=t["driver_id"],
                status="Idle"
            )
            db.add(truck)
        db.commit()
        print(f"  [OK] Inserted {len(TRUCK_FLEET)} trucks")
        
        # ── Generate Historical Fill Data ──
        print("[5/5] Generating 365 days of hourly fill history...")
        
        # Start date: 365 days ago
        start_dt = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - datetime.timedelta(days=365)
        
        BATCH_SIZE = 5000
        records_buffer = []
        total_records = 0
        
        # Track current fill state per bin
        bin_fill_state = {b["bin_id"]: random.uniform(5, 25) for b in BHUBANESWAR_BINS}
        
        # Simulate collection events: each bin collected every ~3-5 days randomly
        last_collection = {b["bin_id"]: start_dt for b in BHUBANESWAR_BINS}
        
        total_hours = 365 * 24
        for h in range(total_hours):
            current_dt = start_dt + datetime.timedelta(hours=h)
            date_str = current_dt.strftime("%Y-%m-%d")
            is_holiday = date_str in BHUBANESWAR_HOLIDAYS
            month = current_dt.month
            
            # Hyderabad climate simulation
            base_temp = 28 + 6 * np.sin(np.pi * (month - 3) / 6)  # Peak in May, low in Jan
            temperature = float(np.clip(np.random.normal(base_temp, 2.5), 18, 45))
            
            # Rainfall (monsoon: June–Oct)
            if month in MONSOON_MONTHS:
                rainfall = float(max(0, np.random.exponential(8)))
            else:
                rainfall = float(max(0, np.random.exponential(0.5)))
            
            for b in BHUBANESWAR_BINS:
                bin_id = b["bin_id"]
                current_fill = bin_fill_state[bin_id]
                
                # Simulate collection: if fill > 85% or > 4 days since last collection
                hours_since = (current_dt - last_collection[bin_id]).total_seconds() / 3600
                should_collect = (current_fill >= 85.0) or (hours_since >= random.randint(72, 120))
                if should_collect and current_fill > 20:
                    current_fill = random.uniform(2, 10)  # Reset after collection
                    last_collection[bin_id] = current_dt
                
                # Generate new fill
                new_fill, waste_gen = generate_hourly_fill(b, current_dt, current_fill, is_holiday, temperature, rainfall)
                bin_fill_state[bin_id] = new_fill
                
                pop_density = AREA_PARAMS[b["area_type"]]["pop_density"]
                
                records_buffer.append({
                    "bin_id": bin_id,
                    "timestamp": current_dt,
                    "fill_percentage": round(new_fill, 2),
                    "battery": round(random.uniform(75, 100), 1),
                    "temperature": round(temperature, 1),
                    "rainfall": round(rainfall, 2),
                    "holiday": int(is_holiday),
                    "population_density": pop_density,
                    "waste_generated": round(waste_gen, 2),
                })
            
            # Batch insert
            if len(records_buffer) >= BATCH_SIZE:
                db.bulk_insert_mappings(FillHistory, records_buffer)
                db.commit()
                total_records += len(records_buffer)
                records_buffer = []
                pct = (h / total_hours) * 100
                print(f"  Progress: {pct:.0f}% — {total_records:,} records written", end="\r")
        
        # Insert remaining
        if records_buffer:
            db.bulk_insert_mappings(FillHistory, records_buffer)
            db.commit()
            total_records += len(records_buffer)
        
        print(f"\n  [OK] Inserted {total_records:,} fill history records")
        print("\n" + "=" * 60)
        print("  DATA GENERATION COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Data generation failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_generation()
