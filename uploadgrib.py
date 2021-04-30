#!/bin/env_vr python3.7.5
# coding: utf-8

#le debut de chargement des gribs intervient en heure UTC à
# 9h30(gfs06) - 15h30(gfs12) -  21h30(gfs18) - 03h30 (gfs00)
# en heure d'hiver
# 10h30(gfs06) - 16h30(gfs12) -  22h30(gfs18) - 04h30 (gfs00)

# les gribs complets sont disponibles en heure UTC à
# 11h(gfs06) - 17(gfs12) -  23(gfs18) - 05 h (gfs00)
# les gribs complets sont disponibles en heure d'hiver à
# 12h(gfs06) - 18(gfs12) -  00(gfs18) - 06 h (gfs00)
# les gribs complets sont disponibles en heure d'ete à
# 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)
import os
import time
import math
import numpy as np
from urllib.request import urlretrieve
from urllib.error import HTTPError
import xarray as xr
import h5py
from datetime import datetime
from scipy.interpolate import RegularGridInterpolator
from pathlib import Path
import requests
from fonctions2021 import *


tic=time.time()
ticstruct = time.localtime()
utc = time.gmtime()
decalage = ticstruct[3] - utc[3]
leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
# constitution d'un nom de fichier
basedir = os.path.abspath(os.path.dirname(__file__))
# ix = np.arange(129)  # temps
# iy = np.arange(181)  # latitudes
# iz = np.arange(361)  # longitudes

iprev = []                 
for a in range(0, 387, 3):                              # Construit le tuple des indexs des fichiers maxi 387
    iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
# recherche du dernier grib disponible
# # *************************************************************************************
# avec tic 
date_tuple           = time.gmtime(tic)             # transformation en tuple utc
date_formatcourt     = time.strftime("%Y%m%d", time.gmtime(tic))
dateveille_tuple     = time.gmtime(tic-86400) 
dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(tic-86400))



# # *************************************************************************************
# pour faire differents essais qui ne soient pas basés  sur le tic
# ces lignes pourront simplement etre commentees en final
datejour         = datetime(2021,1,17, 12,30,0)                  # en heures locales
dateessai_sec    = time.mktime(datejour.timetuple()) # c'est l'equivalent du tic
date_tuple       = time.gmtime(dateessai_sec) 
date_formatcourt = time.strftime("%Y%m%d", time.gmtime(dateessai_sec))
dateveille_tuple = time.gmtime(dateessai_sec-86400) 
dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(dateessai_sec-86400))

# print (date_tuple)
# print(date_formatcourt)
# print (dateveille_formatcourt_utc)
# print(dateveille_tuple)
#*****************************************************************************************




def file_names():
    ''' cherche le dernier grib complet disponible au temps en secondes '''
    ''' temps_secondes est par defaut le temps instantané '''
    ''' Cherche egalement le dernier grib chargeable partiellement'''
    temps_secondes=tic
    date_tuple       = time.gmtime(temps_secondes) 
    date_formatcourt = time.strftime("%Y%m%d", time.gmtime(temps_secondes))
    dateveille_tuple = time.gmtime(temps_secondes-86400) 
    dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(temps_secondes-86400))
    mn_jour_utc =date_tuple[3]*60+date_tuple[4]

    if (mn_jour_utc <310):
        filename384_c="/home/jphe/gribs/gfs_"+dateveille_formatcourt+"-18.hdf5"
        tig384=time.mktime(datetime(dateveille_tuple[0],dateveille_tuple[1],dateveille_tuple[2],18,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<670):   
        filename384_c="/home/jphe/gribs/gfs_"+date_formatcourt+"-00.hdf5"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],0,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1030): 
        filename384_c="/home/jphe/gribs/gfs_"+date_formatcourt+"-06.hdf5"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],6,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1390):   
        filename384_c="/home/jphe/gribs/gfs_"+date_formatcourt+"-12.hdf5"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],12,0,0).timetuple())+decalage*3600
    else:    
        filename384_c="/home/jphe/gribs/gfs_"+date_formatcourt+"-18.hdf5"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],18,0,0).timetuple())+decalage*3600

    #filename384 = os.path.join(basedir,filename384_c) 
    filename384 = filename384_c 
    date  = time.strftime("%Y%m%d", time.gmtime(tig384 +21600))
    heure = time.strftime("%H", time.gmtime(tig384+21600))
    filename_c="/home/jphe/gribs/gfs_"+date+"-"+heure+".hdf5"
    #filename = os.path.join(basedir,filename_c) 
    filename=filename_c
    tig =tig384+21600

    #print('delta temps',temps_secondes-tig384)
    if temps_secondes-tig384> 34500 :
        print ('Fichier partiel  {} '.format(filename))
        status='chargeable'
    else: 
        #print ('Le fichier partiel  {} n est pas encore disponible '.format(filename) ) 
        status='nonchargeable'

    # renvoie le nom du fichier complet384 disponible et son tig384, le nom du fichier suivant et son tig et son statut chargeable ou non chargeable  
    #print ('tig384  dans filenames',time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig384)))
    return filename384,tig384,filename,tig,status  



def chargement_384():
    '''Charge le fichier  complet 384 existant'''
    #print('\nNom des fichiers\n',file_names())
    filename384,tig384,filename,tig,status=file_names()
    date  = time.strftime("%Y%m%d", time.gmtime(tig384 ))
    heure = time.strftime("%H", time.gmtime(tig384))
    GR = np.zeros((len(iprev), 181, 360), dtype=complex)    # initialise le np array de complexes qui recoit les donnees  
    #print ('149 tig384  dans chargement 3842',time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig384)))
    if os.path.exists(filename384) == False:                   #si ce fichier n'existe pas deja
             
        for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + heure + "z.pgrb2.1p00.f" + \
                prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + heure+"%2Fatmos"

            nom_fichier = "grib_" + date + "_" + heure + "_" + prev   # nom sous lequel le  fichier est sauvegarde provisoirement
            try:       
                urlretrieve(url, nom_fichier)   
                # exploitation du fichier et mise en memoire dans GR
                ds = xr.open_dataset(nom_fichier, engine='cfgrib')
                GR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
                os.remove(nom_fichier)                  # On efface le fichier pour ne pas encombrer
                residuel=nom_fichier + '.90c91.idx'
                if os.path.exists(residuel) == True: 
                    os.remove(residuel)   # On efface le fichier residuel

                residuel=nom_fichier + '.4cc40.idx'
                if os.path.exists(residuel) == True: 
                    os.remove(residuel)   # On efface le fichier residuel    
               
                date_p_s=time.strftime("%d %b %Hh", time.gmtime(tig384+indexprev*3*3600))
                print(' Enregistrement  384  {}-{} + {} heures soit {} '.format(date,heure,prev,date_p_s))  # destine a suivre le chargement des previsions
            except HTTPError :
                print ('La Prévisionx {} est non disponible '.format(prev) )
        indice384=indexprev 
        GR=np.concatenate((GR,GR[:,:,0:1]), axis=2)   #mise en place de la prevision longitude 360 =0
        # on sauvegarde 
        f1 = h5py.File(filename384, "w")
        dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
        dset1.attrs['time_grib'] = tig384      # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
        dset1.attrs['dernier_a_jour']=indice384   # Le grib est completement a jour 
        f1.close()
    else :  # on le charge 
        #print ('Chargement du fichier deja existant {}'.format(filename384))
        f2 = h5py.File(filename384, 'r')
        dset1 = f2['dataset_01']
        GR = dset1[:]
        tig384 = dset1.attrs['time_grib']
        #print ('l 184 tig384  dans filenames',time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig384)))
        indice384=dset1.attrs['dernier_a_jour']
        f2.close()   
    return tig384,GR,filename384,indice384   


def chargement_grib():
    '''Cherche s'il existe un grib avec des previsions plus recentes que l on peut charger  '''   
    filename384,tig384,filename,tig,status=file_names()
    if os.path.exists(filename384) == False:
        chargement_384() 

    date  = time.strftime("%Y%m%d", time.gmtime(tig ))
    strhour = time.strftime("%H", time.gmtime(tig))

    if status=='chargeable':  # on peut charger un nouveau fichier
        print('\tOn peut charger de nouvelles previsions')
        # on commence par charger l'ancien pour pouvoir s'en servir pour completer
        f2 = h5py.File(filename384, 'r')
        dset1 = f2['dataset_01']
        GR = dset1[:]
        GR= GR[:,:,:-1] # on  supprime la colonne 360 qui avait ete rajoutee        
        tig = dset1.attrs['time_grib']
        indice=dset1.attrs['dernier_a_jour']
        f2.close() 

        if os.path.exists(filename) == True:            #si ce nouveau fichier existe deja
            # on le charge pour recuperer l'indice de depart
            f2 = h5py.File(filename, 'r')
            dset1 = f2['dataset_01']
            GRN = dset1[:]
            GRN= GRN[:,:,:-1] # on  supprime la colonne 360 qui avait ete rajoutee 
            tign = dset1.attrs['time_grib']
            indice=dset1.attrs['dernier_a_jour']
            #print ('215 dernier indice a jour',indice )
            f2.close() 
        else :
            GRN = np.zeros((len(iprev), 181, 360), dtype=complex)    # initialise le np array de complexes qui recevra les donnees  
            tign=tig+21600
            indice=-1
        # on peut commencer le chargement a l'indice suivant ou a l'indice 0 s il n'y avait rien de charge

        test='Debut'
        indexprev=indice+1                                       # On commence a tester le chargement au nouvel indice
        while test!='fin' and indexprev<len(iprev):
            prev = iprev[indexprev]
            #print ('227 dernier indice a jour',indexprev )
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour+"%2Fatmos"

            nom_fichier = "grib_" + date + "_" + strhour + "_" + prev   # nom sous lequel le  fichier est sauvegarde provisoirement

            try:       
                urlretrieve(url, nom_fichier)
                ds = xr.open_dataset(nom_fichier, engine='cfgrib')
                GRN[indexprev ] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
                os.remove(nom_fichier) 
                                 # On efface le fichier pour ne pas encombrer
                residuel=nom_fichier + '.90c91.idx'
                if os.path.exists(residuel) == True: 
                    os.remove(residuel)   # On efface le fichier residuel
                residuel=nom_fichier + '.4cc40.idx'
                if os.path.exists(residuel) == True: 
                    os.remove(residuel)   # On efface le fichier residuel
                print ("\tPrevision  +{}h chargée dans nouveau grib {} ".format(prev,time.strftime("%Y%m%d %H", time.gmtime(tign )) ) )
                #print ('243 dernier indice a jour',indexprev )
                indice=indexprev
            except HTTPError :
                test='fin'
                if indexprev==0:     #  arrive seulement dans le cas d un probleme NOAA chargement impossible 
                    print("\tLe nouveau grib n'est pas encore  disponible")
                else :    # on complete GRN avec les valeurs de GR entre indexprev et 126 (378 )
                   # print ('249 dernier indice a jour',indexprev )
                    GRN[(indexprev):127,:,:]=np.copy(GR[(indexprev+2):129,:,:])   # on fait une copie et non une vue nb le 127 n'est pas copié
                    GRN[-2:,:,:]=GRN[-3,:,:]       # comme il manque dans GR les valeurs des deux derniers on copie -3 dans -2 et -1 
                    indice=indexprev-1    # la derniere prevision indexprev a ete un echec
                    print ('\tPrevisions completees par les valeurs de lancien grib de +{}h à +{}h'.format(iprev[indexprev],126*3) )
            indexprev+=1         
        # maintenant on peut sauver GRN 
        GRN=np.concatenate((GRN,GRN[:,:,0:1]), axis=2)   #mise en place de la prevision longitude 360 = longitude 0
        #print ('257 dernier indice a jour',indexprev )
        #print ('258 dernier indice a jour',indice )
        f1 = h5py.File(filename, "w")
        dset1 = f1.create_dataset("dataset_01", GRN.shape, dtype='complex', data=GRN)
        dset1.attrs['time_grib'] = tign      # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
        dset1.attrs['dernier_a_jour']=indice   # Le grib est completement a jour  l'indice est enregistre dans le fichier filename
        f1.close() 
        # on retourne les valeurs  
        tig=tign
        GR=GRN         # a priori c'est une vue  ?

    else:
        print('Le dernier fichier disponible est {}'.format(filename384))   
        tig,GR,filename,indice=chargement_384()
    effacement_moins2jours(tig)
    return tig,GR,filename,indice


def chargement():
    '''charge uniquement le dernier fichier mais ne le met pas a jour (tache realisee par cron)'''
    filename384,tig384,filename,tig,status=file_names()
    print ('filename384',filename384)
    print ('filename',filename)


    if os.path.exists(filename) == True:     # si le fichier existe on le charge direct
        f2 = h5py.File(filename, 'r')
        dset1 = f2['dataset_01']
        GR = dset1[:]
        tig = dset1.attrs['time_grib']
        indice=dset1.attrs['dernier_a_jour']
        f2.close() 
    elif os.path.exists(filename384) == True:     # sinon on prend le 384:  
        f2 = h5py.File(filename384, 'r')
        dset1 = f2['dataset_01']
        GR = dset1[:]
        tig = dset1.attrs['time_grib']
        indice=dset1.attrs['dernier_a_jour']
        filename=filename384
        f2.close() 
        
    else:    
        tig,GR,filename,indice=chargement_grib()    # sinon mais cela ne devrait pas se produire , on charge 
    
    return    tig,GR,filename,indice 




def effacement_moins2jours(tig):
    '''efface le grib de 2jours en arriere '''
    #nom du grib
    date  = time.strftime("%Y%m%d", time.gmtime(tig-(3600*24*2)))
    heure = time.strftime("%H", time.gmtime(tig-(3600*24*2)))
    nom="gribs/gfs_"+date+"-"+heure+".hdf5"
    filename = os.path.join(basedir,nom)
    if os.path.exists(filename) == True:
        os.remove(filename)
        #print('fichier effacé ',filename)
    return None 



if __name__ == '__main__':
    temps_secondes=tic
    tic_formate=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    #jeu de valeurs pour prevision 
    latitude='050-00-00-N'
    longitude='003-00-00-W'
    d = chaine_to_dec(latitude, longitude)  
    dateprev       =datetime(2021,4,20,10, 0,  0)
    dateprev_s=time.mktime(dateprev.timetuple()) # en secondes locales
    dateprev_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(dateprev_s))

    # ici on met la date de prevision en instantané
    dateprev_s=tic
    dateprev_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(dateprev_s))


    print ('\nPrevision uploadgrib dans routeur2021 le {} \
           \n****************************************************************'.format(tic_formate))
    tig,GR,filename,indexprev=chargement_grib()   # declenche la mise a jour si possible

    print()
    vit_vent_n, angle_vent = prevision(tig, GR,dateprev_s, d[1], d[0])
    tig_formate    = time.strftime(" %d %b %Y %H", time.gmtime(tig))
    print('\tGrib du {}h +{}h'.format(tig_formate,indexprev*3 ))
    print('\tLe{} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
    print('\tAngle du vent   {:6.3f} °'.format(angle_vent))
    print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
    print()

    effacement_moins2jours(tig)


    
