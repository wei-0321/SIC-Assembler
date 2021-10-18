import os
import numpy as np

class Sic:
    def __init__(self):
        self.instructions = []  #所有指令(透過讀檔獲取)  
        self.loc = 0            #執行某指令會增加多少位址(10進位)
        self.location_list = [] #儲存每行指令的位址
        self.object_code = ""   #目的碼
        self.symbol_dict = {}   #符號表
        self.directive_list = ["START", "WORD", "BYTE", "RESW", "RESB", "END"]   #組譯器指引
        self.opcode_dict = {     #助記碼以及對應的運作碼
         "ADD" : "18", "AND" : "40", "COMP" : "28", "DIV" : "24", "J" : "3C", "JEQ" : "30", "JGT" : "34",
         "JLT" : "38", "JSUB" : "48", "LDA" : "00", "LDCH" : "50", "LDL" : "08", "LDX" : "04", "MUL" : "20",
         "OR" : "44", "RD" : "D8", "RSUB" : "4C", "STA" : "0C", "STCH" : "54", "STL" : "14",
         "STSW" : "E8", "STX" : "10", "SUB" : "1C", "TD" : "E0", "TIX" : "2C", "WD" : "DC"               
        }
        self.operation = False   #檢查機制(若是程式碼已經出錯  後面就不用再執行)
        self.result = "%-10s%-10s%-10s%-10s%-10s" % ("(LOC)", "(Symbol)", "(OP code)", "(Operand)", "(Object Code)") + "\n"
    def is_directive(self, code):   #判斷是否為虛指令
        if code in self.directive_list:
            return True
        else:
            return False
    def is_opcode(self, code):    #判斷是否為助記碼(運作碼)
        if code in self.opcode_dict.keys():
            return True
        else:
            return False
    def read_file(self, file_name, input_path):     #讀檔  獲取正確格式的指令
        try:
            file_path = os.path.join(input_path, file_name)
            file = open(file_path, encoding = "utf-8")
            buffer = []     #暫存:只用來存符號運算元  當找到虛指令或運算碼時，就將buffer裡面的東西加入
            instruction = []
            is_symbol = False
            is_operand = False
            is_comma = False
            line_count = 0    #目前已讀取的行數，為了提醒使用者程式碼哪裡有誤
            for line in file.readlines():
                line = line.upper()        #全先轉為大寫，統一格式
                if line.startswith('.'):   #省略註解行 
                    continue
                line_list = line.split()   #以空白字元分隔
                for element in line_list:
                    if self.is_directive(element) or self.is_opcode(element):   #是虛指令或是運算碼
                        if (len(buffer) == 1):
                            is_symbol = True
                        else:
                            if (len(buffer) != 0):   #代表原來的組合語言程式混入了其他不相關的字元
                                raise Assembler_program_error   
                        is_symbol = (len(buffer) > 0)  
                        if is_symbol:  #暫存裡面有東西 即為符號運算元
                            symbol = buffer.pop()   #拿出符號運算元
                            if (self.is_directive(symbol) or self.is_opcode(symbol)):  #在buffer裡的應該要是符號運算元
                                raise Assembler_program_error #若不是符號運算元  代表原來的組合語言程式有誤
                            instruction.append(symbol)
                        else:          #暫存裡面沒東西 即沒有符號運算元
                            instruction.append("")   #統一指令長度
                        instruction.append(element)
                        if element == "RSUB":
                            is_operand = False      #RSUB沒運算元 
                            instruction.append("")  #統一指令長度
                            self.instructions.append(instruction)
                            instruction = []
                        else:
                            is_operand = True    #下一個讀到的元素是運算元
                    else:   #可能是讀到符號運算元或是運算元(也有可能是不相干的符號)
                        if is_operand:               #運算元 
                            if is_comma:
                                instruction[-1] += element
                                self.instructions.append(instruction)
                                instruction = []
                                is_comma = False
                                is_operand = False
                            else:   
                                instruction.append(element) 
                                if element[-1] == ',':       #有逗號  代表還有延續
                                    is_comma = True              
                                else:
                                    self.instructions.append(instruction)
                                    instruction = []
                                    is_operand = False
                        else:
                            buffer.append(element)   #符號運算元
                line_count += 1
        except FileNotFoundError:
            self.result += "錯誤! 請確認檔名輸入正確" + "\n"
        except Assembler_program_error:
            self.result += "於第%d行出現錯誤 : 組合語言程式碼有錯" % (line_count) + "\n"
        except Exception as e:
            self.result += "其他錯誤 : ", e + "\n"
        else:     #程式沒有出錯
            self.operation = True
        finally:
            file.close()
    def get_loc(self, code, operand):     #計算每行會增加的位址
        if code in self.directive_list:   #組譯器指引 
            if code == "WORD":
                self.loc = 3
            elif code == "BYTE":
                if (operand[0] == 'C'):   #C => ASC碼(每字元以2個16進位表示)
                    self.loc = len(operand) - 3
                else:  #X
                    self.loc = int((len(operand) - 3) / 2)
            elif code == "RESB":
                self.loc = int(operand)
            elif code == "RESW":
                self.loc = int(operand) * 3
        else:                               #一般運算碼
            self.loc = 3
        return self.loc
    def get_obj(self, code, operand):    #處理目的碼
        if code in self.directive_list:  #組譯器指引 
            if code == "WORD":
                number = int(operand)
                if number > ((int("0xFFFFFF", 16) + 1) / 2 - 1):
                    raise Word_error     #拋出例外 : 數值超出1字組(word)所能表示的值 
                if number < 0:   #負數要表示成二補數的形式
                    number += int("0x1000000", 16)  #二補數的概念
                    if number < ((int("0xFFFFFF", 16) + 1) / 2):
                        raise Word_error     #拋出例外 : 數值超出1字組(word)所能表示的值 
                self.object_code = hex(number)[2:]
                #未滿六位數要補0
                for i in range(6 - len(self.object_code)):
                    self.object_code = '0' + self.object_code
            elif code == "BYTE":
                if (operand[0] == 'C'):   #C
                    self.object_code = ""
                    for i in range(2, len(operand) - 1):
                        self.object_code += hex(ord(operand[i]))[2:].upper()
                else:                     #X
                    self.object_code = operand[2 : -1]
            elif code == "RESB":
                self.object_code = ""
            elif code == "RESW":
                self.object_code = ""
            elif code == "START":
                self.object_code = ""    
            elif code == "END":
                self.object_code = "" 
        else:                            #一般運算碼    要找出助記碼的運作碼以及運算元所在的位址
            self.object_code = self.opcode_dict[code]  #先找到運作碼
            if code == "RSUB":     #RSUB較特殊
                self.object_code = "4C0000"
            else:        #找運算元的位址
                x_judge = operand.split(",")   #判斷x位元
                if self.symbol_dict.__contains__(x_judge[0]):  #檢查要用到的符號運算元有沒有在符號表中
                    symbol = self.symbol_dict[x_judge[0]]      #從之前存的符號表找到位址
                else:
                    raise Symbol_undefined    #拋出例外 : 符號運算元未被定義  卻被拿來使用
                if len(x_judge) == 2:        #先檢查長度
                    if x_judge[1] == 'X':         # x bit = 1
                        temp = hex(int(symbol, 16) + int("0x8000", 16))[2:]
                        if len(temp) > 5:   
                            raise X_bit_error     #拋出例外 : 因為x位元為1 使得位址超出範圍 
                        self.object_code += temp    
                    else:
                        raise Symbol_undefined
                else:                             # x bit = 0
                    self.object_code += symbol
        return self.object_code
    def phase1(self):     #目標為算出位址以及建立符號表
        if self.operation == False:    #程式碼已經出錯  不用再執行下去
            return
        self.operation = False
        count = 0
        try:
            for instruction in self.instructions:
                count += 1
                if instruction[1] == "START":  #遇到START 先擷取起始位址
                    self.location_list.append("")   #START前面無位址
                    location = instruction[2]
                    if len(location) > 5 or (len(location) == 4 and int(location[0]) >= 8):  
                        raise Loc_error     #拋出例外 : 位址超出範圍
                    for i in range(4 - len(location)):   #未滿四位數要做補零的動作
                        location = "0" + location
                    self.location_list.append("0x"+ location)
                elif instruction[1] == "END":
                    break
                else:
                    if instruction[0] != "":   #有符號運算元
                        self.symbol_dict.update({instruction[0] : self.location_list[-1][2:]})
                    #計算執行某指令會增加多少位址
                    location = hex(int(self.location_list[-1][2:], 16) + self.get_loc(instruction[1], instruction[2]))
                    location = location[2:]
                    if len(location) > 5 or (len(location) == 4 and int(location[0]) >= 8):  
                        raise Loc_error     #拋出例外 : 位址超出範圍
                    for i in range(4 - len(location)):   #未滿四位數要做補零的動作
                        location = "0" + location
                    self.location_list.append("0x" + location)
        except Loc_error:
            self.result += "出現錯誤 : 位址超出範圍 : %-6s%-6s%-6s" % (self.instructions[count][0], self.instructions[count][1], self.instructions[count][2]) + "\n"
        except Exception as e:
            self.result += "其他錯誤 : ", e + "\n"
        else:      #程式沒有出錯
            self.operation = True
    def phase2(self):    #目標為得到目的碼
        if self.operation == False:    #程式碼已經出錯  不用再執行下去
            return
        count = 0
        try:
            for instruction in self.instructions:
                object_code = ""
                object_code = self.get_obj(instruction[1], instruction[2])   #得到目的碼
                #格式化輸出
                self.result += "%-10s%-10s%-10s%-10s%-10s" % (self.location_list[count][2:].upper(), instruction[0], instruction[1], instruction[2], object_code.upper()) + "\n"
                count += 1
        except X_bit_error:
            self.result += "因為x位元為1 無法符合指令格式 : %-6s%-6s%-6s" % (self.instructions[count][0], self.instructions[count][1], self.instructions[count][2]) + "\n"     
        except Word_error:
            self.result += "數值超出1字組的表示範圍(%d ~ %d) : %-6s%-6s%-6s" % ((np.power(2, 23) - 1), -(np.power(2, 23)), self.instructions[count][0], self.instructions[count][1], self.instructions[count][2]) + "\n"
        except Symbol_undefined:
            self.result += "使用的符號運算元未被定義 : %-6s%-6s%-6s" % (self.instructions[count][0], self.instructions[count][1], self.instructions[count][2]) + "\n"
        except Exception as e:
            self.result += "其他錯誤 : ", e, " : ", self.instructions[count] + "\n"
    def output(self, filename, output_path):   #輸出結果檔案
        file_name = filename
        output_file_name = file_name.split(".")[0] + "_result.txt"
        with open(os.path.join(output_path, output_file_name), 'w', encoding = "utf-8") as file:
            print("writing result in " + output_file_name + "\n") 
            for line in self.result:
                file.writelines(line)
        print("finished ")
    
    def execute(self, file_name, input_path, output_path):   #實際執行流程
        self.read_file(file_name, input_path)
        self.phase1()
        self.phase2()
        self.output(file_name, output_path)
    
#自訂例外類別 以下為可能的錯誤，當錯誤產生時就拋出這些例外
class Assembler_program_error(Exception): #編寫的組合語言程式碼有錯
    pass
class Loc_error(Exception):   #位址超出15位元所能表示的值
    pass
class X_bit_error(Exception):  #因為x位元為1 無法符合指令格式
    pass
class Symbol_undefined(Exception): #有未被定義的符號運算元
    pass
class Word_error(Exception):   #數值超出1字組(word)所能表示的值
    pass


if __name__ == "__main__":
    #路徑處理
    file_name = "example.txt"
    cd = os.getcwd() 
    input_path = os.path.join(cd, "input")
    output_path = os.path.join(cd, "output")

    sic = Sic()
    sic.execute(file_name, input_path, output_path)
    
    

#可以優化的地方
#BYTE C'字元'  能接受空白字元

