# -*- coding: utf-8 -*-
# package imports:
import xdrlib
# import struct:
# 3rd party imports:
# package imports:


def readVARD(stream):
    """
    """
    stream.unpack_int()  # "VARD no sabemos lo que es")
    stream.unpack_int()  # "VARD no sabemos lo que es")
    varName = stream.unpack_string()  # Codigo de Variable
    varLabel = stream.unpack_string()  # Descripcion de Variable
    stream.unpack_string()  # "no sabemos lo que es"
    uType = stream.unpack_string()
    uLabel = stream.unpack_string()  # "no sabemos lo que es"
    stream.unpack_string()  # "no sabemos lo que es"
    stream.unpack_string()  # "no sabemos lo que es"
    stream.unpack_string()  # "no sabemos lo que es"
    stream.unpack_string()  # "no sabemos lo que es"
    stream.unpack_string()  # "no sabemos lo que es"
    stream.unpack_int()  # "no sabemos lo que es"
    stream.unpack_int()  # "no sabemos lo que es"
    return varName, varLabel, uType, uLabel


def readStDA(stream):
    """
    """
    stream.unpack_int()  # "StDA"
    stream.unpack_int()  # "StDA"
    stream.unpack_array(stream.unpack_double)  # "StDA"
    return 

def readGD1D(stream):
    """
    """
    nCells = stream.unpack_int()
    dynAxI = stream.unpack_int()
    print(stream.unpack_int())
    print(stream.unpack_int())
    return nCells, dynAxI


def readGD1A(stream):
    """
    """
    stream.unpack_int()  # GD1A no sabemos lo que es
    nFaces = stream.unpack_int()
    fI = stream.unpack_array(stream.unpack_double)
    grav = stream.unpack_array(stream.unpack_double)
    faI = stream.unpack_array(stream.unpack_double)
    return nFaces, fI, grav, faI


def readGDJn(stream):
    """
    """
    lJCellI = stream.unpack_int()
    lJCellJ = stream.unpack_int()
    lJunctId = stream.unpack_int()
    lJCellK = stream.unpack_int()
    jFace = stream.unpack_int()
    stream.unpack_int()  # GDJn no sabemos lo que es
    stream.unpack_int()  # GDJn no sabemos lo que es
    stream.unpack_int()  # GDJn no sabemos lo que es
    return lJCellI, lJCellJ, lJunctId, lJCellK, jFace

class TraceBpf(object):
    """
    ParcsBpf class is a file parser that allows to read data from
    parcs bpf files.

    nctx Number of catalog entries
    bytesize bytesize of the variable

    Write the start header block to the xdr file.
            @attributes xtvMajorV Major revision number.
            @param xtvMinorV Minor revision number.
            @param revnumber Revision number.
            @param xtvRes    Resolution of data to be written to the file
                             (4==float,8==double).
            @param nPoints   Number of datapoints (times) in file.
            @param nComp     Number of graphics components written to the file.
            @param nSVarAll     Number of static variables in all components.
            @param nDVarAll     Number of dynamic variables in all components.
            @param nSChannels   Number of static variable channels
                                in all components.
            @param nDChannels   Number of dynamic variable channels
                                in all components.
            @param nUnits    Number of additional units information blocks.
            @param unitsSys  Null terminated string identifying
                             the units system.
            @param sysName   Null terminated string identifying
                             the Operating System.
            @param osString  Null terminated string identifying
                             the operating system.
            @param sDate     Null terminated string containing the run date.
            @param sTime     Null terminated string containing the run time.
            @param title     Null terminated string containing the run title.

    """

    def _parse_initial_data(self, stream):
        """
        extract the following information and add it as a class variable:
        """
        # first string in xtv file:
        self.hdrstring = stream.unpack_string().strip()
        self.xtvMajorV = stream.unpack_int()
        self.xtvMinorV = stream.unpack_int()
        self.revnumber = stream.unpack_int()
        self.xtvRes = stream.unpack_int()
        self.nPoints = stream.unpack_int()
        self.nComp = stream.unpack_int()  # Is this a good component number¿?
        self.nSVarAll = stream.unpack_int()  # Is this a good component number¿?
        self.nDVarAll = stream.unpack_int()  # Is this a good component number¿?
        self.nSChannels = stream.unpack_int()  # Is this a good component number¿?
        self.nDChannels = stream.unpack_int()  # Is this a good component number¿?
        self.dataStart = stream.unpack_int()  # numtimeslice
        self.dataLen = stream.unpack_int()  # dataStart
        self.nPoints = stream.unpack_int()  # dataLen
        self.status = stream.unpack_int()  # spare1
        self.spare2 = stream.unpack_int()  # spare2
        self.spare3 = stream.unpack_int()  # spare3
        self.spare4 = stream.unpack_int()  # spare4
        self.fmtstring = stream.unpack_string()  # MUX
        self.unitsSys = stream.unpack_string()  # System Units
        self.sysName = stream.unpack_string()  # Execution Machine Name
        self.osString = stream.unpack_string()  # Execution Machine OS
        self.date = stream.unpack_string()  # Execution Date DD/MM/YY
        self.sTime = stream.unpack_string()  # Execution Time
        self.title = stream.unpack_string()  # case title

    def _parse_comp_var(self, stream):
        """Parse component data from stream

        Parses component data from stream returning a comp object

                    #     Write Generic Header data to the xdr file.
            #     @param compId    The component ID number.
            #     @param compSsId  The Component Sub component ID.
            #     @param cType     The component type (e.g. "pipe")
            #     @param cTitle    Title for the component.
            #     @param cDim      The dimension for the component (0-3 = 0D, 1D, 2D or 3D).
            #     @param nTempl    The number of Templates for this component (0 if cDim ==0)
            #     @param nJun      The number of junctions to this component (0 if cDim ==0)
            #     @param nLegs     The number of side legs on this component (0 if cDim ==0)
            #     @param nSVar     The number of static variables.
            #     @param nDVar     The number of dynamic variables.
            #     @param nVect     The number of vector associations for this component.
            #     @param nChild    The number of children to this component (0 if compSsId !=0)
            #     @param nDynAx    The number of Dynamically Sized Axes...
            #     @param auxStrT   The type of auxilliary structure present (if any.)
        """
        current_var = {}
        var_templ = stream.unpack_string()
        if var_templ == b'VARD':
            print(readVARD(stream), "VARD")
        elif var_templ == b'GD1D':
            print(readGD1D(stream), "GD1D")
        elif var_templ == b'GD1A':
            print(readGD1A(stream), "GD1A")
        elif var_templ == b'GDJn':
            print(readGD1A(stream), "GD1A")
            #current_var['var_templ'] = var_templ
            #current_var['lJCellI'] = stream.unpack_int()
            #current_var['lJCellJ'] = stream.unpack_int()
            #current_var['lJunctId'] = stream.unpack_int()
            #current_var['lJCellK'] = stream.unpack_int()
            #current_var['jFace'] = stream.unpack_int()
            #print(stream.unpack_int(), "GDJn no sabemos lo que es")
            #print(stream.unpack_int(), "GDJn no sabemos lo que es")
            #print(stream.unpack_int(), "GDJn no sabemos lo que es")
        elif var_templ == b'StDA':
            readStDA(stream)
            #current_var['var_templ'] = var_templ
            #print(stream.unpack_int(), "StDA no sabemos lo que es")
            #print(stream.unpack_int(), "StDA no sabemos lo que es")
            #print(stream.unpack_array(stream.unpack_double), "StDA no sabemos lo que es")
        else:
            raise Exception('no sabemos lo que es' + str(var_templ))
        return current_var

    def _parse_component_data(self, stream):
        """
        """
        current_comp = dict()
        comptempl = stream.unpack_string()
        if comptempl != b'GCHd':
            raise Exception('can not parse data' + str(comptempl))
        current_comp['revision'] = stream.unpack_int()
        current_comp['blocksize'] = stream.unpack_int()
        current_comp['compId'] = stream.unpack_int()
        current_comp['compSubId'] = stream.unpack_int()
        current_comp['cType'] = stream.unpack_string()
        current_comp['cTitle'] = stream.unpack_string()
        current_comp['cDim'] = stream.unpack_int()
        current_comp['nTempl'] = stream.unpack_int()
        current_comp['nJun'] = stream.unpack_int()
        current_comp['nLegs'] = stream.unpack_int()
        current_comp['nSVar'] = stream.unpack_int()
        current_comp['nDVar'] = stream.unpack_int()
        current_comp['nVect'] = stream.unpack_int()
        current_comp['nChild'] = stream.unpack_int()
        current_comp['nDynAx'] = stream.unpack_int()
        # process next vars
        print(current_comp)
        # process AUX vars:
        print(stream.unpack_string())
        # process AUX vars END
        current_comp['var_list'] = []
        # parse GD1D
        current_comp['GD1D'] = self._parse_comp_var(stream)
        # parse GD1A
        current_comp['GD1A'] = self._parse_comp_var(stream)
        # parse GDJn
        current_comp['GDJn'] = []
        for i in range(current_comp['nJun']):
            current_comp['GDJn'].append(self._parse_comp_var(stream))
        #for i in range(current_comp['nDVar'] + current_comp['nSVar'] + 1):
        for i in range(10):
            test = self._parse_comp_var(stream)
            current_comp['var_list'].append(test)
        return current_comp

    def __init__(self, filepath):
        """
        :param filepath: string
        """
        self.filepath = filepath
        self.catalogsend = 0
        self.catalog = []
        self.comp_list = []
        with open(filepath, 'rb') as bpf_file:
            stream = xdrlib.Unpacker(bpf_file.read())
            # self.hdrstring = stream.unpack_string().strip()
            self._parse_initial_data(stream)
            #for var in range(self.nComp):
            for var in range(1):
                self.comp_list.append(self._parse_component_data(stream))
            #print(stream.unpack_string(), 'tras la componente')
            self.catalogsend = stream.get_position()
            # this is already for data:



if __name__ == '__main__':
    # test = TraceBpf(
    #    '/home/hmarrao/workspace/nfq-xfp/tests/files/SVEAc_P95.8_W92.4_00.xtv')
    test = TraceBpf(
        '/home/hmarrao/workspace/nfq-xfp/tests/files/Base_Job.xtv')
    # print(test.__dict__)
    #print(test.get_var_data(b'vol', 10))
    from pprint import pprint as print
    print(test.__dict__)
