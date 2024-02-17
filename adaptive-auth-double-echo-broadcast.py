# Adaptive Authenticated Double-Echo Broadcast

from collections import Counter
import time

class Process:
    def __init__(self, id, f):
        self.sentecho = False
        self.sentready = False
        self.delivered = False
        self.echos = {}
        self.readys = {}
        self.id = id
        self.correct = []
        self.suspected = []
        self.faulty = []
        self.f = f
        self.s = ""
        self.byzantinesender = False
        self.senderechos = []
        self.timer = 0
        self.phase1 = False
        self.phase2 = False
        self.phase3 = False
        self.message = ""
        
    def setProcesses(self, Processes):
        self.Processes = Processes
        self.correct = Processes.copy()
        
    def getId(self):
        return self.id
        
    def abrbBroadcast(self, msg):
        print("*Broadcast*: " + str(self.id) + " sends " + msg)
        for q in self.correct:
            print("Sending alSend: " + str(self.id) + " -> " + str(q.getId()))
            q.alSendSend(self.id, self, msg) # Trigger alSendSend
    
    def alSendSend(self, id, sender, msg):
        self.phase1 = True
        self.alDeliverSend(id, sender, msg)
        
    def getPhase1(self):
        return self.phase1
    
    def alDeliverSend(self, id, sender, msg):
        self.s = sender
        if self.sentecho == False:
            print("Delivering alSend by " + str(self.id))
            self.sentecho = True
            for q in self.correct:
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
    
    def consistentMessage(self, echos_set):
        msg = {}
        for id in echos_set.keys():
            if echos_set.get(id) not in msg:
                msg[echos_set.get(id)] = 1
            else:
                msg[echos_set.get(id)] = msg[echos_set.get(id)] + 1
        cons, count = Counter(msg).most_common(1)[0]
        return cons
    
    def consistentEchoWaitEvent(self):
        if len(self.echos) > ((3*len(self.correct))/4):
            cons = self.consistentMessage(self.echos)
            print(self.id + " found cons = " + cons)
            for p in self.echos:
                if self.echos[p] != cons and p != self.s and p not in self.suspected:
                    self.suspected.append(p)
                    f = f + 1
            if self.echos[self.s.getId()] != cons:
                f = f + 1
                self.faulty.append(self.s)
                self.correct.remove(self.s)
                self.byzantinesender = True
                for q in self.correct:
                    q.ByzantineSenderSend(self.echos) # Trigger ByzantineSender
            elif self.suspected is not None and self.s not in self.suspected:
                self.suspected.append(self.s)
            
    def correct_minus_suspected(self):
        correct_minus_suspected = []
        if self.suspected is not None:
            for p in self.correct:
                if p.getId() not in self.suspected:
                    correct_minus_suspected.append(p)
        return correct_minus_suspected
    
    def readyWaitEvent(self, msg):
        if len(self.echos) > ((len(self.correct) + self.f) / 2) and self.sentready == False and self.byzantinesender == False:
            self.sentready = True
            correct_minus_suspected = self.correct_minus_suspected()
            for q in correct_minus_suspected:
                print("Sending alReady: " + str(self.id) + " -> " + str(q.getId()))
                q.alSendReady(self.id, msg) # Trigger alSendReady
            return True
        return False
    
    def alSendReady(self, id, msg):
        self.phase3 = True
        self.alDeliverReady(id, msg)
        
    def getPhase3(self):
        return self.phase3     
    
    def faultyAppend(self, collection, id):
        for p in collection:
            if p.getId() == id:
                self.faulty.append(p)
    
    def correctRemove(self, id):
        for p in self.correct:
            if p.getId() == id:
                self.correct.remove(p)
    
    def alDeliverReady(self, id, msg):
        if self.readys.get(id) is None and self.echos.get(id) == msg:
            print("Delivering alReady by " + str(self.id))
            self.readys[id] = msg
        elif self.readys.get(id) != self.echos.get(id) and id != self.s.getId():
            self.faultyAppend(self.correct, id) # -> Every process think that the others are faulty
            self.correctRemove(id)
        if len(self.echos) > self.f and self.sentready == False:
            self.sentready = True
            for q in self.Processes:
                q.alSendReady(self.id, msg) # Trigger alSendReady
            self.timer = time.time() # StartTimer()
    
    def readyCheckWaitEvent(self):
        if len(self.readys) > 2*self.f and self.byzantinesender == False:
            if self.readys.get(self.s) != self.echos.get(self.s):
                self.f = self.f + 1
                self.faulty.append(self.s)
                self.correct.remove(self.s)
                self.byzantinesender = True
                for q in self.correct:
                    q.ByzantineSenderSend(self.echos) # Trigger ByzantineSender
            elif self.suspected is not None:
                self.suspected.remove(self.s)
                for p in self.suspected:
                    self.faulty.append(p)
                    self.correct.remove(p)
                    self.suspected.remove(p)

    def ByzantineSenderSend(self, echos_p):
        self.ByzantineSenderDeliver(self, echos_p)

    def ByzantineSenderDeliver(self, echos_p):
        self.senderechos = self.senderechos + echos_p[self.s]
    
    def deliverCheckWaitEvent(self):
        correct_minus_suspected = self.correct_minus_suspected()
        if len(self.senderechos) == len(correct_minus_suspected) - 1:
            if self.byzantinesender == False:
                for m in self.senderechos:
                    if self.echos.get(self.getId()) != m:
                        for q in self.suspected:
                            self.correct.append(q)
                            self.f = self.f - 1
                        self.f = self.f + 1
                        self.faulty.append(self.s)
                        self.correct.remove(self.s)
                        self.suspected.remove(self.s)
                        self.byzantinesender = True
                        for p in self.correct:
                            q.ByzantineSenderSend(self.echos) # Trigger ByzantineSender
                        break

    def Timeout(self):
        for q in self.suspected:
            self.faulty.append(q)
            self.correct.remove(q)
            self.suspected.remove(q)
        self.suspected.remove(self.s)
        
    def abrbDeliver(self, msg):
        if len(self.readys) > 2*self.f and self.delivered == False:
            self.delivered = True
            print("*Delivering Broadcast*: " + str(self.id) + " recieves " + msg)
            self.message = msg # Trigger brbDeliver

    def getMessage(self):
        return self.message

if __name__ == "__main__":
    f = 0
    P0 = Process("P0", f)
    P1 = Process("P1", f)
    P2 = Process("P2", f)
    P3 = Process("P3", f)
    Processes = [P0, P1, P2, P3]
    for p in Processes:
        p.setProcesses(Processes)
    msg = "Hello World!"
    
    # BrB broadcast
    P0.abrbBroadcast(msg)
    
    # Send phase
    #print("SendPhase")
    phase1Set = []
    for q in Processes:
        if q.getPhase1() == True:
            phase1Set.append(q)
            q.alDeliverSend(q.getId(), P0, msg)
    
    # Echo phase
    #print("EchoPhase")
    phase2Set = []
    for q in phase1Set:
        if q.getPhase2() == True:
            phase2Set.append(q)
            #q.alDeliverEcho(q.getId(), msg)
            
    # Consistent Echo Message
    for q in phase2Set:
        q.consistentEchoWaitEvent()
    
    # Ready phase
    #print("ReadyPhase")
    phase3Set = []
    for q in phase2Set:
        q.readyWaitEvent(msg)
        if q.getPhase3() == True:
            phase3Set.append(q)
            #q.alDeliverReady(q.getId(), msg)
    
    # Ready Check Wait
    for q in phase3Set:
        q.readyCheckWaitEvent()
    
    # Deliver Check Wait
    for q in phase3Set:
        q.deliverCheckWaitEvent()
    
    # Check timeout
    for q in phase3Set:
        if q.timer != 0 and time.time() - q.timer > 5:
            q.Timeout()
    
    # BrB deliver
    for q in phase3Set:
        q.abrbDeliver(msg)
        
    # Message stored
    for q in phase3Set:
        print("Message stored by " + q.getId() + ": " + q.getMessage())