# package imports:
import xdrlib
#
#import struct
from collections import namedtuple
# 3rd party imports:
# package imports:


ComponentDescription = namedtuple('ComponentDescription', [  "id",
                                           "sub_id",
                                           "cType",
                                           "cTitle",
                                           "dimension",
                                           "nTempl",
                                           "nJun",
                                           "nLegs",
                                           "nSVar",
                                           "nDVar",
                                           "nVect",
                                           "nChild",
                                           "nDynAx"])


TrcChnlRec = namedtuple('TrcChnlRec', [
                            "name",
                            "seqn",
                            "eucode",
                            "unitType",
                            "ptrToX",
                            "ptrToY",
                            "cmode",
                            "size",
                            "csize",
                            "zCompSize",
                            "spare1",
                            "spare2",
                            "spare3",
                            # xtv info
                            "comp_index",
                            "isStatic",
                            "locVarLabel",
                            "static_value",
                            "elevation",
                            "elevIndex",
                            "elevIncrement",
                            "nzmax"])

TrcDynAxis = namedtuple('TrcDynAxis', [
                            "axis",
                            "varType",
                            "scalingVarName",
                            "dimVarName",
                            "maxCells"])


Template = namedtuple('Template', [
                        "dim",
                        #1D components
                        "nCells",
                        "nCellI",
                        "dynAxI",
                        #2D components
                        "nCellJ",
                        "dynAxJ",
                        "coordSys",
                        #3D components
                        "nCellK",
                        "dynAxK",'var_list'])

TrcVar = namedtuple ('TrcVar',[ "comp_index", "vLength",  "vTmpl","blockSize",
                  "varName", "varLabel", "uType",
                  "uLabel", "dimPosAt",  "freqAt",
                  "cMapAt", "vectAt", "spOptAt",
                  "vectName","varIndex" ])

class TraceXTV(object):
    """
    ParcsBpf class is a file parser that allows to read data from
    parcs bpf files.

    nctx Number of catalog entries
    bytesize bytesize of the variable

    Write the start header block to the xdr file.
            @attributes xtvMajorV Major revision number.
            @param xtvMinorV Minor revision number.
            @param revnumber Revision number.
            @param xtvRes    Resolution of data to be written to the file (4==float,8==double).
            @param nPoints   Number of datapoints (times) in file.
            @param nComp     Number of graphics components written to the file.
            @param nSVarAll     Number of static variables in all components.
            @param nDVarAll     Number of dynamic variables in all components.
            @param nSChannels  Number of static variable channels in all components.
            @param nDChannels  Number of dynamic variable channels in all components.
            @param nUnits    Number of additional units information blocks.
            @param unitsSys  Null terminated string identifying the units system.
            @param sysName   Null terminated string identifying the system.
            @param osString  Null terminated string identifying the operating system.
            @param sDate     Null terminated string containing the run date.
            @param sTime     Null terminated string containing the run time.
            @param title     Null terminated string containing the run title.

    """
    def _parse_initial_data(self, stream):
        self.hdrstring = stream.unpack_string().strip()
        self.xtvMajorV = stream.unpack_int()
        self.xtvMinorV = stream.unpack_int()
        self.revnumber = stream.unpack_int()
        self.xtvRes = stream.unpack_int()
        self.nPoints = stream.unpack_int()
        self.nComp = stream.unpack_int()
        self.nSVarAll = stream.unpack_int()
        self.nDVarAll = stream.unpack_int()
        self.nSChannels = stream.unpack_int()
        self.nDChannels = stream.unpack_int()

        stream.unpack_int()  # numtimeslice
        stream.unpack_int()  # dataStart
        stream.unpack_int()  # dataLen
        stream.unpack_int()  # spare1
        stream.unpack_int()  # spare2
        stream.unpack_string()  # spare3
        stream.unpack_string()  # spare4
        stream.unpack_string()  # MUX

        self.unitsSys = stream.unpack_string()
        self.sysName = stream.unpack_string()
        self.osString = stream.unpack_string()
        self.date = stream.unpack_string()
        self.sTime = stream.unpack_string()
        self.title = stream.unpack_string()

    def _parseComponentInfo(self, stream):
        """
        Write Generic Header data to the xdr file.
        @param compId    The component ID number.
        @param compSsId  The Component Sub component ID.
        @param cType     The component type (e.g. "pipe")
        @param cTitle    Title for the component.
        @param cDim      The dimension for the component (0-3 = 0D, 1D, 2D or 3D).
        @param nTempl    The number of Templates for this component (0 if cDim ==0)
        @param nJun      The number of junctions to this component (0 if cDim ==0)
        @param nLegs     The number of side legs on this component (0 if cDim ==0)
        @param nSVar     The number of static variables.
        @param nDVar     The number of dynamic variables.
        @param nVect     The number of vector associations for this component.
        @param nChild    The number of children to this component (0 if compSsId !=0)
        @param nDynAx    The number of Dynamically Sized Axes...
        @param auxStrT   The type of auxilliary structure present (if any.)

        """

        # GCHd
        stream.unpack_string()

        # Revision and blocksize
        stream.unpack_int()
        stream.unpack_int()

        id = stream.unpack_int()
        sub_id = stream.unpack_int()
        cType = stream.unpack_string().strip()
        cTitle = stream.unpack_string().strip()

        dimension = stream.unpack_int()
        nTempl = stream.unpack_int()
        nJun = stream.unpack_int()
        nLegs = stream.unpack_int()
        nSVar = stream.unpack_int()
        nDVar = stream.unpack_int()
        nVect = stream.unpack_int()
        nChild = stream.unpack_int()
        nDynAx = stream.unpack_int()

        self.entries.append(
            ComponentDescription(id, sub_id, cType, cTitle, dimension,
                                 nTempl, nJun, nLegs, nSVar, nDVar, nVect,
                                 nChild, nDynAx))
        # AUX_NONE end of componen header info
        stream.unpack_string()

        return id, dimension,nTempl, nJun,nLegs, nSVar, nDVar, nVect, nChild,nDynAx

    def _getDsAx(self, stream):
        """
         Read/Write Dynamic Axis block to XDR file.
         @param dsAx      The axis being dynamically sized.
         @param varType   The dynamic sizing attribute for the axis.
         @param sVarName  The name of the variable scaling the dynamic axis.
         @param lVarName  The name of the variable dimensioning the dynamic axis.
         @param vMax      The maximum number of cells on dynamic axis.
         """
        # DsAx
        stream.unpack_string()

        # Revision and blocksize
        stream.unpack_int()
        blocksize = stream.unpack_int()

        varType = stream.unpack_string()
        sVarName = stream.unpack_string().strip()
        lVarName = stream.unpack_string().strip()
        stream.unpack_int()

        # Do not know what  are next four vals
        stream.unpack_int()
        stream.unpack_int()
        stream.unpack_int()
        stream.unpack_int()

    def __init__(self, filepath):
        """
        :param filepath: string
        """
        self.filepath = filepath
        self.catalogsend = 0
        #self.catalog = []
        with open(filepath, 'rb') as bpf_file:

            stream = xdrlib.Unpacker(bpf_file.read())

            self._parse_initial_data(stream)

            self.entries = []
            self.catalog = []
            self.template = []
            self.vars =[]
            nCells = 0
            nCellI=0
            dynAxI=0
            nCellJ=0
            dynAxJ=0
            coordSys=0
            nCellK=0
            dynAxK=0
            varIndex = 0

            for var in range(self.nComp):

                var_list=[]

                id,dimension, nTempl, nJun, nLegs, nSVar, nDVar, nVect, nChild, nDynAx\
                    =self._parseComponentInfo( stream)

                for ilNDynAx in range(nDynAx):
                    self._getDsAx (stream)

                if dimension == 1 or dimension==2 :
                    """
                    Write 1D graphics display block data to the xdr file.
                    @param nCells   The number of cells.
                    @param dynAxI   Index of the dynamic axis structure for I Axis (0=NONE)
                    @param fI       The cell face position array (ncell + 1).
                    @param grav     The grav value array (ncell + 1).
                    @param faI      The flow area array. (ncell + 1).

                    """
                    for ilNTempl in range(nTempl):
                        """
                        Write 1D graphics display block data to the xdr file.
                        @param nCells   The number of cells.
                        @param dynAxI   Index of the dynamic axis structure for I Axis (0=NONE)
                        @param fI       The cell face position array (ncell + 1).
                        @param grav     The grav value array (ncell + 1).
                        @param faI      The flow area array. (ncell + 1).

                        """
                        #GD1D
                        stream.unpack_string()
                        ncells =stream.unpack_int()

                        ncellsI = stream.unpack_int()
                        ldinaxi = stream.unpack_int()

                        #unknown int
                        stream.unpack_int()

                        #print("GD1A ", stream.unpack_string())
                        stream.unpack_string()
                        nfaces =stream.unpack_int()

                        dbFI=stream.unpack_int()
                        #print("fi ",
                        stream.unpack_array(stream.unpack_double)
                        #print("grav ",
                        stream.unpack_array(stream.unpack_double)
                        #print("faI ",
                        stream.unpack_array(stream.unpack_double)

                        if  dimension==2 :
                            """
                            Write 2D graphics display block data to the xdr file.
                            @param nCells    The total number of cells.
                            @param nCellI    The number of cells on I axis.
                            @param nCellJ    The number of cells on J axis.
                            @param dynAxI    Index of the dynamic axis structure for I Axis (0=NONE)
                            @param dynAxJ    Index of the dynamic axis structure for J Axis (0=NONE)
                            @param dbFI      The cell length array for the I (x/r) axis (nCellI + 1).
                            @param dbFJ      The cell length array for the J (y/theta or z) axis(nCellJ + 1).
                            @param dbGrav    The grav value array along J axis (nCellJ + 1).
                            @param coordSys  String for the Coordinate system used.
                            """
                            #print("GD2D ",
                            stream.unpack_string()
                            #Block and revision
                            stream.unpack_int()
                            stream.unpack_int()

                            nCells = stream.unpack_int()
                            nCellI = stream.unpack_int()
                            nCellJ = stream.unpack_int()
                            dynAxI = stream.unpack_int()
                            stream.unpack_int()#dynAxJ
                            stream.unpack_string()#CART2D
                            stream.unpack_string()#GD2A
                            stream.unpack_int()#dynAxI
                            stream.unpack_int()#dynAxJ
                            #print("dbFJ ",
                            stream.unpack_array(stream.unpack_double)
                            #print("dbFJ ",
                            stream.unpack_array(stream.unpack_double)
                            #print("dbGrav ",
                            stream.unpack_array(stream.unpack_double)
                            break # Posiblemente habrá forma mejor de pasar esto bien
                            #print("test ", stream.unpack_fstring(100))

                elif dimension == 3:

                    """
                    Write 3D graphics display block data to the xdr file.
                    @param nCells    The total number of cells.
                    @param nCellI    The number of cells on I axis.
                    @param nCellJ    The number of cells on J axis.
                    @param nCellK    The number of cells on J axis.
                    @param dynAxI    Index of the dynamic axis structure for I Axis (0=NONE)
                    @param dynAxJ    Index of the dynamic axis structure for J Axis (0=NONE)
                    @param dynAxK    Index of the dynamic axis structure for K Axis (0=NONE)
                    @param coordSys  String for the Coordinate system used.
                    @param dbFI      The cell length array for the I (x/r) axis (nCellI + 1).
                    @param dbFJ      The cell length array for the J (y/theta or z) axis(nCellJ + 1).
                    @param dbFK      The cell length array for the K (z) axis(nCellK + 1).
                    @param dbGrav    The gravity value array alongthe K axis(nCellK + 1).

                    """
                    #print("GD3D ", stream.unpack_string())
                    stream.unpack_string()
                    #revision and blockSize
                    stream.unpack_int()
                    stream.unpack_int()

                    ncells = stream.unpack_int()
                    nCellI = stream.unpack_int()
                    nCellJ =stream.unpack_int()
                    nCellK = stream.unpack_int()

                    dynAxK = stream.unpack_int()
                    dynAxJ  = stream.unpack_int()
                    dynAxK = stream.unpack_int()

                    coordSys =stream.unpack_string()

                    # print("GD3A ", stream.unpack_string())
                    stream.unpack_string()
                    # revision and blockSize
                    stream.unpack_int()
                    stream.unpack_int()

                    #print("dbFI ",
                    stream.unpack_array(stream.unpack_double)
                    #print("dbFJ ",
                    stream.unpack_array(stream.unpack_double)
                    #print("dbFK ",
                    stream.unpack_array(stream.unpack_double)
                    #print("dbGrav ",
                    stream.unpack_array(stream.unpack_double)

                """
                Write Junction block  data to the xdr file.
                @param junctId  Identifier for the junction.
                @param jCellI   Cell number on I axis that the junction attaches to.
                @param jCellJ   Cell number on J axis that the junction attaches to.
                This should be 0 for 1D junction
                @param jCellK   Cell number on K axis that the junction attaches to.
                This should be 0 for 1D or 2D junction
                @param jFace  The code for which the face junction attaches.
                """
                for ilNJun in range(nJun):
                    #GDJN
                    #print("GDJN ",
                    stream.unpack_string()
                    lJCellI=stream.unpack_int()
                    lJCellJ =stream.unpack_int()
                    lJunctId = stream.unpack_int()
                    lJCellK = stream.unpack_int()
                    jFace = stream.unpack_int()
                    test_int = stream.unpack_int()
                    voidstr = stream.unpack_string()


                """
                Write Leg data to the xdr file.
                @param firstCell The first cell number.
                @param lastCell  The last cell number.
                @param jCell     The cell number the side branch connects to.
                """
                for ilNLegs in range(nLegs):
                    #print("GDLg ", stream.unpack_string())
                    stream.unpack_string()

                    firstCell = stream.unpack_int()
                    lastCell = stream.unpack_int()
                    jCell = stream.unpack_int()

                    #Unknown last two int vals
                    stream.unpack_int()
                    stream.unpack_int()


                if nDVar>0:
                    """
                    Write a variable definition to the xdr file.
                    @param varName     The name of the variable.
                    @param varLabel    The variable label.
                    @param uType       The Units type of the variable.
                    @param uLabel      The units label.(e.g. "m/s")
                    @param vTmpl       The template index.
                    @param dimPosAt    The variable dimension / position attribute.
                    @param freqAt      The variable frequency attribute.
                    @param cMapAt      The variable color Map attribute.
                    @param vectAt      The vector Attribute.
                    @param spOptAt     The variable Special Options attribute.
                    @param vectName    The vector name (only for certain vectAt).
                    @param vLength     The variable length (number of elements)
                    """
                    #print("VARD ", stream.unpack_string())
                    stream.unpack_string()

                    # revision and blockSize
                    stream.unpack_int()
                    blockSize= stream.unpack_int()

                    name= stream.unpack_string().strip()
                    seqn=stream.unpack_string().strip()
                    eucode= stream.unpack_string().strip()
                    unitType = stream.unpack_string().strip()

                    vTmpl = stream.unpack_int()

                    #Do not know next two floats

                    pointerX =stream.unpack_int()
                    pointerY = stream.unpack_int()

                    #print("dimPosAt "
                    dimPosAt=stream.unpack_string()
                    #print(" ",
                    freqAt=stream.unpack_string()
                    #print("cMapAt ",
                    stream.unpack_string()
                    #print("vectAt ",
                    stream.unpack_string()
                    #print("spOptAt ",
                    stream.unpack_string()

                    #Unknown last two int vals
                    stream.unpack_int()
                    vLength = stream.unpack_int()
                    varIndex = varIndex + vLength
                    self.vars.append(
                    TrcVar( id, vLength, vTmpl,blockSize,
                           name, seqn,
                           unitType,
                           "uLabel",
                           dimPosAt,
                           freqAt,
                           "cMapAt",
                           "vectAt",
                           "spOptAt",
                           "vectName",
                            varIndex))
                    var_list.append(TrcVar( id, vLength, vTmpl,blockSize,
                           name, seqn,
                           unitType,
                           "uLabel",
                           dimPosAt,
                           freqAt,
                           "cMapAt",
                           "vectAt",
                           "spOptAt",
                           "vectName",
                            varIndex))


                    self.catalog.append(
                        TrcChnlRec(name,seqn,eucode, unitType,pointerX, pointerY, "cmode",
                        "size",
                        "csize",
                        "zCompSize",
                        "spare1",
                        "spare2",
                        "spare3",
                        id ,
                         "isStatic",
                        "locVarLabel",
                        "static_value",
                        "elevation",
                        "elevIndex",
                        "elevIncrement",
                        "nzmax"       ))

                for ilNSVar in range(nSVar):
                    """
                    Copy the Static floating point Array to the file.
                    @param array   A pointer to the data buffer.
                    @param size    A pointer to the number of values to write.
                    @param xtvRes  A pointer to the number of bytes to write for each value (4==float, 8==double).
                    """
                    stream.unpack_string()
                    stream.unpack_int()

                    size =stream.unpack_int()
                    array =stream.unpack_array(stream.unpack_double)
                    #varIndex = varIndex +size


                for ilNDVar in range(nDVar -1 + nSVar ): # no se como contemplar que las hstr hacen un bucle menos
                    #print(ilNDVar, "**************************")

                    # print("VARD ", stream.unpack_string())
                    stream.unpack_string()
                    # revision and blockSize
                    stream.unpack_int()
                    blockSize = stream.unpack_int()

                    name= stream.unpack_string().strip()
                    seqn=stream.unpack_string().strip()
                    eucode= stream.unpack_string().strip()
                    unitType = stream.unpack_string().strip()

                    vTmpl = stream.unpack_int()

                    #Do not know next two floats
                    stream.unpack_float()
                    stream.unpack_float()

                    #print("dimPosAt ",
                    dimPosAt = stream.unpack_string()
                    #print("freqAt ",
                    freqAt = stream.unpack_string()
                    #print("cMapAt ",
                    stream.unpack_string()
                    #print("vectAt ",
                    stream.unpack_string()
                    #print("spOptAt ",
                    stream.unpack_string()

                    #Unknown last two int vals
                    stream.unpack_int()
                    vLength =stream.unpack_int()
                    varIndex = varIndex +vLength
                    self.vars.append(
                        TrcVar(id, vLength, vTmpl,blockSize,
                               name, seqn,
                               unitType,
                               "uLabel",
                               dimPosAt,
                               freqAt,
                               "cMapAt",
                               "vectAt",
                               "spOptAt",
                               "vectName",
                               varIndex))
                    var_list.append(TrcVar(id, vLength, vTmpl,blockSize,
                                           name, seqn,
                                           unitType,
                                           "uLabel",
                                           dimPosAt,
                                           freqAt,
                                           "cMapAt",
                                           "vectAt",
                                           "spOptAt",
                                           "vectName",
                                           varIndex))

                varIndex = varIndex + 1

                self.template.append(
                    Template(dimension, nCells, nCellI, dynAxI, nCellJ,
                             dynAxJ, coordSys, nCellK, dynAxK,  var_list))
                #print(var_list)
            self.catalogsend = stream.get_position()






    def get_var_data(self, var_name, var_numc, ncell):
        """
        """
        var = [entry for entry in self.vars if (
            var_name == entry.varName) and (entry.comp_index == var_numc)][0]
        # manage the case of an axial variable.
        #print (var)
        #print (var.varIndex)

        varsLen = len(self.vars)
        var_data = []
        moreData = 1

        var_data.append(var)
        # first check if var_code is in the catalog.
        with open(self.filepath, 'rb') as bpf_file:
            stream = xdrlib.Unpacker(bpf_file.read())
            stream.set_position(self.catalogsend)
            try:

                while (moreData):
                    temp_data = []
                    # Just start getting DATA
                    data =stream.unpack_string()

                    if data == b'DATA':
                        moreData == 1
                        current_position = stream.get_position()

                        stream.unpack_int()
                        saltoLinea = stream.unpack_int()
                        numOfVars = stream.unpack_int()

                        time = stream.unpack_float()
                        temp_data.append(time)
                        stream.set_position(current_position + 4 * (var.varIndex +  ncell -1) )

                        value = stream.unpack_float()

                        temp_data.append(value)
                        stream.set_position(current_position+saltoLinea-8)
                        var_data.append(temp_data)
                    else:
                        #print("end of file ")
                        moreData == 0
            except:
                pass



        return var_data


if __name__ == '__main__':
    test = TraceXTV(
        #'/home/ifernandez/workspace/nfq-xfp/tests/files/SVEAc_P95.8_W92.4_00.xtv')
        '/home/ifernandez/workspace/Simulaciones/traceParcs/suite/coupled_to_trace/17chanTRAC-PARCS/stdalone/trcxtv')
    #print(test.__dict__)
    from pprint import pprint
    #print("dimension ",test.template[0][0])
    #print("dimension_xxx ",test.template[0])
    #pprint(test.template[0].var_list[0])
    #pprint(test.vars)
    #print(test.get_var_data(b'cpuTime', 0, 0))
    # test.get_var_data(variableName, component, ncell)
    #print(test.get_var_data(b'pn', 10, 2))
    print(test.get_var_data(b'elm', 10, 1))
