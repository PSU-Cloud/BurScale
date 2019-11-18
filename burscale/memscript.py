import sys
import pickle
import random
import string
from random import choice,  uniform
from time import sleep

KEY_SIZE = 16
VAL_SIZE = 4096 - 16

cdf = []
keys = []
pi_key = []
hotCount = 0
N = 750000
a = 1.03
zeta = sum(1/n**a for n in range(1, N+1))
def generate_keys():
    global keys, hotCount
    for i in range(N):
        key = ''.join([choice(string.ascii_uppercase + string.digits) for n in range(KEY_SIZE)])
        if hotCount < N*0.2:
            key = 'h' + key
            hotCount +=1
        keys.append(key)
    with open("keys", "wb") as kf:
        pickle.dump(keys, kf)

def zipf(x, a, N):
    global zeta
    return (1/x**a) / zeta


def generate_popularities():
    global pi_key,a,N
    for i in range(1,N +1 ):
        pi_key.append(zipf(i, a, N))
    with open("pops", "wb") as pf:
        pickle.dump(pi_key, pf)


def CDF():
    global pi_key, cdf
    cdf.append(pi_key[0])
    for i in range(1,N):
        cdf.append(cdf[i-1] + pi_key[i])


if __name__ == "__main__":
    print("Generating Keys...")
    generate_keys()
    print("Generated Keys.")
    print(len(keys), keys[0], keys[-1])
    print("Generating Populariteis...")
    generate_popularities()
    print("Generated Populariteis.")
    print("Generating CDF map...")
    CDF()
    print("Generated CDF map.")
    print("Popularity of hot keys: ", cdf[int(0.2*len(cdf))])
