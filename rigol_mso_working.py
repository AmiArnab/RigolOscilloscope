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

scope.write(":RUN")
time.sleep(5)

#scope.write(":WAV:STAR 1000")
#scope.write(":WAV:STOP 2000")

scope.write(":SING")

#Get trigger status
#st = scope.query(":TRIG:MODE STAT?")

#cprint(st)


scope.write(":SYSTem:HEADer OFF")

yorigin = scope.query(":WAVeform:YORigin?")
#self.scope.write("*OPC?")
yinc = scope.query(":WAVeform:YINCrement?")
#self.scope.write("*OPC?")
#yrange = self.scope.query(":WAVeform:YRANge?")
#self.scope.write("*OPC?")
yref = scope.query(":WAVeform:YREFerence?")

print("YORG: "),
print(yorigin)
print("YINC: "),
print(yinc)
#print(yrange)
print("YREF: "),
print(yref)

scope.write(":WAV:DATA? CHAN2")
# data_arr = scope.query_binary_values(":WAV:DATA?", datatype = 'f')
data_arr = scope.read_raw()

# data_arr = scope.query(":WAV:DATA?")

# print(type(data_arr[20]))
# print(len(data_arr))

data_arr_trimmed = data_arr[15:-1]

samples_data_unscaled = numpy.array(struct.unpack('<%sc' % len(data_arr_trimmed), data_arr_trimmed))
yref_int = int(yref,10)

fp = open("waveform.csv", "w")
for val in samples_data_unscaled:
    int_val = int.from_bytes(val, "little")-yref_int
    fp.write(str(int_val)+",")
fp.write("\n")
fp.close()    

if scope != None:
    scope.close()