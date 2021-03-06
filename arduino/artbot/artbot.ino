#include <ServoTimer2.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

String inputString;
Adafruit_BNO055 bno = Adafruit_BNO055(55);

// Wires - purple BT receive
//         brown BT transmit

int motSpeed = 255;     
// turn off turn when debugging int turnSpeed = 100;
int turnSpeed = 0;
int Bweight = 0;
int speedA = 6;          // pin 6 sets the speed of motor A (this is a PWM output)
int speedB = 9;          // pin 9 sets the speed of motor B (this is a PWM output) 
int dirA = 8;            // pin 8 sets the direction of motor A
int dirB = 7;            // pin 7 sets the direction of motor B

//int servoPin = A0;
int servoPin = 5;
ServoTimer2 penServo;

// number of ms to rotate in a complete circle
int fullRotationMSecs = 11811;
// number of ms to drive the full length of the sheet
int fullLengthMSecs = 5000;
// time to wait (ms) before polling angle when turning
//int turnDelay = 10;
int turnDelay = 100;

// 10000 drives for 405mm
// so 5000 should go 202.5mm


char charBuf[50];

// define the direction of motor rotation - this allows you change the  direction without effecting the hardware
int fwdA  =  HIGH;         // this sketch assumes that motor A is the right-hand motor of your robot (looking from the back of your robot)
int revA  =  LOW;        // (note this should ALWAYS be opposite the fwdA)
int fwdB  =  LOW;         //
int revB  =  HIGH;        // (note this should ALWAYS be opposite the fwdB)

void stop() {                              // stop: force both motor speeds to 0 (low)
   digitalWrite (speedA, LOW); 
   digitalWrite (speedB, LOW);
}

void forward(int dist, int vel) {          // forward: both motors set to forward direction
   digitalWrite(dirA, fwdA); 
   digitalWrite(dirB, fwdB);
   analogWrite(speedA, vel);   // both motors set to same speed
   analogWrite(speedB, vel+Bweight); 
   delay(dist);                // wait for a while (dist in mSeconds)
   stop();
}

void reverse(int dist, int vel) {          // reverse: both motors set to reverse direction
   digitalWrite(dirA, revA); 
   digitalWrite(dirB, revB);
   analogWrite(speedA, vel);   // both motors set to same speed
   analogWrite(speedB, vel+Bweight); 
   delay(dist);                // wait for a while (dist in mSeconds)  
   stop();   
}
             
void rot_cw (int angle, int vel, boolean dontStop=false) {         // rotate clock-wise: right-hand motor reversed, left-hand motor forward
   digitalWrite(dirA, revA); 
   digitalWrite(dirB, fwdB);
   analogWrite(speedA, vel);   // both motors set to same speed
   analogWrite(speedB, vel+Bweight); 
   if (!dontStop) { 
      delay(angle);               // wait for a while (angle in mSeconds)  
      stop();
   }            
}
             
void rot_ccw (int angle, int vel, boolean dontStop=false) {        // rotate counter-clock-wise: right-hand motor forward, left-hand motor reversed
   digitalWrite(dirA, fwdA); 
   digitalWrite(dirB, revB);
   analogWrite(speedA, vel);   // both motors set to same speed
   analogWrite(speedB, vel+Bweight); 
   if (!dontStop) { 
      delay(angle);               // wait for a while (angle in mSeconds)              
      stop();
   }
}

void rot_ang(float relativeAngle) {
  // relative angle should be between -180 and 180 degrees
   sensors_event_t event; 
   bno.getEvent(&event);
  
   float startingAngle = event.orientation.x;
   float targetAngle = fmod(startingAngle+relativeAngle, 360.0);
   if (targetAngle < 0.0) {
      targetAngle += 360.0;
   }
   Serial.println("Starting angle: ");
   Serial.println(startingAngle);
   Serial.println("relative angle: ");
   Serial.println(relativeAngle);
   Serial.println("target angle: ");
   Serial.println(targetAngle);
   

   // start spinning
   float currentAngle = startingAngle;
   bool turnIncludesWrap = false;
   bool wrapped = false;
   if (relativeAngle > 0.0) {
      if (targetAngle < startingAngle) {
         turnIncludesWrap = true;
      }

      Serial.println("Starting clockwise turn!");
      rot_cw(0, turnSpeed, true);

      while ((!turnIncludesWrap && currentAngle < targetAngle) || (turnIncludesWrap && ((!wrapped && currentAngle > targetAngle) || (wrapped && currentAngle < targetAngle)))) {
         delay(turnDelay);
         bno.getEvent(&event);
         currentAngle = event.orientation.x;
         Serial.println("current angle...");
         Serial.println(currentAngle);
         Serial.print("first clause = "); Serial.println((int)(!turnIncludesWrap && currentAngle < targetAngle));
         Serial.print("second clause = "); Serial.println((int)(turnIncludesWrap && ((!wrapped && currentAngle > targetAngle) || (wrapped && currentAngle < targetAngle))));
         Serial.print("third clause = "); Serial.println((int)((!wrapped && currentAngle > targetAngle) || (wrapped && currentAngle < targetAngle)));
         Serial.print("fourth clause = "); Serial.println((int)(!wrapped && currentAngle > targetAngle));
         Serial.print("fifth clause = "); Serial.println((int)(wrapped && currentAngle < targetAngle));

         //  ( turn includes a wrap      ) AND  ( gone round the 0 degree point )
         if (turnIncludesWrap && (currentAngle < startingAngle-2.0)) {
            Serial.println("wrapped!");
            wrapped = true;
         }
      }
   } else if (relativeAngle < 0.0) {
      if (targetAngle > startingAngle) {
         turnIncludesWrap = true;
      }

      Serial.println("Starting anticlockwise turn!");
      rot_ccw(0, turnSpeed, true);

      while ((!turnIncludesWrap && currentAngle > targetAngle) || (turnIncludesWrap && ((!wrapped && currentAngle < targetAngle) || (wrapped && currentAngle > targetAngle)))) {
         delay(turnDelay);
         bno.getEvent(&event);
         currentAngle = event.orientation.x;
         Serial.println("current angle...");
         Serial.println(currentAngle);
         Serial.print("first clause = "); Serial.println((int)(!turnIncludesWrap && currentAngle > targetAngle));
         Serial.print("second clause = "); Serial.println((int)(turnIncludesWrap && ((!wrapped && currentAngle < targetAngle) || (wrapped && currentAngle > targetAngle))));
         Serial.print("third clause = "); Serial.println((int)((!wrapped && currentAngle < targetAngle) || (wrapped && currentAngle > targetAngle)));
         Serial.print("fourth clause = "); Serial.println((int)(!wrapped && currentAngle < targetAngle));
         Serial.print("fifth clause = "); Serial.println((int)(wrapped && currentAngle > targetAngle));
         if (turnIncludesWrap && (currentAngle > startingAngle+2.0)) {
            Serial.println("wrapped!");
            wrapped = true;
         }
      }
   } else {
      // altready at target angle, do nothing
      // or could set up an angle threshold, like 0.5 degrees and also do nothing
   }

   Serial.println("Turn finished!");
   Serial.print("final state clockwise. first clause = "); Serial.println((targetAngle > startingAngle && currentAngle < targetAngle));
   Serial.print("final state clockwise. second clause = "); Serial.println((targetAngle < startingAngle && currentAngle > targetAngle));
   Serial.print("final state clockwise. third clause = "); Serial.println((wrapped && currentAngle < targetAngle));
   Serial.print("final state anticlockwise. first clause = "); Serial.println((targetAngle < startingAngle && currentAngle > targetAngle));
   Serial.print("final state anticlockwise. second clause = "); Serial.println((targetAngle > startingAngle && currentAngle < targetAngle));
   Serial.print("final state anticlockwise. third clause = "); Serial.println((wrapped && currentAngle < targetAngle));         
   stop();
}
  


void setup() {
   // setup motor pins
   pinMode (dirA, OUTPUT);         
   pinMode (dirB, OUTPUT); 
   pinMode (speedA, OUTPUT); 
   pinMode (speedB, OUTPUT); 
   
   penServo.attach(servoPin);

   // setup orientation sensor
   if(!bno.begin())
   {
      /* There was a problem detecting the BNO055 ... check your connections */
      Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
      while(1);
   }
   delay(1000);
   bno.setExtCrystalUse(true);
  
   Serial.begin(9600);
   //Serial.write("Power On\n");
}

// message formats. <num>is any integer
// C<num> - rotate clockwise for <num>
// A<num> - rotate anticlockwise for <num>
// F<num> - drive forwards for <num>
// R<num> - drive backwards for <num>
// P<num> - set pen servo position to <num> (from 0 to 180)
// T<float> - turn by this relative angle
void processInputString() {
   if (inputString.charAt(0) == 'C') {
      // turn 'C'lockwise for some amount of ms
      inputString.substring(1).toCharArray(charBuf, 50);
      int cwMS = atoi(charBuf);
      
      rot_cw(cwMS, motSpeed);
      
      Serial.println("DONE");
   } else if (inputString.charAt(0) == 'A') {
      // turn 'A'nti-clockwise for some amount of ms
      inputString.substring(1).toCharArray(charBuf, 50);
      int acwMS = atoi(charBuf);
      
      rot_ccw(acwMS, motSpeed);
      
      Serial.println("DONE");
   } else if (inputString.charAt(0) == 'F') {
      // drive 'F'orward for some amount of ms
      inputString.substring(1).toCharArray(charBuf, 50);
      int forwardMS = atoi(charBuf);
      
      forward(forwardMS, motSpeed);
      
      Serial.println("DONE");
   } else if (inputString.charAt(0) == 'R') {
      // drive 'R'everse for some amount of ms
      inputString.substring(1).toCharArray(charBuf, 50);
      int reverseMS = atoi(charBuf);
      
      reverse(reverseMS, motSpeed);
      
      Serial.println("DONE");
   } else if (inputString.charAt(0) == 'P') {
      // set 'P'en to angle
      inputString.substring(1).toCharArray(charBuf, 50);
      int penAngle = atoi(charBuf);
      
      penServo.write(penAngle);
      
      Serial.println("DONE");
   } else if (inputString.charAt(0) == 'T') {
      // 'T' turn by the angle given (floating point number)
      inputString.substring(1).toCharArray(charBuf, 50);
      float turnAng = atof(charBuf);

      rot_ang(turnAng);

      Serial.println("DONE");
   } else {
      Serial.write("unknown message: ");
      Serial.println(inputString);
   }

   inputString = "";
}

void loop()
{
    /* Get a new sensor event */ 
  sensors_event_t event; 
  bno.getEvent(&event);
  
  /* Display the floating point data */
  /*Serial.print("X: ");
  Serial.print(event.orientation.x, 4);
  Serial.print("\tY: ");
  Serial.print(event.orientation.y, 4);
  Serial.print("\tZ: ");
  Serial.print(event.orientation.z, 4);
  Serial.println("");*/
  
  delay(100);
  
   while (Serial.available() > 0) {
      char received = Serial.read();
      
      // process message when new line character is received
      if (received == '\n' || received == '\r') {
         processInputString();
      } else {
         // only add in the char if it's not a line term
         inputString += received;      
      }
   }
}   

