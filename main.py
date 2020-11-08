from process_coordinates import *
import matplotlib.pyplot as plt
from collections import OrderedDict


df = main("./data/")
# print(get_coordinates_info((31.771511, 76.984304), (31.770879, 76.98317)))
# print(df[0][0])
ret_val = get_attr_per_day()
print(ret_val[2])

def dun(a):
    s = a.split('/').reverse() 
    s[0], s[1] = s[1], s[0]
    s = ''.join(s)
    return s


sp_map = OrderedDict(sorted(ret_val[2], key=dun))


plt.bar((*zip(*sp_map.items())))
plt.show()




# basic gui with buttons & input field & folder select // a
# coordinates:  // d
# plots, stats  // d
# overall stats: plots, stats. // rahul