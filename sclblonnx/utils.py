import json
from onnx import helper as xhelp
from onnx import onnx_ml_pb2 as xpb2

import sclblonnx._globals as glob


# _parse_element parses a graph input  or output element and return its properties for printing.
def _parse_element(elem):
    """ Parse a graph input or output element and return a string.

    Utility.

    Args:
        elem, a TypeProto.

    Returns:
        name The name of the element
        data_type The data type of the element
        shape_str The dimensions of the element
    """
    name = getattr(elem, 'name', "None")
    data_type = "NA"
    shape_str = "NA"
    etype = getattr(elem, 'type', False)
    if etype:
        ttype = getattr(etype, 'tensor_type', False)
        if ttype:
            data_type = _data_string(getattr(ttype, 'elem_type', 0))
            shape = getattr(elem.type.tensor_type, "shape", False)
            if shape:
                shape_str = "["
                dims = getattr(shape, 'dim', [])
                for dim in dims:
                    vals = getattr(dim, 'dim_value', "?")
                    shape_str += (str(vals) + ",")
                shape_str = shape_str.rstrip(",")
                shape_str += "]"
    return name, data_type, shape_str


# _value creates a new value description
def _value(name, data_type, dimensions):

    dtype = _data_type(data_type)
    if not dtype:
        return False

    val = xhelp.make_tensor_value_info(name, dtype, dimensions)
    return val


def _input_details(graph: xpb2.GraphProto):
    if type(graph) is not xpb2.GraphProto:
        print("graph is not a valid ONNX graph.")
        return False

    names = {}
    for elem in graph.input:
        name, dtype, shape = _parse_element(elem)
        desc = {"data_type": dtype, "shape": shape}
        names[name] = desc

    return names


def _output_details(graph: xpb2.GraphProto):
    if type(graph) is not xpb2.GraphProto:
        print("graph is not a valid ONNX graph.")
        return False

    names = {}
    for elem in graph.output:
        name, dtype, shape = _parse_element(elem)
        desc = {"data_type": dtype, "shape": shape}
        names[name] = desc

    return names


# colors, used for printing.
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# _print controls the printing of user feedback throughout the package
def _print(
        msg: str,
        print_type: str = "ERR",
        silent: bool = False):
    """ print controls the printing throughout the package.

    Args:
        msg: The message to print
        print_type: "feedback" or "warning"
        silent: Suppress printing, default False
    """
    if not silent:
        if print_type == "MSG":
            print(msg)
        elif print_type == "ERR":
            print(f"{bcolors.FAIL}ERROR: "+msg+f"{bcolors.ENDC}")
        else:
            print(msg)


# _load_version_info loads info of supported ONNX versions (see _globals.py)
def _load_version_info() -> bool:
    """Loads the version info json.
    Function opens and parses the file supported_onnx.json in the current
    package folder to check current Scailable toolchain requirements.

    Note: the supported models are loaded into the glob.ONNX_VERSION_INFO
    dictionary to make them available to the whole package.

    Args:

    Returns:
        True if the supported version info is successfully loaded.
    """
    try:
        with open(glob.VERSION_INFO_LOCATION, "r") as f:
            glob.ONNX_VERSION_INFO = json.load(f)
    except FileNotFoundError:
        print("Unable to locate the ONNX_VERSION INFO.")
        return False
    return True


# _data_type converts a data_string to the actual data_type int (see _globals.py)
def _data_type(data_string: str):
    """ convert the data type to the appropriate number

    See: https://deeplearning4j.org/api/latest/onnx/Onnx.TensorProto.DataType.html
    """
    for key, val in glob.DATA_TYPES.items():
        if key == data_string:
            return val
    print("Data type not found. Use `list_data_types()` to list all supported data types.")
    return False


# _data_string converts a data_type int to a data string
def _data_string(data_type: int):
    """ convert the data type mumber to the appropriate string

    See: https://deeplearning4j.org/api/latest/onnx/Onnx.TensorProto.DataType.html
    """
    for key, val in glob.DATA_TYPES.items():
        if val == data_type:
            return key
    return "NaN"