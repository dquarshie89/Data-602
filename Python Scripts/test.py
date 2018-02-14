#for a in range(1,101):
#    print('a',a)
#print('done');

def sum_func(a,s,d,f):
    if a>=1:
        x = (a*s*d)/f
        print('a>=1')
        return(x)
    else:
        x=f
        print('a<1')
        return(x)

z = sum_func(0,35,6,100)
print(z)

    
