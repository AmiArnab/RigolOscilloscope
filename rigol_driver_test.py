import serial
import rigol_driver

# ser = serial.Serial('/dev/ttyUSB1', 115200, xonxoff=0, rtscts=0, bytesize=8, parity='N', stopbits=1)

trig_sig = "T"

#Initialise MSO
rigol_mso = rigol_driver.RigolMSO()
rigol_mso.OpenMSO()
rigol_mso.Initialise()

#File to store the sample values
#Each row is one indiviual acquisition
#"num_samples" number of sample per acquisition
fp = open("waveform.csv", "w+")

#Number of samples per acquisition
num_samples = 500

#Starting sample index to store
start_position = 10

#End sample index to store
stop_position = start_position + num_samples

#Number of acquisitions
num_iterations = 20

for i in range(num_iterations):
    
    print("Iteration: " + str(i))

    #Arm the MSO for triggering
    rigol_mso.TriggerMSO()

    #Start computation on board and trigger MSO
    # ser.write(chr(trig_sig))

    #Read response from board
    # status = ord(ser.read())
    # print("Received: " + status)

    #Read captured samples from MSO
    samples = rigol_mso.ReadWaveform()

    for j in range(start_position,stop_position):
        # int_val = float.from_bytes(samples[j], "little")
        fp.write(str(samples[j])+",")
    fp.write('\n')

fp.close()    
# ser.close()
rigol_mso.CloseMSO()