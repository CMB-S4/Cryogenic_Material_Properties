## This file serves to 'scrape' the fits to materials as published by NIST at the following website:
## https://trc.nist.gov/cryogenics/materials/materialproperties.htm
## Authors: Oorie Desai, Henry Nachman
## Last Edited: 21 June 2024

import requests
from bs4 import BeautifulSoup
import numpy as np

from tc_utils import *

def main():
    ## Scraping functions

    ############################################################
    ## Function 1
    ############################################################

    def func1(x):
        response = requests.get(x)
        soup = BeautifulSoup(response.content,'html.parser')
        results = soup.find(id = 'content') 
        s = results.find('h1')
        tds = []
        b = []
        c = []
        d = []
        e = []
        fourth = []
        g = []
        y = []
        x = []
        divs = soup.findAll('table', {'class':'properties'})
        for div in divs:
            rows = div.findAll('tr')
            for row in rows:
                tds.append(row.text)

        for i in tds:
            w = i.find('curve fit')
            if tds.index(i)<16:
                if w!=-1:
                    r = tds.index(i)
                    x.append(r)
                else:
                    pass

        for i in range(1,14):
                a = str.split(tds[i], sep='\n')
                b.append(a[1])
                c.append(a[2])
                d.append(a[3])
                if len(a)>4:
                    e.append(a[4])
                if len(a)>5:
                    fourth.append(a[5])

        tuples = [(key, value) for i, (key, value) in enumerate(zip(b, c))]
        res = dict(tuples)
        key = list(res.keys())
        val = list(res.values())
        t = key.index('data range')
        keys1 = []
        vals1 = []
        for i in range(1,t):
                keys1.append(key[i])
                vals1.append(float(val[i]))

        keys2 = []
        vals2 = []
        for i in range(t,t+2):
                keys2.append(key[i])
                f = str.split(val[i], sep='-')
                h = (float(f[0]),float(f[1]))
                vals2.append(h)

        keys3 = []
        vals3 = []
        for i in range(t+2,len(res)):
                keys3.append(key[i])
                vals3.append(float(val[i]))

        return [str.split(s.text, ":")[1][1:]], vals1, vals2[0], vals3


    ############################################################
    # Function 2
    ############################################################

    def func2(x):
        response = requests.get(x)
        soup = BeautifulSoup(response.content,'html.parser')
        results = soup.find(id = 'content') 
        s = results.find('h1')
        tds = []
        b = []
        c = []
        d = []
        e = []
        fourth = []
        g = []
        y = []
        x = []
        divs = soup.findAll('table', {'class':'properties'})
        for div in divs:
            rows = div.findAll('tr')
            for row in rows:
                tds.append(row.text)

        for i in tds:
            w = i.find('curve fit')
            if tds.index(i)<16:
                if w!=-1:
                    r = tds.index(i)
                    x.append(r)
                else:
                    pass

        for i in range(1,11):
                a = str.split(tds[i], sep='\n')
                b.append(a[1])
                c.append(a[2])
                d.append(a[3])
                if len(a)>4:
                    e.append(a[4])
                if len(a)>5:
                    fourth.append(a[5])

        tuples = [(key, value) for i, (key, value) in enumerate(zip(b, c))]
        res = dict(tuples)
        key = list(res.keys())
        val = list(res.values())
        t = key.index('data range')
        keys1 = []
        vals1 = []
        for i in range(1,t):
                keys1.append(key[i])
                vals1.append(float(val[i]))

        keys2 = []
        vals2 = []
        for i in range(t,t+2):
                keys2.append(key[i])
                f = str.split(val[i], sep='-')
                h = (float(f[0]),float(f[1]))
                vals2.append(h)

        keys3 = []
        vals3 = []
        for i in range(t+2,len(res)):
                keys3.append(key[i])
                vals3.append(val[i])

        return [str.split(s.text, ":")[1][1:]], vals1, vals2[0], d[9]



    ############################################################
    # Function 3
    ############################################################

    def func3(x):
        response = requests.get(x)
        soup = BeautifulSoup(response.content,'html.parser')
        results = soup.find(id = 'content') 
        s = results.find('h1')
        tds = []
        b = []
        c = []
        d = []
        e = []
        fourth = []
        g = []
        y = []
        x = []
        n = []
        p3 = []
        r3 = []
        e3 = []
        divs = soup.findAll('table', {'class':'properties'})
        for div in divs:
            rows = div.findAll('tr')
            for row in rows:
                tds.append(row.text)

        for i in tds:
            w = i.find('curve fit')
            if tds.index(i)<16:
                if w!=-1:
                    r = tds.index(i)
                    x.append(r)
                else:
                    pass

        for i in range(1,14):
                a = str.split(tds[i], sep='\n')
                b.append(a[1])
                c.append(a[2])
                d.append(a[3])
                if len(a)>4:
                    e.append(a[4])
                if len(a)>5:
                    fourth.append(a[5])

        n.append(str.split(s.text, ":" )[1][1:])
        tuples = [(key, value) for i, (key, value) in enumerate(zip(b, c))]
        res = dict(tuples)
        key = list(res.keys())
        val = list(res.values())
        t = key.index('data range')
        keys1 = []
        vals11 = []
        for i in range(1,t):
                keys1.append(key[i])
                vals11.append(float(val[i]))

        keys2 = []
        vals21 = []
        for i in range(t,t+2):
                keys2.append(key[i])
                f = str.split(val[i], sep='-')
                h = (float(f[0]),float(f[1]))
                vals21.append(h)

        keys3 = []
        vals31 = []
        for i in range(t+2,len(res)):
                keys3.append(key[i])
                vals31.append(float(val[i]))

        p3.append(vals11)
        r3.append(vals21[0])
        e3.append(vals31)

        #second column of thermal conductivity
        n.append(str.split(s.text, ":" )[1][1:])
        tuples = [(key, value) for i, (key, value) in enumerate(zip(b, d))]
        res = dict(tuples)
        key = list(res.keys())
        val = list(res.values())
        t = key.index('data range')
        keys1 = []
        vals12 = []
        for i in range(1,t):
                keys1.append(key[i])
                vals12.append(float(val[i]))

        keys2 = []
        vals22 = []
        for i in range(t,t+2):
                keys2.append(key[i])
                f = str.split(val[i], sep='-')
                h = (float(f[0]),float(f[1]))
                vals22.append(h)

        keys3 = []
        vals32 = []
        for i in range(t+2,len(res)):
                keys3.append(key[i])
                vals32.append(float(val[i]))

        p3.append(vals12)
        r3.append(vals22[0])
        e3.append(vals32)

        #third column(if exits)
        if e[0]!='':
            n.append(str.split(s.text, ":" )[1][1:])
            tuples = [(key, value) for i, (key, value) in enumerate(zip(b, e))]
            res = dict(tuples)
            key = list(res.keys())
            val = list(res.values())
            t = key.index('data range')
            keys1 = []
            vals13 = []
            for i in range(1,t):
                    keys1.append(key[i])
                    vals13.append(float(val[i]))

            keys2 = []
            vals23 = []
            for i in range(t,t+2):
                    keys2.append(key[i])
                    f = str.split(val[i], sep='-')
                    h = (float(f[0]),float(f[1]))
                    vals23.append(h)

            keys3 = []
            vals33 = []
            for i in range(t+2,len(res)):
                    keys3.append(key[i])
                    vals33.append(float(val[i]))

            p3.append(vals13)
            r3.append(vals23[0])
            e3.append(vals33)

        #4th column, if it exists
        if fourth[0]!='':
            n.append(str.split(s.text, ":" )[1][1:])
            tuples = [(key, value) for i, (key, value) in enumerate(zip(b, fourth))]
            res = dict(tuples)
            key = list(res.keys())
            val = list(res.values())
            t = key.index('data range')
            keys1 = []
            vals14 = []
            for i in range(1,t):
                    keys1.append(key[i])
                    vals14.append(float(val[i]))

            keys2 = []
            vals24 = []
            for i in range(t,t+2):
                    keys2.append(key[i])
                    f = str.split(val[i], sep='-')
                    h = (float(f[0]),float(f[1]))
                    vals24.append(h)

            keys3 = []
            vals34 = []
            for i in range(t+2,len(res)):
                    keys3.append(key[i])
                    vals34.append(float(val[i]))

            p3.append(vals14)
            r3.append(vals24[0])
            e3.append(vals34)
        return n, p3, r3, e3


    ############################################################
    # Function 4
    ############################################################

    def func4(x):
        response = requests.get(x)
        soup = BeautifulSoup(response.content,'html.parser')
        results = soup.find(id = 'content') 
        s = results.find('h1')
        tds = []
        b = []
        c = []
        d = []
        e = []
        fourth = []
        g = []
        y = []
        x = []
        n = []
        p4 = []
        r4 = []
        e4 = []
        divs = soup.findAll('table', {'class':'properties'})
        for div in divs:
            rows = div.findAll('tr')
            for row in rows:
                tds.append(row.text)

        for i in tds:
            w = i.find('curve fit')
            if tds.index(i)<16:
                if w!=-1:
                    r = tds.index(i)
                    x.append(r)
                else:
                    pass

        for i in range(1,14):
                a = str.split(tds[i], sep='\n')
                b.append(a[1])
                c.append(a[2])
                d.append(a[3])
                if len(a)>4:
                    e.append(a[4])
                if len(a)>5:
                    fourth.append(a[5])

        n.append(str.split(s.text, ":" )[1][1:])

        tuples = [(key, value) for i, (key, value) in enumerate(zip(b, c))]
        res = dict(tuples)
        key = list(res.keys())
        val = list(res.values())
        t = key.index('data range')
        keys1 = []
        vals11 = []
        for i in range(1,t):
                keys1.append(key[i])
                vals11.append(float(val[i]))

        keys2 = []
        vals21 = []
        for i in range(t,t+2):
                keys2.append(key[i])
                f = str.split(val[i], sep='-')
                h = (float(f[0]),float(f[1]))
                vals21.append(h)

        keys3 = []
        vals31 = []
        for i in range(t+2,len(res)):
                keys3.append(key[i])
                vals31.append(float(val[i]))

        p4.append(vals11)
        r4.append(vals21[0])
        e4.append(vals31)

        #second column of thermal conductivity
        n.append(str.split(s.text, ":" )[1][1:])
        
        tuples = [(key, value) for i, (key, value) in enumerate(zip(b, d))]
        res = dict(tuples)
        key = list(res.keys())
        val = list(res.values())
        t = key.index('data range')
        keys1 = []
        vals12 = []
        for i in range(1,t):
                keys1.append(key[i])
                vals12.append(float(val[i]))

        keys2 = []
        vals22 = []
        for i in range(t,t+2):
                keys2.append(key[i])
                f = str.split(val[i], sep='-')
                h = (float(f[0]),float(f[1]))
                vals22.append(h)

        keys3 = []
        vals32 = []
        for i in range(t+2,len(res)):
                keys3.append(key[i])
                vals32.append(float(val[i]))

        p4.append(vals12)
        r4.append(vals22[0])
        e4.append(vals32)
        return n, p4, r4, e4

    ############################################################
    # Function 5
    ############################################################

    def func5(x):
        response = requests.get(x)
        soup = BeautifulSoup(response.content,'html.parser')
        results = soup.find(id = 'content') 
        s = results.find('h1')
        tds = []
        b = []
        c = []
        d = []
        e = []
        fourth = []
        g = []
        y = []
        x = []
        n = []
        p5 = []
        r5 = []
        e5 = []
        divs = soup.findAll('table', {'class':'properties'})
        for div in divs:
            rows = div.findAll('tr')
            for row in rows:
                tds.append(row.text)

        for i in tds:
            w = i.find('curve fit')
            if tds.index(i)<16:
                if w!=-1:
                    r = tds.index(i)
                    x.append(r)
                else:
                    pass

        for i in range(1,14):
                a = str.split(tds[i], sep='\n')
                b.append(a[1])
                c.append(a[2])
                d.append(a[3])
                if len(a)>4:
                    e.append(a[4])
                if len(a)>5:
                    fourth.append(a[5])
                if len(a)>6:
                    g.append(a[6])

        n.append(str.split(s.text, ":" )[1][1:])
        tuples = [(key, value) for i, (key, value) in enumerate(zip(b, c))]
        res = dict(tuples)
        key = list(res.keys())
        val1 = list(res.values())

        vals10 = float(val1[10][:-1])
        vals11 = float(val1[11][:-1])
        vals1=[]
        for i in range(1,10):
            vals1.append(float(val1[i]))
        t1 = (vals10,vals11)
        p5.append(vals1)
        r5.append(t1)
        e5.append(float(val1[12]))

        #second column of thermal conductivity
        n.append(str.split(s.text, ":")[1][1:])
        tup = [(key, value) for i, (key, value) in enumerate(zip(b, d))]
        res = dict(tup)
        key = list(res.keys())
        val2 = list(res.values())

        vals20 = float(val2[10][:-1])
        vals21 = float(val2[11][:-1])
        vals2=[]
        for i in range(1,10):
            vals2.append(float(val2[i]))
        t2 = (vals20,vals21)
        p5.append(vals2)
        r5.append(t2)
        e5.append(float(val2[12]))

        #third column(if exits)
        if e[0]!='':
            n.append(str.split(s.text, ":" )[1][1:])
            tuples = [(key, value) for i, (key, value) in enumerate(zip(b, e))]
            res = dict(tuples)
            key = list(res.keys())
            val3 = list(res.values())

            vals30 = float(val3[10][:-1])
            vals31 = float(val3[11][:-1])
            vals3=[]
            for i in range(1,10):
                vals3.append(float(val3[i]))
            t3 = (vals30,vals31)
            p5.append(vals3)
            r5.append(t3)
            e5.append(float(val3[12]))

        #4th column, if it exists
        if fourth[0]!='':
            n.append(str.split(s.text, ":" )[1][1:])
            tuples = [(key, value) for i, (key, value) in enumerate(zip(b, fourth))]
            res = dict(tuples)
            key = list(res.keys())
            val4 = list(res.values())

            vals40 = float(val4[10][:-1])
            vals41 = float(val4[11][:-1])
            vals4=[]
            for i in range(1,10):
                vals4.append(float(val4[i]))
            t4 = (vals40,vals41)
            p5.append(vals4)
            r5.append(t4)
            e5.append(float(val4[12]))

        #5th column, if exists
        if g[0]!='':
            n.append(str.split(s.text, ":" )[1][1:])
            tuples = [(key, value) for i, (key, value) in enumerate(zip(b, g))]
            res = dict(tuples)
            key = list(res.keys())
            val5 = list(res.values())

            vals50 = float(val5[10][:-1])
            vals51 = float(val5[11][:-1])
            vals5=[]
            for i in range(1,10):
                vals5.append(float(val5[i]))
            t5 = (vals50,vals51)
            p5.append(vals5)
            r5.append(t5)
            e5.append(float(val5[12]))
        return n, p5, r5, e5


    ############################################################
    # Defining the material names and urls
    ############################################################

    name_arr = ['Aluminum 1100', 'Aluminum 3003-F', 'Aluminum 5083-O', 'Aluminum 6061-T6', 'Aluminum 6063-T5', 'Balsa',
            'Beechwood phenolic', 'Beryllium Copper', 'Brass', 'Copper (OFHC)', 'Fiberglass Epoxy G-10', 
            'Glass Fabric/Polyester', 'Inconel 718', 'Invar (Fe-36Ni)', 'Kevlar-49 Fiber (Aramid)', 
            'Kevlar-49 Composite (Aramid)', 'Lead', 'Molybdenum', 'Nickel Steel Fe 2.25 Ni', 'Nickel Steel Fe 3.25 Ni', 
            'Nickel Steel Fe 5.0 Ni', 'Nickel Steel Fe 9.0 Ni', 'Platinum', 'Nylon', 'Mylar/PET', 'Kapton', 
            'Polystyrene', 'Polyurethane', 'PVC', 'Stainless Steel 304', 'Stainless Steel 304L', 'Stainless Steel 310',
            'Stainless Steel 316', 'Teflon', 'Ti-6Al-4V', 'Titanium 15-3-3-3']

    Urls = ['https://trc.nist.gov/cryogenics/materials/1100%20Aluminum/1100%20Aluminum_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/3003F%20Aluminum/3003FAluminum_rev.htm', 
            'https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/6061%20Aluminum/6061_T6Aluminum_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/6063_T5%20Alulminum/6063-T5Aluminum_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Balsa/Balsa_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Beechwood_Phenolic/beechwood_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Beryllium%20Copper/BerylliumCopper_rev.htm', 
            'https://trc.nist.gov/cryogenics/materials/Brass/Brass_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/OFHC%20Copper/OFHC_Copper_rev1.htm',
            'https://trc.nist.gov/cryogenics/materials/G-10%20CR%20Fiberglass%20Epoxy/G10CRFiberglassEpoxy_rev.htm', 
            'https://trc.nist.gov/cryogenics/materials/Glass%20Fabric%20-%20Polyester/GlassFabric_Polyester_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Iconel%20718/Inconel718_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Invar(Fe-36Ni)/Invar_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Kevlar49/kevlarfiber.htm',
            'https://trc.nist.gov/cryogenics/materials/Kevlar49/kevlarcomposite.htm',
            'https://trc.nist.gov/cryogenics/materials/Lead/Lead_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Molybdenum/Molybdenum_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/NickelSteel/NickelSteel_Fe2.25Ni)_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/NickelSteel/NickelSteel_Fe3.25Ni)_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/NickelSteel/NickelSteel_Fe5.0Ni)_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/NickelSteel/NickelSteel_Fe9.0Ni)_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Platinum/Platinum_rev.htm', 
            'https://trc.nist.gov/cryogenics/materials/Polyamide%20(Nylon)/PolyamideNylon_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/PET/PET_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Polyimide%20Kapton/PolyimideKapton_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Polystyrene/polystyrenerev.html',
            'https://trc.nist.gov/cryogenics/materials/Polyurethane/polyurethanerev.html',
            'https://trc.nist.gov/cryogenics/materials/PVC/PVCrev.htm',
            'https://trc.nist.gov/cryogenics/materials/304Stainless/304Stainless_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/310%20Stainless/310Stainless_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/316Stainless/316Stainless_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Teflon/Teflon_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Ti6Al4V/Ti6Al4V_rev.htm',
            'https://trc.nist.gov/cryogenics/materials/Titanium/Titanium.htm']
    # Types: Determines the function to use to scrape from the NIST website
    Types = [1,1,1,1,1,4,4,1,1,5,4,3,1,1,2,2,1,1,1,1,1,1,1,1,1,1,3,3,4,1,1,1,1,1,1,1] 
    # eq_types: Determines the fit equation type that will be included in the output file
    eq_types = [1,1,1,1,1,1,1,1,1,2,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] 

    Materials = {}

    for i in range(0,len(name_arr)):
        Materials[name_arr[i]] = {'Nist Name': name_arr[i], 'Url': Urls[i], 'Type': Types[i]}

    special_names = {"Copper (OFHC)" : ["Cu OFHC RRR50", "Cu OFHC RRR100", "Cu OFHC RRR150", "Cu OFHC RRR300", "Cu OFHC RRR500"],
                    "Fiberglass Epoxy G-10" : ["G10 CR Normal", "G10 CR Warp"],
                    "Glass Fabric/Polyester" : ["Glass Fabric/Polyester He, warp", "Glass Fabric/Polyester Ni, warp", "Glass Fabric/Polyester Ni, normal"],
                    "Polystyrene" : ["Polystyrene 1.99 lb/ft3, Freon", "Polystyrene 2.0 lb/ft3", "Polystyrene 3.12 lb/ft3", "Polystyrene 6.24 lb/ft3"],
                    "Polyurethane" : ["Polyurethane 1.99 lb/ft3, Freon", "Polyurethane 2.0 lb/ft3, CO2", "Polyurethane 3.06 lb/ft3, He", "Polyurethane 4.00 lb/ft3, Freon"],
                    "PVC" : ["PVC 1.25 lb/ft3, air", "PVC 3.5 lb/ft3, CO2"],
                    "Balsa": ["Wood Balsa 6 lb/ft3", "Wood Balsa 11 lb/ft3"],
                    "Beechwood phenolic": ["Wood Beechwood grain", "Wood Beechwood flatwise"]}



    ############################################################
    # The scraping
    ############################################################

    name = []
    para = []
    data_range = []
    error = []
    eq_type_arr = []
    for i in range(len(Materials)):
        keys = list(Materials.keys())
        key = keys[i]
        if Materials[key]['Type']==1:
            n1, p1,r1,e1 = func1(Materials[key]['Url'])
        if Materials[key]['Type']==2:
            n1, p1,r1,e1 = func2(Materials[key]['Url'])
        if Materials[key]['Type']==3:
            n1, p1,r1,e1 = func3(Materials[key]['Url'])
        if Materials[key]['Type']==4:
            n1, p1,r1,e1 = func4(Materials[key]['Url'])
        if Materials[key]['Type']==5:
            n1, p1,r1,e1 = func5(Materials[key]['Url'])

        for n in range(len(list(n1))):
            if key in special_names:
                nappendval = f"{special_names[key][n]}"
                para.append(p1[n][::-1])
                data_range.append(r1[n][:])
            else:
                nappendval= key
                para.append(p1[::-1])
                data_range.append(r1)
            error.append(e1[n])
            name.append(nappendval)
            eq_type_arr.append(eq_types[i])


    final = zip(para, data_range, error, eq_type_arr)

    final_dict = {}
    for key, values in zip(name, final):
            final_dict[key] = values



    ############################################################
    # Now pulling references
    ############################################################

    mats = ['Aluminum 1100','Aluminum 1100-F','Aluminum 3003-F','Aluminum 5083-O','Aluminum 6061-T6','Aluminum 6063-T5',
        'Apiezon N','Balsa','Beechwood phenolic','Beryllium','Beryllium Copper','Brass','Copper OFHC',
            'Copper ETP','Copper Pure','G10','Fiberglass Epoxy - G11','Glass Fabric – Polyester',
        'Inconel - 718','Indium','Invar (Fe-36Ni)','Kevlar 49 Fiber','Kevlar 49 Composite','Lead','Molybdenum',
            'Nickel Steel (Fe-2.5Ni)','Nickel Steel (Fe-3.5Ni)','Nickel Steel (Fe-5.0Ni)','Nickel Steel (Fe-9.0Ni)',
        'Platinum','Polyamide (Nylon)','PET (Polyethylene Terephthalate) (amorphous) Mylar','Polyimide (Kapton)',
        'Polystyrene','Polyurethane','PVC','Stainless Steel 304','Stainless Steel 304L',
        'Stainless Steel 310','Stainless Steel 316','Teflon','Titanium-6Al-4V','Titanium 15-3-3-3']


    refs = [['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977.'],
        ['Wadd Technical Report. Part II: Properties of Solids. Editor: Victor J. Johnson. A compendium of the properties of materials at low temperature (phase I). National Bureau of Standards. October 1960', 'A Compendium of the Properties of Materials at Low Temperatures Part II. Properties of Solids WADD Technical Report 60-56 Oct 1960'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977.'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977.'],
        ['Thermal Properties Database for Materials at Cryogenic Temperatures. Ed. Holly M. Veres. Volume 1','Recommended values of the Thermophysical Properties of eight Alloys,Major Constituents and their Oxides Y.S.Touloukian ( Purdue University) Feb, 1965'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977.'],
        ['A correlation between thermal conductance and specific heat anomalies and the glass temperature of Apiezon N and T greases Cryogenics v.12 n.2 p.32-34 February 1972 M.M. Kreitman, T. Ashworth, and M. Rechowicz'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977.'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977.'],
        ['The TPRC Data Series. Y.S. Touloukian, R.W. Powell, C.Y. Ho, and P.G. Klemens. Volume 1: Thermal Conductivity-Metallic Elements and Alloys NewYork-Washington 1970'],
        ['Wadd Technical Report. Part II: Properties of Solids. Editor: Victor J. Johnson. A compendium of the properties of materials at low temperature (phase I). National Bureau of Standards. October 1960','2 Be, 98 Cu, Held at 300C for Two Hhours. R. Berman, E.L. Foster, H.M. Rosenberg, Brit. J. A;;l. Physics 6, 181-182 (1955)'],
        ['Thermal Conductivities of Copper and Copper Alloys Powell, R.L., Rogers, W.M., and Roder, H.M. Advances in Cryogenic Engineering vol. 2, 1956, pp. 166-171.'],
        ['Properties of Copper and Copper Alloys at Cryogenic Temperature NIST Monograph 177 N.J. Simon, E.S. Drexler, and R.P. Reed February 1992, p 7-23'],
        ['Mechanical, Thermal Electrical, and Magnetic Properties of Structural Materials. Handbook on Materials for Superconducting Machinery Metals and Ceramics Information Center, Battelle, Columbus Laboratories. November 1974 (With November 1975 and January 1977 Supplements) p 5.1.2-7.','Wadd Technical Report. Part II: Properties of Solids. Editor: Victor J. Johnson. A compendium of the properties of materials at low temperature (phase I). National Bureau of Standard. October 1960 Page 45'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977 6/1/1979', 'Wadd Technical Report. Part II: Properties of Solids Editor: Victor J. Johnson A compendium of the properties of materials at low temperature (phase I). National Bureau of Standards. October 1960.'],
        ['Thermal Properties Database for Materials at Cryogenic Temperatures. Ed. Holly M. Veres. P. 4.503','Thermal Conductivity Of Glass Fiber/Epoxy Composite Support Bands For Cryogenic Dewars, J.C. Hust. Phase II NBS, Boulder 1984.', 'Thermal Conductivity of Solids at Room Temperature and Below, G. Child, L.J. Erics, R.L. Powell. NBS Monograph 131 (1973).'],
        ['Thermal Properties Database for Materials at Cryogenic Temperatures. Ed. Holly M. Veres. P. 4.503'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977. 6/1/1979'],
        ['Handbook on Materials for Superconducting Machinery Mechanical, Thermal Electrical, and Magnetic Properties of Structural Materials. Metals and Ceramics Information Center, Battelle, Columbus Laboratories. November 1974 (With November 1975 and January 1977 Supplements) p 5.1.2-7.'],
        ['A Compendium of the Properties of Materials at Low Temperatures (Phase 1) National Bureau of Standards Cryogenic Engineering Library. Part 2: Properties of Solids. Victor J. Johnson Ed. October 1960, P 3.132.'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977.'],
        ['Thermal Conductivity of Kevlar 49 between 7 and 290 K, Ventura, G., and V. Martelli Cryogenics 49 (2009): 735-37.', 'Very Low Temperature Thermal Conductivity of Kevlar 49 Ventura, G., and V. Martelli Cryogenics 49 (2009): 376-77.','Temperature Variation of the Thermal Conductivity of Kevlar Polymer Communications, 1985, Vol 26, May B. Poulaert, J.C. Chieliens, C. Vandehande, and R. Legras (Digitized Data)'],
        ['Low-temperature thermal conductivity of two fibre-epoxy composites J.G. Hust, Cryogenics vol. 15 (1975), pp. 125-128.','Thermal Conductivityi Measurements of Fiberglass/Epoxy Structural Tubes from 4 K to 320 K W.G. Foster, L.G. Naes, and C.B. Barnes AIAA paper 75-711, AIAA 10 th Thermophysics Conference, Denver, 1975.','The thermal conductivity of Kevlar fibre-reinforced composites J.P. Harris, B. Yates, J. Batchelor, and P.J. Garrington J. of Material Science 17 (1982), pp 2925-2935.'],
        ['A Compendium of the Properties of Materials at Low Temperatures (Phase 1) National Bureau of Standards Cryogenic Engineering Library. Part 2: Properties of Solids. Victor J. Johnson Ed. October 1960, P 3.132.'],
        ['CRC Materials Reference Handbook. Editors: James Shackelford and William Alexander. The TPRC Data Series. Y.S. Touloukian, R.W. Powell, C.Y. Ho, and P.G. Klemens. Volume 1: Thermal Conductivity-Metallic Elements and Alloys NewYork-Washington 1970', 'AKA Thermophysical Properties of Matter Volume 1 Thermal Conductivity-Metallic Elements and Alloys R.S. Touloukian, R.W. Powell, C.Y. Ho, P.G. Klemens'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977.'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977. 6/1/1979 '],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977. 6/1/1979 '],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977. 6/1/1979 '],
        ['Wadd Technical Report. Part II: Properties of Solids. Editor: Victor J. Johnson. A compendium of the properties of materials at low temperature (phase I). National Bureau of Standard. October 1960, 3.182'],
        ['Wadd Technical Report. Part II: Properties of Solids. Editor: Victor J. Johnson. A compendium of the properties of materials at low temperature (phase I). National Bureau of Standard. October 1960 ','Thermal Properties Database for Materials at Cryogenic Temperature edited by Holly M. Veres'],
        ['The low temperature thermal conductivity of a semi-crystalline polymer, polyethylene terephthalate Journal of Physics C: Solid State Physics v.8 n.19 p.3121-3129 October 1975 C. L. Choy and D. Grieg'],
        ['Thermal Conductivity of a Polyimide Film Between 4.2 and 300K, With and Without Alumina Particles as Filler, D.L. Rule, D.R. Smith, and L.L. Sparks NISTIR 3948, August 1990.'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards First Edition, 1977. 6/1/1979'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards First Edition, 1977. 6/1/1979'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards First Edition, 1977. 6/1/1979'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977. 6/1/1979','Thermophysical Properties of Selected Aerospace Materials Part II: Thermophysical Properties of Seven Materials Y.S Touloukian and C.Y. Ho Editors 1976, p.39-46'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977. 6/1/1979','Thermophysical Properties of Selected Aerospace Materials Part II: Thermophysical Properties of Seven Materials Y.S Touloukian and C.Y. Ho Editors 1976, p.39-46'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977. 6/1/1979','Thermophysical Properties of Selected Aerospace Materials Part II: Thermophysical Properties of Seven Materials Y.S Touloukian and C.Y. Ho Editors 1976, p.39-46'],
        ['LNG Materials and Fluids. Ed. Douglas Mann National Bureau of Standards, Cryogenics Division First Edition, 1977. 6/1/1979','Thermophysical Properties of Selected Aerospace Materials Part II: Thermophysical Properties of Seven Materials Y.S Touloukian and C.Y. Ho Editors 1976, p.39-46'],
        ['Thermal Properties Database for Materials at Cryogenic Temperatures. Ed. Holly M. Veres. P. 4.503'],
        ['Specific Heat and Thermal Conductivity of Four Commercial Titanium Alloys From 20 to 300K, W.T. Ziegler, J.C. Mullins, and S.C.P. Hwa, Advances in Cryogenic Engineering Vol. 8, 1963, p. 268-277.'],
        ['Thermal Conductivity and Specific Heat Measurements of Candidate Structural Materials for the JWST Optical Bench, E.R. Canavan and J.G. Tuttle, Advances in Cryogenic Engineering Vol. 52, 2006, p. 233-240.']]

    reference_dict = {}

    for i in range(0,len(mats)):
        reference_dict[mats[i]] = refs[i]



    ############################################################
    # Now saving to the repository
    ############################################################

    Nist_fit_dict = {1:"polylog",
                    2:"NIST-copperfit",
                    3:"NIST-experf"}
    for key in final_dict:
        material_name = key
        if key in reference_dict:
            reference = reference_dict[key]
        replace_chars = {"(":"", ")":"", "-":"", "/":"", ",":"", "  ":" ", " ":"_"}
        for char in replace_chars:
            material_name = material_name.replace(char, replace_chars[char])
        
        parameters, eq_range, perc_err = final_dict[key][0], final_dict[key][1], final_dict[key][2]
        # if final_dict[key][3] == 1:
        #     fit_types = f"polylog"
        # else:
        #     fit_types = f"NIST-{final_dict[key][3]}"
        fit_types = Nist_fit_dict[final_dict[key][3]]
        # print(material_name, parameters, eq_range, perc_err, fit_types)

        fit_args = dict_monofit(np.array(parameters), eq_range, fit_types, perc_err)
        
        output_array = format_monofit(fit_args)
        # print(output_array)
        # print(material_name)
        if not os.path.exists(f"lib\{material_name}"):
            os.mkdir(f"lib\{material_name}")
        # if "NIST" in fit_types:
        output_folder = f"lib\{material_name}\\NIST"
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        create_tc_csv(output_array, f"{output_folder}\{material_name}.csv")
        # else:
        #     output_folder = f"lib\{material_name}\OTHERFITS"
        #     if not os.path.exists(output_folder):
        #         os.mkdir(output_folder)
        #     create_tc_csv(output_array, f"{output_folder}\{material_name}.csv")
        with open(f"{output_folder}\\reference.txt", 'w') as file:
                file.write(f"{reference}")

if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    path_to_lib = f"{os.chdir(os.path.split(abspath)[0])}{os.sep}lib"
    main()