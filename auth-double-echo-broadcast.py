# Authenticated Double-Echo Broadcast

class Process:
    def __init__(self, id, f):
        self.sentecho = False
        self.sentready = False
        self.delivered = False
        self.echos = {}
        self.readys = {}
        self.id = id
        self.f = f
        self.phase1 = False
        self.phase2 = False
        self.phase3 = False
        self.message = ""
        
    def setProcesses(self, Processes):
        self.Processes = Processes
        
    def getId(self):
        return self.id
        
    def brbBroadcast(self, msg):
        print("*Broadcast*: " + str(self.id) + " sends " + msg)
        for q in self.Processes:
            print("Sending alSend: " + str(self.id) + " -> " + str(q.getId()))
            q.alSendSend(self.id, msg) # Trigger alSendSend
    
    def alSendSend(self, id, msg):
        self.phase1 = True
        self.alDeliverSend(id, msg)
        
    def getPhase1(self):
        return self.phase1
    
    def alDeliverSend(self, id, msg):
        if self.sentecho == False:
            print("Delivering alSend by " + str(self.id))
            self.sentecho = True
            for q in self.Processes:
                print("Sending alEcho: " + str(self.id) + " -> " + str(q.getId()))
                q.alSendEcho(self.id, msg) # Trigger alSendEcho
    
    def alSendEcho(self, id, msg):
        self.phase2 = True
        self.alDeliverEcho(id, msg)
        
    def getPhase2(self):
        return self.phase2

    def alDeliverEcho(self, id, msg):
        if self.echos.get(id) is None:
            print("Delivering alEcho by " + str(self.id))
            self.echos[id] = msg
    
    def readyWaitEvent(self, msg):
        if len(self.echos) > ((len(self.Processes) + self.f) / 2) and self.sentready == False:
            self.sentready = True
            for q in self.Processes:
                print("Sending alReady: " + str(self.id) + " -> " + str(q.getId()))
                q.alSendReady(self.id, msg) # Trigger alSendReady
            return True
        return False
    
    def alSendReady(self, id, msg):
        self.phase3 = True
        self.alDeliverReady(id, msg)
        
    def getPhase3(self):
        return self.phase3     
         
    def alDeliverReady(self, id, msg):
        if self.readys.get(id) is None:
            print("Delivering alReady by " + str(self.id))
            self.readys[id] = msg  
        if len(self.echos) > self.f and self.sentready == False:
            self.sentready = True
            for q in self.Processes:
                q.alSendReady(self.id, msg) # Trigger alSendReady
        
    def brbDeliver(self, msg):
        if len(self.readys) > 2*self.f and self.delivered == False:
            self.delivered = True
            print("*Delivering Broadcast*: " + str(self.id) + " recieves " + msg)
            self.message = msg # Trigger brbDeliver

    def getMessage(self):
        return self.message

if __name__ == "__main__":
    f = 1
    P0 = Process("P0", f)
    P1 = Process("P1", f)
    P2 = Process("P2", f)
    P3 = Process("P3", f)
    Processes = [P0, P1, P2, P3]
    for p in Processes:
        p.setProcesses(Processes)
    msg = "Hello World!"
    
    # BrB broadcast
    P0.brbBroadcast(msg)
    
    # Send phase
    #print("SendPhase")
    phase1Set = []
    for q in Processes:
        if q.getPhase1() == True:
            phase1Set.append(q)
            q.alDeliverSend(q.getId(), msg)
    
    # Echo phase
    #print("EchoPhase")
    phase2Set = []
    for q in phase1Set:
        if q.getPhase2() == True:
            phase2Set.append(q)
            #q.alDeliverEcho(q.getId(), msg)
    
    # Ready phase
    #print("ReadyPhase")
    phase3Set = []
    for q in phase2Set:
        q.readyWaitEvent(msg)
        if q.getPhase3() == True:
            phase3Set.append(q)
            #q.alDeliverReady(q.getId(), msg)
    
    # BrB deliver
    for q in phase3Set:
        q.brbDeliver(msg)
        
    # Message stored
    for q in phase3Set:
        print("Message stored by " + q.getId() + ": " + q.getMessage())