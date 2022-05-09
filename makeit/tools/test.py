


def outer(func):
    def inner(a,*args,**kwargs):
        if a > 10:
            a = 5
        elif a <= 10:
            a = 11
        return func(a,*args,**kwargs)
    return inner

@outer
def calcu(a):
    return a + 10

print(calcu(12))