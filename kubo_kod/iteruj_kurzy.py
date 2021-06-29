from random import randint

subor = open("kurzy.txt","r")
kurzy = eval(subor.read())
subor.close()

trend = randint(-50,60)

for spolocnost, cena in kurzy.items():
	kurzy[spolocnost]=round(cena*(trend + randint(-70,85)+1000)/1000,2)


subor = open("kurzy.txt","w")
subor.write(str(kurzy))
subor.close()


subor = open("historia.txt","r")
historia = eval(subor.read())
subor.close()

for spolocnost, cena in kurzy.items():
	historia[spolocnost].append(cena)
	historia[spolocnost] = historia[spolocnost][-20:]

subor = open("historia.txt","w")
subor.write(str(historia))
subor.close()

print("Ďalší deň za nami")


