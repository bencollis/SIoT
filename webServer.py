#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    RPi Web Server for DHT captured data  
'''

from flask import Flask, render_template, request
app = Flask(__name__)

import sqlite3

@app.route('/footprint')
def footprint():
   return render_template('LineChart.html')

@app.route('/recycling')
def recycling():
   return render_template('PieCharts.html')

@app.route('/data')
def data():
   return render_template('table.html')

if __name__ == "__main__":
   app.run(host='192.168.1.188', port=5000, debug=False)

