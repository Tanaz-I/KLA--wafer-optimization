import json
class steps:
    def __init__(self,id,parameters,dependency):
        self.id=id
        self.parameters=parameters
        self.dependency=dependency

    def machine_can(self,machine):
        machine_allocated=[]
       
        for machine_iter in machine:
            if(machine_iter.step_id==self.id and machine_iter.free==True):                
                for parameter in self.parameters:
                    value=self.parameters[parameter]
                    if machine_iter.initial_parameters[parameter]>=value[0] and machine_iter.initial_parameters[parameter]<=value[1]:
                        machine_allocated.append(machine_iter)      
                        
        return machine_allocated
        

class machines:
    def __init__(self,machine_id,step_id,cooldown_time,initial_parameters,fluctuation,n,enable=False,free=True,count=0,start_time=0):
        self.machine_id=machine_id
        self.step_id=step_id
        self.cooldown_time=cooldown_time
        self.initial_parameters=initial_parameters
        self.fluctuation=fluctuation
        self.n=n
        self.enable=enable
        self.free=free
        self.count=0
        self.start_time=start_time

class wafers:
    def __init__(self,type,processing_times,free=True):
        self.type=type
        self.processing_times=dict(sorted(processing_times.items(), key=lambda item: item[1]))
        self.free=True
        self.completed=[]
    
    def in_schedule(self,schedule):
        for schedule_iter in range(len(schedule)):
            if schedule[schedule_iter].wafer_id==self.type and schedule[schedule_iter].complete==False:
                return schedule_iter
        return -1
    
    def in_schedule2(self,schedule,step):
        for schedule_iter in range(len(schedule)):
            if schedule[schedule_iter].wafer_id==self.type and schedule[schedule_iter].step==step and schedule[schedule_iter].complete==True:
                return schedule_iter
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

        
with open(r'Z:\Milestone6a.json', 'r') as file:
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
    for wafer_iter in wafer:
        for process_iter in wafer_iter.processing_times:
            if (wafer_iter.in_schedule2(schedule,process_iter) ==-1):
                flag=-1
    if flag==0:
        break
    
    for machine_iter in machine:
        if(time-machine_iter.start_time==machine_iter.cooldown_time and machine_iter.enable==True):
            print("A:",machine_iter.machine_id,time)
            machine_iter.initial_parameters,machine_iter.fluctuation=machine_iter.fluctuation,machine_iter.initial_parameters
            machine_iter.start_time=0
            machine_iter.enable=False
            


    for schedule_iter in schedule:
        if schedule_iter.time_req == time-schedule_iter.start_time:
            wafer_iter=wafer_index(schedule_iter.wafer_id,wafer)
            wafer[wafer_iter].free=True
            machine_iter=machine_index(schedule_iter.machine,machine)
            machine[machine_iter].free=True
            schedule_iter.end_time=time
            schedule_iter.complete=True 
            

    for wafer_iter in wafer:
         
        if not wafer_iter.free:
            continue  

        for process_iter in wafer_iter.processing_times:
            schedule_index=wafer_iter.in_schedule2(schedule,process_iter)
            if schedule_index!=-1 and schedule[schedule_index].complete==True:
                continue
            step_iter=step_index(process_iter,step)
            flag2=0
            if step[step_iter].dependency != None:
                for dependency in step[step_iter].dependency:
                    if dependency not in wafer_iter.completed:  
                        flag2=1                  
            if flag2==1:
                continue            
                           

            machine_allocated=step[step_iter].machine_can(machine)
            if machine_allocated==[]:
                continue
            
            for machine_iter in machine_allocated: 
                if machine_iter.free==True:               
                    machine_iter.free=False
                    wafer_iter.free=False
                    print(wafer_iter.type,process_iter,machine_iter.machine_id,time)
                    machine_iter.count+=1
                    if(machine_iter.n==machine_iter.count):
                        
                        for parameter in machine_iter.initial_parameters:
                            ans=machine_iter.fluctuation[parameter]+machine_iter.initial_parameters[parameter]
                            machine_iter.fluctuation[parameter]=machine_iter.initial_parameters[parameter]
                            machine_iter.initial_parameters[parameter]=ans                        
                        
                        machine_iter.start_time=wafer_iter.processing_times[process_iter]+time
                        print("Cooling: ",machine_iter.machine_id,time,machine_iter.start_time,machine_iter.count)
                        machine_iter.count=0
                        machine_iter.enable=True
                    schedule.append(schedules(wafer_iter.type,process_iter,machine_iter.machine_id,time,wafer_iter.processing_times[process_iter])) 
                    if process_iter not in wafer_iter.completed:  
                        wafer_iter.completed.append(process_iter)
                    break
            break             
    time+=1

schedule_dict=[] 
for i in schedule:
    schedule_dict.append(i.create_dict())
#print(schedule_dict)
for i in schedule_dict:
    print(i)
output={}
output['schedule']=schedule_dict
json_object = json.dumps(output,indent=1)
with open("Milestone6a.json", "w") as outfile:
    outfile.write(json_object)
print(time-1)
time=time-1