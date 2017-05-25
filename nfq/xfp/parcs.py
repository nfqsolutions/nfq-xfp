# system imports:
import xdrlib
#
from collections import namedtuple
# 3rd party imports:
# package imports:


CatalogItem = namedtuple('CatalogItem', ['code',
                                         'index'])


class ParcsBpf(object):
    """
    ParcsBpf class is a file parser that allows to read data from
    parcs bpf files.

    nctx Number of catalog entries
    bytesize bytesize of the variable
    """

    def __init__(self, filepath):
        """

        """
        self.filepath = filepath
        self.catalogsend = 0
        self.catalog = []
        with open(filepath, 'rb') as bpf_file:
            stream = xdrlib.Unpacker(bpf_file.read())
            self.filetype = stream.unpack_string()
            self.fileversion = stream.unpack_string()
            self.filedesc = stream.unpack_string()
            # starting headers:
            PlotFileHdr = str(stream.unpack_string())
            if 'PlotFileHdr' in PlotFileHdr:
                stream.unpack_int()  # bytes in each time plot dump
                stream.unpack_int()  # end of data
                self.case_text1 = stream.unpack_string()
                self.case_text2 = stream.unpack_string()
                self.case_text3 = stream.unpack_string()
                self.case_text4 = stream.unpack_string()
                stream.unpack_int()  # size of data in bytes
                catalog_size = stream.unpack_int()  # size of data
                stream.unpack_int()  # not know what is
                stream.unpack_int()  # not know what is
                stream.unpack_int()  # not know what is
                for i in range(catalog_size):
                    stream.unpack_int()
                    var_code = stream.unpack_string().strip()
                    stream.unpack_int()
                    var_index = stream.unpack_int()
                    self.catalog.append(
                        CatalogItem(str(var_code), var_index - 1))
                    # print(stream.unpack_int())"""
                self.catalogsend = stream.get_position()

    def get_var_data(self, var_code):
        """
        """
        # first get var_code index:
        var_indexes = [0] + [entry.index for entry in self.catalog
                             if var_code in entry.code]
        var_data = []
        if not var_indexes:
            print("no variable found")
            return
        # first check if var_code is in the catalog.
        with open(self.filepath, 'rb') as bpf_file:
            stream = xdrlib.Unpacker(bpf_file.read())
            stream.set_position(self.catalogsend)
            while 'PlotDataFlt' in str(stream.unpack_string()):
                stream.unpack_int()  # some unkown data
                stream.unpack_int()  # some unkown data
                stream.unpack_int()  # some unkown data
                array_size = stream.unpack_int()  # the array size:
                current_position = stream.get_position()
                temp_data = []
                for i in var_indexes:
                    stream.set_position(current_position + 4 * i)
                    temp_data.append(stream.unpack_float())
                var_data.append(temp_data)
                stream.set_position(current_position + array_size * 4)
        return var_data


if __name__ == '__main__':
    test = ParcsBpf('/home/hmarrao/workspace/tracbf1-parcs/validation/executions/Benchmark/3/CNC_c5_SCRAM61_SSA.bpf')
    print(test.get_var_data('bank-0145'))
    print(test.get_var_data('bank-0144'))
    print(test.get_var_data('bank-0143'))
    print(test.get_var_data('bank-0142'))
    print(test.get_var_data('bank-0020'))
