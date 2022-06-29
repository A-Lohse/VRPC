import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 16})

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    This function was develop by user: Greenstick (https://stackoverflow.com/users/2206251/greenstick)
    on https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()
        
        
def event_plot(model,xlim1 = -20.5,xlim2= 20.5,ylim1 = -0.2, ylim2 = 0.2, unit = "week", summary = False, save = ""):
    res = pd.concat([model.params, model.bse,model.pvalues], axis = 1)
    res.columns = ['parameter', 'std','p']
    # Scale standard error to 95% CI
    res['ci'] = res['std']*1.96
    
    

    # We only want time interactions (though if you include controls, the time dummies are still controlled for them)
    res = res.filter(like='INX', axis=0)
    # Turn the coefficient names back to numbers
    res.index = (
        res.index
            .str.replace('INX_', '')
            .str.replace('m', '-')
            .astype('int')
            .rename('time_to_treat')
    )

    # And add our reference period back in, and sort automatically
    res.reindex(range(res.index.min(), res.index.max()+1)).fillna(0)

    # Plot the estimates as connected lines with error bars
    plt.figure(figsize=(18,12))
    
        # Add a horizontal line at 0
    plt.axhline(0, linestyle='dashed', color = "black", alpha = 0.5, label = unit.capitalize() + " before speech", linewidth=4)
    plt.axvline(0, linestyle='dashed', color = "red", alpha = 0.5, label = "First {} after speech".format(unit), linewidth=4)
    
    for i in range(len(res)):
        parm = res.iloc[i].parameter 
        pos = res.iloc[i].name 
        ci = res.iloc[i].ci
        p = res.iloc[i].p

        if p >= 0.05  :
           

            er = plt.errorbar(y = parm, x = pos,yerr =ci,
                         label = 'No effects',
                         color = 'black',
                         elinewidth=6,
                        alpha = 0.5)
            er[-1][0].set_linestyle('-')
            plt.scatter(y = parm, x =  pos, s = 200, marker = "o", color = 'black', alpha = 1)

        else:

            er = plt.errorbar(y = parm, x = pos, yerr = ci, 
                         ecolor = 'black', 
                         color = 'black', 
                         alpha = 1,
                         label = "Significant effect",
                         elinewidth=6)
                        #label = "Weeks with significant effect")
            er[-1][0].set_linestyle('-')
            plt.scatter(y = parm, x =  pos, s = 400, marker = "*", color = 'black', alpha = 1)



    #plt.scatter(-1, 0, color =  "black", s = 620,alpha = 1)
    plt.scatter(-1, 0, color =  "black", s = 620,alpha = 1, marker = 'X')

    

    if len(unit.split('_')) > 1:
        unit = " ".join(unit.split('_')[0:2])
        unit = unit.replace(' after',"")
        
    


    # And a vertical line at the treatment time
    # some versions of pandas have bug return x-axis object with data_interval
    # starting at 0. In that case change 0 to 21
    plt.xlim(xlim1 - 0.5,xlim2 + 0.5)
    plt.ylim(ylim1,ylim2)
    
    plt.xticks(list(range(xlim1,xlim2 +1)),list(range(xlim1,xlim2 +1)))

    
    plt.xlabel(unit)
    plt.ylabel("Effect size")
    
    #plt.legend()
    legs = [plt.Line2D([0], [0], marker='o',lw = 3, color = (0, 0, 0, 1), label='Scatter', markerfacecolor='black', markersize=15, alpha =       1),
            plt.Line2D([0], [0], marker='*',lw = 3, color='black', label='Scatter', markerfacecolor=(0, 0, 0, 1), markersize=15),
            plt.Line2D([0],[0], linestyle='-.', color = "black", alpha = 0.5, linewidth=2.5),
            plt.Line2D([0],[0], linestyle='-.', color = "red", alpha = 0.5, linewidth=2.5)]
        

    plt.legend(legs, ['No effect', 'Significant effect',"Mean week before speech","First week after speech"], shadow = True)

    
    if save != "":
        plt.tight_layout()
        plt.savefig(save)
    
    plt.show()
    
    if summary:
        print(model.summary())