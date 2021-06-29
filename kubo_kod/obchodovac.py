import subprocess

def nakup(akcia,tim,mnozstvo):
    subor = open(tim+".txt","r")
    portfolio = eval(subor.read())
    subor.close()

    subor = open("kurzy.txt","r")
    kurzy = eval(subor.read())
    subor.close()
    
    hodnota = round(kurzy[akcia]*mnozstvo*1.02)
    if portfolio["peniaze"] >= hodnota:
        portfolio["peniaze"] = round(portfolio["peniaze"] - hodnota,2)
        portfolio[akcia] += mnozstvo

        subor = open(tim+".txt","w")
        subor.write(str(portfolio))
        subor.close()
        subprocess.call("python3 vykresli_portfolia.py", shell=True)
        return("Operácia prebehla úspešne.")
        
    else:
        return("Nemáte dosť financií, transakcia neprebehla.")

def predaj(akcia,tim,mnozstvo):
    subor = open(tim+".txt","r")
    portfolio = eval(subor.read())
    subor.close()

    subor = open("kurzy.txt","r")
    kurzy = eval(subor.read())
    subor.close()
    
    hodnota = kurzy[akcia]*mnozstvo*0.98
    if portfolio[akcia] >= mnozstvo:
        portfolio["peniaze"] = round(portfolio["peniaze"] + hodnota,2)
        portfolio[akcia] -= mnozstvo

        subor = open(tim+".txt","w")
        subor.write(str(portfolio))
        subor.close()
        subprocess.call("python3 vykresli_portfolia.py", shell=True)
        return("Operácia prebehla úspešne.")
    else:
        return("Nemáte dosť akcií, transakcia neprebehla.")


def vloz_kesu(kesu):
    subor = open("zoznam_timov.txt","r")
    zoznam_timov = eval(subor.read())
    subor.close()
    for tim in zoznam_timov:
        subor = open(tim+".txt","r")
        portfolio = eval(subor.read())
        subor.close()
    
        portfolio["peniaze"]+= kesu

        subor = open(tim+".txt","w")
        subor.write(str(portfolio))
        subor.close()
    subprocess.call("python3 vykresli_portfolia.py", shell=True)
    return("Operácia prebehla úspešne. Na účet bolo vložených " + str(kesu) + "€.")

##print(vloz_kesu("kačiatka",500))

###########################################################################
### Ideme na grafiku a GUI !!!!!! ######################################### 

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QComboBox, QSpinBox, QMessageBox


################## definujem akciu nákupu po kliknutí #####################
def klikli_nakup():
    alert = QMessageBox()
    nazov_timu = vyber_timu.currentText()
    nazov_akcie = akcia.currentText()
    pocet_akcii = mnozstvo_akcii.value()
    alert.setText(nakup(nazov_akcie,nazov_timu,pocet_akcii))
    alert.exec_()

def klikli_predaj():
    alert = QMessageBox()
    nazov_timu = vyber_timu.currentText()
    nazov_akcie = akcia.currentText()
    pocet_akcii = mnozstvo_akcii.value()
    alert.setText(predaj(nazov_akcie,nazov_timu,pocet_akcii))
    alert.exec_()

def klikli_vklad():
    alert = QMessageBox()
#    nazov_timu = vyber_timu.currentText()
    pocet_kesu = mnozstvo_kesu.value()
    alert.setText(vloz_kesu(pocet_kesu))
    alert.exec_()

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(QLabel('Aktívny tím:'))

###### vyberanie tímov #####################################################

vyber_timu = QComboBox()
layout.addWidget(vyber_timu)
subor=open("zoznam_timov.txt","r")
zoznam_timov = eval(subor.read())
subor.close()
vyber_timu.addItems(zoznam_timov)


layout.addWidget(QLabel('Akcia:'))

###### vyberanie akcií #####################################################

akcia = QComboBox()
layout.addWidget(akcia)
subor=open("kurzy.txt","r")
kurzy = eval(subor.read())
subor.close()
for firma, cena in kurzy.items():
    akcia.addItem(firma)

###### vyberanie kolko akcii predame #######################################

layout.addWidget(QLabel('množstvo:'))
mnozstvo_akcii = QSpinBox()
mnozstvo_akcii.setValue(1)
layout.addWidget(mnozstvo_akcii)

sprav_nakup = QPushButton('NAKÚP!')
sprav_nakup.clicked.connect(klikli_nakup)
layout.addWidget(sprav_nakup)

sprav_predaj = QPushButton('PREDAJ!')
sprav_predaj.clicked.connect(klikli_predaj)
layout.addWidget(sprav_predaj)

layout.addWidget(QLabel('Suma na vklad:'))

###### vkladáme peniaze ####################################################

mnozstvo_kesu = QSpinBox()
mnozstvo_kesu.setMaximum(1000)
mnozstvo_kesu.setValue(500)
layout.addWidget(mnozstvo_kesu)

sprav_vklad = QPushButton('Vlož peniaze.')
layout.addWidget(sprav_vklad)
sprav_vklad.clicked.connect(klikli_vklad)

window.setLayout(layout)
window.show()
app.exec_()
