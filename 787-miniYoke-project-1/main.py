import threading, sys
from systems import FCC, MiniYoke, ApLAT, ApLONG, FMGS, FCU, FlightModel
from bus import AviBus

aviBus = AviBus(appName="MiniYokeModule", adress="127.255.255.255:2010")

apLat = ApLAT()
apLong = ApLONG()
fmgs = FMGS()
fcu = FCU()
flightModel = FlightModel()

fcc = FCC(fcu, aviBus)
miniYoke = MiniYoke(fcc, fmgs, flightModel, alphaFilter=0.1)

running = True

def init():
    #while not miniYoke.begin() :
        #pass

    #global yokeThread
    #yokeThread = threading.Thread(target=miniYoke.listener)
    #yokeThread.start()

    # Bind avi bus msg here
    aviBus.bindMsg(apLat.parser, apLat.regex)
    aviBus.bindMsg(apLong.parser, apLong.regex)
    aviBus.bindMsg(fmgs.parser, fmgs.regex)
    aviBus.bindMsg(fcu.parser, fcu.regex)
    aviBus.bindMsg(flightModel.parser, flightModel.regex)

def main():
    match fcc.state :  # Manage states transitions
        case 'MANUAL':
            if fcu.ApState == 'ON':
                print('fcc state switch from MANUAL to AP_ENGAGED')
                aviBus.sendMsg('FCUAP1 on') # Send acknowledge message to the fcu

                fcc.setState('AP_ENGAGED')

        case 'AP_ENGAGED':
            if fcu.ApState == 'OFF':
                print('fcc state switch from AP_ENGAGED to MANUAL')
                aviBus.sendMsg('FCUAP1 off') # Send acknowledge message to the fcu

                fcc.setState('MANUAL')
            
            elif miniYoke.moved : 
                print('miniYoke has been mooved state switch from AP_ENGAGED to MANUAL')
                aviBus.sendMsg('FCUAP1 off') # Send AP off message to the fcu
                
                fcu.setApState('OFF')
                fcc.setState('MANUAL')

        case _:
            print("Error : unknown miniYoke state")
        
    match fcc.state :  # Manage states actions
        case 'MANUAL':
            if fcc.ready:
                aviBus.sendMsg('APNxControl nx={}'.format(float(fcc.nx)))
                aviBus.sendMsg('APNzControl nz={}'.format(float(fcc.nz)))
                aviBus.sendMsg('APLatControl rollRate={}'.format(float(fcc.p)))
                

                #print('Sent APNxControl nx={}'.format(fcc.nx))
                #print('Sent APNzControl nz={}'.format(fcc.nz))
                #print('Sent APLatControl p={}'.format(fcc.p))

                fcc.setReady(False)

        case 'AP_ENGAGED':
            if apLat.ready and apLong.ready :
                aviBus.sendMsg('APNxControl nx={}'.format(apLong.nx))
                aviBus.sendMsg('APNzControl nz={}'.format(apLong.nz))
                aviBus.sendMsg('APLatControl rollRate={}'.format(apLat.p))
                

                print('Sent APNxControl nx={}'.format(apLong.nx))
                print('Sent APNzControl nz={}'.format(apLong.nz))
                print('Sent APLatControl p={}'.format(apLat.p))

                apLat.setReady(False)
                apLong.setReady(False)
            
        case _:
            print("Error : unknown miniYoke state")
    
def close():
    miniYoke.end()
    aviBus.stop()

if __name__ == '__main__':
    init()
    try:
        while running:
            main()
    except KeyboardInterrupt:
        running = False
    close()
    sys.exit(0)