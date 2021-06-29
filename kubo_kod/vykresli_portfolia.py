subor = open("zoznam_timov.txt","r")
zoznam_timov = eval(subor.read())
subor.close()

portfolio_global = {}
for tim in zoznam_timov:
    subor = open(tim+".txt","r")
    portfolio_global[tim]=eval(subor.read())
    subor.close()

subor = open("kurzy.txt","r")
portfolio_global["hodnota akcie"] = eval(subor.read())
subor.close()

import pandas as pd
df =  pd.DataFrame(portfolio_global)
df = pd.concat([df.loc[["peniaze"],:], df.drop(["peniaze"]) ])


#df = pd.concat([df,(df.loc["peniaze"]))])

import matplotlib.pyplot as plt
from pandas.plotting import table


plt.figure(figsize=(10,8))
ax = plt.subplot(111, frame_on=False) # no visible frame
ax.xaxis.set_visible(False)  # hide the x axis
ax.yaxis.set_visible(False)  # hide the y axis
###
table(ax, df,loc='center',colWidths=(len(zoznam_timov) + 1)*[0.15])  # where df is your data frame



plt.tight_layout()
plt.savefig('portfolia.png')

print("portfóliá zakreslené do súboru 'portfolia.png'")
