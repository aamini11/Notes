def will_freeze(f, x) -> bool:
    """
    Predicts if a function f will get stuck or not when given an input x.
    A.K.A. will f(x) get stuck in an infinite loop or not?
    """
    pass  # Possible to implement?


# We see that its impossible to write will_freeze because we can always write
# a function like "opposite" to brick it:
def opposite(f):
    if will_freeze(f, f):
        return False
    else:
        while True:
            print("Infinite loop")

"""
If will_freeze(opposite, opposite) == True:
    This means will_freeze predicts that opposite will get stuck in an infinite loop when fed itself as input. 
    In other words, it thinks the function call opposite(opposite) will freeze. 
    
    However, if we look at the code for opposite, we see that opposite is specifically designed to return False 
    if will_freeze predicts an infinite loop. So, opposite(opposite) would finish and return False, contradicting 
    the prediction of will_freeze. This means will_freeze was wrong.

If will_freeze(opposite, opposite) == False:
    This means will_freeze predicts that opposite will not get stuck when fed itself as input. 
    
    However, if we look at the code for opposite, we see that opposite is designed to loop forever 
    if will_freeze predicts that it will not freeze. So, opposite(opposite) would enter an infinite loop, 
    contradicting the prediction of will_freeze. This means will_freeze was wrong again.
    
Because in both possible cases will_freeze is wrong, a paradox was reached and designing will_freeze is impossible.

QED.
"""