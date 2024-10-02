import re
import argparse
import random
import math
import matplotlib.pyplot as plt
class Block:
    def __init__(self, block_name, is_soft, length, width):
        # Details of the block
        self.block_name = block_name
        self.is_soft = is_soft # True for a soft-macro, None (or False) for a hard-macro
        self.length = length
        self.width = width
        self.area = length * width
        # To keep track of slicing tree for incremental cost update
        self.parent_block = None
        self.left_child = None
        self.right_child = None
        # For soft-macros only, otherwise None
        self.min_aspect_ratio = None
        self.max_aspect_ratio = None
        self.optimal_aspect_ratio = None # the optimal aspect ratio
        # To print the coordinates of each block.
        self.x_coordinate = 0.0 # lower left
        self.y_coordinate = 0.0 # lower left





class Floorplan():
    def __init__(self):
        self.blocks=[]
        self.blocks_dict={}
        self.polish_expression=[]
        self.operands_list=[]
        self.operators_list=[]
        self.best = []
        self.best_length_width = []
        self.possible_dimensions = {}
        self.causal_left_dimensions = {}
        self.causal_right_dimensions = {}
    
    def blocks_parse(self,file):
        with open(file,"r") as f:
            content = f.read()
            if content[0]!=' ':
                lines = re.split('\n',content)
                for line in lines:
                    if len(line)>1:
                        if(line.find('hardrectilinear'))!= -1:
                            spec = re.split(' ',line)
                            #print(spec)
                            new_block = Block(spec[0],False, float(spec[6][0:len(spec[6])-1]), float(spec[7][1:len(spec[7])-1]))
                            self.blocks.append(new_block) 
                            self.blocks_dict[new_block.block_name] = len(self.blocks)-1
                        if(line.find('softrectangular')!=-1):
                            
                            spec = re.split(' ',line)
                            #print(spec)
                            length = math.sqrt(float(spec[2]))
                            new_block = Block(spec[0],True,length,length)
                            new_block.max_aspect_ratio = spec[4]
                            new_block.min_aspect_ratio = spec[3] 
                            self.blocks.append(new_block)
                            self.blocks_dict[new_block.block_name] = len(self.blocks)-1 
                #if spec[1].find('hardrectilinear') != -1:
                 #   new_block = Block(spec[0],False, spec[4], spec[5])
                #  self.blocks.append(new_block)
    def display(self):
        for b in self.blocks:
            print(b.block_name,' ',b.is_soft,' ',b.length,' ',b.width, ' ', b.area,' ', self.blocks_dict[b.block_name])

    def polish_initial(self):
        for b in self.blocks:
            if len(self.polish_expression) == 0:
                self.operands_list.append(len(self.polish_expression))
                self.polish_expression.append(b.block_name)
            else:
                self.operands_list.append(len(self.polish_expression))
                self.polish_expression.append(b.block_name)
                self.operators_list.append(len(self.polish_expression))
                self.polish_expression.append('|')
        #print(self.polish_expression)
    
    def find_area(self):
        stack = []
        for x in self.polish_expression:
            if(x!=''):
                if(x == '|'):
                    d2=stack.pop()
                    d1=stack.pop()
                    dn=(max(d1[0],d2[0]),d1[1]+d2[1])
                    stack.append(dn)
                elif(x == '-'):
                    d2=stack.pop()
                    d1=stack.pop()
                    dn=(d1[0]+d2[0],max(d1[1],d2[1]))
                    stack.append(dn)
                else:
                    dn=(self.blocks[self.blocks_dict[x]].length,self.blocks[self.blocks_dict[x]].width)
                    stack.append(dn)
        df=stack.pop()
        return df[0]*df[1]
    
    def add_coordinates(self,string_pos,origin):
        if string_pos[0]==string_pos[1]:
            self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].x_coordinate=origin[0]
            self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].y_coordinate=origin[1]
            return self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].width+origin[0],self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].length+origin[1]
        else:
            j=string_pos[1]-1
            operator=self.polish_expression[string_pos[1]]
            operator_count=0
            operands_count=0
            while j>string_pos[0]:
                if self.polish_expression[j]=='|' or self.polish_expression[j]=='-':
                    operator_count=operator_count+1
                else:
                    operands_count=operands_count+1
                if operands_count>operator_count:
                    right_start=j
                    break
                j=j-1
            right_string_pos = right_start,string_pos[1]-1
            left_string_pos = string_pos[0],right_start-1
            if operator == '|':
                left_right_corner = self.add_coordinates(left_string_pos,origin)
                right_origin = left_right_corner[0],origin[1]
                right_right_corner = self.add_coordinates(right_string_pos,right_origin)
                return right_right_corner[0],max(left_right_corner[1],right_right_corner[1])
            elif operator =='-':
                bottom_right_corner = self.add_coordinates(left_string_pos,origin)   ###left tree is considered at bottom
                right_origin = origin[0],bottom_right_corner[1]
                top_right_corner = self.add_coordinates(right_string_pos,right_origin)
                return max(bottom_right_corner[0],top_right_corner[0]),top_right_corner[1]
            




    def operation1(self):
        lindex_operand = random.choice(range(len(self.operands_list)-1))
        lindex = self.operands_list[lindex_operand]
        rindex = self.operands_list[lindex_operand + 1]
        #print("lindex:",lindex)
        #print("rindex:",rindex)
        temp = self.polish_expression[rindex]
        self.polish_expression[rindex] = self.polish_expression[lindex]
        self.polish_expression[lindex]=temp
        
    def operation2(self):
        random_numbers = random.sample(range(1,len(self.operands_list)),2)    #to make sure atleast one sign change will happen atevery time assuming that the first two in a polish expression are always blocks 
        lindex=min(self.operands_list[random_numbers[0]],self.operands_list[random_numbers[1]])
        rindex=max(self.operands_list[random_numbers[0]],self.operands_list[random_numbers[1]])
        #print("lindex",lindex)
        #print("rindex:",rindex)
        while(lindex<rindex):
            if(self.polish_expression[lindex]=='|'):
                self.polish_expression[lindex]='-'
            elif(self.polish_expression[lindex]=='-'):
                self.polish_expression[lindex]='|'
            lindex=lindex+1

    def is_normal(self, index):
        if 0<index<len(self.polish_expression)-1:
            return ((self.polish_expression[index]!=self.polish_expression[index+1]) and (self.polish_expression[index]!=self.polish_expression[index-1]))
        elif index ==0:
            return self.polish_expression[index]!=self.polish_expression[index+1]
        elif index == len(self.polish_expression)-1:
            return self.polish_expression[index]!=self.polish_expression[index-1]

    def is_valid(self):
        operators_count=0
        operands_count=0
        for x in self.polish_expression:
            if x =='|' or x =='-':
                operators_count= operators_count+1
            else:
                operands_count = operands_count+1
            if operators_count>=operands_count:
                return False
        return True

    def operation3(self):
        #change_successfull=False
        index = random.choice(range(self.operands_list[len(self.operands_list)-1]+1))
        #print(index)
        index2 =  random.choice(range(2))
        if index2 == 0:
            while (index < len(self.polish_expression)-1):
                #if condition checks for first symbol then a block so no issue of expression being a valid one
                if (index in self.operators_list) and (index+1 in self.operands_list):
                    self.polish_expression[index], self.polish_expression[index+1] = self.polish_expression[index+1],self.polish_expression[index]   
                    #print(index+1)
                    #print("Truth",self.is_normal(index+1))
                    if self.is_normal(index+1) and self.is_valid():
                        #print("operators first",index)
                        self.operands_list[self.operands_list.index(index+1)]=index
                        self.operators_list[self.operators_list.index(index)]=index+1
                        #print("operands_list opertion3:",self.operands_list)
                        #print("operators_list opertion3:",self.operators_list)
                        break
                    else:
                        self.polish_expression[index], self.polish_expression[index+1] = self.polish_expression[index+1],self.polish_expression[index]   
                        
                index = index+1
        else:
            if index == 0:
                index =2
            while (index < len(self.polish_expression)-1):
                if (index in self.operators_list) and (index - 1 in self.operands_list):
                    self.polish_expression[index],self.polish_expression[index-1] = self.polish_expression[index-1],self.polish_expression[index]
                    #print(index)
                    if self.is_normal(index-1) and self.is_valid():
                        #print("operands first",index)
                        self.operators_list[self.operators_list.index(index)]=index-1
                        self.operands_list[self.operands_list.index(index-1)]=index
                        break
                    else:
                        self.polish_expression[index],self.polish_expression[index-1] = self.polish_expression[index-1],self.polish_expression[index]
                index = index + 1
                #print(index)
            #print(self.operands_list)
            #print(self.operators_list)

    def operation_randomise(self):
        ##add a randomise function to select any of the below operations
        index= random.choice(range(3))
        if index ==0:
            self.operation1()
            #print("op1")
        elif index ==1:
            self.operation2()
            #print("op2")
        elif index == 2:
            #print("op3")
            self.operation3()

    def simulated_annealing_parameter(self):
        length_cumulated=0
        breadth_cumulated = 0
        area_max = 1000000000.00
        area_cumulated = 0
        for x in self.blocks:
            length_cumulated=length_cumulated + x.length
            breadth_cumulated= breadth_cumulated + x.width  
            area_max = min(area_max , (x.length * x.width))
            area_cumulated = area_cumulated + (x.length * x.width)
        Thot = length_cumulated * breadth_cumulated
        return Thot,area_max,area_cumulated

    def sizing(self,string_pos):
        if string_pos[0]==string_pos[1]:
            if self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].is_soft==False:
                self.possible_dimensions[string_pos[0]]=[]
                minimum=min(self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].length,self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].width)
                maximum=max(self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].length,self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].width)
                if minimum!=maximum:
                    self.possible_dimensions[string_pos[0]]=[]
                    self.possible_dimensions[string_pos[0]].append((minimum,maximum))
                    self.possible_dimensions[string_pos[0]].append((maximum,minimum))
                else:
                    self.possible_dimensions[string_pos[0]].append((minimum,maximum))
            else:
                #print("abc")
                self.possible_dimensions[string_pos[0]]=[]
                square_dimension = self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].width
                
                if self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].min_aspect_ratio!=self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].max_aspect_ratio:
                    ar =float(self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].min_aspect_ratio)
                    area = self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].area

                    width = math.sqrt(ar*area)
                    length = area/width
                    self.possible_dimensions[string_pos[0]].append((width,length))

                    if float(self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].min_aspect_ratio)<1 and 1<float(self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].max_aspect_ratio):
                        square_dimension = self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].width
                        self.possible_dimensions[string_pos[0]].append((square_dimension,square_dimension))

                    ar = float(self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].max_aspect_ratio)
                    area = self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].area

                    width = math.sqrt(ar*area)
                    length = area/width
                    self.possible_dimensions[string_pos[0]].append((width,length))

                else:
                    ar =float(self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].min_aspect_ratio)
                    area = self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].area

                    width = math.sqrt(ar*area)
                    length = area/width
                    self.possible_dimensions[string_pos[0]].append((width,length))
            #else if for soft blocks to add elements
        else:
            #print(string_pos)
            j=string_pos[1]-1
            operator=self.polish_expression[string_pos[1]]
            operator_count=0
            operands_count=0
            while j>string_pos[0]:
                if self.polish_expression[j]=='|' or self.polish_expression[j]=='-':
                    operator_count=operator_count+1
                else:
                    operands_count=operands_count+1
                if operands_count>operator_count:
                    right_start=j
                    break
                j=j-1
            right_string_pos = right_start,string_pos[1]-1
            left_string_pos = string_pos[0],right_start-1
            ''' print("///////")
            print(left_string_pos)
            print(right_string_pos)
            print("///////")'''
            self.sizing(left_string_pos)
            self.sizing(right_string_pos)
            self.possible_dimensions[string_pos[1]]=[]
            self.causal_left_dimensions[string_pos[1]]=[]
            self.causal_right_dimensions[string_pos[1]]=[]
            if operator == '|':
                #print(self.polish_expression)
                t=len(self.possible_dimensions[string_pos[1]-1])
                s=len(self.possible_dimensions[right_start-1])
                left=self.possible_dimensions[right_start-1]
                right=self.possible_dimensions[string_pos[1]-1]
                '''print(t,s)
                print(left)
                print(right)
                print(left_string_pos)
                print(right_string_pos)'''
                i=0
                jiter=0
                kiter=0
                while i<s and jiter<t:
                    width=right[jiter][0] + left[i][0]
                    length=max(right[jiter][1], left[i][1])
                    self.possible_dimensions[string_pos[1]].append((width,length))
                    self.causal_left_dimensions[string_pos[1]].append((left[i][0],left[i][1]))
                    self.causal_right_dimensions[string_pos[1]].append((right[jiter][0],right[jiter][1]))
                    kiter = kiter +1
                    if length == left[i][1]:
                        i=i+1
                    else:
                        jiter=jiter+1   
                #operation of vertical node sizing at string_pos[1]

            elif operator =='-':
                #print(self.polish_expression)
                t=len(self.possible_dimensions[string_pos[1]-1])
                s=len(self.possible_dimensions[right_start-1])
                left=self.possible_dimensions[right_start-1]
                right=self.possible_dimensions[string_pos[1]-1]
                '''print("failure check")'''
                i=0
                jiter=0
                kiter=0
                while i<s and jiter<t and kiter <s+t-1:
                    length=right[t-jiter-1][1] + left[s-i-1][1]
                    width=max(right[t-jiter-1][0], left[s-i-1][0])
                    self.possible_dimensions[string_pos[1]].insert(0,(width,length))
                    self.causal_left_dimensions[string_pos[1]].insert(0,(left[s-i-1][0],left[s-i-1][1]))
                    self.causal_right_dimensions[string_pos[1]].insert(0,(right[t-jiter-1][0],right[t-jiter-1][1]))
                    kiter = kiter +1
                    if width == left[s-i-1][0]:
                        i=i+1
                    else:
                        jiter=jiter+1

    def blocks_size(self,string_pos,required_dimensions):
        if string_pos[0]==string_pos[1]:
            if ~self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].is_soft:
                self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].width = required_dimensions[0]
                self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].length = required_dimensions[1]
            else:
                self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].width = required_dimensions[0]
                self.blocks[self.blocks_dict[self.polish_expression[string_pos[0]]]].length = required_dimensions[1]
        else:
            j=string_pos[1]-1
            operator=self.polish_expression[string_pos[1]]
            operator_count=0
            operands_count=0
            while j>string_pos[0]:
                if self.polish_expression[j]=='|' or self.polish_expression[j]=='-':
                    operator_count=operator_count+1
                else:
                    operands_count=operands_count+1
                if operands_count>operator_count:
                    right_start=j
                    break
                j=j-1
            right_string_pos = right_start,string_pos[1]-1
            left_string_pos = string_pos[0],right_start-1
            index = self.possible_dimensions[string_pos[1]].index(required_dimensions)
            left_required_dimension = self.causal_left_dimensions[string_pos[1]][index]
            right_required_dimension = self.causal_right_dimensions[string_pos[1]][index]
            self.blocks_size(left_string_pos,left_required_dimension)
            self.blocks_size(right_string_pos,right_required_dimension)

    def simulated_annealing(self, Tfreeze, Thot):
        #self.polish_initial()
        length=(0,len(self.polish_expression)-1)
        self.sizing(length)
        best_config = min(self.possible_dimensions[len(self.polish_expression)-1], key = lambda x: x[0]*x[1])
        area = best_config[0]*best_config[1]
        current_area = area #self.find_area()
        ##Thot is area when all the breadths and heights are added and multiplied.
        ##T freeze is the area of all the blocks or the maximum area among the blocks
        ##cooldown is 0.98T
        ##number of steps should be higher at high temperature to make sure we have some steps = 7 + (T -Tfreeze)/
        count=1
        best_area = current_area
        self.best = self.polish_expression[:]
        accepted =0 
        T = Thot
        cost_function=[]
        iteration=[]
        temperature=[]
        percentage=[]
        temperature2=[]
        while (T > Tfreeze):
            tempstep = 100 
            #print(tempstep)
            accepted_T =0
            for i in range(tempstep):
                current_expression = self.polish_expression[:]

                #self.operation_randomise()
                index = i%4 
                #index = random.choice(range(4))
                if index ==4:
                    #swap_width_length = random.choice(self.operands_list)
                    #temp=self.blocks[self.blocks_dict[self.polish_expression[swap_width_length]]].width
                    #self.blocks[self.blocks_dict[self.polish_expression[swap_width_length]]].width = self.blocks[self.blocks_dict[self.polish_expression[swap_width_length]]].length
                    #self.blocks[self.blocks_dict[self.polish_expression[swap_width_length]]].length = temp
                    swap_width_length = random.choice(range(len(self.blocks)))
                    temp = self.blocks[swap_width_length].width
                    self.blocks[swap_width_length].width = self.blocks[swap_width_length].length
                    self.blocks[swap_width_length].length = temp
                elif index ==0:
                    self.operation1()
                elif index ==1:
                    self.operation2()
                elif index ==2:
                    #print(self.polish_expression)
                    #print(self.operands_list)
                    #print(self.operators_list)
                    self.operation3()
                    #print(self.polish_expression)
                    #print(self.operands_list)
                    #print(self.operators_list)
                length=(0,len(self.polish_expression)-1)
                self.sizing(length)
                best_config = min(self.possible_dimensions[len(self.polish_expression)-1], key = lambda x: x[0]*x[1])
                area = best_config[0]*best_config[1]
                new_area = area #self.find_area()
                #print(self.polish_expression)
                cost_reversed = current_area-new_area
                if cost_reversed/T >= 200:
                    accepted = accepted+1
                    current_area = new_area
                    best_area = min(best_area,current_area)
                    cost_function.append(math.exp(cost_reversed/T))
                    temperature.append(T)
                    iteration.append(count)
                    accepted_T = accepted_T + 1
                    if current_area == best_area:
                        self.best = self.polish_expression[:]
                        self.best_length_width = []
                        for x in self.blocks:
                            self.best_length_width.append((x.length,x.width))
                        

                else:
                    if 0.99 < math.exp(cost_reversed/T):
                        accepted = accepted+1
                        current_area = new_area
                        best_area = min(best_area,current_area)
                        cost_function.append(math.exp(cost_reversed/T))
                        temperature.append(T)
                        iteration.append(count)
                        accepted_T = accepted_T + 1
                        #print(self.polish_expression)
                        ####still incomplete
                    else:
                        self.polish_expression = current_expression[:]
                        self.operands_list = []
                        self.operators_list = []
                        cost_function.append(math.exp(cost_reversed/T))
                        temperature.append(T)
                        iteration.append(count)
                        for i in range(len(self.polish_expression)):
                            if self.polish_expression[i] == '|' or self.polish_expression[i]=='-':
                                self.operators_list.append(i)
                            else:
                                self.operands_list.append(i)
                        if index == 4:
                            temp = self.blocks[swap_width_length].width
                            self.blocks[swap_width_length].width = self.blocks[swap_width_length].length
                            self.blocks[swap_width_length].length = temp
                count = count+1
            percentage.append(accepted_T/tempstep) 
            temperature2.append(T)
            T = 0.98 * T
        
        for i in range(len(cost_function)):
            if cost_function[i]>1:
                cost_function[i]=1
        
        
        '''print("count",count,"accepted",accepted)
        print("best_area",best_area)
        plt.figure(figsize=(8,6))
        plt.ylim(0,1.5)
        plt.plot(iteration,cost_function)
        plt.title('Cost Function vs Iteration')
        plt.xlabel('Iteration')

        plt.ylabel('Cost Function')
        plt.show()

        plt.figure(figsize=(8,6))
        plt.plot(iteration,temperature)
        plt.title('Temperature vs Iteration')
        plt.xlabel('Iteration')
        plt.ylabel('Temperature')
        plt.show()

        plt.figure(figsize=(8,6))
        plt.plot(temperature2,percentage)
        plt.title('percentage vs temperature')
        plt.xlabel('temperature')
        plt.ylabel('percentage')
        plt.xlim(0,120000000)
        plt.show()
'''
import time
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument("-input", type=str, help="File name of the blocks details")
parser.add_argument("-output", type=str, help="File nme where the output needs to be stored")

args = parser.parse_args()
inp =  args.input
outp = args.output     

start_time = time.time()





f=Floorplan()
f.blocks_parse(inp)
#f.display()
#print("operands list:",f.operands_list)
#print("operators list:", f.operators_list)
Thot,Tfreeze,area_blocks = f.simulated_annealing_parameter()
#print(f.polish_expression)
#print(Tfreeze)
f.polish_initial()
polLen = len(f.polish_expression)
Thot = polLen*polLen/2

try:
    f.simulated_annealing(1,Thot*1)
except IndexError:
    print(f.polish_expression)
    print('operands list',f.operands_list)
    print('operators list',f.operators_list)
string_pos = (0,len(f.polish_expression)-1)
origin = (0,0)

best_config = min(f.possible_dimensions[len(f.polish_expression)-1], key = lambda x: x[0]*x[1])
blank_area=best_config[0]*best_config[1] - area_blocks
area= best_config[0]*best_config[1]
f.blocks_size(string_pos,best_config)
#print(f.polish_expression)
f.add_coordinates(string_pos,origin)
with open(outp,'w') as a:
    a.write("Final area = "+str(best_config[0]*best_config[1])+"\n")
    a.write("Black area = "+ str(best_config[0]*best_config[1] - area_blocks)+"\n")
    a.write("block_name lower_left(x,y)coordinate upper_right(x,y)coordinate"+"\n")
    for x in f.blocks:
        a.write(x.block_name + " ("+str(x.x_coordinate) + ', '+str(x.y_coordinate)+") ("+ str(x.x_coordinate+x.width)+ ", "+ str(x.y_coordinate+x.length)+")"+"\n")

end_time = time.time()

print("time taken",end_time-start_time)