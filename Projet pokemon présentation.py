# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 14:00:20 2016

@author: bphan
"""
import random as rd
import copy 


def sign(n):
    if n>=0:
        return(1)
    else:
        return(-1)
        
def myprint(texte,test=False): #permet d'éviter qu'il y ait plein de print quand une IA teste les différentes possibilités
    if not test:
        print(texte)
        
def myinput(texte,action=-42):
    if action !=-42:
        return(str(action))
    else:
        action=input(texte)
        return(action)

class pokemon:
    def __init__(self,nom,statistiques,PVactuels,competences,types,niveau,etat,bonus,sexe,confusion,sommeil):
        self.nom=nom
        self.statistiques=statistiques
        self.PVmax=statistiques[0]
        self.attaque_init=statistiques[1] #détermine la force des attaques physiques
        self.defense_init=statistiques[2] #détermine la résistance aux attaques physiques
        self.attaque_speciale_init=statistiques[3] #détermine la force des attaques spéciales
        self.defense_speciale_init=statistiques[4] ##détermine la résistance attaques spéciales
        self.vitesse_init=statistiques[5] #détermine qui agit en premier
        self.PVactuels=PVactuels
        self.competences=competences #les 4 mouvements que connait le pokemon
        self.types=types #le(s) type(s) du pokemon
        self.niveau=niveau
        self.etat=etat #altération d'état (empoisonné, paralysé, ...)
        self.bonus=bonus #bonus doit etre un tableau de 7 entiers entre -6 et 6 donnant les bonus/malus des stats (autres que les PV) ainsi que la precision et l'esquive
        self.sexe=sexe
        self.statistiques_modifiees=[self.PVmax]+[statistiques[i]*(1+abs(self.bonus[i-1]/2))**sign(self.bonus[i-1]) for i in range(1,6)]
        self.attaque_modifiee=self.statistiques_modifiees[1]
        self.defense_modifiee=self.statistiques_modifiees[2]
        self.attaque_speciale_modifiee=self.statistiques_modifiees[3]
        self.defense_speciale_modifiee=self.statistiques_modifiees[4]
        self.vitesse_modifiee=self.statistiques_modifiees[5]
        if etat=="paralyse":
            self.vitesse_modifiee=self.vitesse_modifiee/4
        self.confusion=confusion #nombre de tours de confusion prévu et nombre de tours déjà passés confus
        self.sommeil=sommeil #nombre de tours prévu à dormir et nombre de tours déjà passés endormi
            
    def actualiser_stats(self): #modifie les stats en fonction des bonus/malus
        self.statistiques_modifiees=[self.PVmax]+[self.statistiques[i]*(1+abs(self.bonus[i-1]/2))**sign(self.bonus[i-1]) for i in range(1,6)]
        self.attaque_modifiee=self.statistiques_modifiees[1]
        self.defense_modifiee=self.statistiques_modifiees[2]
        self.attaque_speciale_modifiee=self.statistiques_modifiees[3]
        self.defense_speciale_modifiee=self.statistiques_modifiees[4]
        self.vitesse_modifiee=self.statistiques_modifiees[5]
        if self.etat=="paralyse":
            self.vitesse_modifiee=self.vitesse_modifiee/4
            
        
    def attaquer(self,other,attaque,test=False): #attaquer un autre pokemon
        bonus_precision=self.bonus[5]-other.bonus[6] #précision affecté par son bonus de précision et le bonus d'esquive de l'adversaire
        degats=0
        action_possible=True
        if self.sommeil[0]!=self.sommeil[1]: #sommeil est une liste de 2 variables : la premiere indique le nombre de tour que le pokemon va passer à dormir, la deuxieme le nombre de tour qu'il a déjà passé à dormir
            self.sommeil[1]+=1 #augmentation du nombre de tour passé à dormir
            if self.sommeil[0]==self.sommeil[1]:
                self.sommeil=[0,0]
                myprint("{} s'est réveillé".format(self.nom),test)
                self.etat="" #etat redevient normal
            else:
                myprint("{} est en train de dormir".format(self.nom),test)
                if attaque.nom!="Blabla dodo": #ne peut pas attaquer sauf avec Blabla dodo
                    action_possible=False
        if self.etat=="paralyse":
            p=rd.uniform(0,100)
            if p<=25:  #une chance sur 4 de ne pas pouvoir attaquer
                myprint("{} est complètement paralysé".format(self.nom),test)
                action_possible=False
        if self.etat=="gele":
            if rd.uniform(0,100)<80: #une chance sur 5 de dégeler
                action_possible=False
                myprint("{} est complètement gelé".format(self.nom),test)
            else:
                self.etat=""
                myprint("{} est dégelé".format(self.nom),test)
        if action_possible:
            if self.confusion[0]!=self.confusion[1]: #système similaire au sommeil
                self.confusion[1]+=1
                if self.confusion[1]==self.confusion[0]:
                    self.confusion=[0,0]
                    myprint("{} a repris ses esprits".format(self.nom),test)
                else:
                    myprint("{} est confus".format(self.nom),test)
                    p=rd.uniform(0,100)
                    if p<=50: #Le pokemon se blesse lui-même 1 fois sur 2
                        degats=((self.niveau*.4+2)*self.attaque_modifiee*40/(self.defense_modifiee*50)+2)*rd.uniform(.85,1) #formule de dégats
                        degats=int(max(min(self.PVactuels,degats),1))
                        myprint("{} se blesse dans sa confusion".format(self.nom),test)
                        self.PVactuels=self.PVactuels-degats
                        myprint("{} a {} PV".format(self.nom,self.PVactuels),test)
                        if self.PVactuels<=0:
                            self.etat="K.O."
                            myprint("{} est K.O.".format(self.nom),test)
            if degats==0: #un pokemon qui se blesse dans sa confusion ne peut plus attaquer
                myprint("{} utilise {}".format(self.nom,attaque.nom),test)
                attaque.PPactuels=attaque.PPactuels-1 #nb d'utilisations d'une attaque est limité par le nb de PP
                reussite=rd.uniform(0,100)
                if reussite<=attaque.precision*(1+abs(bonus_precision/3))**sign(bonus_precision):
                    if attaque.puissance>0: #si l'attaque inflige des dégats
                        if attaque.Type=="feu" and other.etat=="gele": #une attaque de feu dégèle l'adversaire
                            other.etat=""
                            myprint("{} a dégelé {}".format(attaque.nom,other.nom),test)
                        K=efficacite(attaque,other)
                        if K==0:
                            myprint("Ca n'a aucun effet ...",test)
                        else:
                            coeff=K
                            if attaque.speciale=="speciale":
                                i=2
                            else:
                                i=0
                            if self.etat=="brule" and i==0: #malus attaque physique si brule
                                coeff=coeff/2
                            if attaque.Type in self.types: #Same Type Ability Bonus (STAB)
                                coeff=coeff*1.5
                            est_critique=False
                            critique=rd.uniform(0,100)
                            if critique<=6.25: #Bonus en cas de coup critique
                                coeff=coeff*2
                                est_critique=True
                            puissance=attaque.puissance
                            bonus_attaque=(1+abs(self.bonus[0+i]/2))**sign(self.bonus[0+i])
                            if (est_critique and self.bonus[0+i]>0) or (not est_critique):
                                stat_attaque=self.attaque_init*bonus_attaque
                            else: #un coup critique ignore les malus d'attaque
                                stat_attaque=self.attaque_init
                            bonus_defense=(1+abs(other.bonus[1+i]*1/2))**sign(other.bonus[1+i])
                            if (est_critique and other.bonus[1+i]<0) or (not est_critique):
                                defense=other.defense_init*bonus_defense
                            else: #un coup critique ignore les bonus de defense adverses
                                defense=other.defense_init
                            degats=coeff*((self.niveau*.4+2)*stat_attaque*puissance/(defense*50)+2)*rd.uniform(.85,1)
                            degats=int(max(min(other.PVactuels,degats),1))
                            other.PVactuels=other.PVactuels-degats
                            if K>1:
                                myprint("C'est tres efficace!",test)
                            elif K<1:
                                myprint("Ce n'est pas tres efficace ...",test)
                            if est_critique:
                                myprint("Coup critique!",test)
                            myprint("{} a {} PV".format(other.nom,other.PVactuels),test)
                        if other.PVactuels<=0:
                            other.etat="K.O."
                            myprint("{} est K.O.".format(other.nom),test)
                    if attaque.effet!=None: #les attaques peuvent avoir des effets particuliers
                        attaque.effet(self,other,degats,test)
                else:
                    myprint("Attaque échouée",test)
        self.actualiser_stats()
        other.actualiser_stats
        myprint("\n",test)
        
    def rerandomiser_sommeil_confusion(self): #sera utile pour l'IA
        if self.etat=="sommeil" and len(self.sommeil)==2: #si len!=2 le sommeil est dû à un repos donc on sait le nb de tours restants
            self.sommeil[0]=rd.randint(self.sommeil[1]+1,7)
        if self.confusion[0]!=0:
            self.confusion[0]=rd.randint(self.confusion[1]+1,5)
        
class competence:
    def __init__(self,nom,puissance,precision,Type,speciale,priorite,effet,PPmax,PPactuels):
        self.nom=nom
        self.puissance=puissance
        self.precision=precision
        self.Type=Type
        self.speciale=speciale
        self.priorite=priorite
        self.effet=effet
        self.PPmax=PPmax
        self.PPactuels=PPactuels

def conversion_type(T): #utile pour le calcul de l'efficacite des attaques
    acier,combat,dragon,eau,electrik,fee,feu,glace,insecte,normal,plante,poison,psy,roche,sol,spectre,tenebres,vol,autre=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
    return(eval(T))

            
def efficacite(attaque,defenseur):
    T=conversion_type(attaque.Type)
    T1=conversion_type(defenseur.types[0])
    table_types=[0]*18
    for i in range(18):
        table_types[i]=[1]*19
    table_types[0][0],table_types[0][2],table_types[0][5],table_types[0][7],table_types[0][8],table_types[0][9],table_types[0][10],table_types[0][12],table_types[0][13],table_types[0][17]=.5,.5,.5,.5,.5,.5,.5,.5,.5,.5
    table_types[0][1],table_types[0][6],table_types[0][14]=2,2,2
    table_types[0][11]=0
    table_types[1][5],table_types[1][12],table_types[1][17]=2,2,2
    table_types[1][8],table_types[1][13],table_types[1][16]=.5,.5,.5
    table_types[2][3],table_types[2][4],table_types[2][6],table_types[2][10]=.5,.5,.5,.5
    table_types[2][2],table_types[2][5],table_types[2][7]=2,2,2
    table_types[3][0],table_types[3][3],table_types[3][6],table_types[3][7]=.5,.5,.5,.5
    table_types[3][4],table_types[3][10]=2,2
    table_types[4][0],table_types[4][4],table_types[4][17]=.5,.5,.5
    table_types[4][14]=2
    table_types[5][0],table_types[5][11]=2,2
    table_types[5][1],table_types[5][8],table_types[5][16]=.5,.5,.5
    table_types[5][2]=0
    table_types[6][3],table_types[6][13],table_types[6][14]=2,2,2
    table_types[6][0],table_types[6][5],table_types[6][6],table_types[6][7],table_types[6][8],table_types[6][10]=.5,.5,.5,.5,.5,.5
    table_types[7][0],table_types[7][1],table_types[7][6],table_types[6][13]=2,2,2,2
    table_types[7][7]=.5
    table_types[8][6],table_types[8][13],table_types[8][17]=2,2,2
    table_types[8][1],table_types[8][10],table_types[8][14],=.5,.5,.5
    table_types[9][1]=2
    table_types[9][15]=0
    table_types[10][6],table_types[10][7],table_types[10][8],table_types[10][11],table_types[10][17]=2,2,2,2,2
    table_types[10][3],table_types[10][4],table_types[10][10],table_types[10][14]=.5,.5,.5,.5
    table_types[11][12],table_types[11][14]=2,2
    table_types[11][1],table_types[11][5],table_types[11][8],table_types[11][10],table_types[11][11]=.5,.5,.5,.5,.5
    table_types[12][6],table_types[12][15],table_types[12][16]=2,2,2
    table_types[12][1],table_types[12][12]=.5,.5
    table_types[13][0],table_types[13][1],table_types[13][3],table_types[13][10],table_types[13][14]=2,2,2,2,2
    table_types[13][6],table_types[13][9],table_types[13][11],table_types[13][17]=.5,.5,.5,.5
    table_types[14][3],table_types[14][7],table_types[14][10]=2,2,2
    table_types[14][11],table_types[14][13]=.5,.5
    table_types[14][4]=0
    table_types[15][15],table_types[15][16]=2,2
    table_types[15][8],table_types[15][11]=.5,.5
    table_types[15][1],table_types[15][9]=0,0
    table_types[16][1],table_types[16][5],table_types[16][8]=2,2,2
    table_types[16][15],table_types[16][16]=.5,.5
    table_types[16][12]=0
    table_types[17][4],table_types[17][7],table_types[17][13]=2,2,2
    table_types[17][1],table_types[17][8],table_types[17][10]=.5,.5,.5
    table_types[17][14]=0
    coeff=table_types[T1][T]
    n=len(defenseur.types)
    if n==2: #Si le pokémon défenseur a 2 types
        T2=conversion_type(defenseur.types[1])
        coeff=coeff*table_types[T2][T]
    return(coeff)
    
            
class dresseur:
    def __init__(self,nom,pokemons,poke_actif,joueur,perdu=False):
        self.nom=nom
        self.pokemons=pokemons
        self.poke_actif=poke_actif
        self.joueur=joueur
        self.perdu=perdu        

class IA:
    def __init__(self,nom,humain,strategie_competence,strategie_changer_pokemon):
        self.nom=nom
        self.humain=humain #booléen
        self.strategie_competence=strategie_competence
        self.strategie_changer_pokemon=strategie_changer_pokemon
        


humain=IA("Humain",True,None,None) #joueur humain


def strategie_competence_i(i): 
    def strat_i(dresseur,adversaire,n=20): #strategie d'une IA qui utilise tout le temps la competence i
        return([1,1,i],0)
    return(strat_i)

#pokemon,score_KO=-0.8006110698082329,coeff_bonus=1.3300638680915746,coeff_etat=0.061818715181948744,coeff_confusion=0.16454866255039424
#pokemon,score_KO=-.5,coeff_bonus=1.5,coeff_etat=.4,coeff_confusion=.3
def score(pokemon,score_KO=-.5,coeff_bonus=1.5,coeff_etat=.4,coeff_confusion=.3): #fonction déterminant à quel point un pokemon peut encore être utile
    if pokemon.PVactuels<=0: #Un pokemon K.O. est significativement moins utile qu'un pokemon à 1 PV
        return(score_KO)
    S=pokemon.PVactuels/pokemon.PVmax
    S_bonus=1
    for i in range(7):
        S_bonus+=pokemon.bonus[i]
    S=S*coeff_bonus**S_bonus
    if pokemon.etat!="":
        S=S*coeff_etat
    if pokemon.confusion[0]!=0:
        S=S*coeff_confusion
    return(S)
        
          
def strategie_IA_MiniMax_1(dresseur,adversaire,n=20,S=score):
    COPIE1=copy.deepcopy(dresseur)
    COPIE2=copy.deepcopy(adversaire)
    COPIE1.joueur.humain=False
    COPIE2.joueur.humain=False
    tableau_scores=[0]*4
    for i in range(4):
        tableau_scores[i]=[0]*4
    for i in range(4):
        for j in range(4):
            if COPIE1.poke_actif.competences[i].PPactuels==0 or COPIE2.poke_actif.competences[j].PPactuels==0:
                tableau_scores[i][j]=10000*n
            else:
                for k in range(n):
                    copie1=copy.deepcopy(COPIE1) #besoin de deepcopy pour avoir des copies des pokémons indépendantes des originaux
                    copie2=copy.deepcopy(COPIE2)
                    copie1.poke_actif.rerandomiser_sommeil_confusion()
                    copie2.poke_actif.rerandomiser_sommeil_confusion()
                    copie1.joueur.strategie_competence=strategie_competence_i(i+1)
                    copie2.joueur.strategie_competence=strategie_competence_i(j+1)
                    tour(copie1,copie2,True,0) #le 0 correspondant à K dans la fonction tour empêche une deuxieme application des degats du poison/brulure
                    score1=S(copie1.poke_actif)
                    score2=S(copie2.poke_actif)
                    tableau_scores[i][j]+=score1-score2
    Max=[-10000*n,0]
    for i in range(4):
        Min=10000*n
        for j in range(4):
            Min=min(Min, tableau_scores[i][j])
        if Min>Max[0] and Min!=10000*n:
            Max=[Min,i]
    return([1,1,Max[1]+1],Max[0])

def strategie_changer_pokemon_IA_MiniMax_1(dresseur,adversaire,n=20,S=score):
    COPIE1=copy.deepcopy(dresseur)
    COPIE2=copy.deepcopy(adversaire)
    COPIE1.joueur.humain=False
    COPIE2.joueur.humain=False
    k=len(COPIE1.pokemons)
    tableau_scores=[0]*k
    for i in range(k):
        if COPIE1.pokemons[i].etat=="K.O.":
            tableau_scores[i]=-100000*n
        else:
            tableau_scores[i]=strategie_IA_MiniMax_1(COPIE1,COPIE2,n,S)[1]
    Max=[-10000*n,0]
    for i in range(k):
        if tableau_scores[i]>Max[0]:
            Max=[tableau_scores[i],i]
    return(Max[1]+1)
                    
IA_MiniMax_1=IA("MiniMax1",False,strategie_IA_MiniMax_1,strategie_changer_pokemon_IA_MiniMax_1)
                
def strategie_competence_random(dresseur,adversaire,n=20): #strategie d'une IA qui joue au hasard
    l=[0,1,2,3]
    K=0
    for i in range(4):
        if dresseur.poke_actif.competences[i].PPactuels==0:
            l.pop(i-K)
            K+=1
    if len(l)==0:
        return([1,1,1])
    else:
        m=rd.randint(1,len(l))
        return([1,1,l[m-1]+1],m-1)

def strategie_changer_pokemon_random(dresseur,adversaire,n=20):
    l=[0,1,2,3,4,5]
    K=0
    for i in range(6):
        if dresseur.pokemons[i].etat=="K.O.":
            l.pop(i-K)
            K+=1
        elif dresseur.pokemons[i].nom==dresseur.poke_actif.nom:
            l.pop(i-K)
            K+=1
    n=rd.randint(1,len(l))
    return(l[n-1]+1)

IA_random=IA("Random",False,strategie_competence_random,strategie_changer_pokemon_random)

def degats_poison_brulure(pokemon,dresseur,adversaire,test=False,K=-42): #Un pokemon empoisonné ou brulé perd des PV à chaque tour 
    if pokemon.etat in ["brule","empoisonne"] and K!=0: #si K=0 on empêche une deuxième application des dégats si c'est un test. J'avais introduit ce K et pas seulement utliser la variable test dans l'optique de faire une IA qui antcipe 2 tours mais je ne l'ai pas faite.
        myprint("{} souffre. Il est {}.".format(pokemon.nom,pokemon.etat),test)
        degats=int(max(min(pokemon.PVmax/8,pokemon.PVactuels),1))
        pokemon.PVactuels-=degats
        myprint("{} a {} PV".format(pokemon.nom,pokemon.PVactuels),test)
        if verifier_KO(dresseur,pokemon,adversaire,test):
            pokemon=dresseur.poke_actif

def tour(dresseur1,dresseur2,test=False,K=-42): #definition de comment se passe un tour de jeu
    myprint("{} : {} {} PV / {} {} \n {} : {} {} PV / {}  {}".format(dresseur1.nom, dresseur1.poke_actif.nom,dresseur1.poke_actif.PVactuels,dresseur1.poke_actif.PVmax,dresseur1.poke_actif.etat,dresseur2.nom, dresseur2.poke_actif.nom,dresseur2.poke_actif.PVactuels,dresseur2.poke_actif.PVmax,dresseur2.poke_actif.etat),test) #Situation des 2 pokemons combattants
    pokemon1=dresseur1.poke_actif #commodité pour alléger le code
    pokemon2=dresseur2.poke_actif
    degats_poison_brulure(pokemon1,dresseur1,dresseur2,test,K)
    degats_poison_brulure(pokemon2,dresseur2,dresseur1,test,K)
    if not verifier_fin_partie(dresseur1,dresseur2,True):
        if dresseur1.joueur.humain: #un joueur humain rentrera ses choix
            choix_dresseur1=[-42]*3    
        else:
            choix_dresseur1=dresseur1.joueur.strategie_competence(dresseur1,dresseur2)[0] #l'IA choisit d'avance ses choix
        myinput(dresseur1.nom,choix_dresseur1[0])
        action1=choisir_action(dresseur1,choix_dresseur1[1],choix_dresseur1[2],dresseur2,test)
        if dresseur2.joueur.humain:
            choix_dresseur2=[-42]*3    
        else:
            choix_dresseur2=dresseur2.joueur.strategie_competence(dresseur2,dresseur1)[0]
        myinput("\n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n {}".format(dresseur2.nom),choix_dresseur2[0]) #le joueur 2 ne vera pas les choix du joueur 1
        action2=choisir_action(dresseur2,choix_dresseur2[1],choix_dresseur2[2],dresseur1,test)
        myprint("\n \n \n",test)
        if type(action1)==type_pokemon: #si dresseur1 change de poke
            changer_pokemon(dresseur1,action1,test)
            pokemon1=action1
        if type(action2)==type_pokemon:#si dresseur2 change de poke
            changer_pokemon(dresseur2,action2,test)
            pokemon2=action2
        if type(action1)==type_competence: #si dresseur1 attaque
            if type(action2)==type_competence: #si les 2 actions sont des attaques
                if action1.priorite>action2.priorite or (action1.priorite==action2.priorite and pokemon1.vitesse_modifiee+rd.uniform(-.01,.01)>pokemon2.vitesse_modifiee): #Si Pokemon1 attaque en premier
                    pokemon1.attaquer(pokemon2,action1,test)
                    if verifier_KO(dresseur1,pokemon1,dresseur2,test): #Un Pokemon peut se tuer lui-meme (par exemple confusion)
                        pokemon1=dresseur1.poke_actif
                    if verifier_KO(dresseur2,pokemon2,dresseur1,test):
                        pokemon2=dresseur2.poke_actif
                    elif not verifier_fin_partie(dresseur1,dresseur2,True): #si poke2 pas K.O il attaque
                        pokemon2.attaquer(pokemon1,action2,test)
                        if verifier_KO(dresseur2,pokemon2,dresseur1,test):
                            pokemon2=dresseur2.poke_actif
                        if verifier_KO(dresseur1,pokemon1,dresseur2,test):
                            pokemon1=dresseur1.poke_actif
                else: #Pokemon2 attaque en premier
                    pokemon2.attaquer(pokemon1,action2,test)
                    if verifier_KO(dresseur2,pokemon2,dresseur1,test):
                        pokemon2=dresseur2.poke_actif
                    if verifier_KO(dresseur1,pokemon1,dresseur2,test):
                        pokemon1=dresseur1.poke_actif                    
                    elif not verifier_fin_partie(dresseur1,dresseur2,True):#poke1 attaque si non K.O
                        pokemon1.attaquer(pokemon2,action1,test)
                        if verifier_KO(dresseur1,pokemon1,dresseur2,test):
                            pokemon1=dresseur1.poke_actif
                        if verifier_KO(dresseur2,pokemon2,dresseur1,test):
                            pokemon2=dresseur2.poke_actif
            else:#Si seul poke1 attaque
               pokemon1.attaquer(pokemon2,action1,test)
               if verifier_KO(dresseur1,pokemon1,dresseur2,test):
                   pokemon1=dresseur1.poke_actif
               if verifier_KO(dresseur2,pokemon2,dresseur1,test):
                   pokemon2=dresseur2.poke_actif
        elif type(action2)==type_competence:#si seul poke2 attaque
            pokemon2.attaquer(pokemon1,action2,test)
            if verifier_KO(dresseur2,pokemon2,dresseur1,test):
                pokemon2=dresseur2.poke_actif
            if verifier_KO(dresseur1,pokemon1,dresseur2,test):
                pokemon1=dresseur1.poke_actif
        actualiser_pokemon(dresseur1,pokemon1)
        dresseur1.poke_actif=pokemon1
        actualiser_pokemon(dresseur2,pokemon2)
        dresseur2.poke_actif=pokemon2
        if verifier_fin_partie(dresseur1,dresseur2) and not test:
            return(True)
        else:
            return(False)
                    
        
def actualiser_pokemon(dresseur,pokemon):
    for i in range(len(dresseur.pokemons)):
        if dresseur.pokemons[i].nom==pokemon.nom:
            dresseur.pokemons[i]=pokemon
            

def choisir_action(dresseur,choix1,choix2,adversaire,test=False):
    action=""
    while (action not in ["1","2","0"]) and (type(action) not in [type_competence,type_pokemon]):
        action=myinput("Choisir une action : \n Attaquer : 1 \n Changer de Pokemon : 2 \n Abandonner : 0",choix1)
        if action not in ["1","2","0"]:
            myprint("choisir '1', '2' ou '0'",test)
            choix1=-42 #Ne devrait pas être nécessaire mais évite une boucle infinie s'il y a eu une erreur de codage
        if action=="1":
            action=choisir_attaque(dresseur,choix2,test)
        if action=="2":
            action=choisir_pokemon(dresseur,adversaire,test)
        if action=="0":
            dresseur.perdu=True
    return(action)
                        
                    
def choisir_attaque(dresseur,choix2,test=False):
    attaque=None
    poke_actif=dresseur.poke_actif
    lutte=competence("Lutte",50,100,"autre","physique",0,recul,1000,1000)
    if [poke_actif.competences[i].PPactuels==0 for i in range(4)] == [True]*4:
        attaque=lutte #attaque par défaut si plus de PP pour chaque attaque
    else:
        choix=""
        while choix not in [0,1,2,3,4]:
            choix=myinput("Choisir une competence : \n {0}({1}/{2}): 1 \n {3}({4}/{5}): 2 \n {6}({7}/{8}): 3 \n {9}({10}/{11}): 4 \n Retour : 0".format(poke_actif.competences[0].nom,poke_actif.competences[0].PPactuels,poke_actif.competences[0].PPmax,poke_actif.competences[1].nom,poke_actif.competences[1].PPactuels,poke_actif.competences[1].PPmax,poke_actif.competences[2].nom,poke_actif.competences[2].PPactuels,poke_actif.competences[2].PPmax,poke_actif.competences[3].nom,poke_actif.competences[3].PPactuels,poke_actif.competences[3].PPmax),choix2)
            choix2=-42 #Ne devrait pas être nécessaire mais évite une boucle infinie s'il y a eu une erreur de codage
            if choix not in ["0","1","2","3","4"]:
                myprint("Choisir '0', '1', '2', '3' ou '4'",test)
                choix=""
            else:
                choix=int(choix)
                if choix==0:
                    myprint('Retour',test)
                    return("")
                elif poke_actif.competences[choix-1].PPactuels==0:
                    myprint("Plus de PP pour cette competence.",test)
                    choix="" #retour à la boucle sur competence
                else:
                    attaque=poke_actif.competences[choix-1]
    if attaque:
        return(attaque)
            
def choisir_pokemon(dresseur,adversaire,test=False):
    poke_actif=dresseur.poke_actif
    poke_choisi=""
    poke_arrivant=None
    if dresseur.joueur.strategie_changer_pokemon!=None: #Si ce test est vérifié, le joueur est une IA et elle choisit elle-même le pokemon
        choix=dresseur.joueur.strategie_changer_pokemon(dresseur,adversaire)
    else:
        choix=-42
    while poke_choisi not in [0,1,2,3,4,5,6]:
        poke_choisi=myinput("Choisir un Pokemon : \n {}\n Retour : 0" .format([[dresseur.pokemons[i].nom, dresseur.pokemons[i].PVactuels,dresseur.pokemons[i].PVmax,dresseur.pokemons[i].etat, i+1] for i in range(len(dresseur.pokemons))]),choix)
        choix=-42 #Normalement non nécessaire mais évite une boucle infinie s'il y a une erreur
        if poke_choisi not in ["0","1","2","3","4","5","6"]:
            myprint("Choisir '0', '1', '2', '3', '4', '5' ou '6'",test)
            poke_choisi=""
        else:
            poke_choisi=int(poke_choisi)
            if poke_choisi==0:
                myprint('Retour',test)
                return("")
            elif dresseur.pokemons[poke_choisi-1].PVactuels<=0: #impossible de choisir un pokemon K.O.
                myprint("Pokemon K.O.",test)
                poke_choisi=""
            elif dresseur.pokemons[poke_choisi-1]==poke_actif:#impossible de choisir le pokemon actif
                myprint("Pokemon déjà actif",test)                
                poke_choisi=""
            else:
                poke_arrivant=dresseur.pokemons[poke_choisi-1]
            if poke_arrivant:
                return(poke_arrivant)
                
def changer_pokemon(dresseur,pokemon,test):
    myprint("{} rappelle {} et envoie {}".format(dresseur.nom,dresseur.poke_actif.nom,pokemon.nom),test)
    dresseur.poke_actif.bonus=[0]*7 #réinitialisation des bonus et de la confusion lors d'un changement
    dresseur.poke_actif.confusion=[0,0]
    dresseur.poke_actif=pokemon
    
    
def verifier_KO(dresseur,pokemon,adversaire,test=False): #Teste si un pokemon est K.O., permet de le changer si c'est le cas et renvoie le résultat du test
    if pokemon.etat=="K.O.":
        actualiser_pokemon(dresseur,pokemon)
        if not test:
            if ([poke.etat=="K.O." for poke in dresseur.pokemons]==[True]*len(dresseur.pokemons)):
                    dresseur.perdu=True
            elif not test: #changement s'il reste des poke non K.O et si ce n'est pas un test
                action=""
                while action=="":
                    action=choisir_pokemon(dresseur,adversaire,test)
                changer_pokemon(dresseur,action,test)
        return(True)
    else:
        return(False)

def verifier_fin_partie(dresseur1,dresseur2,test=False): #Vérifie si l'un des joueurs a perdu
    if dresseur1.perdu:
        if dresseur2.perdu:
            myprint("Match nul",test)
        else:
            myprint("{} a perdu".format(dresseur1.nom),test)
    elif dresseur2.perdu:
        myprint("{} a perdu".format(dresseur2.nom),test)
    if dresseur1.perdu or dresseur2.perdu:
        return(True)
    else:
        return(False)
    
#les différents effets spéciaux des attaques

def bruler10(self,pokemon,degats,test=False): # 1 chance sur 10 de bruler
    if pokemon.etat=="":
        if True not in ["feu"==Type for Type in pokemon.types]:          
            if rd.uniform(0,100)<=10:
                pokemon.etat="brule"
                myprint("{} est brule".format(pokemon.nom),test)
                
                
def rendre_confus(self,pokemon,degats,test=False): #rends l'adversaire confus
    if pokemon.confusion==[0,0]:
        pokemon.confusion[0]=rd.randint(2,5)
        myprint("{} est confus".format(pokemon.nom),test)
    else:
        myprint("{} est déjà confus".format(pokemon.nom),test)

def rendre_confus10(self,pokemon,degats,test=False): #1 chance sur 10 de rendre confus
    if rd.uniform(0,100)<=10:
        rendre_confus(self,pokemon,degats,test)

def paralyser(self,pokemon,degats,test=False): #paralyse l'adversaire
    if pokemon.etat=="":                
        pokemon.etat="paralyse"
        myprint("{} est paralysé".format(pokemon.nom),test)
    else:
        myprint("{} est déjà paralysé".format(pokemon.nom),test)

        
def paralyser10(self,pokemon,degats,test=False): #1 chance sur 10 de paralyser l'adversaire
    if rd.uniform(0,100)<=10:
        paralyser(self,pokemon,degats,test)

def paralyser30(self,pokemon,degats,test=False): #3 chances sur 10 de paralyser
    if rd.uniform(0,100)<=30:
        paralyser(self,pokemon,degats,test)

def empoisonner30(self,pokemon,degats,test=False): #3 chances sur 10 d'empoisonner l'adversaire
    if pokemon.etat=="":
        if rd.uniform(0,100)<=30:
            pokemon.etat="empoisonne"
            myprint("{} est empoisonné".format(pokemon.nom),test)

def geler10(self,pokemon,degats,test=False): #1 chance sur 10 de geler l'adversaire
    if pokemon.etat=="":
        if rd.uniform(0,100)<=10:
            pokemon.etat="gele"
            myprint("{} est gelé.".format(pokemon.nom),test)
            
def endormir(self,pokemon,degats,test=False): #endort l'adversaire
    if pokemon.etat=="":
        pokemon.sommeil=[rd.randint(1,7),0]
        pokemon.etat="sommeil"
        myprint("{} s'est endormi".format(pokemon.nom),test)
        
    

def effet_triplattaque(self,pokemon,degats,test=False): #2 chance sur 10 de bruler paralyser ou geler
    if pokemon.etat=="":
        if rd.uniform(0,100)<20:
            p=rd.randint(1,3)
            if p==1:
                pokemon.etat="brule"
                myprint("{} est brulé".format(pokemon.nom),test)
            if p==2:
                pokemon.etat="paralyse"
                myprint("{} est paralysé".format(pokemon.nom),test)
            if p==3:
                pokemon.etat="gele"
                myprint("{} est gelé".format(pokemon.nom),test)
        
def vol_vie(self,pokemon,degats,test=False): #récupère la moitié des dégats infligés
    if degats>0:
        vol=max(int(degats/2),1)
        self.PVactuels=min(self.PVmax,self.PVactuels+vol)
        myprint("{0} draine les PV de {1}. \n {0} a {2} PV".format(self.nom,pokemon.nom,self.PVactuels),test)

def recul(self,pokemon,degats,test=False): #se blesse à la hauteur de 1/4 des dégats infligés
    if degats>0:
        degats_recul=max(int(degats/4),1)
        self.PVactuels=max(self.PVactuels-degats_recul,0)
        myprint("{} se blesse avec le recul. \n Il a {} PV".format(self.nom,self.PVactuels),test)

def autodestruction(self,pokemon,degats,test=False): #se mettre K.O. soi-même
    self.PVactuels=0
    self.etat="K.O."
    myprint("{} s'est auto-détruit.".format(self.nom),test)

def attaque_et_attaque_speciale_augmentees(self,pokemon,degats,test=False): 
    if self.bonus[0]<6:
        self.bonus[0]+=1
        myprint("L'attaque de {} a augmenté.".format(self.nom),test)
    else:
        myprint("L'attaque de {} est déjà au maximum.".format(self.nom),test)
    if self.bonus[2]<6:
        self.bonus[2]+=1
        myprint("L'attaque spéciale de {} a augmenté.".format(self.nom),test)
    else:
        myprint("L'attaque spéciale de {} est déjà au maximum.".format(self.nom),test)

def attaque_speciale_augmentee(self,pokemon,degats,test=False):
    if self.bonus[2]<6:
        self.bonus[2]+=1
        myprint("L'attaque spéciale de {} a augmenté.".format(self.nom),test)
    else:
        myprint("L'attaque spéciale de {} est déjà au maximum.".foramt(self.nom),test)

def attaque_augmentee2(self,pokemon,degats,test=False): #augmente l'attaque de 2 niveaux
    if self.bonus[0]<6:
        self.bonus[0]=min(self.bonus[0]+2,6)
        myprint("L'attaque de {} a fortement augmenté.".format(self.nom),test)
    else:
        myprint("L'attaque de {} est déjà au maximum.".format(self.nom),test)

def effet_papillodanse(self,pokemon,degats,test=False): #augmente attaque/defense spéciales et vitesse
    if self.bonus[2]<6:
        self.bonus[2]+=1
        myprint("L'attaque spéciale de {} a augmenté.".format(self.nom),test)
    else:
        myprint("L'attaque spéciale de {} est déjà au maximum.".format(self.nom),test)
    if self.bonus[3]<6:
        self.bonus[3]+=1
        myprint("La défense spéciale de {} a augmenté.".format(self.nom),test)
    else:
        myprint("La défense spéciale de {} est déjà au maximum.".format(self.nom),test)
    if self.bonus[4]<6:
        self.bonus[4]+=1
        myprint("La vitesse de {} a augmenté.".format(self.nom),test)
    else:
        myprint("La vitesse de {} est déjà au maximum.".format(self.nom),test)
        
def baisser_defense_speciale10(self,pokemon,degats,test=False): # 1 chance sur 10 de baisser def speciale
    if pokemon.bonus[3]>-6 and rd.uniform(0,100)<=10:
        pokemon.bonus[3]-=1
        myprint("La défense spéciale de {} a baissé.".format(pokemon.nom),test)

def effet_repos(self,pokemon,degats,test=False): #s'endort et restaure PV
    if self.PVactuels<self.PVmax:
        self.PVactuels=self.PVmax
        self.sommeil=[3,0,"repos"] #l'attaque repos fait toujours dormir le meme nb de tours
        self.etat="sommeil"
        myprint("{} s'endort.".format(self.nom),test)

def effet_blabla_dodo(self,pokemon,degats,test=False): #fait une attaque aléatoire si endormit
    if self.etat=="sommeil":
        ok=False
        while not ok:
            i=rd.randint(0,3)
            if self.competences[i].nom!="Blabla dodo":
                ok=True
        etat_sommeil=self.sommeil
        self.sommeil=[0,0]
        self.etat=""
        self.competences[i].PPactuels+=1
        self.attaquer(pokemon,self.competences[i],test)
        self.sommeil=etat_sommeil
        self.etat="sommeil"
    else:
        myprint("Blabla dodo ne fonctionne qu'une fois endormi",test)


#définition du type "pokemon" et "competence" pour faire des tests
stats_gravalanche=[251,203,239,113,113,95]
deflagration=competence("Deflagration",110,85,"feu","physique",0,bruler10,5,5)
type_pokemon=type(pokemon("Gravalanche",stats_gravalanche,251,[deflagration],["roche","sol"],100,"",[-2,2,1,1,0,-3,2],[],[0,0],[0,0]))
type_competence=type(deflagration)



#definition des différentes compétences

hydrocanon=competence("Hydrocanon",120,80,"eau","speciale",0,None,5,5)
onde_folie=competence("Onde folie",0,100,"spectre","speciale",0,rendre_confus,10,10)
deflagration=competence("Deflagration",110,85,"feu","physique",0,bruler10,5,5)
fatal_foudre=competence("Fatal Foudre",120,70,"electrik","speciale",0,paralyser10,5,5)
vive_attaque=competence("Vive-Attaque",40,100,"normal","physique",1,None,30,30)
triplattaque=competence("Triplattaque",80,100,"normal","speciale",0,effet_triplattaque,10,10)
giga_sangsue=competence("Giga-Sangsue",75,100,"plante","speciale",0,vol_vie,10,10)
belier=competence("Bélier",90,85,"normal","physique",0,recul,20,20)
poudre_dodo=competence("Poudre dodo",0,75,"plante","speciale",0,endormir,15,15)
bomb_beurk=competence("Bomb-beurk",90,100,"poison","physique",0,empoisonner30,10,10)
croissance=competence("Croissance",0,1000000,"normal","physique",0,attaque_et_attaque_speciale_augmentees,40,40)
laser_glace=competence("Laser glace",90,100,"glace","speciale",0,geler10,10,10)
surf=competence("Surf",95,100,"eau","speciale",0,None,15,15)
luminocanon=competence("Luminocanon",80,100,"acier","speciale",0,baisser_defense_speciale10,10,10)
aeropique=competence("Aeropique",60,1000000,"vol","physique",0,None,20,20)#Aeropique a normalemen une précision infinie
lance_flamme=competence("Lance flamme",90,100,"feu","speciale",0,bruler10,15,15)
danse_lames=competence("Danse-lames",0,1000000,"normal","physique",0,attaque_augmentee2,20,20)
papillodanse=competence("Papillodanse",0,1000000,"insecte","physique",0,effet_papillodanse,20,20)
bourdon=competence("Bourdon",90,100,"insecte","speciale",0,baisser_defense_speciale10,10,10)
rafale_psy=competence("Rafale psy",65,100,"psy","speciale",0,rendre_confus10,20,20)
ball_ombre=competence("Ball'Ombre",80,100,"spectre","speciale",0,baisser_defense_speciale10,15,15)
psyko=competence("Psyko",90,100,"psy","speciale",0,baisser_defense_speciale10,10,10)
cage_eclair=competence("Cage-éclair",0,100,"electrik","speciale",0,paralyser,20,20)
explosion=competence("Explosion",250,100,"normal","physique",0,autodestruction,5,5)
rayon_charge=competence("Rayon Chargé",50,90,"electrik","speciale",0,attaque_speciale_augmentee,10,10)
repos=competence("Repos",0,1000000,"psy","physique",0,effet_repos,10,10)
blabla_dodo=competence("Blabla dodo",0,1000000,"normal","physique",0,effet_blabla_dodo,10,10)
seisme=competence("Séisme",100,100,"sol","physique",0,None,10,10)
plaquage=competence("Plaquage",85,100,"normal","physique",0,paralyser30,15,15)

lutte=competence("Lutte",50,100,"autre","physique",0,recul,-1,1000)


#définition des différents pokémons

stats_ronflex=[461,230,149,149,230,86]
competences_ronflex=[copy.copy(plaquage),copy.copy(blabla_dodo),copy.copy(repos),copy.copy(seisme)]
ronflex=pokemon("Ronflex",stats_ronflex,461,competences_ronflex,["normal"],100,"",[0]*7,[],[0,0],[0,0])

stats_florizarre=[301,180,181,212,212,176]  
competences_florizarre=[copy.copy(bomb_beurk),copy.copy(giga_sangsue),copy.copy(poudre_dodo),copy.copy(croissance)]      
florizarre=pokemon("Florizarre",stats_florizarre,301,competences_florizarre,["plante","poison"],100,"",[0]*7,[],[0,0],[0,0])    

stats_tortank=[299,181,212,185,221,172]
competences_tortank=[copy.copy(hydrocanon),copy.copy(surf),copy.copy(luminocanon),copy.copy(laser_glace)]
tortank=pokemon("Tortank",stats_tortank,299,competences_tortank,["eau"],100,"",[0]*7,[],[0,0],[0,0])

stats_dracaufeu=[297,183,172,228,185,212]
competences_dracaufeu=[copy.copy(deflagration),copy.copy(danse_lames),copy.copy(lance_flamme),copy.copy(aeropique)]
dracaufeu=pokemon("Dracaufeu",stats_dracaufeu,297,competences_dracaufeu,["feu","vol"],100,"",[0]*7,[],[0,0],[0,0])

stats_papilusion=[261,113,122,176,176,158]
competences_papilusion=[copy.copy(papillodanse),copy.copy(bourdon),copy.copy(rafale_psy),copy.copy(aeropique)]
papilusion=pokemon("Papilusion",stats_papilusion,261,competences_papilusion,["insecte","vol"],100,"",[0]*7,[],[0,0],[0,0])

stats_ectoplasma=[261,149,140,266,167,230]
competences_ectoplasma=[copy.copy(ball_ombre),copy.copy(psyko),copy.copy(onde_folie),copy.copy(bomb_beurk)]
ectoplasma=pokemon("Ectoplasma",stats_ectoplasma,261,competences_ectoplasma,["spectre","poison"],100,"",[0]*7,[],[0,0],[0,0])

stats_electrode=[261,122,158,176,176,284]
competences_electrode=[copy.copy(fatal_foudre),copy.copy(explosion),copy.copy(cage_eclair),copy.copy(rayon_charge)]
electrode=pokemon("Electrode",stats_electrode,261,competences_electrode,["electrik"],100,"",[0]*7,[],[0,0],[0,0])

liste_pokemons=[ronflex,florizarre,tortank,dracaufeu,papilusion,ectoplasma,electrode]



def choisir_joueur(i,choix1="",choix2=""): #choisir le type de joueur avant de commencer une partie
    choix=""
    while choix not in ['1','2','0']:
        choix=myinput("Choisir joueur {} : \n 1 : joueur humain \n 2 : IA \n 0 : Quitter le jeu".format(i),choix1)
        choix1=-42
        if choix not in ['1','2','0']:
            print("Choisir '1', '2' ou '0'")
        else:
            if choix=='1': #joueur humain
                Dresseur=dresseur("Dresseur",None,None,humain)
            if choix=='2': #IA
                choix_IA=""
                while choix_IA not in ['1','2','0']: #Choisir le type d'IA
                    choix_IA=myinput("Choisir l'IA : \n 1: IA niveau 1 \n 2:IA random \n 0 : retour",choix2)
                    choix2=-42
                    if choix_IA=='1':
                        Dresseur=dresseur("Dresseur",[],None,IA_MiniMax_1)
                    elif choix_IA=='2':
                        Dresseur=dresseur("Dresseur",[],None,IA_random)
                    elif choix_IA=='0':
                        choix=""
            if choix=='0':
                Dresseur=""
    return(Dresseur)
                        
def choisir_pokemons(dresseur,liste_pokemons,choix=[-42]*6): #choisir les pokemons avec lesquels on va combattre
    K=0
    dresseur.pokemons=[]
    while K<6: #on choisit 6 pokemons
        poke_choisi=""
        poke_choisi=myinput("Choisir un Pokemon : \n {}" .format([[liste_pokemons[i].nom, liste_pokemons[i].PVactuels,liste_pokemons[i].PVmax, i+1] for i in range(len(liste_pokemons))]),choix[K])
        choix[K]=-42
        poke_choisi=int(poke_choisi)
        if poke_choisi in range(1,len(liste_pokemons)+1):
            if liste_pokemons[poke_choisi-1] not in dresseur.pokemons:
                poke_choisi=liste_pokemons[poke_choisi-1]
                dresseur.pokemons.append(copy.deepcopy(poke_choisi))
                print("{} ajouté.".format(poke_choisi.nom))
                K+=1
            else:
                print("Ce pokemon est déjà choisi.")
        else:
            print("Choisir un nombre entre 1 et {}.".format(len(liste_pokemons)))
    return(dresseur.pokemons)
    
def choisir_poke_actif(dresseur,choix=-42): #Choisir le 1er pokemon qui va combattre
    if dresseur.joueur==humain:
        poke_choisi=""
        while poke_choisi=="":
            poke_choisi=myinput("Choisir le Pokemon actif : \n {}" .format([[dresseur.pokemons[i].nom, dresseur.pokemons[i].PVactuels,dresseur.pokemons[i].PVmax, i+1] for i in range(len(dresseur.pokemons))]),choix)
            choix=-42
            poke_choisi=int(poke_choisi)
            if poke_choisi in range(1,7):
                dresseur.poke_actif=dresseur.pokemons[poke_choisi-1]
            else:
                print("Choisir '1', '2', '3', '4', '5' ou '6'")
    else:
        dresseur.poke_actif=dresseur.pokemons[rd.randint(0,5)] #l'IA choisit aléatoirement
        
                        
def commencer_partie(choix11="",choix12="",choix_pokemons1=[-42]*6,choix21="",choix22="",choix_pokemons2=[-42]*6,meme_poke=-42):
    dresseur1=choisir_joueur(1,choix11,choix12) #choisir le type de joueur pour le joueur 1
    if dresseur1=="": #si on a choisit "Quitter le jeu"
        return()
    dresseur1.nom+='1' #permet de différencier le nom des dresseurs
    meme_poke=myinput("Choisir les mêmes pokemons pour les 2 dresseurs? \n Oui : 1 \n Non : 2",meme_poke) #choisir si les 2 dresseurs auront les memes pokemons
    dresseur1.pokemons=choisir_pokemons(dresseur,liste_pokemons,choix_pokemons1) #choix des pokemons
    dresseur2=choisir_joueur(2,choix21,choix22) #choisir le type de joueur pour le joueur 2
    if dresseur2=="":
        return()
    dresseur2.nom+='2'
    if meme_poke=='1': 
        dresseur2.pokemons=copy.deepcopy(dresseur1.pokemons)
    else:
        choisir_pokemons(dresseur2,liste_pokemons,choix_pokemons2)
    for i in range(6):
        dresseur1.pokemons[i].nom+='1' #permet de différencier le nom des pokemons
        dresseur2.pokemons[i].nom+='2'
    choisir_poke_actif(dresseur1) #choisir le premier pokemon qui va combattre
    choisir_poke_actif(dresseur2)
    fin_partie=False
    while not fin_partie:
        fin_partie=tour(dresseur1,dresseur2,False) #faire un tour tant que la partie n'est pas finie
    return([dresseur1.perdu,dresseur2.perdu])
    
    
#commencer_partie()    
#commencer_partie("1","1",["1","2","3","4","5","6"],2,1,[-42]*6,"1")

def tester_IA(n=20): #permet de tester l'IA_MiniMax_1 contre l'IA_random sur n matchs
    SCORE=[0,0]
    for i in range(n):
        print(i)
        resultat=commencer_partie("2","1",["1","2","3","4","5","6"],2,2,[-42]*6,"1")
        SCORE[0]+=resultat[0]
        SCORE[1]+=resultat[1]
    print(SCORE)
    return(SCORE) #renvoie dans l'ordre le nb de défaites de IA_MiniMax_1 et le nb de défaites de IA_random (si somme suppérieure à n il y a eu match nul)
        
#tester_IA()    


def optimisation_parametres(tour_opti=20,n=10,nb_matchs=9,score_KO=-.5,coeff_bonus=1.5,coeff_etat=.4,coeff_confusion=.3):
    global IA_MiniMax_1
    global IA_random
    COPIE1=copy.deepcopy(IA_MiniMax_1)
    COPIE2=copy.deepcopy(IA_random)
    coeffs1=[score_KO,coeff_bonus,coeff_etat,coeff_confusion] #paramètres definissant la fonction score de l'IA
    memoire_coeffs=[0]*tour_opti
    for i in range(tour_opti):
        print("Tour d'optimisation numéro {}".format(i+1))
        coeffs2=copy.copy(coeffs1)
        for j in range(4):
            coeffs2[j]+=rd.uniform(-.1,.1) #modification aléatoire des parametres
            
        def score1(pokemon): #fonction de score pour l'IA 1
            return(score(pokemon,coeffs1[0],coeffs1[1],coeffs1[2],coeffs1[3]))
        
        def strategie_1(dresseur,adversaire): #fonction de strategie pour l'IA 1
            return(strategie_IA_MiniMax_1(dresseur,adversaire,n,score1))
        
        def changer_pokemon1(dresseur,adversaire): #fonction de changement de pokemon pour l'IA 1
            return(strategie_changer_pokemon_IA_MiniMax_1(dresseur,adversaire,n,score1))
            
        
        def score2(pokemon): #fonction de score pour l'IA 2
            return(score(pokemon,coeffs2[0],coeffs2[1],coeffs2[2],coeffs2[3]))
            
        def strategie_2(dresseur,adversaire):
            return(strategie_IA_MiniMax_1(dresseur,adversaire,n,score2))
        
        def changer_pokemon2(dresseur,adversaire):
            return(strategie_changer_pokemon_IA_MiniMax_1(dresseur,adversaire,n,score2))
        
        IA_MiniMax_1.strategie_competence=strategie_1
        IA_MiniMax_1.strategie_changer_pokemon=changer_pokemon1
        IA_random.strategie_competence=strategie_2 # attention ce n'est pas une IA aléatoire mais cela permet de reprendre la fonction tester_IA sans changements
        IA_random.strategie_changer_pokemon=changer_pokemon2
        resultats=tester_IA(nb_matchs)
        if resultats[0]>resultats[1]:
            coeffs1=copy.copy(coeffs2) #conservations des coeffs de l'IA qui a gagné le plus souvent
        memoire_coeffs[i]=copy.copy(coeffs1)
    IA_MiniMax_1=copy.deepcopy(COPIE1)
    IA_random=copy.deepcopy(COPIE2)
    print(coeffs1)
    print(memoire_coeffs)
    return(memoire_coeffs)
    
#parametres=optimisation_parametres()
    
#[-0.8006110698082329, 1.3300638680915746, 0.061818715181948744, 0.16454866255039424]        
        
        
        
                
            
        
    
    
    
    
    
    

def test1(): #test de 2 tours
    stats_gravalanche=[251,203,239,113,113,95]
    stats_tortank=[299,181,212,185,221,172]
    hydrocanon=competence("Hydrocanon",120,80,"eau","speciale",0,None,5,5)
    onde_folie=competence("Onde folie",0,100,"spectre","speciale",0,rendre_confus,10,10)
    deflagration=competence("Deflagration",110,85,"feu","physique",0,bruler10,5,5)
    fatal_foudre=competence("Fatal Foudre",120,70,"electrik","speciale",0,paralyser10,5,5)
    vive_attaque=competence("Vive-Attaque",40,100,"normal","physique",1,None,30,30)
    triplattaque=competence("Triplattaque",80,100,"normal","speciale",0,effet_triplattaque,10,10)
    giga_sangsue=competence("Giga-Sangsue",75,100,"plante","speciale",0,vol_vie,10,10)
    lutte=competence("Lutte",50,100,"autre","physique",0,recul,-1,1000)
    gravalanche=pokemon("Gravalanche",stats_gravalanche,251,[deflagration],["roche","sol"],100,"",[-2,2,1,1,0,-3,2],[],[0,0],[0,0])
    tortank=pokemon("Tortank",stats_tortank,299,[hydrocanon],["eau"],100,"",[0]*7,[],[0,0],[0,0]) #[-2,-2,1,1,0,-3,2], [0]*7
    pokemons1=[pokemon("Tortank",stats_tortank,299,[copy.copy(hydrocanon),copy.copy(fatal_foudre),copy.copy(vive_attaque),copy.copy(onde_folie)],["eau"],100,"",[0]*7,[],[0,0],[0,0]),pokemon("Gravalanche",stats_gravalanche,251,[copy.copy(deflagration),copy.copy(triplattaque),copy.copy(giga_sangsue),copy.copy(onde_folie)],["roche","sol"],100,"",[-2,2,1,1,0,-3,2],[],[0,0],[0,0])]
    pokemons2=[pokemon("Tortank2",stats_tortank,299,[copy.copy(hydrocanon),copy.copy(fatal_foudre),copy.copy(vive_attaque),copy.copy(onde_folie)],["eau"],100,"",[0]*7,[],[0,0],[0,0]),pokemon("Gravalanche2",stats_gravalanche,251,[copy.copy(deflagration),copy.copy(triplattaque),copy.copy(giga_sangsue),copy.copy(onde_folie)],["roche","sol"],100,"",[-2,2,1,1,0,-3,2],[],[0,0],[0,0])]
    dresseur1=dresseur("Dresseur1",pokemons1,pokemons1[0],humain)
    dresseur2=dresseur("Dresseur2",pokemons2,pokemons2[1],humain)
    #dresseur2.joueur=humain
    tour(dresseur1,dresseur2)
    tour(dresseur1,dresseur2)
    #copydresseur1=copy.copy(dresseur1)
    #deepcopydresseur1=copy.deepcopy(dresseur1)
    #dresseur1.pokemons[0].PVactuels-=10
    #copydresseur1.pokemons[0].PVactuels-=10
    #deepcopydresseur1.pokemons[0].PVactuels-=10
    #print([dresseur1.pokemons[0].PVactuels,copydresseur1.pokemons[0].PVactuels,deepcopydresseur1.pokemons[0].PVactuels])
#test1()



def test2(): #test sur le copiage d'une competence
    hydrocanon=competence("Hydrocanon",120,80,"eau","speciale",0,None,5,5)
    attaques=[copy.copy(hydrocanon),copy.copy(hydrocanon)]
    attaques[0].PPactuels-=1
    return(attaques[0]==attaques[1])


#test2()


def test3(): #test sur le dynamisme des stats d'un pokemon (résultat : j'ai fait la fonction actualiser_stats)
    stats_tortank=[299,181,212,185,221,172]
    hydrocanon=competence("Hydrocanon",120,80,"eau","speciale",0,None,5,5)
    tortank=pokemon("Tortank",stats_tortank,299,[hydrocanon],["eau"],100,"",[-1]*7,[],0,0)
    print(tortank.vitesse_modifiee)
    tortank.bonus=[-2]*7
    print(tortank.vitesse_modifiee)
    tortank2=pokemon("Tortank2",stats_tortank,299,[hydrocanon],["eau"],100,"",[-2]*7,[],0,0)
    print(tortank2.vitesse_modifiee)
    
#test3()

def test4(): #test de fonction retournant une fonction
    def f(x):
        def g(n):
            return(n*x)
        return(g)
    g=f(2)
    h=g(3)
    print(h)

#test4()

def test5():
    action=myinput("test",3)
    print(action)
    print(type(action))
    action2=input("test2")
    print(action2)
    print(type(action2))

#test5()

