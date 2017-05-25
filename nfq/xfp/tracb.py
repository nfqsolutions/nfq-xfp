# system imports:
import struct
import array
from collections import namedtuple
# 3rd party imports:
# package imports:

CatalogItem = namedtuple('CatalogItem', ['name',
                                         'icomp',
                                         'numc',
                                         'igarty',
                                         'ipos',
                                         'nwrd',
                                         'ilrn',
                                         'ieuc',
                                         'byte_index'])


class Trcgrf(object):
    """
    Trcgrf class is a file parser that allows to postproccess TRACB results.

    nctx Number of catalog entries
    bytesize bytesize of the variable
    """

    def __init__(self, filepath):
        """
        """
        self.filepath = filepath
        self.catalogsend = 0
        file = open(filepath, 'rb')
        # first get bytesize for this array:
        bytesize = struct.unpack('<i', file.read(4))[0]
        self.catalogsend += 4
        # Number of catalog entries:
        self.nctx = struct.unpack('<i', file.read(bytesize))[0]
        self.catalogsend += bytesize
        bytesize = struct.unpack('<i', file.read(4))[0]
        self.catalogsend += 4
        self.entries = []
        byte_index = 0
        for i in range(self.nctx):
            size = struct.unpack('<i', file.read(bytesize))[0]
            self.catalogsend += bytesize
            name, icomp, numc, igarty, ipos, nwrd, ilrn, ieuc = struct.unpack(
                '<8s I I I I I I I', file.read(size))
            self.entries.append(
                CatalogItem(
                    name, icomp, numc, igarty, ipos, nwrd, ilrn, ieuc,
                    byte_index))
            self.catalogsend += size
            size = struct.unpack('<i', file.read(bytesize))[0]
            self.catalogsend += bytesize
            byte_index = byte_index + nwrd

    def get_var_data(self, var_name, var_numc):
        """

        """
        var_entry = [entry for entry in self.entries if (
            var_name in entry.name) and (entry.numc == var_numc)][0]
        # manage the case of an axial variable.
        time_data = []
        var_indexes = [var_entry.byte_index + i for i in range(var_entry.nwrd)]
        var_data = []
        # first check if var exists in catalog:
        with open(self.filepath, 'rb') as file:
            # skip catalog part:
            file.read(self.catalogsend)
            for i in range(501):
                size = struct.unpack('<i', file.read(4))[0]
                timesize = struct.unpack('<i', file.read(size))[0]
                size = struct.unpack('<i', file.read(4))[0]
                bytesize = struct.unpack('<i', file.read(4))
                timestep_array = array.array('d')
                timestep_array.frombytes(file.read(timesize * 8))
                bytesize = struct.unpack('<i', file.read(4))
                time_data.append(timestep_array[0])
                var_data.append([timestep_array[i] for i in var_indexes])
        return time_data, var_data


if __name__ == '__main__':
    # Test drive this
    test = Trcgrf('/home/hmarrao/workspace/nfq-xfp/tests/files/TRCGRF_example')
    # test.get_var_data('phony')
    print(test.get_var_data(b'CLEVL', 68))
    #for entry in test.entries:
    #    print(entry)
