
Gas Adsorption Experiment Procedure

#Initialize the equipment: v1 = valve 1

#make sure regulator & valve Vn1 on regulator are turned on
#manually adjust the Omega MFC to the desired flow rate

p11 = Pump(chain,address=1) #define p11 as an object of the class Pump
p11.setdiameter(25) #input syringe diameter
p11.setflowrate(100) #100 uL/min
p11.settargettime(3600) #seconds

df = ['Time','Temperature','Pressure','Flow Rate']

V1.open() #flush the system with Argon
delay(6) #unit is hour

heat1.on()#turn on heater for the chamber
heat2.on() #turn on heater for the pipe

settemp = 70 #desired temp

if omegatemp(X)== settemp
   V2.open()
   V3.open()
   V4.open()
   p11.infuse()
   df=getdata #code this
   
#and then, manually access the STM-2 software to record %f values


if pump.finish == True
   V4.close()
   V2.close()
   V3.close()
   heat1.off()
   heat2.off()

delay(8)
V1.close()
