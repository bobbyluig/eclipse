import matplotlib.pyplot as plt
import itertools


fig = plt.figure()
ax = fig.add_subplot(111)

body = [[8.625, -7.75], [-7.875, 7.75]]
com = (-0.15476190476190477, 0.0)
closest = (0.093580139372822863, 0.26436411149825845)

plt.plot(
    *zip(*itertools.chain.from_iterable(itertools.combinations(body, 2))),
    color='blue', marker='o')
plt.plot(com[0], com[1], color='red', marker='+')
plt.plot(closest[0], closest[1], color='green', marker='o')
plt.axis('equal')


plt.show()