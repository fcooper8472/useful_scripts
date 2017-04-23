import psutil
import time

import matplotlib
matplotlib.use('svg')
from matplotlib import pyplot as plt


list_of_times = []
list_of_mem_free = []
list_of_swap_used = []

start_time = time.time()
timeout = 7200  # 2 hours

try:
    while True:
        list_of_times.append(time.time() - start_time)

        # Current memory snapshot
        mem_snapshot = psutil.virtual_memory()
        swp_snapshot = psutil.swap_memory()

        list_of_mem_free.append(100.0 * float(mem_snapshot[1]) / float(mem_snapshot[0]))
        list_of_swap_used.append(100.0 * float(swp_snapshot[1]) / float(swp_snapshot[0]))

        if list_of_times[-1] > timeout:
            break

        time.sleep(1.0)

except KeyboardInterrupt:
    pass


# In case keyboard interrupt occurs between appends
if len(list_of_mem_free) != len(list_of_times) or len(list_of_swap_used) != len(list_of_times):
    min_length = min(len(list_of_mem_free), len(list_of_swap_used), len(list_of_times))

    list_of_times = list_of_times[0: min_length]
    list_of_mem_free = list_of_mem_free[0: min_length]
    list_of_swap_used = list_of_swap_used[0: min_length]


plt.rc('font', family='monospace')
plt.rc('figure', figsize=[8, 4.5])  #inches
plt.rc('axes', linewidth=0.5, edgecolor='0.4', axisbelow=True)
plt.rc('xtick', labelsize=10)
plt.rc('ytick', labelsize=10)
plt.rc('xtick.major', size=0, pad=4)
plt.rc('ytick.major', size=0, pad=4)


x_lims = [list_of_times[0], list_of_times[-1]]
y_lims = [0, 100]

plt.plot(list_of_times, list_of_mem_free, label=r'Mem free (%)', color='#F39200')
plt.plot(list_of_times, list_of_swap_used, label=r'Swap used (%)', color='#0072bd')

plt.xlim(x_lims)
plt.ylim(y_lims)

plt.title('Memory usage', fontsize=14, y=1.05)
plt.xlabel(r'Time (sec)', fontsize=12, labelpad=20)
plt.ylabel(r'Memory (%)', fontsize=12, labelpad=20)

ax = plt.gca()
ax.grid(b=True, which='major', color='0.4', linestyle='dotted', dash_capstyle='round')

plt.legend(fontsize=10)

plt.savefig('mem_free.svg', bbox_inches='tight', facecolor='0.9')
