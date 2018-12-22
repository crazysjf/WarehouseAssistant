import getopt
import numpy as np
import pandas as pd
import math

df = pd.DataFrame(np.random.randn(5, 3), columns=['a', 'b', 'c'])
print(df)

print(df.a)
a = df.a
m = a.map(lambda x: math.sin(x) > 0)

print(m)
#m

dd = df.loc[m]
print(dd)

ddd = df.loc[lambda d: np.sin(d.a)>0]
print(ddd)