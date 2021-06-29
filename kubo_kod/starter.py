import subprocess
import time

dlzka_hry = 55 ##v minutach

subprocess.call("python3 generuj_pociatocne_kurzy.py", shell=True)
for i in range(20):
    subprocess.call("python3 iteruj_kurzy.py", shell=True)
subprocess.call("python3 kresli_historiu.py", shell=True)
subprocess.call("python3 vykresli_portfolia.py", shell=True)

subprocess.call('gnome-terminal -x sh -c "python3 obchodovac.py; bash"', shell=True)

for i in range(0,dlzka_hry):
    time.sleep(50)
    print ("Do konca hry ostáva " +str(dlzka_hry-i)+ " dní")
    subprocess.call("python3 iteruj_kurzy.py", shell=True)
    subprocess.call("python3 kresli_historiu.py", shell=True)
    subprocess.call("python3 vykresli_portfolia.py", shell=True)

subprocess.call("python3 ukoncit_hru.py", shell=True)
subprocess.call("python3 vykresli_portfolia.py", shell=True)
