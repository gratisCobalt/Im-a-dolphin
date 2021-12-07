import psutil
from byteConverter import get_size

svmem = psutil.virtual_memory()
swap = psutil.swap_memory()

def printMemory():
    # Memory Information
    print("="*40, "Memory Information", "="*40)

    # get the memory details
    print(f"Total: {getTotalMemory()}")
    print(f"Available: {getAvailableMemory()}")
    print(f"Used: {getUsedMemory()}")
    print(f"Percentage: {getUsedMemoryPercentage()}%")
    print("="*20, "SWAP", "="*20)
    
    # get the swap memory details (if exists)
    print(f"Total: {getTotalSwap()}")
    print(f"Free: {getFreeSwap()}")
    print(f"Used: {getUsedSwap()}")
    print(f"Percentage: {getUsedSwapPercentage()}% \n")

def getTotalMemory():
    return get_size(svmem.total)

def getAvailableMemory():
    return get_size(svmem.available)

def getUsedMemory():
    return get_size(svmem.used)

def getUsedMemoryPercentage():
    return svmem.percent

def getTotalSwap():
    return get_size(swap.total)

def getFreeSwap():
    return get_size(swap.free)

def getUsedSwap():
    return get_size(swap.used)

def getUsedSwapPercentage():
    return swap.percent
