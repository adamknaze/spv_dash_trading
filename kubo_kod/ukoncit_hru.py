subor = open("zoznam_timov.txt","r")
zoznam_timov = eval(subor.read())
subor.close()

def predaj(akcia,tim,mnozstvo):
    subor = open(tim+".txt","r")
    portfolio = eval(subor.read())
    subor.close()

    subor = open("kurzy.txt","r")
    kurzy = eval(subor.read())
    subor.close()
    
    hodnota = round(kurzy[akcia]*mnozstvo*0.98,2)

    portfolio["peniaze"]= round(portfolio["peniaze"] + hodnota)
    portfolio[akcia] -= mnozstvo

    subor = open(tim+".txt","w")
    subor.write(str(portfolio))
    subor.close()




for tim in zoznam_timov:
    subor = open(tim+".txt","r")
    majetok_timu=eval(subor.read())
    subor.close()
    
    for akcia, mnozstvo in majetok_timu.items():
        if (not (akcia == "peniaze")) and (mnozstvo > 0):
            predaj(akcia,tim,mnozstvo)
        




