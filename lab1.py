# Universidade de Brasília - Organização e Arquitetura de Computadores
# Professor: Flávio Vidal
# Trabalho 1: Montador Assembly

#Recebe nome do arquivo.asm e abre para leitura
arqv = input("Digite o nome do arquivo: ") 
entrada = open(arqv, 'r')

#Abre arquivos .mif para escrita
text = open('text.mif', 'w') 
data = open('data.mif', 'w')

#Escreve cabeçalho do arquivo .data
data.write("DEPTH = 16384;\nWIDTH = 32;\nADDRESS_RADIX = HEX;\nDATA_RADIX = HEX;\nCONTENT\nBEGIN\n\n")

#Escreve cabeçalho do arquivo .text
text.write("DEPTH = 4096;\nWIDTH = 32;\nADDRESS_RADIX = HEX;\nDATA_RADIX = HEX;\nCONTENT\nBEGIN\n\n")

#Reseta o ponteiro da função readlines para o inicio da lista
entrada.seek(0) 
#Retorna todas as linhas do arquivo como uma lista, cada linha é um item da lista
linhas = entrada.readlines()
global conta #Contador para número de linhas

#Troca caracteres especiais de cada linha por espaço
def troca(L):
    L = L.replace("(", " ")
    L = L.replace(")", " ")
    L = L.replace(","," ")
    L = L.replace(":"," ")
    L = L.replace("0x"," ")
    return L

#Recebe uma linha de código e retorna a instrução da mesma
def ler_linha(linha):
    nova_linha = troca(linha)
    instrucao = nova_linha.split() #Transforma a linha atual em uma lista
    return instrucao

#Transforma para binario
def set_bin(num):
    num_bin = format(int(num), 'b')
    num_bin = completa(num_bin, 16)
    return num_bin

#Transforma em n bits
def completa(num_incompleto, n):
    while(len(num_incompleto) < n):#Insere com '0' até ter n bits 
        num_incompleto = '0' + num_incompleto
    num_completo = num_incompleto
    return num_completo #Retorna numero com 16 bits

#Transforma binario em hexadecimal 
def bin_hexa(word):
    var = int(word, 2) 
    hexa_word = hex(var)
    hexa_word = hexa_word[2:]
    return hexa_word #Retorna uma string

#Transforma decimal em hexadecimal 
def dec_hexa(word):
    hexa_word = hex(word)
    hexa_word = hexa_word[2:]
    hexa_word = completa(hexa_word,8)
    return hexa_word #Retorna uma string

def verifica_registrador(lista_linha):
    if(len(lista_linha)<=3):#Trata o caso de existir apenas 2 registradores por instrucao
        return "00000"
    else:
        return numero_registradores(lista_linha[3]) #Segundo registrador de operando origem

#Identificação o tipo de instrucao e retorna seu binário
def identifica(lista_linha, conta_aux):
    global conta
    conta = conta_aux
    #Trata a exceção de Label - endereço
    if("Label" in lista_linha):
        #endereco = conta
        lista_linha.remove("Label")
    op = lista_linha[0]

    #Tratamento para tipo I
    if(opcode_tipoI(op)!=None):
            if(op=="addi" or op=="xori"):#Tratamento para casos especiais, como: xori e Label
                op = opcode_tipoI(op)
                rs = numero_registradores(lista_linha[2])
                rt = numero_registradores(lista_linha[1])
                imm = lista_linha[3]
                imm = set_bin(imm)
                op = op + rs + rt + imm
                return op

            rt = numero_registradores(lista_linha[1])
            imm = lista_linha[2] #Tratar imm
            imm = set_bin(imm) #Transforma em binario de 16 bits
            rs = numero_registradores(lista_linha[3])
            op = opcode_tipoI(op) + rs + rt + imm

            return op

    #Tratamento para tipo R
    elif(funct_tipoR(op)!=None): 
            funct = funct_tipoR(op) #Variação da operação
            shamt = "00000"
            op = "000000" #Op_Code é sempre 0 para operações do tipo R
            rd = numero_registradores(lista_linha[1]) #Registrador de destino
            rs = numero_registradores(lista_linha[2]) #Primeiro registrador de operando origem
            rt = verifica_registrador(lista_linha) #Verifica a existencia do segundo registrador de operando origem
            op = op + rs + rt + rd + shamt + funct #Concatenção em binário da linha inteira
            return op #Retorna linha em binário

    #Tratamento para tipo J
    elif(opcode_tipoJ(op)!=None): 
        op = opcode_tipoJ(op) + lista_linha[1]
        return op 
    
    #Tratamento para Pseudo-Instruções e excessoes
    else:
        if(lista_linha[0]=="li"): #Load Immediate
            op = "lui"
            op = opcode_tipoI(op)
            rt = "00001" # $at
            rs = "00000"
            #Recebe imediato em hexadecimal
            imm = int(lista_linha[2],16) #Hexadecimal para Decimal
            imm = format(int(imm), 'b') #Decimal para binario
            imm = completa(imm, 32) #Transforma em 32 bits
            op = op + rs + rt + imm
            op = escreve_linha_hexa(op)
            escreve_text(op, conta)


            temp_op = "ori"
            temp_op = opcode_tipoI(temp_op)
            temp_rs = rt # $at    
            temp_rt = numero_registradores(lista_linha[1])
            temp_op = temp_op + temp_rs + temp_rt + completa('0', 16)
            conta += 1
            return temp_op
        
        if(lista_linha[0]=="clo"):
            shamt = "00000"
            rt = "00000"    
            funct = "100001"
            op = "011100"
            rd = numero_registradores(lista_linha[1])
            rs = numero_registradores(lista_linha[2]) 
            op = op + rs + rt + rd + shamt + funct
            return op

        if(lista_linha[0]=="clz"):
            shamt = "00001"
            rt = "00000"
            funct = "010000"
            op = "000000"
            rd = numero_registradores(lista_linha[1])
            rs = numero_registradores(lista_linha[2]) 
            op = op + rs + rt + rd + shamt + funct
            return op
        
        if(lista_linha[0]=="teq"):
            op = "000000"
            code = "0000000000"
            rs = numero_registradores(lista_linha[1])
            rt = numero_registradores(lista_linha[2]) 
            funct = "110100"
            op = op + rs + rt + code + funct
            return op
        
        if(lista_linha[0]=="movn"): 
            op = "000000"
            funct = "001011"
            shamt = "00000"
            rd = numero_registradores(lista_linha[1])  
            rs = numero_registradores(lista_linha[2])  
            rt = numero_registradores(lista_linha[3])  
            op = op + rs + rt + rd + shamt + funct 
            return op
        
        if(lista_linha[0]=="mul"): 
            op = "011100"
            funct = "000010"
            shamt = "00000"
            rd = numero_registradores(lista_linha[1])  
            rs = numero_registradores(lista_linha[2])  
            rt = numero_registradores(lista_linha[3])  
            op = op + rs + rt + rd + shamt + funct 
            return op
        
        if(lista_linha[0]=="madd"): 
            op = "011100"
            funct = "000000"
            shamt = "00000"
            rs = numero_registradores(lista_linha[1])  
            rt = numero_registradores(lista_linha[2])  
            rd = "00000"
            op = op + rs + rt + rd + shamt + funct 
            return op

        if(lista_linha[0]=="msubu"): 
            op = "011100"
            funct = "000101"
            shamt = "00000"
            rs = numero_registradores(lista_linha[1])  
            rt = numero_registradores(lista_linha[2])  
            rd = "00000"
            op = op + rs + rt + rd + shamt + funct 
            return op
        
        if(lista_linha[0]=="bgezal"): 
            op = "000001"
            rt = "10001"
            rs = numero_registradores(lista_linha[1])  
            offset = numero_registradores(lista_linha[2])
            op = op + rs + rt + offset 
            return op

        if(lista_linha[0]=="add.d"): 
            op = "010001"
            funct = "000000"
            fmt = "00000"
            fd = numero_registradores(lista_linha[1]) 
            fs = numero_registradores(lista_linha[2])
            ft = numero_registradores(lista_linha[3])
            op = op + fmt + ft + fs + fd + funct 
            return op
        
        if(lista_linha[0]=="add.s"): 
            op = "010011"
            fmt = "110000"
            fd = numero_registradores(lista_linha[1]) 
            fs = numero_registradores(lista_linha[2])
            ft = numero_registradores(lista_linha[3])
            op = op + ft + fs + fd + fmt
            return op

        if(lista_linha[0]=="sub.d"): 
            op = "010011"
            fmt = "101000"
            fd = numero_registradores(lista_linha[1]) 
            fr = numero_registradores(lista_linha[2])
            fs = numero_registradores(lista_linha[3])
            ft = numero_registradores(lista_linha[4])
            op = op + fr + ft + fs + fd + fmt
            return op
        
        if(lista_linha[0]=="sub.s"): 
            op = "010011"
            fmt = "111000"
            fd = numero_registradores(lista_linha[1]) 
            fr = numero_registradores(lista_linha[2])
            fs = numero_registradores(lista_linha[3])
            ft = numero_registradores(lista_linha[4])
            op = op + fr + ft + fs + fd + fmt
            return op
        
        if(lista_linha[0]=="c.eq.d"): 
            cache = "100101"
            base = numero_registradores(lista_linha[1]) 
            offset = "000000000"
            offset = offset + "0" + cache
            op = "011111" + base + op + offset
            return op
        
        if(lista_linha[0]=="c.eq.s"): 
            cache = "100110"
            base = numero_registradores(lista_linha[1]) 
            offset = "000000000"
            offset = offset + "0" + cache
            op = "011111" + base + op + offset
            return op

        if(lista_linha[0]=="mul.d"): 
            op = "010001"
            mul = "000010"
            fmt = "00000"
            fd = numero_registradores(lista_linha[1])  
            fs = numero_registradores(lista_linha[2])  
            ft = numero_registradores(lista_linha[3])  
            op = op + fmt + ft + fs + fd + mul
            return op
        
        if(lista_linha[0]=="mul.s"): 
            op = "010001"
            mul = "000010"
            fmt = "00001"
            fd = numero_registradores(lista_linha[1])  
            fs = numero_registradores(lista_linha[2])  
            ft = numero_registradores(lista_linha[3])  
            op = op + fmt + ft + fs + fd + mul
            return op
        
        if(lista_linha[0]=="div.d"): 
            op = "010001"
            fmt = "00000"
            div = "000011"
            fd = numero_registradores(lista_linha[1])  
            fs = numero_registradores(lista_linha[2])  
            ft = numero_registradores(lista_linha[3])  
            op = op + fmt + ft + fs + fd + div
            return op
        
        if(lista_linha[0]=="div.s"): 
            op = "010001"
            fmt = "00001"
            div = "000011"
            fd = numero_registradores(lista_linha[1])  
            fs = numero_registradores(lista_linha[2])  
            ft = numero_registradores(lista_linha[3])  
            op = op + fmt + ft + fs + fd + div
            return op
        
        if(lista_linha[0]=="tge"): 
            op = "000000"
            funct = "110000"
            code = "0000000000"
            rs = numero_registradores(lista_linha[1])  
            rt = numero_registradores(lista_linha[2])    
            op = op + rs + rt + code + funct
            return op
        
        if(lista_linha[0]=="tgei"): 
            op = "000001"
            tgei = "01000"
            rs = numero_registradores(lista_linha[1])  
            #Tratar imm
            imm = lista_linha[2] 
            if("$" in imm):#Tratamento para casos especiais, como: xori e Label
                imm = numero_registradores(imm)
            imm = set_bin(imm) #Transforma em binario de 16 bits
            op = op + rs + tgei + imm
            return op
        
        if(lista_linha[0]=="tne"): 
            op = "000000"
            tne = "110110"
            code = "0000000000"
            rs = numero_registradores(lista_linha[1])  
            rs = numero_registradores(lista_linha[2])  
            op = op + rs + rt + code + tne
            return op
        
        if(lista_linha[0]=="tnei"): 
            op = "000001"
            tnei = "01110"
            rs = numero_registradores(lista_linha[1])  
            imm = lista_linha[2] 
            if("$" in imm):#Tratamento para casos especiais, como: xori e Label
                imm = numero_registradores(imm)
            imm = set_bin(imm) #Transforma em binario de 16 bits
            op = op + rs + tnei + imm
            return op
                
        return "NAO REGISTRADO!"

#Tabela contendo o opcode das instruções tipo I
def opcode_tipoI(instrucao):
    tabela_opcode = {
        "addi": '001000',
        "addiu": '001001',
        "andi": '001100',
        "beq": '000100',
        "bgez": '000001',
        "bgtz": '000111',
        "blez": '000110',
        "bne": '000101',
        "lb": '100000',
        "lbu": '100100',
        "lh": '100001',
        "lhu": '100101',
        "ll": '110000',
        "lui": '001111',
        "lw": '100011',
        "ori": '001101',
        "slti": '001010',
        "sltiu": '001011',
        "sb": '101000',
        "sc": '111000',
        "sh": '101001',
        "sw": '101011',
        "lwc1": '110001',
        "ldc1": '110101',
        "swc1": '111001',
        "sdc1": '111101',
        "xori": '001110'
    }
    if(instrucao in tabela_opcode):
        return tabela_opcode[instrucao]
    else:
        return None
 
#Tabela contendo o número de function das instruções tipo R
def funct_tipoR(instrucao):
    tabela_funct = {
        "add":'100000',
        "addu":'100001',
        "and":'100100',
        "break": '001101',
        "jr":'001000',
        "div": '011010',
        "divu": '011011',
        "jalr": '001001',
        "nor":'100111',
        "or":'100101',
        "slt":'101010',
        "sltu":'101011',
        "sll":'000000',
        "sllv":'000100',
        "srl":'000010',
        "srlv":'000110',
        "sub":'100010',
        "subu":'100011',
        "div":'011010',
        "divu":'011011',
        "mfhi":'010000',
        "mflo":'010010',
        "mthi": '010001', 
        "mtlo": '010011',
        "mult":'011000',
        "multu":'011001',
        "sra":'000011',
        "srav": '000111',
        "syscall": '001100',
        "xor": '100110'
    }
    if(instrucao in tabela_funct):
        return tabela_funct[instrucao]
    else:
        return None

#Tabela contendo o opcode das instruções tipo J
def opcode_tipoJ(instrucao):
    tabela_opcode = {
        "j": '000010',
        "jal": '000011'
    }
    if(instrucao in tabela_opcode):
        return tabela_opcode[instrucao]
    else:
        return None

#Tabela contendo o numero dos registradores em binario
def numero_registradores(registrador):
    tabela_registrador = { 
        "$zero": '00000',
        "$at": '00001',
        "$v0": '00010',
        "$v1": '00011',
        "$a0": '00100',
        "$a1": '00101',
        "$a2": '00110',
        "$a3": '00111',
        "$t0": '01000',
        "$t1": '01001',
        "$t2": '01010',
        "$t3": '01011',
        "$t4": '01100',
        "$t5": '01101',
        "$t6": '01110',
        "$t7": '01111',
        "$s0": '10000',
        "$s1": '10001',
        "$s2": '10010',
        "$s3": '10011',
        "$s4": '10100',
        "$s5": '10101',
        "$s6": '10110',
        "$s7": '10111',
        "$t8": '11000',
        "$t9": '11001',
        "$k0": '11010',
        "$k1": '11011',
        "$gp": '11100',
        "$sp": '11101',
        "$fp": '11110',
        "$rs": '11111'
    }
    if(registrador in tabela_registrador):
        return tabela_registrador[registrador]
    else:
        return "00000" #Tratar caso XORI
    
#Finaliza programa fechando os arquivos .mif
def fim():
    text.write("\nEND;")
    text.close()
    data.write("\nEND;")
    data.close()
    entrada.close()

#Escreve uma linha(na base 2) em hexadecimal
def escreve_linha_hexa(linha_bin):
    n = 0
    word_32 = ""
    while(n<32):
        word = linha_bin[n:n+4]
        n += 4
        word_32 = word_32 + bin_hexa(word)
    return word_32

#Escreve em text
def escreve_text(linha, conta):
    #Para o .text
    conta_hex = conta
    conta_hex = dec_hexa(conta_hex)
    endereco = conta_hex
    #Para o .data
    
    text.write(endereco + " : " + linha)#Transformar para hexadecimal
    data.write(endereco + " : " + str(conta))
    conta += 1
    #Pula para proxima linha
    text.write("\n")
    data.write("\n")
    return conta

#Laço para ler o arquivo data
for linha in linhas: 
    if(".data" in linha):
        continue
    if(linha == "\n"):
        continue
    if(".text" in linha):
        break
    
start_text = 0 #Variável para identificar o inicio de .text
conta = 0

#Laço principal do algoritmo
for linha in linhas: #Laço para ler o arquivo text
    dados = ler_linha(linha) #Variável que armazena uma lista de uma linha
    if(start_text == 1):
        linha_bin = identifica(dados, conta)#Chama função para identificar operação
        if(linha_bin == None):
            text.write(linha_bin)
        else:
            #Escreve linha em hexadecimal
            linha_hexa = escreve_linha_hexa(linha_bin)
            conta = escreve_text(linha_hexa, conta) #Escreve linha em hexadecimal no arquivo .text

    if(".text" in linha):
        start_text = 1

#Chama função de finalização
fim()