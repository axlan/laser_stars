
#include <Servo.h>

Servo yaw_servo;  // side to side
Servo pitch_servo; // up down

#define BUF_LEN 16
byte message_buf[BUF_LEN];

void setup() {
  Serial.begin(9600);
  //Serial.setTimeout(100*1000);
  yaw_servo.attach(9);  // attaches the servo on pin 9 to the servo object
  pitch_servo.attach(10);  // attaches the servo on pin 9 to the servo object
}

void loop() {

    if (Serial.readBytes(message_buf, 2) == 2) {
      yaw_servo.write(message_buf[0]);
      pitch_servo.write(message_buf[1]);
      Serial.println(message_buf[0]);
      Serial.println(message_buf[1]);
    }
    
  
//   int val = Serial.parseInt();
//   myservo.write(val);
//   Serial.println(val);
//    for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
//    // in steps of 1 degree
//      myservo.write(pos);              // tell servo to go to position in variable 'pos'
//      delay(150);                       // waits 15ms for the servo to reach the position
//    }
//    for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
//      myservo.write(pos);              // tell servo to go to position in variable 'pos'
//      delay(150);                       // waits 15ms for the servo to reach the position
//    }
}

