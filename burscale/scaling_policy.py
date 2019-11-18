def scale(rate, mu):
    '''
    The scaling policy.
    Here we do use the very simple scaling policy, SR Rule.
    Any other scaling policy can be used.
    '''
    r = rate/mu
    return int(r + c*math.sqrt(r))