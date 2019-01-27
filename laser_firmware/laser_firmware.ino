
#include <Servo.h>

Servo roll_servo;  // side to side
Servo pitch_servo; // up down

#define ROLL_PWM_PIN 2
#define PITCH_PWM_PIN 3
#define RELAY_PIN 5

#define CMD_ROLL  100
#define CMD_PITCH 101
#define CMD_POWER 102

#define BUF_LEN 16
byte message_buf[BUF_LEN];

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);
  roll_servo.attach(ROLL_PWM_PIN);
  pitch_servo.attach(PITCH_PWM_PIN);
  pinMode(RELAY_PIN, OUTPUT);
  Serial.write(0xFF);
}

void loop() {
  if (Serial.readBytes(message_buf, 2) == 2) {
    switch(message_buf[0]) {
      case CMD_ROLL: roll_servo.write(message_buf[1]); break;
      case CMD_PITCH: pitch_servo.write(message_buf[1]); break;
      case CMD_POWER: digitalWrite(RELAY_PIN, (message_buf[1])?HIGH:LOW); break;
      default : break; 
      //Serial.write(message_buf, 2);
    }
  } else {
    Serial.flush();
  }
}
