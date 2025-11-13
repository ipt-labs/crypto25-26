def rozshyrenyy_evklid(chyslo_a, chyslo_b):
    if chyslo_a == 0:
        return chyslo_b, 0, 1
    
    poperedni_r, potochni_r = chyslo_a, chyslo_b
    poperedni_u, potochni_u = 1, 0
    poperedni_v, potochni_v = 0, 1
    
    while potochni_r != 0:
        chastnyk = poperedni_r // potochni_r
        
        poperedni_r, potochni_r = potochni_r, poperedni_r - chastnyk * potochni_r
        
        poperedni_u, potochni_u = potochni_u, poperedni_u - chastnyk * potochni_u
        
        poperedni_v, potochni_v = potochni_v, poperedni_v - chastnyk * potochni_v
    
    return poperedni_r, poperedni_u, poperedni_v


def znayty_obernenyy_element(element, modul):
    znachennya_nsd, koefitsiyent_u, _ = rozshyrenyy_evklid(element, modul)
    
    if znachennya_nsd != 1:
        return None
    
    obernenyy = koefitsiyent_u % modul
    return obernenyy


def vyrishyty_liniyне_porivnyannya(koefitsiyent, konstanta, modul):
    znachennya_nsd = rozshyrenyy_evklid(koefitsiyent, modul)[0]
    
    if konstanta % znachennya_nsd != 0:
        return []
    
    if znachennya_nsd == 1:
        obernenyy = znayty_obernenyy_element(koefitsiyent, modul)
        if obernenyy is None:
            return []
        rozviazok = (obernenyy * konstanta) % modul
        return [rozviazok]
    
    zmenshenyy_koef = koefitsiyent // znachennya_nsd
    zmenshena_konst = konstanta // znachennya_nsd
    zmenshenyy_mod = modul // znachennya_nsd
    
    obernenyy = znayty_obernenyy_element(zmenshenyy_koef, zmenshenyy_mod)
    if obernenyy is None:
        return []
    
    bazovyy_rozviazok = (obernenyy * zmenshena_konst) % zmenshenyy_mod
    
    rozviazky = []
    for i in range(znachennya_nsd):
        rozviazky.append(bazovyy_rozviazok + i * zmenshenyy_mod)
    
    return rozviazky
