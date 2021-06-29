from random import randint

####### zakladám akcieové fondy a určujem hodnotu #####################

kurzy = dict()
kurzy['google'] = randint(1,100)+50
kurzy['facebook'] = randint(1,100)+50
kurzy['vacumlabs'] = randint(1,100)+50
kurzy['apple'] = randint(1,100)+50
kurzy['microsoft'] = randint(1,100)+50
kurzy['xiaomi'] = randint(1,100)+50
kurzy['hame'] = randint(1,100)+50
kurzy['NRSR'] = randint(1,100)+50
kurzy['opavia'] = randint(1,100)+50
kurzy['kraft'] = randint(1,100)+50
kurzy['vajda'] = randint(1,100)+50
kurzy['samsung'] = randint(1,100)+50
kurzy['kozel'] = randint(1,100)+50
kurzy['BMW'] = randint(1,100)+50
kurzy['dacia'] = randint(1,100)+50
kurzy['sustredko inc.'] = randint(1,100)+50


## retazec = str(kurzy)
## kurzy2 = eval (retazec)

subor = open("kurzy.txt","w")
subor.write(str(kurzy))
subor.close()

####### zakladám súbory na ukladanie histórie #################

historia = dict()
for spolocnost, cena in kurzy.items():
	historia[spolocnost] = [cena]

subor = open("historia.txt","w")
subor.write(str(historia))
subor.close()

print("kurzy vygenerované")

############## ideme založiť účty tímom. ###################

subor = open("zoznam_timov.txt","r")
zoznam_timov = eval(subor.read())
subor.close()

for tim in zoznam_timov:
    
    mapa = {"peniaze": 500}
    for spolocnost, cena in kurzy.items():
	    mapa[spolocnost] = 0
    subor = open(tim+".txt","w")
    subor.write(str(mapa))

print("Účty založené")
