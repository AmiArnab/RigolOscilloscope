import pyvisa
import time
import struct
import numpy

class RigolMSO:
    """Rigol MSO Access Class"""

    def __init__(self):
        self.rm = pyvisa.ResourceManager('')
        self.scope = None

    def OpenMSO(self):
        # This the USB VISA interface address of the oscilloscope
        self.scope = self.rm.open_resource("USB0::0x1AB1::0x0515::MS5A241804510::0::INSTR")
        print(self.scope.query('*IDN?'))
        return 0

    def CloseMSO(self):
        if(self.scope != None):
            self.scope.close()
        print("Closing MSO...")
        return 0

    def Initialise(self):
        try:
            #Turn unused channels OFF
            self.scope.write(":CHAN1:DISP OFF")
            self.scope.write(":CHAN2:DISP ON")
            self.scope.write(":CHAN3:DISP OFF")
            self.scope.write(":CHAN4:DISP ON")

            self.scope.write(":FUNC1:DISPlay OFF")
            self.scope.write(":SYSTem:HEADer OFF")

            #Channel 2 settings
            self.scope.write(":CAHNnel2:DIFFerential OFF")
            self.scope.write(":CHANnel2:BWLimit OFF")
            self.scope.write(":CHANnel2:PROBe 1.0")
            self.scope.write(":CHANnel2:PROBe:COUPling AC")
            self.scope.write(":CHANnel2:INPut DC")
            self.scope.write(":CHANnel2:INVert OFF")
            self.scope.write(":CHA2Nel2:OFFSet 0")
            self.scope.write(":CHANnel2:RANge 2E-2")
            self.scope.write(":CHANnel2:SCALe 500E-3")

            #Channel 4 settings
            self.scope.write(":CAHNnel4:DIFFerential OFF")
            self.scope.write(":CHANnel4:BWLimit OFF")
            self.scope.write(":CHANnel4:PROBe 1.0")
            self.scope.write(":CHANnel4:PROBe:COUPling AC")
            self.scope.write(":CHANnel4:INPut DC")
            self.scope.write(":CHANnel4:INVert OFF")
            self.scope.write(":CHA2Nel4:OFFSet 0")
            self.scope.write(":CHANnel4:RANge 2")
            self.scope.write(":CHANnel4:SCALe 1")

            #Horizontal Setting
            # self.scope.write(":TIMebase:VIEW MAIN")
            # self.scope.write(":TIMebase:POSition 0")
            # self.scope.write(":TIMebase:RANGe 5E-4")
            # self.scope.write(":TIMebase:REFerence:PERCent 10")
            # self.scope.write(":TIMebase:SCALe 4E-6")

            self.scope.write(":TIM:MAIN:SCAL 0.0005")
            self.scope.write(":TIM:DEL:ENAB OFF")

            #Recordlength Setting
            # self.scope.write(":ACQuire:BANDwidth MAX")
            # self.scope.write(":ACQuire:SRATe:ANALog MAX")
            # self.scope.write(":ACQuire:POINts:ANALog 100000")
            # self.scope.write(":ACQuire:MODE: RTIMe")
            # self.scope.write(":ACQuire:COUNt 1")

            #Trigger Setting
            self.scope.write(":TRIG:MODE EDGE")
            self.scope.write(":TRIG:COUP AC")
            self.scope.write(":TRIG:SWE SING")
            self.scope.write(":TRIG:EDGE:SOUR CHAN2")
            self.scope.write(":TRIG:EDGE:SLOP POS")
            self.scope.write(":TRIG:EDGE:LEV 1")

            #Waveform Setting
            self.scope.write(":WAV:SOUR CHAN2")
            self.scope.write(":WAV:MODE NORM")
            self.scope.write(":WAV:FORM BYTE")
            self.scope.write(":WAV:POIN:MODE RAW")
            self.scope.write(":WAV:POIN 10000")

        except Exception as err:
            print('Exception' + str(err.message))
        finally:
            print('Tried Initialing Settings')
        
        return 0

    def TriggerMSO(self):
        self.scope.write(":*CLS")
        self.scope.write(":SING")

        while self.scope.query(":TRIG:STAT?")[:4] != "STOP":
            time.sleep(0.05)

        return 0

    def ReadWaveform(self):
        self.scope.write(":SYSTem:HEADer OFF")

        yorigin = self.scope.query(":WAVeform:YORigin?")
        yinc = self.scope.query(":WAVeform:YINCrement?")
        yref = self.scope.query(":WAVeform:YREFerence?")

        self.scope.write(":WAV:DATA? CHAN2")
        data_arr = self.scope.read_raw()

        data_arr_trimmed = data_arr[15:-1]

        yref_int = int(yref,10)
        samples_data_unscaled = numpy.array(struct.unpack('<%sc' % len(data_arr_trimmed), data_arr_trimmed))
        offset_y_byte = bytes([yref_int]*len(samples_data_unscaled))
        offset_y = numpy.frombuffer(offset_y_byte,'B')
        temp_data_unscaled = numpy.frombuffer(samples_data_unscaled,dtype=numpy.uint8) - offset_y
        
        samples_data = []
        for v in temp_data_unscaled:
            sample_val = yinc * (int.from_bytes(v, "little"))
            samples_data.append(sample_val)

        return samples_data