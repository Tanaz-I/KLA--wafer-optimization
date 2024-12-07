import json
class steps:
    def __init__(self,id,parameters,dependency):
        self.id=id
        self.parameters=parameters
        self.dependency=dependency

    def machine_can(self,machine):
        m=[]
        for i in machine:
            if(i.step_id==self.id and i.enable==True and i.free==True):                
                for k in self.parameters:
                    val=self.parameters[k]
                    if i.initial_parameters[k]>=val[0] and i.initial_parameters[k]<=val[1]:
                        m.append(i)
        return m
        

class machines:
    def __init__(self,machine_id,step_id,cooldown_time,initial_parameters,fluctuation,n,enable=True,free=True):
        self.machine_id=machine_id
        self.step_id=step_id
        self.cooldown_time=cooldown_time
        self.initial_parameters=initial_parameters
        self.fluctuation=fluctuation
        self.n=n
        self.enable=enable
        self.free=free

class wafers:
    def __init__(self,type,processing_times,free=True):
        self.type=type
        self.processing_times=processing_times
        self.free=True
    
    def in_schedule(self,schedule):
        for i in range(len(schedule)):
            if schedule[i].wafer_id==self.type and schedule[i].complete==False:
                return i
        return -1
    
    def in_schedule2(self,schedule,step):
        for i in range(len(schedule)):
            if schedule[i].wafer_id==self.type and schedule[i].step==step and schedule[i].complete==True:
                return i
        return -1
    
class schedules:
    def __init__(self,wafer_id,step,machine,start_time,time_req,end_time=0,complete=False):
        self.wafer_id=wafer_id
        self.step=step
        self.machine=machine
        self.start_time=start_time
        self.end_time=end_time
        self.complete=complete
        self.time_req=time_req

    def create_dict(self):
        d={}
        d['wafer_id']=self.wafer_id
        d['step']=self.step
        d['machine']=self.machine
        d['start_time']=self.start_time
        d['end_time']=self.end_time
        return d

def step_index(st,step):
    for i in range(len(step)):
        if(step[i].id==st):
            return i
        
def machine_index(m,machine):
    for i in range(len(machine)):
        if(machine[i].machine_id==m):
            return i
        
def wafer_index(w,wafer):
    for i in range(len(wafer)):
        if(wafer[i].type==w):
            return i

        
with open(r'C:\Users\csuser\Desktop\Input\Milestone0.json', 'r') as file:
    data = json.load(file)

step=[]
for i in data['steps']:
    step.append(steps(i['id'],i['parameters'],i['dependency']))
machine=[]
for i in data['machines']:
    machine.append(machines(i['machine_id'],i['step_id'],i['cooldown_time'],i['initial_parameters'],i['fluctuation'],i['n']))
wafer=[]
for i in data['wafers']:
    for j in range(i['quantity']):
        a=i['type']+'-'+str(j+1)
        wafer.append(wafers(a,i['processing_times']))

#print(data)
schedule=[]
time=0
q=[]
while True:  
    flag=0
    for i in wafer:
        for j in i.processing_times:
            if (i.in_schedule2(schedule,j) ==-1):
                flag=-1
    if flag==0:
        break

    for i in schedule:
        if i.time_req == time-i.start_time:
            k=wafer_index(i.wafer_id,wafer)
            wafer[k].free=True
            id=machine_index(i.machine,machine)
            machine[id].free=True
            i.end_time=time
            i.complete=True 

    for i in wafer:
        k=i.in_schedule(schedule)        
        if not i.free and k!=-1 and not time==i.processing_times[schedule[k].step]:
            continue  

        for j in i.processing_times:
            r=i.in_schedule2(schedule,j)
            if r!=-1 and schedule[r].complete==True:
                continue
            k=step_index(j,step)
            m=step[k].machine_can(machine)
            if m==[]:
                continue
            m[0].free=False
            i.free=False
            #print(i.type,j,m[0].machine_id,time)
            schedule.append(schedules(i.type,j,m[0].machine_id,time,i.processing_times[j]))   
            break             
    time+=1

schedule_dict=[] 
for i in schedule:
    schedule_dict.append(i.create_dict())
print(schedule_dict)
output={}
output['schedule']=schedule_dict
json_object = json.dumps(output,indent=1)
with open("Milestone0.json", "w") as outfile:
    outfile.write(json_object)
print(time-1)
time=time-1