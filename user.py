import os
from main import MNTR

files = MNTR.discover_mntr_files(os.path.abspath('D:\\ANSYS\\20.167.90 - Delle\\'), filter='_GMNIA')
# files = MNTR.discover_mntr_files(os.path.abspath('D:\\Berechnungen\\20.167.90 - Delle\\'), filter='900x520x15_GMNIA')
# monitor = MNTR(files[-1])

# monitor.plot()
for file in files:
    monitor = MNTR(file)
    print(monitor.jobname, '{:.4f}'.format(max(monitor.data['variable2'])))
    monitor.plot(vertical=('time',), horizontal='variable2')
