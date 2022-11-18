from lib.data_handler import path_grabber, file_grabber
import matplotlib.pyplot as plt

path = path_grabber('20221111', 'rabi', 47)
data = file_grabber(path)

data_resonant = [x for x in data[0] if 'f301' in x[1]]

a1 = data_resonant[4]
a2 = data_resonant[9]
a3 = data_resonant[-1]

fig, ax = plt.subplots(1,1)
ax.plot(a1[0]['times'], a1[0]['counts'], label=a1[1])
ax.plot(a2[0]['times'], a2[0]['counts'], label=a2[1])
ax.plot(a3[0]['times'], a3[0]['counts'], label=a3[1])
plt.show()
