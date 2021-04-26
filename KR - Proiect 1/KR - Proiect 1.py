import re
import copy
import time
from typing import List, Tuple 

def combine_arrays(element1, element2):
    #element 1, 2 poate sa fie de orice tip
    #combinam 2 liste intr-o stiva
        temp = []
        temp.append(element1)
        temp.append(element2)
        return temp 

def convert_to_numbers(value): 
    #un switch care e mult mai rapid si mai ordonat decat if uri
        return {'cub': 2, 'sfera': 3, 'piramida': 1}.get(value)        

class NodParcurgere:
    #cod scris in totalitate de Irina Ciocan evident adaptat la cod:
    #https://replit.com/@IrinaCiocan/a-star-optimizat#main.py
    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # consider cost=1 pentru o mutare
        self.h = h
        self.f = self.g + self.h
        NodParcurgere.ct = 0
 
    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l
 
    def afisDrum(self, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        for nod in l: print(str(nod))
        if afisCost: print("Cost: ", self.g)
        if afisLung: print("Lungime: ", len(l))
        return len(l)
 
    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info): return True
            nodDrum = nodDrum.parinte
        return False
 
    def __repr__(self): return str(self.info)
  
    def __str__(self):
        sir = str(NodParcurgere.ct) + ")\n"
        NodParcurgere.ct += 1
        maxInalt = max([len(stiva) for stiva in self.info])
        for inalt in range(maxInalt, 0, -1):
            for stiva in self.info:
                if len(stiva) < inalt:
                    sir += "    "
                else:
                    if  stiva[inalt - 1][0] == 1: sir += '/' + stiva[inalt - 1][1] + '\ '
                    elif  stiva[inalt - 1][0] == 3: sir += '(' + stiva[inalt - 1][1] + ') '
                    else: sir += '[' + stiva[inalt - 1][1] + '] '
            sir += "\n"
        sir += "#" * (4 * len(self.info) - 1)
        return sir
 

class Graph:
    def __init__(self, location):
        #initializarea clasei
        self.file_input = open(location, "r+")
        self.k = int(self.file_input.readline())
        self.stack_list_converted = []
        for line in self.file_input.readlines(): self.stack_list_converted.append(self.convert_to(line))
        if(not self.verificare_configurare(self.stack_list_converted)):
                       print("Configuratie gresita -> FAIL")
                       return


    def verificare_configurare(self, stiva):
        #@stiva - stiva pe care vreau sa verifica daca e ok sau nu
        #imi returneaza valoare boolean

        #pas 1 verificare configuratie pentru piramida
        #Cum am gandit aici, simplu:
        #Logic nu poate aseza nimeni pe piramida => piramida trebuie sa fie ultimul element daca exista
        #Adica presupun ca piramida nu exista
        for i in range(len(stiva)):
                    index = len(stiva[i]) - 1 #presupunem ca piramida nu exista sau exista dar e ultimul element
                    for j in range(len(stiva[i])):   
                            if(stiva[i][j][0] == 1):  #verificam daca exista piramdia si-i atribuim indicele primei piramide gasite
                                    index = j 
                                    break     
                    if(index != len(stiva[i]) - 1): return False #daca exita piramida => indexu e schimbat si vom verifica din nou daca e ultimul element sau nu, \\
                    #daca NU e => false
                    #daca e => true
        
        #cautam pozitiile unde se afla sfera pentru orice stiva din stiva principala
        #aici la sfera este simplu, vom lua un triplet
        #inainte, acum, dupa
        #daca in subvectorul acum am gasit 2 sfere spre exemplu => trebuie neaparat sa existe elementele pentru inainte si dupa pe baza indicelului a sferei
        #daca NU exista element pe indicele sferei => catch adica fail, altfel imi da true

        #se verifica de asemenea daca exista sfere pe pozitile 0 si n, pe coloana, daca exista => fail, altfel imi da true
        for i in range(len(self.stack_list_converted)):
                for j in range(len(self.stack_list_converted[i])):
                  if(self.stack_list_converted[i][j][0] == 3):  
                    if(i == 0 or i == len(self.stack_list_converted) - 1):  return False        
                    else:
                            try: 
                                self.stack_list_converted[i - 1][j] #verificam daca exista sau nu, element pe pozitia indicelui a sferei aici pentru vectorul inainte
                                self.stack_list_converted[i + 1][j] #aici pentru vectorul dupa
                            except:
                                return False

        return True

    def convert_to(self, line):
            #@line - substiva citita din fisier
            #imi returneaza o stiva de stiva de liste de forma [cost, litera]
            #functia asta imi converge din datele citite si transforma direct in [cost, litera] si dupa mi-l baga intr-un vector
            arr = line.split(')');
            return_arr = []
            for i in range(len(arr)):
                    new_arr = arr[i].split('(')
                    new_arr[0] = re.sub(',', '', new_arr[0]) #imi curata de caractere cum ar fi virgula sau spatiu
                    new_arr[0] = re.sub(' ', '', new_arr[0])   
                    try: return_arr.append(combine_arrays(convert_to_numbers(new_arr[0]), new_arr[1]))  #combin 2 subliste si fac un tuplu
                    except: break
            return return_arr
        

    def get_count_not_null_lists(self, nodCurent: List) -> List: 
        #@nodCurent reprezita stiva din nodCurent, adica nodCurent.info
        #Returneaza lista cu 2 elemente
        #determin cate liste nenule sunt intr-un nodcurent.info, implicit imi returneaza ca List, si ca parametru 
        #e necesar sa fie list
        not_null_list_count = 0
        for i in range(len(nodCurent)):
             if(len(nodCurent[i])!=0): not_null_list_count += 1

        return [not_null_list_count, len(nodCurent) - self.k]     

    def testeaza_scop(self, nodCurent: List) -> int:
        #@nodCurent reprezita stiva din nodCurent, adica nodCurent.info
        #Returneaza o valoare boolean parsata in int
        #vom testa scopul daca functioneaza cum trebuie folosind get_count_not_null_lists, in INT daca sunt egale sau nu 
        #asta e folosita mai ales pentru euristica banala
            result = self.get_count_not_null_lists(nodCurent)
            return result[0] == result[1]
    
    def generare_de_succesori(self, nodCurent, tip_euristica="euristica banala"):
            #@nodCurent - nodul curent
            #@tip_euristica - euristica
            #generarea de succesori este exact identica ca tema pe care ne-ati dat-o, insa trebuie respectata conditiile de mutare
            #in principiu scot un bloc dintr-o copie stiva de stive, si il bag intr-o alta copie, a copiei de stiva, si incerc pentru fiecare substiva in parte
            #voi verifica daca stiva fara acel bloc e compatibil daca DA => voi introduce blocul intr-o alta pozitie a substivei si voi reverifica daca e compatibil sau nu
            #daca e compatibil => DONE
            #evident bloc este o lista de 2 elemente de forma [cost, litera]
            listaSuccesori = []
            stiva = nodCurent.info
            ok = False
            for i in range(len(stiva)):
                copie_stiva = copy.deepcopy(stiva)
                if len(copie_stiva[i]) == 0: continue
                bloc = copie_stiva[i].pop() 
                for j in range(len(copie_stiva)):
                    stiva_t = copy.deepcopy(copie_stiva)
                    if i == j or not self.verificare_configurare(stiva_t): continue #verificare daca stiva fara bloc e inca valida sau nu, si vom introduce blocul pe o pozitie
                    #diferite de i
                    stiva_t[j].append(bloc)  
                    if(not self.verificare_configurare(stiva_t)):  continue
                    nod_nou = NodParcurgere(stiva_t, nodCurent, cost = nodCurent.g + bloc[0], h = self.calculeaza_h(stiva_t, tip_euristica))
                    if not nodCurent.contineInDrum(stiva_t): listaSuccesori.append(nod_nou)
                                       
            return listaSuccesori

    def calculeaza_h(self, infoNod, tip_euristica="euristica_banala") -> int:
        #@InfoNod - reprezinta chiar stiva din nodul curent
        #@tip_euristica - euristica
        #aici vom calcula costuriile in functie de tipul de euristici
        #avem euristica banala aici imi verifica strict daca e egal sau nu cu numarul de costuri
        [not_null_list_count, null] = self.get_count_not_null_lists(infoNod)
        if tip_euristica == "euristica_banala": return self.testeaza_scop(infoNod)
        elif tip_euristica == "euristica_nebanala_1": return self.k - (len(infoNod) - not_null_list_count)
        #sigur mai exista 1 mutare
        elif tip_euristica == "euristica_nebanala_2": return 2 * (int(self.k) - (len(infoNod) - not_null_list_count))
        #aici e sigur ca mai exista 2 mutari

def tema(input):
    gr = Graph(input)
    uniform_cost(gr, 1)


#Toti algoritmii de mai jos au fost scris de Irina Ciocan in totalitate, evident adaptate in cod
#https://repl.it/@IrinaCiocan/uniform-cost-search#main.py
#https://repl.it/@IrinaCiocan/a-star#main.py
#https://replit.com/@IrinaCiocan/a-star-optimizat#main.py
#https://replit.com/@IrinaCiocan/ida-star#main.py

def uniform_cost(gr, nrSolutiiCautate, tip_euristica = "euristica_nebanala_1"):
    t1 = time.time()
    c = [NodParcurgere(gr.stack_list_converted, None, 0, gr.calculeaza_h(gr.stack_list_converted))]
    while len(c) > 0:
        nodCurent = c.pop(0)
        if gr.testeaza_scop(nodCurent.info):
            t2 = time.time()
            print("Solutie:\n", end="")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            print("\n================\n")
            print('Timpul de gasire a unei solutii: ', str(round(1000 * (t2 - t1))) + " ms")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0: return
        lSuccesori = gr.generare_de_succesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                if c[i].g > s.g:
                    gasit_loc = True
                    break
            if gasit_loc: c.insert(i, s)
            else: c.append(s)


def a_star(gr, nrSolutiiCautate, tip_euristica = "euristica_nebanala_1"):
    t1 = time.time()
    c = [NodParcurgere(gr.stack_list_converted, None, 0, gr.calculeaza_h(gr.stack_list_converted))]
 
    while len(c) > 0:
        nodCurent = c.pop(0)
        if gr.testeaza_scop(nodCurent) == 1:
            t2 = time.time()
            print("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            print("\n================\n")
            print('Timpul de gasire a unei solutii: ', round(1000*(t2-t1)))
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0: return
        lSuccesori = gr.generare_de_succesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                if c[i].f >= s.f:
                    gasit_loc = True
                    break;
            if gasit_loc: c.insert(i, s)
            else: c.append(s)
 
 
 
 
def a_star_optimizat(gr, tip_euristica = "euristica_nebanala_1"):
    t1 = time.time()
    l_open = [NodParcurgere(gr.stack_list_converted, None, 0, gr.calculeaza_h(gr.stack_list_converted))]
    l_closed = []
    while len(l_open) > 0:
        nodCurent = l_open.pop(0)
        l_closed.append(nodCurent)
        if gr.testeaza_scop(nodCurent):
            t2 = time.time()
            print("Solutie: \n", end="")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            print("\n================\n")
            print('Timpul de gasire a unei solutii: ', round(1000 * (t2 - t1)))
            return
        lSuccesori = gr.generare_de_succesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            gasitC = False
            for nodC in l_open:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f: lSuccesori.remove(s)
                    else:  l_open.remove(nodC)
                    break
 
            if not gasitC:
                for nodC in l_closed:
                    if s.info == nodC.info:
                        if s.f >= nodC.f: lSuccesori.remove(s)
                        else:  l_closed.remove(nodC)
                        break

        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(l_open)):
                if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc: l_open.insert(i, s)
            else: l_open.append(s)
 
 
 
 
def ida_star(gr, nrSolutiiCautate, tip_euristica = "euristica_nebanala_1"):
    t1 = time.time()
    nodStart = NodParcurgere(gr.stack_list_converted, None, 0, gr.calculeaza_h(gr.stack_list_converted))
    limita = nodStart.f
    while True:
        nrSolutiiCautate, rez = construieste_drum(gr, nodStart, limita, nrSolutiiCautate, tip_euristica, t1)
        if rez == "gata": break
        if rez == float('inf'): break
        limita = rez


def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate, tip_euristica, t1):
    if nodCurent.f > limita: return nrSolutiiCautate, nodCurent.f
    if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
        t2 = time.time()
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        print("\n================\n")
        print('Timpul de gasire a unei solutii: ', round(1000 * (t2 - t1)))
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0: return 0, "gata"
    lSuccesori = gr.generare_de_succesori(nodCurent, tip_euristica=tip_euristica)
    minim = float('inf')
    for s in lSuccesori:
        nrSolutiiCautate, rez = construieste_drum(gr, s, limita, nrSolutiiCautate, tip_euristica, t1)
        if rez == "gata": return 0, "gata"
        if rez < minim:  minim = rez
    return nrSolutiiCautate, minim
    