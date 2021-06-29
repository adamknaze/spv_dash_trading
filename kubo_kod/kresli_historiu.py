subor = open("historia.txt","r")
historia = eval(subor.read())
subor.close()


# libraries and data
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
 
# Make a data frame
df=pd.DataFrame.from_dict(historia)
 
# Initialize the figure
plt.style.use('seaborn-darkgrid')
 
# create a color palette
palette = plt.get_cmap('Set1')
 
# multiple line plot
num=0

plt.figure(figsize=(12,9))

for column in df:
    num+=1

    # Find the right spot on the plot
    plt.subplot(4,4, num)
 
    # plot every groups, but discreet
    for v in df:
        plt.plot(df[v], marker='', color='grey', linewidth=0.6, alpha=0.6)
 
    # Plot the lineplot
    plt.plot(df[column], marker='', color=palette(num%8), linewidth=3, alpha=0.9, label=column)
 
    # Not ticks everywhere
    plt.tick_params(labelbottom=False)
    if num not in [1,5,9,13] :
        plt.tick_params(labelleft=False)
 
    # Add title
    plt.title(column, loc='left', fontsize=12, fontweight=0, color=palette(num%8))
 

plt.tight_layout()
plt.savefig("ceny_akcii.png")

print("história zakreslená do súboru 'ceny_akcii.png'")

