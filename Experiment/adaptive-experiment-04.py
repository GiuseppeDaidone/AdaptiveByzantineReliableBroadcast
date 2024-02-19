# Adaptive Authenticated Double-Echo Broadcast
# Experiment 01 - Processes = [P0, P1, P2, P3], Sender = P0, Byzantine P3
# Processes P0, P1, P2 ready m but P3 ready m'

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
        
    def setSender(self, sender):
        self.s = sender
        
    def getId(self):
        return self.id
        
    def abrbBroadcast(self, msg):
        print("*Broadcast*: " + str(self.id) + " sends " + msg)
        for q in self.correct:
            print("Sending alSend: " + str(self.id) + " -> " + str(q.getId()))
            q.alSendSend(self.id, self, msg) # Trigger alSendSend
    
    def alSendSend(self, id, sender, msg):
        self.phase1 = True
        
    def getPhase1(self):
        return self.phase1
    
    def alDeliverSend(self, id, sender, msg):
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
    
    def suspectedAppend(self, id):
        for p in self.Processes:
            if p.getId() == id:
                self.suspected.append(p)
    
    def consistentEchoWaitEvent(self):
        if len(self.echos) > ((3*len(self.correct))/4):
            cons = self.consistentMessage(self.echos)
            print(self.id + " found cons = " + cons)
            for p in self.echos:
                if self.echos[p] != cons and p != self.s.getId() and p not in self.suspected:
                    self.suspectedAppend(p)
                    self.f = self.f + 1
            if self.echos[self.s.getId()] != self.echos[self.getId()]:
                self.f = self.f + 1
                self.faulty.append(self.s)
                self.correct.remove(self.s)
                self.byzantinesender = True
                print(self.getId() + " detected the sender as Byzantine")
                for q in self.correct:
                    q.ByzantineSenderSend(self.getId(), self.echos) # Trigger ByzantineSender
            elif self.suspected is not None and self.s not in self.suspected:
                self.suspected.append(self.s)
            
    def correct_minus_suspected(self):
        correct_minus_suspected = self.correct.copy()
        if self.suspected is not None:
            for p in self.suspected:
                if p in correct_minus_suspected:
                    correct_minus_suspected.remove(p)
        return correct_minus_suspected
    
    def readyWaitEvent(self, msg):
        if len(self.echos) > ((len(self.correct) + self.f) / 2) and self.sentready == False and self.byzantinesender == False:
            self.sentready = True
            correct_minus_suspected = self.correct_minus_suspected()
            correct_minus_suspected.append(self.s)
            for q in correct_minus_suspected:
                print("Sending alReady: " + str(self.id) + " -> " + str(q.getId()))
                q.alSendReady(self.id, msg) # Trigger alSendReady
            return True
        return False
    
    def alSendReady(self, id, msg):
        self.phase3 = True
        if id == "P3":
                self.alDeliverReady(id, "Hello Byzantine!")
        else:
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
                
    def suspectedRemove(self, id):
        for p in self.suspected:
            if p.getId() == id:
                self.suspected.remove(p)
    
    def alDeliverReady(self, id, msg):
        if self.readys.get(id) is None and self.echos.get(id) == msg:
            print("Delivering alReady by " + str(self.id))
            self.readys[id] = msg
        elif self.readys.get(id) != self.echos.get(id) and id != self.s.getId():
            self.f = self.f + 1
            self.faultyAppend(self.correct, id)
            self.correctRemove(id)
            self.suspectedRemove(id)
        if len(self.echos) > self.f and self.sentready == False:
            self.sentready = True
            for q in self.correct:
                q.alSendReady(self.id, msg) # Trigger alSendReady
            self.timer = time.time() # StartTimer()
    
    def readyCheckWaitEvent(self):
        if len(self.readys) > 2*self.f and self.byzantinesender == False:
            if self.readys.get(self.s) != self.echos.get(self.s):
                self.f = self.f + 1
                self.faulty.append(self.s)
                self.correct.remove(self.s)
                self.byzantinesender = True
                print(self.getId() + " detected the sender as Byzantine")
                for q in self.correct:
                    q.ByzantineSenderSend(self.getId(), self.echos) # Trigger ByzantineSender
            elif self.suspected is not None:
                self.suspected.remove(self.s)
                for p in self.suspected:
                    self.faulty.append(p)
                    self.correct.remove(p)
                    self.suspected.remove(p)

    def ByzantineSenderSend(self, p_id, echos_p):
        self.ByzantineSenderDeliver(p_id, echos_p)

    def ByzantineSenderDeliver(self, p_id, echos_p):
        self.senderechos.append(echos_p[p_id])
        
    def suspected_minus_sender(self):
        suspected_minus_sender = self.suspected.copy()
        if self.s in suspected_minus_sender:
            suspected_minus_sender.remove(self.s)
        return suspected_minus_sender
    
    def misledCheckWaitEvent(self):
        correct_minus_suspected = self.correct_minus_suspected()
        if len(self.senderechos) == len(correct_minus_suspected) - 1:
            if self.byzantinesender == False:
                for m in self.senderechos:
                    if self.echos.get(self.getId()) != m:
                        suspected_minus_sender = self.suspected_minus_sender()
                        for q in suspected_minus_sender:
                            self.correct.append(q)
                            self.f = self.f - 1
                        self.f = self.f + 1
                        self.faulty.append(self.s)
                        self.correct.remove(self.s)
                        self.suspected.remove(self.s)
                        self.byzantinesender = True
                        print(self.getId() + " detected the sender as Byzantine")
                        for p in self.correct:
                            p.ByzantineSenderSend(self.getId(), self.echos) # Trigger ByzantineSender
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
            self.message = msg # Trigger abrbDeliver

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
        p.setSender(P0)
    msg = "Hello World!"
    
    # BrB broadcast
    P0.abrbBroadcast(msg)
    
    # Send phase
    phase1Set = []
    for q in Processes:
        if q.getPhase1() == True:
            phase1Set.append(q)
            q.alDeliverSend(q.getId(), P0, msg)
    
    # Echo phase
    phase2Set = []
    for q in phase1Set:
        if q.getPhase2() == True:
            phase2Set.append(q)
            
    # Consistent Echo Message
    for q in phase2Set:
        q.consistentEchoWaitEvent()
    
    # Ready phase
    phase3Set = []
    for q in phase2Set:
        q.readyWaitEvent(msg)
        if q.getPhase3() == True:
            phase3Set.append(q)
    
    # Ready Check Wait
    for q in phase3Set:
        q.readyCheckWaitEvent()
    
    # Misled Check Wait
    phase3SetReduced = phase3Set.copy()
    if P0 in phase3SetReduced:
        phase3SetReduced.remove(P0)
    for q in phase3SetReduced:
        q.misledCheckWaitEvent()
    
    # Check timeout
    for q in phase3Set:
        if q.timer != 0 and time.time() - q.timer > 5:
            q.Timeout()
    
    # ABrB deliver
    for q in phase3Set:
        q.abrbDeliver(msg)
        
    # Message stored
    for q in phase3Set:
        print("Message stored by " + q.getId() + ": " + q.getMessage())

    # Check values in case of Byzantines
    Correct = [P0, P1, P2]
    for p in Correct:
        echos = "[ "
        for e in p.echos.items():
            echos = echos + str(e) + " "
        echos = echos + "]"
        readys = "[ "
        for r in p.readys.items():
            readys = readys + str(r) + " "
        readys = readys + "]"
        correct = "[ "
        for c in p.correct:
            correct = correct + c.getId() + " "
        correct = correct + "]"
        faulty = "[ "
        for b in p.faulty:
            faulty = faulty + b.getId() + " "
        faulty = faulty + "]"
        print(p.getId() + ": Echos " + echos + ", Readys" + readys + ", Correct " + correct + ", Faulty " + faulty + ", f = " + str(p.f))