import os
import re
import time
import matplotlib.pyplot as plt

JOBNAME = 3
DATE = 4
VARNAMES = 8
FIRST_DATA_LINE = 10


class MNTR:

    def __init__(self, path):
        self.path = path
        self.content = None

    def delete_content(self):
        self.content = None
        self.path = None

    def read_content(self):
        with open(self.path) as file_in:
            lines = []
            for line in file_in:
                lines.append(line.strip('\n'))
        self.content = lines

    @property
    def jobname(self):
        """returns the jobname"""
        if self.content is None:
            self.read_content()
        _ret = self.content[JOBNAME]
        _ret = _ret.strip('SOLUTION HISTORY INFORMATION FOR JOB: ')
        return _ret

    def _get_line(self, lineno: int, later_lines=False):
        if self.content is None:
            self.read_content()
        if not later_lines:
            return self.content[lineno]
        else:
            return self.content[lineno:]

    @staticmethod
    def _fix_whitespaces(line_):
        _ret = line_.split('  ')  # splitting at longer whitespaces
        _ret = [x.split() for x in _ret if x]  # removing whitespaces within and empty strings
        _ret = [' '.join(x) for x in _ret]
        return _ret

    @property
    def _release_date(self):
        _ret = self._get_line(DATE)
        return self._fix_whitespaces(_ret)

    @property
    def release(self):
        return self._release_date[:2]

    @property
    def datetime(self):
        return self._release_date[2:]

    @property
    def variables(self):
        _ret = self._get_line(VARNAMES)
        return self._fix_whitespaces(_ret)

    @property
    def data(self):
        _ret = self._get_line(FIRST_DATA_LINE, later_lines=True)
        _ret = [self._extract_values(x) for x in _ret]
        _transformed = []
        for line in _ret:
            _transformed.append([float(x) for x in line])

        _ret = {
            'loadstep': tuple([x[0] for x in _transformed]),
            'substep': tuple([x[1] for x in _transformed]),
            'attempts': tuple([x[2] for x in _transformed]),
            'iterations': tuple([x[3] for x in _transformed]),
            'total iterations': tuple([x[4] for x in _transformed]),
            'increment': tuple([x[5] for x in _transformed]),
            'time': tuple([x[6] for x in _transformed]),
            'variable1': tuple([x[7] for x in _transformed]),  # default: Wall
            'variable2': tuple([x[8] for x in _transformed]),  # default: MxDs
            'variable3': tuple([x[9] for x in _transformed]),  # default: MxPl
            'variable4': tuple([x[10] for x in _transformed]),  # default: MxRe
        }
        return _ret

    @property
    def _numeric_const_pattern(self):
        """
        Extracts the numeric values from the line.
        source: https://stackoverflow.com/a/4703508/2179994
        """
        pattern = r"""
            [-+]? # optional sign
            (?:
            (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
            |
            (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
        )
        # followed by optional exponent part if desired
        (?: [Ee] [+-]? \d+ ) ?
        """
        rx = re.compile(pattern, re.VERBOSE)
        return rx

    def _extract_values(self, line_: str):
        return self._numeric_const_pattern.findall(line_)

    @classmethod
    def discover_mntr_files(cls, path, filter=None):
        """
        it looks for mntr files in path
        """
        if os.path.isfile(path):
            dirname = os.path.dirname(path)
        else:
            dirname = path
        _ret = os.listdir(dirname)
        _ret = [os.path.join(dirname, x) for x in _ret if x.lower().endswith('.mntr')]
        if filter is not None:
            _ret = [x for x in _ret if filter in x]
        _ret = sorted(_ret, key=lambda x: time.ctime(os.path.getmtime(x)))
        return _ret

    def plot(self, horizontal='total iterations', vertical=('time',)):
        """plots"""
        data = self.data
        _x = data[horizontal]
        for dataline in vertical:
            _y = data[dataline]
            if _y:
                plt.plot(data[horizontal], _y, 'bD--', markersize=5)
                plt.title(self.jobname + '.\nmax: {:.4f}, time: {}'.format(max(_y), self.datetime[0]))
                plt.xlabel(horizontal)
                plt.ylabel(dataline)
            else:
                print('No data yet for {}'.format(self.jobname))
        plt.show()


if __name__ == '__main__':
    files = MNTR.discover_mntr_files(os.path.abspath('D:\\ANSYS\\20.167.90 - Delle\\'), filter='MNA')
    # monitor = MNTR(files[-1])
    # monitor.plot()
    for file in files:
        monitor = MNTR(file)
        print(monitor.jobname, max(monitor.data['time']))
        monitor.plot()