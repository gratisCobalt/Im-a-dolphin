import psutil

def printCPU():
    print("="*40, "CPU Info", "="*40)

    # number of cores
    print("Physical cores:", getPhysicalCores())
    print("Total cores:", getTotalCores())

    # CPU frequencies
    print(f"Max Frequency: {getCpuMaxFreq()}Mhz")
    print(f"Min Frequency: {getCpuMinFreq()}Mhz")
    print(f"Current Frequency: {getCpuCurrentFreq()}Mhz")
    
    # CPU usage
    print("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    print(f"Total CPU Usage: {psutil.cpu_percent()}% \n")

def getPhysicalCores():
    return psutil.cpu_count(logical=False)

def getTotalCores():
    return psutil.cpu_count(logical=True)

def getCpuMaxFreq():
    return psutil.cpu_freq().max

def getCpuMinFreq():
    return psutil.cpu_freq().min

def getCpuCurrentFreq():
    return psutil.cpu_freq().current
