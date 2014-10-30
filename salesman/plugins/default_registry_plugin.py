import xlsxwriter
import salesman.plugintypes as pt

class Writer(pt.IRegistryWriter):
    ext_info = ('xlsx', 'Excel Workbook')
    pass
