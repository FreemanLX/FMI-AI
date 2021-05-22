import time
import copy
from numpy import multiply
from numpy.lib.function_base import average
import pygame
import sys
import threading
from pygame.constants import DOUBLEBUF
import statistics
 
ADANCIME_MAX=4
 
 
def elem_identice(lista):
    if(len(set(lista))==1) :
        return lista[0] if lista[0]!=Joc.GOL else False
    return False
 

global count_mutari_jucator
score = []
score.append(0)
score.append(0) 
SCMAX = int(input("Introduceti un scor maxim: "))
global mutari_arr
mutari_arr = []



 
class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    JMIN=None
    JMAX=None
    GOL='#'
    NR_LINII=None
    NR_COLOANE=None
    scor_maxim=0

    def __init__(self, matr=None, NR_LINII=None, NR_COLOANE=None):
        #creez proprietatea ultima_mutare # (l,c)
        #Functie scrisa de @Irina Ciocan editata de @Mihalea Andreas (github.com/FreemanLX)
        #Update: Introdus in matrice la initializere x 0 pozitionate in centru
        self.ultima_mutare=None
        self.nomutari = False #suntem la inceput
        self.score_boolean = False #verifica daca captureaza simbolul sau nu doar pentru calculator  / nu pentru jucator
        if matr:
            #e data tabla, deci suntem in timpul jocului
            self.matr=matr 
        else:
            #nu e data tabla deci suntem la initializare
            self.matr= [[self.__class__.GOL] * NR_COLOANE for i in range(NR_LINII)]
            self.matr[(int(NR_LINII / 2))][int(NR_COLOANE / 2 - 1)] = 'x' 
            self.matr[(int(NR_LINII / 2))][int(NR_COLOANE / 2)] = '0'
            self.ultima_mutare = [(int(NR_LINII/2), int(NR_COLOANE / 2) - 1), (int(NR_LINII/2), int(NR_COLOANE / 2))]  #for x and 0
            if NR_LINII is not None:
                self.__class__.NR_LINII= NR_LINII
            if NR_COLOANE is not None:
                self.__class__.NR_COLOANE= NR_COLOANE
            
            ######## calculare scor maxim ###########
            sc_randuri=(NR_COLOANE-3)*NR_LINII
            sc_coloane = (NR_LINII - 3)*NR_COLOANE
            sc_diagonale = (NR_LINII - 3) * (NR_COLOANE - 3) * 2
            self.__class__.scor_maxim = sc_randuri + sc_coloane + sc_diagonale
 
    def deseneaza_grid(self, marcaj_linie = None, marcaj_coloana = None): # tabla de exemplu este ["#","x","#","0",......]
        #Functie scrisa de @Irina Ciocan editata de @Mihalea Andreas (github.com/FreemanLX)
        #Update: Editat tipul de culoare pentru oponent si pentru jucator
        for ind in range(self.__class__.NR_COLOANE*self.__class__.NR_LINII):
            linie=ind // self.__class__.NR_COLOANE # // inseamna div
            coloana=ind % self.__class__.NR_COLOANE
            last_i, last_j = self.get_last_indices(Joc.JMIN)
            last_i_bot, last_j_bot = self.get_last_indices(Joc.JMAX)
            
            if marcaj_linie == linie and marcaj_coloana == coloana or linie == last_i and coloana == last_j:
                #daca am o patratica selectata, o desenez cu albastru
                culoare=(0, 191, 255)
            elif linie == last_i_bot and coloana == last_j_bot:
                culoare=(139, 0, 0)    
            else:
                #altfel o desenez cu alb
                culoare=(255,255,255)
            pygame.draw.rect(self.__class__.display, culoare, self.__class__.celuleGrid[ind]) #alb = (255,255,255)
            if self.matr[linie][coloana]=='x':
                self.__class__.display.blit(self.__class__.x_img,(coloana*(self.__class__.dim_celula+1),linie*(self.__class__.dim_celula+1)))
            elif self.matr[linie][coloana]=='0':
                self.__class__.display.blit(self.__class__.zero_img,(coloana*(self.__class__.dim_celula+1),linie*(self.__class__.dim_celula+1)))

        #pygame.display.flip()
        pygame.display.update()         
 
    @classmethod
    def jucator_opus(cls, jucator):
        return cls.JMAX if jucator==cls.JMIN else cls.JMIN
 
 
    @classmethod
    def initializeaza(cls, display, NR_LINII=6, NR_COLOANE=7, dim_celula=100):
        #Functie scrisa de @Irina Ciocan
        cls.display=display
        cls.dim_celula=dim_celula
        cls.x_img = pygame.image.load('ics.png')
        cls.x_img = pygame.transform.scale(cls.x_img, (dim_celula,dim_celula))
        cls.zero_img = pygame.image.load('zero.png')
        cls.zero_img = pygame.transform.scale(cls.zero_img, (dim_celula,dim_celula))
        cls.celuleGrid=[] #este lista cu patratelele din grid
        for linie in range(NR_LINII):
            for coloana in range(NR_COLOANE):
                patr = pygame.Rect(coloana*(dim_celula+1), linie*(dim_celula+1), dim_celula, dim_celula)
                cls.celuleGrid.append(patr)
 
    def find_in_table(self, str):
        #Functie scrisa de @Mihalea Andreas (github.com/FreemanLX)
        #Imi cauta simbolul in matrice daca mai exista sau nu, complexitatea in cel mai rau caz e O(linii * coloane)
        for ind in range(self.NR_LINII):
            for jnd in range(self.NR_COLOANE):
                 if(str == self.matr[ind][jnd]):
                       return True
        return False    
 
    def final(self):
        #Functie scrisa @Mihalea Andreas (github.com/FreemanLX)
        #Eu aici verific in principiu 2 lucruri ori in functie de scor ori in functie daca nu mai e 0 sau x in el
        #Se pune cazul de remiza doar in cazaul in care scorul este identic si e mai mare decat SCMAX, fiind o variabila globala
        if(self.find_in_table('0') == False or (score[0] > score[1] and score[0] > SCMAX)):
            return "X"
        if(self.find_in_table('x') == False or (score[0] < score[1] and score[1] > SCMAX)):
            return "0"
        if (score[0] == score[1] and score[1] > SCMAX):
            return 'remiza'
        if(self.nomutari == True):
            return " "   
        else:
            return False
    

    def get_last_indices(self, jucator):
        #Functie scrisa de @Mihalea Andreas (github.com/FreemanLX)
        #Aici imi returneaza indiicile de la ultima mutare (in cazul in care jocul este la inceput imi returneaza mutarea de la inceput)
        for i in range(self.NR_LINII):
            for j in range(self.NR_COLOANE):
                if(jucator == 'x'):
                   if(i == self.ultima_mutare[0][0] and j == self.ultima_mutare[0][1]):
                     return i, j
                else:
                   if(i == self.ultima_mutare[1][0] and j == self.ultima_mutare[1][1]):
                     return i, j      

        if(jucator == 'x'):
           return int(self.NR_LINII / 2), int(self.NR_COLOANE / 2 - 1)
        else:
           return int(self.NR_LINII / 2), int(self.NR_COLOANE / 2) 

    def protejare(self, ind, jnd):
        #Functie scrisa de @Mihalea Andreas (github.com/FreemanLX)
        #Imi returneaza vecinii pentru indicii ind si jnd
        #Timpul de executie este max(T(n)) = 6 \in O(1)
        #Imi returneaza un vector de vecini, complexitatea in spatiu O(n)
        arr = []
        first = lambda t : 0 if t == 0 else -1
        last = lambda t, last_p : 0 if t == last_p else 2
        for i in range(first(ind), last(ind, self.NR_LINII)):
            for j in range(first(jnd), last(jnd, self.NR_COLOANE)):
                if(ind + i < self.NR_LINII and jnd + j < self.NR_COLOANE):
                  arr.append((ind + i, jnd + j)) 
        try:
           arr.remove((ind, jnd))
           return arr
        except:
           return arr    
  
    def convert(self, str):
        return 1 if str == 'x' else 0

    def mutari(self, jucator):
        #Functie scrisa de @Irina Ciocan editata de @Mihalea Andreas (github.com/FreemanLX)
        #Update: schimbat conditia specific cerintei (functia moving)
        l_mutari=[]
        start_i, start_j = self.ultima_mutare[self.convert(self.JMIN)]
        if(self.JMIN == '0'):
                start_j = start_j + 1
        for j in range(self.__class__.NR_COLOANE):
            for i in range(self.__class__.NR_LINII):
                continuity_of_game = moving(self, i, j, Joc.JMAX, Joc.JMIN)
                #Imi returneaza cine nu mai are mutari disponibile fiind blocat 
                if(continuity_of_game == -1):
                   self.nomutari = True #Special case
                   break
                   
                elif(continuity_of_game == 1 or continuity_of_game == 2):
                    #In functie de valoare imi genereaza mutari
                          matr_tabla_noua = copy.deepcopy(self.matr)
                          matr_tabla_noua[i][j] = jucator
                          jn=Joc(matr_tabla_noua)
                          jn.ultima_mutare = copy.deepcopy(self.ultima_mutare)
                          if(continuity_of_game == 2):
                              jn.score_boolean = True
                          if(jucator == 'x'):
                             jn.ultima_mutare[0] = (i, j)
                          else:
                             jn.ultima_mutare[1] = (i, j)   
                          l_mutari.append(jn)
                  
        return l_mutari
 
    def linie_deschisav2(self, lista, jucator):
        jo = self.jucator_opus(jucator)
        if not jo in lista:
             return 1
        return 0

    def linie_deschisa(self,lista, jucator):
        #Functie scrisa de @Irina Ciocan
        jo=self.jucator_opus(jucator)
		#verific daca pe linia data nu am simbolul jucatorului opus 
        if not jo in lista:
                return lista.count(jucator)
        return 0
			


    def linii_deschise(self, jucator):
        #Scrisa de @Mihalea Andreas (github.com/FreemanLX)
        #Liniile deschise reprezinta de fapt si de drept vecinii ai indiciilor i si j (standard)
        #liniile = 8 * lista.count(jucator) sau 8 in functie de functia linie deschisa
        # range(-1, 2) = -1 0 1
        linii = 0
        for i in range(1, self.__class__.NR_LINII - 1):
            for j in range(1, self.__class__.NR_COLOANE - 1):
                linii += self.linie_deschisa([self.matr[i+k][j+k2] for k in range(-1, 2) for k2 in range(-1, 2) ],jucator)
                #linii += self.linie_deschisav2([self.matr[i+k][j+k2] for k in range(-1, 2) for k2 in range(-1, 2) ],jucator)
        return linii       
        
    def estimeaza_scor(self, adancime):
        #Estimeaza_scor functie scrisa de @Irina Ciocan 
        t_final=self.final()
        if t_final==self.__class__.JMAX :
            return (self.__class__.scor_maxim+adancime)
        elif t_final==self.__class__.JMIN:
            return (-self.__class__.scor_maxim-adancime)
        elif t_final=='remiza':
            return 0
        else:
            return (self.linii_deschise(self.__class__.JMAX) - self.linii_deschise(self.__class__.JMIN))

            
    def sirAfisare(self):
        sir="  |"
        sir+=" ".join([str(i) for i in range(self.NR_COLOANE)])+"\n"
        sir+="-"*(self.NR_COLOANE+1)*2+"\n"
        sir+= "\n".join([str(i)+" |"+" ".join([str(x) for x in self.matr[i]]) for i in range(len(self.matr))])
        return sir
 
    def __str__(self):
        return self.sirAfisare()
 
    def __repr__(self):
        return self.sirAfisare()    
    

 
class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """
    #Functie scrisa de @Irina Ciocan editata de @Mihalea Andreas (github.com/FreemanLX)
    #Editat modul de afisare a matricii dintr-o stare:
    #1) Afiseaza matricea 
    #2) Afiseaza jucatorul curent
    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.tabla_joc=tabla_joc
        self.j_curent=j_curent
        
        #adancimea in arborele de stari
        self.adancime=adancime  
        
        #scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor=scor
        
        #lista de mutari posibile din starea curenta
        self.mutari_posibile=[]
        
        #cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa=None
 
    
 
    def mutari(self):       
        l_mutari=self.tabla_joc.mutari(self.j_curent)
        juc_opus=Joc.jucator_opus(self.j_curent)
        l_stari_mutari=[Stare(mutare, juc_opus, self.adancime-1, parinte=self) for mutare in l_mutari] 
        return l_stari_mutari
        
    
    def __str__(self):
        sir = str(self.tabla_joc) + "\n Jucator curent: " + self.j_curent + "\n"
        return sir  
    def __repr__(self):
        sir = str(self.tabla_joc) + "\n Jucator curent: " + self.j_curent + "\n"
        return sir
    
 
            
#functia de comparare pentru sortare stari
# imi returneaza valoarea ei    
def sort_mutari(e):
    if(e != None):
       return e.tabla_joc.estimeaza_scor(e.adancime)

""" Algoritmul MinMax """
 
def min_max(stare):
    #Functie scrisa de @Irina Ciocan editata de @Mihalea Andreas (github.com/FreemanLX)
    #Introdus o optiune ca daca algoritmul nu mai are mutari sa-mi returneze starea => DONE
    if stare.adancime==0 or stare.tabla_joc.final() :
        stare.scor=stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare
        
    if(len(stare.mutari()) == 0):
        stare.scor=stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare    
    #calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile=stare.mutari()
    mutari_arr.append(len(stare.mutari_posibile))
    #aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor=[min_max(mutare) for mutare in stare.mutari_posibile]
    
 
    if stare.j_curent==Joc.JMAX :
        #daca jucatorul e JMAX aleg starea-fiica cu scorul maxim
        stare.stare_aleasa=max(mutari_scor, key=lambda x: x.scor)
    else:
        #daca jucatorul e JMIN aleg starea-fiica cu scorul minim
        stare.stare_aleasa=min(mutari_scor, key=lambda x: x.scor)
    stare.scor=stare.stare_aleasa.scor
    return stare
    
 
def alpha_beta(alpha, beta, stare):
    #Functie scrisa de @Irina Ciocan editata de @Mihalea Andreas (github.com/FreemanLX)
    #Update: 
    #Introdus un thread pentru a sorta vectorul de mutari posibile in functie de estimeaza scor pentru fiecare adancime 
    #Threadul principal asteapta dupa acest thread pentru ca am folosit join()
    #Introdus o optiune ca daca algoritmul nu mai are mutari sa-mi returneze starea => DONE
    if stare.adancime==0 or stare.tabla_joc.final() :
        stare.scor=stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare
    
    if alpha>beta:
        return stare #este intr-un interval invalid deci nu o mai procesez
    
    stare.mutari_posibile=stare.mutari()
    mutari_arr.append(len(stare.mutari_posibile))
    if(len(stare.mutari()) == 0):
        stare.scor=stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare
    
    #vom sorta mutari posibile pentru alpha beta
    if stare.j_curent==Joc.JMAX :
            scor_curent=float('-inf')
            thread = threading.Thread(target= lambda : stare.mutari_posibile.sort(reverse=True, key=sort_mutari))
            thread.start()   
            thread.join()
            for mutare in stare.mutari_posibile:
                #calculeaza scorul
                stare_noua=alpha_beta(alpha, beta, mutare)
                
                if (scor_curent<stare_noua.scor):
                    stare.stare_aleasa=stare_noua
                    scor_curent=stare_noua.scor
                if(alpha<stare_noua.scor):
                    alpha=stare_noua.scor
                    if alpha>=beta:
                        break
    
    elif stare.j_curent==Joc.JMIN :
            scor_curent=float('inf')
            thread = threading.Thread(target= lambda : stare.mutari_posibile.sort(reverse=False, key=sort_mutari))
            thread.start()   
            thread.join()
            for mutare in stare.mutari_posibile:
                
                stare_noua=alpha_beta(alpha, beta, mutare)
                
                if (scor_curent>stare_noua.scor):
                    stare.stare_aleasa=stare_noua
                    scor_curent=stare_noua.scor
    
                if(beta>stare_noua.scor):
                    beta=stare_noua.scor
                    if alpha>=beta:
                        break

    stare.scor=stare.stare_aleasa.scor
    return stare
 

def afis_daca_final(stare_curenta):
    #Functie scrisa de @Irina Ciocan
    final=stare_curenta.tabla_joc.final()
    if(final):
        if (final == " "):
            return True
        if (final=="remiza"):
            print("Remiza!")
        else:
            print("A castigat "+ final)
            
        return True
        
    return False
 
class Buton:
    #Clasa scrisa de @Irina Ciocan
    def __init__(self, display=None, left=0, top=0, w=0, h=0,culoareFundal=(53,80,115), culoareFundalSel=(89,134,194), text="", font="arial", fontDimensiune=16, culoareText=(255,255,255), valoare=""):
        self.display=display        
        self.culoareFundal=culoareFundal
        self.culoareFundalSel=culoareFundalSel
        self.text=text
        self.font=font
        self.w=w
        self.h=h
        self.selectat=False
        self.fontDimensiune=fontDimensiune
        self.culoareText=culoareText
        #creez obiectul font
        fontObj = pygame.font.SysFont(self.font, self.fontDimensiune)
        self.textRandat=fontObj.render(self.text, True , self.culoareText) 
        self.dreptunghi=pygame.Rect(left, top, w, h) 
        #aici centram textul
        self.dreptunghiText=self.textRandat.get_rect(center=self.dreptunghi.center)
        self.valoare=valoare
 
    def update_top(self, top = 0):
        self.top = top

    def selecteaza(self,sel):
        self.selectat=sel
        self.deseneaza()
    def selecteazaDupacoord(self,coord):
        if self.dreptunghi.collidepoint(coord):
            self.selecteaza(True)
            return True
        return False
 
    def updateDreptunghi(self):
        self.dreptunghi.left=self.left
        self.dreptunghi.top=self.top
        self.dreptunghiText=self.textRandat.get_rect(center=self.dreptunghi.center)
 
    def deseneaza(self):
        culoareF= self.culoareFundalSel if self.selectat else self.culoareFundal
        pygame.draw.rect(self.display, culoareF, self.dreptunghi)   
        self.display.blit(self.textRandat ,self.dreptunghiText) 
 
class GrupButoane:
    #Clasa scrisa de @Irina Ciocan
    def __init__(self, listaButoane=[], indiceSelectat=0, spatiuButoane=10,left=0, top=0):
        self.listaButoane=listaButoane
        self.indiceSelectat=indiceSelectat
        self.listaButoane[self.indiceSelectat].selectat=True
        self.top=top
        self.left=left
        leftCurent=self.left
        for b in self.listaButoane:
            b.top=self.top
            b.left=leftCurent
            b.updateDreptunghi()
            leftCurent+=(spatiuButoane+b.w)
 
    def selecteazaDupacoord(self,coord):
        for ib,b in enumerate(self.listaButoane):
            if b.selecteazaDupacoord(coord):
                self.listaButoane[self.indiceSelectat].selecteaza(False)
                self.indiceSelectat=ib
                return True
        return False

    def update_top(self, top = 0 ):
        self.top = top    
 
    def deseneaza(self):
        #atentie, nu face wrap
        for b in self.listaButoane:
            b.deseneaza()
 
    def getValoare(self):
        return self.listaButoane[self.indiceSelectat].valoare
 
 
def deseneaza_alegeri(display, tabla_curenta, type) :
    #Functie scrisa de @Irina Ciocan, editata de @Mihalea Andreas (github.com/FreemanLX)
    #Functia reprezina ecranul initial inainte de a incepe jocul.
    #Update: In functie de tipul de joc vom afisa butoanele de tip algoritm sau nu
    #        Schimbat fundalul la aplicatie inainte de a incepe jocul
    #        
    if(type != 2):
        btn_alg=GrupButoane(
            top=30, 
            left=30,  
            listaButoane=[
                Buton(display=display, w=80, h=30, text="minimax", valoare="minimax"), 
                Buton(display=display, w=80, h=30, text="alphabeta", valoare="alphabeta")
                ],
            indiceSelectat=1)
    btn_juc=GrupButoane(
        top=100, 
        left=30, 
        listaButoane=[
            Buton(display=display, w=35, h=30, text="x", valoare="x"), 
            Buton(display=display, w=35, h=30, text="zero", valoare="0")
            ], 
        indiceSelectat=0)
    if(type == 2):
         btn_juc.update_top(top = 30) 
    ok=Buton(display=display, top=170, left=30, w=40, h=30, text="ok", culoareFundal=(0, 52, 155))
    #Vom schimba culoarea la display sa fie albastra, ca sa fie ok
    pygame.draw.rect(display, (0, 191, 255), display.get_rect()) 
    if(type != 2):
       btn_alg.deseneaza()
    btn_juc.deseneaza()
    ok.deseneaza()
    boolean = lambda pos : False
    if(type != 2):
        boolean = lambda pos : btn_alg.selecteazaDupacoord(pos)
    while True:
        for ev in pygame.event.get(): 
            if ev.type== pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN: 
                pos = pygame.mouse.get_pos()
                if not btn_juc.selecteazaDupacoord(pos):
                    if not boolean(pos):
                        if ok.selecteazaDupacoord(pos):
                            display.fill((0,0,0)) #stergere ecran 
                            tabla_curenta.deseneaza_grid()
                            if(type == 2): return btn_juc.getValoare(), 0
                            return btn_juc.getValoare(), btn_alg.getValoare()
        pygame.display.update()
 
 
 
def main():
    #Functie scrisa de @Irina Ciocan, editata de @Mihalea Andreas
    #Update: Schimbat interfata grafica
    #        Titlul se actualizeaza cu scorul calculatorului vs scorul jucatorului
    #        Adaugat nivele de dificultate, tipul de joc (C - C, J - C, J - J)
    #        Introdus SCMAX (e deasupra)
    #        Introdus scorul global ce calculeaza daca un simbol a fost capturat sau nu
    #        Inlocuit while(true) cu while(1) (optimizare d.p.v computational in timp cu 10%)
    #        
    global count_mutari_jucator 
    count_mutari_jucator = 0
    pygame.init()
    pygame.display.set_caption("311 Mihalea Andreas - ex-jocuri-exemple-modificate 0 - 0")
    #Selectare tip joc (NU FUNCTIONEAZA CU THREADING CA E GLOBALA VARIABILA)
    select_type_boolean = False
    global select_type_game
    while(select_type_boolean == False):
       score_level = int(input("Selectati modul de joc:\n1) User vs Calculator (implicit)\n2) User vs User\n3) Calculator vs Calculator\n"))
       if(score_level == 1 or score_level == 2 or score_level == 3):
           select_type_game = score_level
           break
       else:
           break   
    #Selectare nivel dificultate     
    score_level_boolean = False
    if(select_type_game == 1):    
        while(score_level_boolean == False):
            score_level = int(input("Selectati nivelul de dificultate a jocului:\n1) Usor\n2) Mediu\n3) Greu\n"))
            if(score_level == 1 or score_level == 2 or score_level == 3):
                ADANCIME_MAX = score_level
                score_level_boolean = True
            else:
                print("Trebuie ales de la 1 la 3, inclusiv.")    
    length_validate = False
    #Selectare numar coloana si linii
    while not length_validate:
        Colstr = input("Dati numarul de coloane pentru acest joc: ")
        Rowsstr = input("Dati numarul de randuri pentru acest joc: ")
        Col = int(Colstr)
        Rows = int(Rowsstr)
        if(Rows < 10 and Rows % 2 == 1 and Col > 5 and Col % 2 == 0): 
                length_validate = True                  
        if(length_validate == False):
            print("Introduceti numarul de coloane sa fie par si mai mare decat 5 (strict), iar numarul de linii sa fie mai mic decat 10 si impar")
        else:
            break;          
    nl=Rows
    nc=Col
    w=50
    ecran=pygame.display.set_mode(size=(nc*(w+1)-1,nl*(w+1)-1), flags = DOUBLEBUF)# N *w+ N-1= N*(w+1)-1
    Joc.initializeaza(ecran, NR_LINII=nl, NR_COLOANE=nc, dim_celula=w)
    #initializare tabla
    tabla_curenta = Joc(NR_LINII=Rows, NR_COLOANE=Col)
    Joc.JMIN, tip_algoritm = deseneaza_alegeri(ecran,tabla_curenta, select_type_game)
    print(Joc.JMIN, tip_algoritm) 
    Joc.JMAX = '0' if Joc.JMIN == 'x' else 'x'
    print("Tabla initiala")
    print(str(tabla_curenta))
    #creare stare initiala
    if(select_type_game == 2 or select_type_game == 3): ADANCIME_MAX = 2
    stare_curenta=Stare(tabla_curenta,'x',ADANCIME_MAX)
    #boolean este o expresie lambda conditionata in functie de tipul de joc pe care-l avem
    #J - J, J - C, C - C
    boolean = lambda juc_curent : True
    if(select_type_game == 1): boolean = lambda juc_curent : juc_curent==Joc.JMIN
    if(select_type_game == 3): boolean = lambda juc_curent : False
    tabla_curenta.deseneaza_grid()
    while 1 :
        pygame.display.set_caption("311 Mihalea Andreas - ex-jocuri-exemple-modificate " + str(score[0]) + "-" + str(score[1]))
        if boolean(stare_curenta.j_curent):
            #punem cazul in care no_mutari nu poate acoperi
            #ca stare_curenta sa nu aiba mutari
            if(len(stare_curenta.mutari()) == 0):
                print("A castigat " + str(stare_curenta.tabla_joc.jucator_opus(stare_curenta.j_curent)))
                break    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    afisare()
                    pygame.quit()
                    sys.exit()
                #Imi afiseaza si-mi coloreaza     
                if event.type == pygame.MOUSEMOTION:		
                    for np in range(len(Joc.celuleGrid)):						
                          if Joc.celuleGrid[np].collidepoint(pygame.mouse.get_pos()):
                                stare_curenta.tabla_joc.deseneaza_grid(marcaj_coloana=np % Joc.NR_COLOANE, marcaj_linie = np // Joc.NR_COLOANE)
                                break    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()#coordonatele cursorului la momentul clickului
                    for np in range(len(Joc.celuleGrid)):
                        
                        if Joc.celuleGrid[np].collidepoint(pos):
                            linie=np // Joc.NR_COLOANE
                            coloana=np % Joc.NR_COLOANE
                            ############################### 
                            continuity_of_game = moving(stare_curenta.tabla_joc, linie, coloana, Joc.JMIN, Joc.JMAX) 
                           # if(continuity_of_game == - 1):
                            #    pygame.quit()
                             #   sys.exit()
                            if(continuity_of_game == 1 or continuity_of_game == 2):
                                              count_mutari_jucator = count_mutari_jucator + 1
                                              stare_curenta.tabla_joc.ultima_mutare = copy.deepcopy(stare_curenta.tabla_joc.ultima_mutare)
                                              if(stare_curenta.tabla_joc.JMIN == 'x'): 
                                                   stare_curenta.tabla_joc.ultima_mutare[0]=(linie, coloana)
                                              else:
                                                    stare_curenta.tabla_joc.ultima_mutare[1]=(linie, coloana)   
                                              if(continuity_of_game == 2):      
                                                score[0] = score[0] + 1      
                                              stare_curenta.tabla_joc.matr[linie][coloana] = Joc.JMIN
                                              stare_curenta.tabla_joc.deseneaza_grid(marcaj_coloana=coloana, marcaj_linie=linie)
                                              print("\nTabla dupa mutarea jucatorului")
                                              print(str(stare_curenta))
                                              if (afis_daca_final(stare_curenta)):
                                                    break

                                           
                                              stare_curenta.j_curent=Joc.jucator_opus(stare_curenta.j_curent)
                                              #print(stare_curenta.j_curent)
                                              print("Scor-ul jucatorului " + str(Joc.JMIN) + ": " + str(score[0]))  
                                              if(select_type_game == 2):
                                                    stare_curenta.j_curent='0' if Joc.JMIN == 'x' else 'x'
                                                    score[0], score[1] = score[1], score[0]
                                                    Joc.JMIN = stare_curenta.j_curent
                                                    Joc.JMAX = Joc.jucator_opus(stare_curenta.j_curent)  
                            
                            else:
                                print("Mutare invalida")
                              
            
    
        #--------------------------------
        else: #jucatorul e JMAX (calculatorul)
            #punem cazul in care no_mutari nu poate acoperi
            #ca stare_curenta sa nu aiba mutari
            #altfel => eroare la cei doi algoritmi (ab + minimax)
            if(len(stare_curenta.mutari()) == 0):
                print("A castigat " + str(stare_curenta.tabla_joc.jucator_opus(stare_curenta.j_curent)))
                break    
            t_inainte=int(round(time.time() * 1000))
            if tip_algoritm=='minimax':
                stare_actualizata=min_max(stare_curenta)
            else:
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            stare_curenta.tabla_joc=stare_actualizata.stare_aleasa.tabla_joc
            if(stare_curenta.tabla_joc.score_boolean == True):
               score[1] = score[1] + 1
            print("Tabla dupa mutarea calculatorului\n"+str(stare_curenta))
            print("\nNumarul de mutari este in aceasta iteratie este: " + str(mutari_arr[-1]))
            #preiau timpul in milisecunde de dupa mutare
            t_dupa=int(round(time.time() * 1000))
            print("Calculatorul a \"gandit\" timp de "+str(t_dupa-t_inainte)+" milisecunde.")
            stare_curenta.tabla_joc.deseneaza_grid()
            #thread = threading.Thread(target = stare_curenta.tabla_joc.deseneaza_grid)
            #thread.start()
            if (afis_daca_final(stare_curenta)):
                break    
            print("Scor-ul calculatorului " + str(Joc.JMAX) +  ": " +  str(score[1]))
            #S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.j_curent=Joc.jucator_opus(stare_curenta.j_curent)
            if(select_type_game == 3):
                    stare_curenta.j_curent='0' if Joc.JMAX == 'x' else 'x'
                    score[0], score[1] = score[1], score[0]
                    Joc.JMAX = stare_curenta.j_curent
                    Joc.JMIN = Joc.jucator_opus(stare_curenta.j_curent)     
    
       
#arr_vecin =  stare_curenta.protejare(arr[k][0], arr[k][1]) 
#                                        if(stare_curenta.matr[arr[k][0]][arr[k][1]] == jucator_opus):
#                                             return no_mutari(stare_curenta, jucator, jucator_opus, arr_vecin)
#                                        else:             
#                                            count = 0
#                                            for e in range(len(arr_vecin)):
#                                                try:  
#                                                    if(stare_curenta.matr[arr_vecin[e][0]][arr_vecin[e][1]] == jucator):
#                                                            count = count + 1
#                                                except:
#                                                    continue
#                                            if(count < 8):
#                                                return True



def no_mutari(stare_curenta, jucator, jucator_opus, arr):
    #Functie scrisa de @Mihalea Andreas (github.com/FreemanLX)
    #Functia asta reprezinta o completare a functiei final() din clasa Joc
    #stare_curenta e de fapt un obiect din clasa Joc
    #jucator_opus = Joc.JMAX / JMIN depinde de tip
    #Fie [x] \in [Joc.JMIN = 0, Joc.JMAX = 1] 
    #Aici in principiu vom presupune ca x este inconjurat sau nu
    #       
    #     x   x   x   x  x                      x   0   0   0  0                                             x   #   0   #   0 
    #     x   x   x   x  x  => 0 castiga        x   x   x   0  x   => 0 castiga, fiindca 0 e protejat,       x   x   x   0   x  => jocul continua fiindca x poate sa iasa mancand-ul pe 0, 
    #     x   x  [x]  x  x                      x   x  [x]  x  x      deci [x] e blocat                      x   x  [x]  x   x     ne fiind protejat
    #     x   x   x   x  x                      x   x   x   x  x                                             x   x   x   x   x
    #
    for k in range(len(arr)):
                count = 0 
                if(stare_curenta.matr[arr[k][0]][arr[k][1]] == '#'):
                            return True
                elif(stare_curenta.matr[arr[k][0]][arr[k][1]] == jucator_opus):      
                    arr_vecini = stare_curenta.protejare(arr[k][0], arr[k][1])
                    for arr in arr_vecini:
                        if(arr == jucator_opus or arr == jucator):
                           count = count + 1
                    if(count < 3):
                         return True               
    return False         

def moving(stare_curenta, linie, coloana, jucator, jucator_opus):
    #Functie scrisa de @Mihalea Andreas (github.com/FreemanLX)
    #stare_curenta e de fapt un obiect din clasa Joc
    #jucator = Joc.JMIN / JMAX depinde de tip
    #jucator_opus = Joc.JMAX / JMIN depinde de jucator ca e opus
    #In principiu noi vom impartii in 2 parti
    #1) Verificam daca mai are mutari valabile
    #2) Daca mai are mutari valabile vom verifca:
    # 2.1) Daca vreau sa mut pe ceva gol => verific daca e vecin (daca nu) => FAIL
    # 2.2) Daca vreau sa atac pe jucatorul opus => verific daca e protejat sau nu, daca e protejat => FAIL
    #                                           => verific daca e vecin sau nu, daca nu => FAIL
    #                                           => daca respecta conditiile de mai sus, mutarea va fi scoasa a jucatorului opus si voi inlocui cu cea castigata, 
    #                                              implicit si scorul creste cu 1
    #
                            last_i, last_j = stare_curenta.get_last_indices(jucator)
                            last_i_jucator_opus, last_j_jucator_opus = stare_curenta.get_last_indices(jucator_opus)
                            if(linie == last_i_jucator_opus and coloana == last_j_jucator_opus):
                                return 0    
                            arr = stare_curenta.protejare(last_i, last_j)
                            if stare_curenta.matr[linie][coloana] == Joc.GOL:                         
                                for k in range(len(arr)):
                                  if(arr[k] == (linie, coloana)):
                                     return 1                                    
                            if(no_mutari(stare_curenta, jucator, jucator_opus, arr) == False):
                                print("A castigat " + jucator_opus)
                                return -1
                            if stare_curenta.matr[linie][coloana] == jucator_opus: 
                                try:
                                 vecini_jucator_opus = stare_curenta.protejare(last_i_jucator_opus, last_j_jucator_opus)
                                 vecini_jucator = stare_curenta.protejare(last_i, last_j)
                                except:
                                    return 0 
                                in_range_last_move = False
                                for k in range(len(vecini_jucator_opus)):
                                    if(vecini_jucator_opus[k] == (linie, coloana)):
                                            in_range_last_move = True
                                            break
                                
                                if(in_range_last_move == False):
                                    count = 0
                                    vecini_i_j = stare_curenta.protejare(linie, coloana)
                                    for k in range(len(vecini_i_j)):
                                            if(stare_curenta.matr[vecini_i_j[k][0]][vecini_i_j[k][1]] == jucator_opus):
                                                count = count + 1 

                                    for k in range(len(vecini_jucator)):
                                        if(vecini_jucator[k] == (linie, coloana) and count < 3):  
                                              return 2  
                                              
def afisare():
    #Functie scrisa de @Mihalea Andreas (github.com/FreemanLX)
    #Aici afisam minimul de mutari, maximul de mutari, media mutariilor, mediana mutariilor
    #Numarul total de mutari folosit de jucator si de calculator

                print("Minimul de mutari: " + str(min(mutari_arr)))
                print("Maximul de mutari: " + str(max(mutari_arr)))
                print("Media mutariilor: " + str(average(mutari_arr)))
                print("Mediana mutariilor: " + str(statistics.median(mutari_arr)))
                t_dupa = int(round(time.time() * 1000)) 
                print("Timpul efectuat de joc este: "+str(t_dupa-t_inainte)+" milisecunde.")  
                print("Numarul total de mutari folosit de jucator este " + str(count_mutari_jucator))
                print("Numarul total de mutari folosit de calculator este: " + str(sum(mutari_arr)))  


if __name__ == "__main__" :
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    #result = loop.run_until_complete(main())
    t_inainte = int(round(time.time() * 1000))
    #pentru stabilitate fac un thread diferit de programul in general sicronizat
    #function_main_thread = threading.Thread(main)
    #function_main_thread.start()
    #function_main_thread.join()
    main()
    while True :
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                afisare()
                pygame.quit()
                sys.exit()
                
                 
        
 
