
import json
from numpy import ubyte;
from numpy import uint64;
from numpy import double;
from numpy import array;
from numpy import fix;
from struct import pack;

def convert_from_24bitfloat(floatbytes):
    #converts a binary 24 bit float into a numpy double precision float
    #expects byte array with 3 bytes
    #from numpy uses ubyte, int64, double, array, and fix
    #breaks down floatbytes into their components by bits
    sign = ubyte(floatbytes[0] >> 7);
    exponent = uint64((floatbytes[0] & 0b01111110) >> 1);
    mantissa = array([floatbytes[0] & 0b00000001, floatbytes[1], floatbytes[2]],ubyte);
    fraction = double();
    for i in range(0,17): #iterates through all the bits adding together binary fractions
        operatingbyte = ubyte(fix((i + 7) / 8)); #which byte will be operating on
        bitmask = ubyte(7 - ((i + 7) % 8));
        value = ubyte((floatbytes[operatingbyte] >> bitmask) & 0b1); #value of the current bit
        if (value == 0b1):
            fraction += 2 ** (-1 * (1 + i));
    #executes the float math
    sign = ((-1 * sign) ** 0);
    exponent = 2 ** exponent;
    fraction += 1;
    return (sign * exponent * fraction);
def convert_to_24bitfloat(number):
    #converts a float or float-like number into a 24 bit binary representation
    #from numpy uses ubyte and array
    #from struct uses pack
    return_array = array([0,0,0], ubyte);
    ieee754_float = pack('>f', number);
    return_array[0] = return_array[0] | (ieee754_float[0] & 0b10000000); #set sign bit
    exponent = ubyte(((ieee754_float[0] & 0b01111111) << 1) | ((ieee754_float[1] & 0b10000000) >> 7));
    exponent -= 127; #remove bias
    exponent = exponent & 0b00111111; #conform to 6 bits instead of 8 bits
    return_array[0] = return_array[0] | (exponent << 1); #adds exponent to return array
    return_array[0] = return_array[0] | (0b1 & (ieee754_float[1] >> 6)); #adds mantissa to array
    return_array[1] = (0b11111100 & (ieee754_float[1] << 2)) | (ieee754_float[2] >> 6);
    return_array[2] = 0b11111100 & (ieee754_float[2] << 2) | (ieee754_float[3] >> 6);
    return int((return_array[0] << 16) | (return_array[1] << 8) | (return_array[2]))

def lambda_handler(event, context):
    # JSON Payload is organized as following
    #{
    # "convertto": True or False
    # "number": Float or Int
    #}
    # convertto determines whether to convert to a 24-bit float, or convert from a 24-bit float
    # number may be a float or integer when converting to a 24-bit float, but must be an Int when converting from a 24-bit float
    return_statement = 0;
    if (event["convertto"] == "true"): #convert to 24bitfloat
        number = float(event["number"]);
        if (number < 1) and (number > -1): #numbers between -1 and 1 are impossible to be represented
            return { #invalid JSON sent
            'statusCode': 400,
            }
        return_statement = hex(convert_to_24bitfloat(number));
    elif (event["convertto"] == "false"): #convert from 24bitfloat
        float24bit = int(event["number"]);
        float24bit = array([((float24bit & 0xFF0000) >> 16),((float24bit & 0XFF00) >> 8),(float24bit & 0xFF)],ubyte);
        return_statement = float(convert_from_24bitfloat(float24bit));
    else: 
        return { #invalid JSON sent
            'statusCode': 400,
        }
    return {
        'statusCode': 200,
        'results': json.dumps(return_statement)
    }
