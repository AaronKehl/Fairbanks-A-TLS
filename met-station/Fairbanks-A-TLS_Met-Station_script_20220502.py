from sl3 import *
import serial
import utime

#------------------------------- Constants -------------------------------
# Serial COM settings for CS655 Sensor
CRLF = chr(13) + chr(10)
BAUDRATE = 9600
PORT = "RS232"
PARITY = 'N'
DATA_BITS = 8
STOP_BITS = 1
FLOW_CONTROL = False
RTSCTS = False
DSRDTR = False
TIMEOUT = .5
INTER_BYTE_TIMEOUT = 0.01
#---------------------------- END Constants ------------------------------

#------------------------------- Variables -------------------------------
is_busy = False
lastCall = 0
soil_moisture = float( -99999.00 )
soil_conductivity = float( -99999.00 )
soil_temp = float( -99999.00 )
soil_permittivity = float( -99999.00 )
soil_period = float( -99999.00 )
soil_voltage_ratio = float( -99999.00 )
#---------------------------- END Variables ------------------------------

#------------------------------- FUNCTIONS -------------------------------
#------------------------------ CS655_open() -----------------------------
""" Simple open function to do some port status checking and error reporting.
"""
def CS655_open():
    closed = True

    #Check to see if the port is already open, if so, close it.
    if ( serial.Serial.is_open ):
        try:
            serial.Serial.close()
            closed = True
        except:
            print( "Unable to close an already open serial port." )
            closed = False

    max_tries = 5

    while ( closed == True and max_tries > 0 ):
        try:
            #Open the CS655 Port to the CS655
            with serial.Serial( "RS232", 9600, timeout = 0.1 ) as CS655:
                CS655.inter_byte_timeout = 0.05
                closed = False
        except:
            print( "Unable to open the serial port." )
            max_tries -= 1

    if( closed == True and max_tries == 0 ):
        print( "Max attempts to open serial port reached." )
    else:
        CS655.open()
        return( CS655 )
#--------------------------- END CS655_open() ----------------------------
#------------------------ CS655_cmd( cmd, CS655 ) ------------------------
""" This function condenses the calls required to make a transmission
    to the CS655 Sensor.
"""
def CS655_cmd( cmd, CS655 ):
    CS655.reset_input_buffer()

    count = 0
    while count < 10:
        CS655.write( chr(13) )
        utime.sleep( 0.05 )
        try:
            response = str( CS655.readall() )
            if ( response.find( "CS650>" ) != -1 ):
                utime.sleep( 0.2 )
                CS655.write( cmd + chr( 13 ) )
                break
        except:
            print( "Nothing to print." )
        count += 1

    count = 0
    while( CS655.in_waiting == False and count <= 50 ):
        #do nothing, add timeout structure?
        utime.sleep(0.1)
        count += 1

    return( str( CS655.readall() ) )
#---------------------------- END CS655_cmd ------------------------------
#-------------------------- CS655_close( CS655 ) -------------------------
""" This function is responsible for returning the Sutron to its state
    of functionality prior to the CS655 operating.  Currently,
    this is comprised of ensuring the serial port has been closed.
"""
def CS655_close( CS655 ):
    CS655.close()
#------------------------ END CS655_close( CS655 ) -----------------------
#------------------------- CS655_sample( CS655 ) -------------------------
""" This function is responsible for obtaining sampling measurements from
    the CS655.
"""
def CS655_sample( CS655 ):
    #Send the measure command that we want to the soil meter
    response = CS655_cmd( '3', CS655 )
    #Now let's break apart the message and extract the measurement values
    # Example return message:
    #    b'3\r\nVWC = 0.0000\r\nEC (dS/m)= 0.0002\r\nTS (\xb0C)= 18.93\r\n
    #    Ka = 1.0000\r\nPA (uS)= 1.0523\r\nVR = 1.0000\r\n'

    # First, find the start position of each sesnsor
    vwc_start = response.find( "VWC" )
    ec_start = response.find( "EC" )
    ts_start = response.find( "TS" )
    ka_start = response.find( "Ka" )
    pa_start = response.find( "PA" )
    vr_start = response.find( "VR" )

    # Then, refine the string to only contain the sensor measurement
    vwc = float( response[ (vwc_start + 6):(ec_start-4) ] )
    ec = float( response[ (ec_start + 11):(ts_start-4) ] )
    ts = float( response[ (ts_start + 12):(ka_start-4) ] )
    ka = float( response[ (ka_start + 5):(pa_start-4) ] )
    pa = float( response[ (pa_start + 9):(vr_start-4) ] )
    vr = float( response[ (vr_start + 5):(len(response)-5) ] )

    return( [ vwc, ec, ts, ka, pa, vr ] )
#--------------------------- END CS655_sample ----------------------------
#------------------------- CS655_process( data ) -------------------------
""" This function is responsible for processing the raw recorded data
    taken by the CS655.
"""
def CS655_process( dataset ):
    global soil_moisture
    global soil_conductivity
    global soil_temp
    global soil_permittivity
    global soil_period
    global soil_voltage_ratio

    soil_voltage_ratio = dataset.pop()
    soil_period = dataset.pop()
    soil_permittivity = dataset.pop()
    soil_temp = dataset.pop()
    soil_conductivity = dataset.pop()
    soil_moisture = dataset.pop()

    # No further processing to data at this time.
#--------------------------- END S200_process ----------------------------
#---------------------------- END FUNCTIONS ------------------------------

#-------------------------------- TASKS ----------------------------------
@TASK
def on_startup():
    # so far, do nothing
    print( "I do nothing" )
""" This task is responsible for operations performed whenever the Sutron
    has been rebooted.
"""
#---------------------------- END on_startup() ---------------------------
@TASK
def sensors_on():
    power_control( "SW1", True )
    utime.sleep( 5 )
#------------------------------ sensors_on() -----------------------------
""" This task controls the power status for the SWD_12 port.  This allows
    Sensors requiring external power, to be powered on demand.  This will
    reduce power consumpsion, in comparison to being continuously powered.

    This task should be executed approximately 5 seconds before sensors
    will conduct measurements.
"""
#----------------------------- End sensors_on ----------------------------

@TASK
def sensors_off():
    power_control( "SW1", False )
#----------------------------- sensors_off() -----------------------------
""" This task controls the power status for the SWD_12 port.  This allows
    Sensors requiring external power, to be powered on demand.  This will
    reduce power consumpsion, in comparison to being continuously powered.

    This task should be executed after the necessary sensor readings.
"""
#---------------------------- End sensors_off ----------------------------

@TASK
def get_measurements():
    global lastCall
    currentCall = utime.time()

    if( currentCall - lastCall > ( 1 ) ):
        CS655 = CS655_open()
        CS655_process( CS655_sample( CS655 ) )
        CS655_close( CS655 )
        lastCall = utime.time()
    else:
        # The sensor is not ready to record another measurement
        print( "Re-sampling too soon..." )
""" Obtain recordings of soil meter measurements."""
#------------------------- END get_measurements() ------------------------

#-------------------------------- END TASKS ------------------------------

#---------------------------- get_moisture( arg ) ------------------------
""" Update sensor reading and assign volumetric water content to variable,
    soil_moisture.
"""
@MEASUREMENT
def get_moisture( arg ):
    global is_busy

    #first priority, but if get_measurements() is busy, wait...
    while( is_busy ):
        utime.sleep( 0.1 )

    #Update get_measurements() to busy so other measurements cannot use it.
    is_busy = True

    try:
        get_measurements()
    except:
        #catches exceptions when accessing get_measurements() fails.
        print("busy")
    finally:
        #the data is available, update busy to false so other functions
        #can access the get_measurements() function.
        is_busy = False
        return( soil_moisture )
#-------------------------- END get_moisture( arg ) ----------------------

#-------------------------- get_conductivity( arg ) ----------------------
""" Update sensor reading and assign electrical conductivity to variable,
    soil_conductivity.
"""
@MEASUREMENT
def get_conductivity( arg ):
    global is_busy

    # small delay to ensure measurements are not simultaneously called
    utime.sleep( 0.05 )

    #second priority, but if get_measurements() is busy, wait...
    while( is_busy ):
        utime.sleep( 0.1 )

    #Update get_measurements() to busy so other measurements cannot use it.
    is_busy = True

    try:
        get_measurements()
    except:
        #catches exceptions when accessing get_measurements() fails.
        print("busy")
    finally:
        #the data is available, update busy to false so other functions
        #can access the get_measurements() function.
        is_busy = False
        return( soil_conductivity )
#------------------------ END get_conductivity( arg ) --------------------

#-------------------------- get_temperature( arg ) -----------------------
""" Update sensor reading and assign temperature to variable, soil_temp.
"""
@MEASUREMENT
def get_temperature( arg ):
    global is_busy

    # small delay to ensure measurements are not simultaneously called
    utime.sleep( 0.10 )

    #third priority, but if get_measurements() is busy, wait...
    while( is_busy ):
        utime.sleep( 0.1 )

    #Update get_measurements() to busy so other measurements cannot use it.
    is_busy = True

    try:
        get_measurements()
    except:
        #catches exceptions when accessing get_measurements() fails.
        print("busy")
    finally:
        #the data is available, update busy to false so other functions
        #can access the get_measurements() function.
        is_busy = False
        return( soil_temp )
#------------------------- END get_temperature( arg ) --------------------

#--------------------------- get_permittivity( arg ) ----------------------
""" Update sensor reading and assign permittivity to variable, soil_permittivity.
"""
@MEASUREMENT
def get_permittivity( arg ):
    global is_busy

    # small delay to ensure measurements are not simultaneously called
    utime.sleep( 0.15 )

    #fourth priority, but if get_measurements() is busy, wait...
    while( is_busy ):
        utime.sleep( 0.1 )

    #Update get_measurements() to busy so other measurements cannot use it.
    is_busy = True

    try:
        get_measurements()
    except:
        #catches exceptions when accessing get_measurements() fails.
        print("busy")
    finally:
        #the data is available, update busy to false so other functions
        #can access the get_measurements() function.
        is_busy = False
        return( soil_permittivity )
#-------------------------- END get_permittivity( arg ) -------------------

#---------------------------- get_period( arg ) --------------------------
""" Update sensor reading and assign sampling period to variable, soil_peroid.
"""
@MEASUREMENT
def get_period( arg ):
    global is_busy

    # small delay to ensure measurements are not simultaneously called
    utime.sleep( 0.20 )

    #fifth priority, but if get_measurements() is busy, wait...
    while( is_busy ):
        utime.sleep( 0.1 )

    #Update get_measurements() to busy so other measurements cannot use it.
    is_busy = True

    try:
        get_measurements()
    except:
        #catches exceptions when accessing get_measurements() fails.
        print("busy")
    finally:
        #the data is available, update busy to false so other functions
        #can access the get_measurements() function.
        is_busy = False
        return( soil_period )
#--------------------------- END get_period( arg ) -----------------------

#-------------------------- get_voltage_ratio( arg ) ---------------------
""" Update sensor reading and assign voltage ratio to variable, soil_voltage_ratio.
"""
@MEASUREMENT
def get_voltage_ratio( arg ):
    global is_busy

    # small delay to ensure measurements are not simultaneously called
    utime.sleep( 0.25 )

    #sixth priority, but if get_measurements() is busy, wait...
    while( is_busy ):
        utime.sleep( 0.1 )

    #Update get_measurements() to busy so other measurements cannot use it.
    is_busy = True

    try:
        get_measurements()
    except:
        #catches exceptions when accessing get_measurements() fails.
        print("busy")
    finally:
        #the data is available, update busy to false so other functions
        #can access the get_measurements() function.
        is_busy = False
        return( soil_voltage_ratio )
#------------------------ END get_voltage_ratio( arg ) -------------------

#------------------------- Battery Temperature( arg ) --------------------
""" Battery temperature and controller temperature are sent via 2 bytes of
    same value.  Sutron reports the combined decimal value, but we must process
    the value back into its pieces to report either battery or controller.
"""
@MEASUREMENT
def get_batt_temperature( arg ):
    # we are given the decimal value and must break it out into parts.
    # High byte: controller temp
    # Low byte: auxilliary temp sensor
    temps = bin_to_str( arg, 2 )
    return( bit_convert( temps[1:], 1 ) )
#---------------------- End of Battery Temperature( arg ) ----------------

#---------------------- Controller Temperature( arg ) --------------------
""" Battery temperature and controller temperature are sent via 2 bytes of
    same value.  Sutron reports the combined decimal value, but we must process
    the value back into its pieces to report either battery or controller.
"""
@MEASUREMENT
def get_controller_temperature( arg ):
    # we are given the decimal value and must break it out into parts.
    # High byte: controller temp
    # Low byte: auxilliary temp sensor
    temps = bin_to_str( arg, 2 )
    return( bit_convert( temps[:1], 1 ) )
#------------------- End of Controller Temperature( arg ) ---------------
