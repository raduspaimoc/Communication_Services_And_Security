import matplotlib.pyplot as plt 

logFile = 'log.md'


# Creates 'log.md' file and inserts the header values in the correct format to be displayed as a table
def createLogFile():
    header = "|Time (s)|Event|Eff.Win. (MSS)|cwnd (MSS)|RTT (s)|sRTT (s)|TOut (s)\n"
    secondLine = "|---|---|---|---|---|---|---|\n"
    with open(logFile, mode='w', newline='\n') as file:
        file.write(header)
        file.write(secondLine)
        file.close()


# Prints values to 'log.md' file in the correct format to be displayed as a table
def logData(t, log, effectiveWindow, cwnd, rtt, srtt, TOut):
    with open(logFile, mode='a', newline='\n') as file:
        row = ("%.2f" % t)
        row += "|" + log
        row += "|" + str(effectiveWindow)
        row += "|" + str(cwnd)
        row += "|" + ("%.2f" % rtt)
        row += "|" + ("%.2f" % srtt)
        row += "|" + str(TOut)
        row += "\n"
        file.write(row)
        file.close()


# Checks if a number is prime (True) or not (False)
def isPrime(number):
    if number > 1:
        for i in range(2, number):
            if (number % i) == 0:
                return False
                break
        else:
            return True
    return False


# Calculates Round Trip Time (RTT)
def calculateRTT(currentTime, sentTime):
    return currentTime - sentTime


# Calculates Estimated Round Trip Time (sRTT)
def calculateSRTT(alpha, srtt, rtt):
    return alpha * srtt + (1 - alpha) * rtt

# Calculates Effective Window (cwnd)
def calculateEffectiveWindow(cwnd, last_sent, last_ack):
    return int(cwnd - (last_sent - last_ack))


# Plots the cwnd as a function of time 
def plot_cwnd(times, cwnd):

    # plotting the line cwnd points  
    plt.plot(times, cwnd, color = 'tab:red', label = "Congestion Window (cwnd)")
    
    # naming the x axis 
    plt.xlabel('Time (s)') 

    # naming the y axis 
    plt.ylabel('cwnd (MSS)') 

    # giving a title to my graph 
    plt.title('cwnd as a function of time') 
    
    # show a legend on the plot 
    plt.legend() 
    
    # function to show the plot 
    plt.show() 


# Plots the cwnd and sRTT as a function of time 
def plot_sRTT(times, sRTT):
    
    # plotting the line sRTT points  
    plt.plot(times, sRTT, label = "Estimated RTT (sRTT)") 
    
    # naming the x axis 
    plt.xlabel('Time (s)')

    # naming the y axis 
    plt.ylabel('sRTT (s)') 

    # giving a title to my graph 
    plt.title('sRTT as a function of time') 
    
    # show a legend on the plot 
    plt.legend() 
    
    # function to show the plot 
    plt.show() 


# Plots the cwnd and sRTT as a function of time 
def plot(times, sRTT, cwnd):
        
    # naming the x axis 
    plt.xlabel('Time (s)') 

    # giving a title to my graph 
    plt.title('cwnd and sRTT as a function of time') 

    fig, ax1 = plt.subplots()

    # naming the x axis
    ax1.set_xlabel('time (s)')

    # cwnd plot
    color = 'tab:red'
    ax1.set_ylabel('cwnd (MSS)', color=color)
    ln1 = ax1.plot(times, cwnd, color=color, label = "Congestion Window (cwnd)")
    ax1.tick_params(axis='y', labelcolor=color)

    # sRTT plot
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('sRTT (s)', color=color)
    ln2 = ax2.plot(times, sRTT, color=color, label = "Estimated RTT (sRTT)")
    ax2.tick_params(axis='y', labelcolor=color)

    # otherwise the right y-label is slightly clipped
    fig.tight_layout()

    # show a legend on the plot 
    lns = ln1+ln2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0)

    # function to show the plot 
    plt.show()
