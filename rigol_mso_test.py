import pyvisa
import time
import numpy
import struct

rm = pyvisa.ResourceManager('@py')

scope = rm.open_resource("USB0::0x1AB1::0x0515::MS5A241804510::0::INSTR")

print(scope.query('*IDN?'))

scope.write(":CHAN1:DISP OFF")
scope.write(":CHAN2:DISP ON")
scope.write(":CHAN3:DISP OFF")
scope.write(":CHAN4:DISP ON")

scope.write(":CHAN2:SCAL 1")

#Set timebase parameters
scope.write(":TIM:MAIN:SCAL 0.0005")
scope.write(":TIM:DEL:ENAB OFF")

#Set trigger parameters
scope.write(":TRIG:MODE EDGE")
scope.write(":TRIG:COUP AC")
scope.write(":TRIG:SWE SING")
scope.write(":TRIG:EDGE:SOUR CHAN2")
scope.write(":TRIG:EDGE:SLOP POS")
scope.write(":TRIG:EDGE:LEV 1")

scope.write(":WAV:SOUR CHAN2")
scope.write(":WAV:MODE NORM")
scope.write(":WAV:FORM BYTE")
scope.write(":WAV:POIN:MODE RAW")
scope.write(":WAV:POIN 10000")

#Arm MSO for single acquisition
scope.write(":SING")
#Get trigger status
while scope.query(":TRIG:STAT?")[:4] != "STOP":
    print("Waiting for trigger...")

scope.write(":SYSTem:HEADer OFF")

yorigin = scope.query(":WAVeform:YORigin?")
yinc = scope.query(":WAVeform:YINCrement?")
yref = scope.query(":WAVeform:YREFerence?")

scope.write(":WAV:DATA? CHAN2")
data_arr = scope.read_raw()

data_arr_trimmed = data_arr[15:-1]

yref_int = int(yref,10)
samples_data_unscaled = numpy.array(struct.unpack('<%sc' % len(data_arr_trimmed), data_arr_trimmed))
offset_y_byte = bytes([yref_int]*len(samples_data_unscaled))
offset_y = numpy.frombuffer(offset_y_byte,'B')
samples_data = numpy.frombuffer(samples_data_unscaled,dtype=numpy.uint8) - offset_y

print(yinc)

fp = open("waveform.csv", "w")
for val in samples_data:
    int_val = int.from_bytes(val, "little")
    fp.write(str(int_val)+",")
fp.write("\n")
fp.close()    

if scope != None:
    scope.close()