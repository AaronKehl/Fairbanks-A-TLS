/*  Aaron Kehl
 *  CRREL - RS/GIS CX
 *  Summer 2022
 *
 *  GPO.INO:
 *  This program serves as a serial driven GPO device for any device with serial capabilities.  The functionality of the device is
 *  simplistic as only one command and one relay are directed at a time.
 *
 *  The Equipment:
 *    - Arduino Uno
 *    - Aruduino Uno 4 Relay Sheild ( 2A Max, 48V Max )
 *
 *  The Wiring:
 *    - C : The power in to the relay from the external source (0-48V)
 *    - NO : Normal Open lead, no power flows as default.
 *    - NC : Normal Closed lead, power flows as default.
 *
 *  The Larger System:
 *    - INPUT: Raspberry Pi or NUC or Stealth or other CPU device to provide serial commands to this GPO device.
 *    - OUTPUT: Drive the input relay of the Crydom D1D40(L) relays.
 *
 *  But Why?
 *    - Raspberry Pi GPIO pins use 3.3V logic, worst case scenario a high pin voltage can be approximately 2.1V (didn't actually look).
 *    - Arduino GPIO pins use 5V logic, worst case scenario a high pin voltage can be approximately 3V (didn't actually look).
 *    - Crydom Relay requires a minimum of 3.5V to drive the input, in colder temperatures it requires a minimum of 4.5V.
 *    - In conclusion, at MINIMUM a constant/reliable voltage threshold to drive crydom relays in 4.5V. Pi/Arduino GPIO is not stable.
 */

//========================================================= Initialization ===============================================================
//-------------------------------------------------------- Global Constants --------------------------------------------------------------
int relay_1 = 4, relay_2 = 7;
int relay_3 = 8, relay_4 = 12;
//----------------------------------------------------------------------------------------------------------------------------------------

//----------------------------------------------------------- setup() --------------------------------------------------------------------
/*
 * Initialize the serial interface and initialize the relay pins.
 */
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode( relay_1, OUTPUT );
  pinMode( relay_2, OUTPUT );
  pinMode( relay_3, OUTPUT );
  pinMode( relay_4, OUTPUT );
}
//----------------------------------------------------------------------------------------------------------------------------------------
//====================================================== END Initialization ==============================================================

//========================================================  Main Programs ================================================================
//-------------------------------------------------- executeCommand( String, int ) -------------------------------------------------------
/*
 *  Simple function to execute an already confirmed valid instruction.
 *
 *    INPUTS:
 *      - cmd : a string command. already confirmed to be a valid request of ON, OFF, or STATUS.
 *      - pin : a integer corresponding to the pin that drives the respective relay on the arduino shield.
 *
 *    OUTPUTS:
 *      - none.
 */
void executeCommand( String cmd, int pin ){
  if( cmd.equalsIgnoreCase( "ON" ) ){
    digitalWrite( pin, HIGH );
    Serial.println( String( "!RELAY:" + String( identify_relay( pin) ) + " ON" ) );
  } else if ( cmd.equalsIgnoreCase( "OFF" ) ){
    digitalWrite( pin, LOW );
    Serial.println( String( "!RELAY:" + String( identify_relay( pin) ) + " OFF" ) );
  } else if ( cmd.equalsIgnoreCase( "STATUS" ) ){
    Serial.println( String( "!STATUS: " + String( digitalRead( pin ) ) + "" ) );
  } else {
    Serial.println( "!Something went very wrong." );
  }

}
//----------------------------------------------------------------------------------------------------------------------------------------

//------------------------------------------------------ indentify_pin( int ) ------------------------------------------------------------
/*
 * The Relay numbers do not correspond to the pin controlling the relay's on/off status.  This function requires a relay number as input
 * and then it will process the relay number to convert it into the pin number to be driven.
 *
 *    INPUT:
 *      - relay : an integer number corresponding to the ardunio shield relay number.
 *
 *    OUTPUT:
 *      - an integer number corresponding with the PIN number for the respective relay number.
 */
int identify_pin( int relay ){
  switch ( relay ){
    case 1:
      return ( relay_1 );
    case 2:
      return( relay_2 );
    case 3:
      return( relay_3 );
    case 4:
      return( relay_4 );
    default:
      return 0;
  }
}
//----------------------------------------------------------------------------------------------------------------------------------------

//------------------------------------------------------ indentify_relay( int ) ----------------------------------------------------------
/*
 * The Relay numbers do not correspond to the pin controlling the relay's on/off status.  This function requires a pin number as input
 * and then it will process the number to convert it into the relay number.
 *
 *    INPUT:
 *      - relay : an integer number corresponding to the ardunio pin number.
 *
 *    OUTPUT:
 *      - an integer number corresponding with the PIN number for the respective relay number.
 */
int identify_relay( int pin ){
  if( pin == relay_1 ){
    return 1;
  } else if ( pin == relay_2 ){
    return 2;
  } else if ( pin == relay_3 ){
    return 3;
  } else if ( pin == relay_4 ){
    return 4;
  } else {
    return 0;
  }
}
//----------------------------------------------------------------------------------------------------------------------------------------

//------------------------------------------------------------ checkIO() -----------------------------------------------------------------
/*
 * Scans the serial monitor when an input is decected... Reads the input and converts the input to a string to be processed
 * in the decodeMessage subroutine.
 */
String checkIO(){
  if( Serial.available() > 0 ){
    String str; char c;
    while( Serial.available() ){
      c = Serial.read();                                          // read each character one by one from the serial monitor
      str = String( str + c );                                    // and compile a string of the input.
      delay(25);
    }
    str.trim();                                                   // nix off any added spaces, only supports 1 word commands currently
    return str;
  }
}
//----------------------------------------------------------------------------------------------------------------------------------------

//---------------------------------------------------- decodeMessage( string ) -----------------------------------------------------------
/*
 * Pass a string via serial port to the arduino and parse out its arguments to issue a command.  The expected structure will be
 *
 *              command 'space' relay-number
 *
 *              Valid Commands:
 *                    1. ON : Set a relay on the shield to ON
 *                    2. OFF : Set a relay on the shield to OFF
 *                    3. STATUS : Check the status of a relay on the sheild.
 *
 *              Valid Relays:
 *                    1. Relay 1 : Corresponds to PIN 4
 *                    2. RELAY 2 : Corresponds to PIN 7
 *                    3. RELAY 3 : Corresponds to PIN 8
 *                    4. RELAY 4 : Corresponds to PIN 12
 *
 *              INPUT:
 *                - str : an input instruction provided by the serial port in the form of:
 *                          <command> <delimiter> <relay number>.
 *              OUTPUT:
 *                - none.
 */
void decodeMessage( String str ){
  int pin, delimiter_index, valid_cmd = 0, valid_relay = 0;
  String relay, cmd, delimiter = " ";

  // Check to see if a delimiter is present, if not the message is not valid
  if ( str.indexOf( delimiter ) != -1 ) {
    delimiter_index = str.indexOf( delimiter );

    // Check command validity
    cmd = str.substring( 0, delimiter_index );
    if ( cmd.equalsIgnoreCase( "ON" ) || cmd.equalsIgnoreCase( "OFF" ) || cmd.equalsIgnoreCase( "STATUS" ) ) {
      valid_cmd = 1;
    } else {
      valid_cmd = 0;
      Serial.println( "!Invalid command." );
    }

    // Check relay validity
    relay = str.substring( delimiter_index + 1 );
    if( relay.equalsIgnoreCase( "1" ) || relay.equalsIgnoreCase( "2" ) || relay.equalsIgnoreCase( "3" ) || relay.equalsIgnoreCase( "4" ) ){
      valid_relay = 1;
    } else {
      valid_relay = 0;
      Serial.println( "!Invalid relay." );
    }

    // Issue command, only if valid
    if( valid_cmd && valid_relay ){
      pin = identify_pin( relay.toInt() );
      executeCommand( cmd, pin );
    }

  } else {
    Serial.println( "!Invalid message structure." );
  }
}
//----------------------------------------------------------------------------------------------------------------------------------------
//======================================================== End Main Programs =============================================================

//========================================================== Serial Monitor ==============================================================
//--------------------------------------------------------------- loop() -----------------------------------------------------------------
/*
 *  Essentially this function will just montior for available serial input from an external source.  Once serial data is available
 *  the monitor will use other functions to parse the message and issue commands.
 */
void loop() {
  // put your main code here, to run repeatedly:
  if( !Serial.available() ){
    // wait for input, do nothing.
    delay( 20 );
  }
  else{
    decodeMessage( checkIO() );
  }
}
//----------------------------------------------------------------------------------------------------------------------------------------
//======================================================== End Serial Monitor ============================================================
