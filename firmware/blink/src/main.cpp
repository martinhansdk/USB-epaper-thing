#include <Arduino.h>
#include "usb_epaper_board.h"



void setup() {
  pinMode(LED0_PIN, OUTPUT);
  pinMode(LED1_PIN, OUTPUT);
}

void loop() {
  digitalToggle(LED0_PIN);
  delay(1000);
}
