#include <SPI.h>
#include <Ethernet.h>

byte mac[] = { 0x90, 0xA2, 0xDA, 0x11, 0x28, 0xCB }; 
IPAddress ip(192, 168, 1, 2); 

EthernetServer server(80);
const int ledPin = 9;

void setup() {
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW); 
  Ethernet.begin(mac, ip);
  delay(1000);
  server.begin();
}

void loop() {
  EthernetClient client = server.available();
  if (client) {
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        
        // 1. HANDLE TOGGLE COMMANDS FROM OCS
        if (c == 'H') {
          digitalWrite(ledPin, HIGH);
          client.println("ACK");
        } 
        else if (c == 'L') {
          digitalWrite(ledPin, LOW);
          client.println("ACK");
        }
        // 2. HANDLE RAW TELEMETRY DATA REQUESTS FROM OCS
        else if (c == 'R') {
          // Replace these mock calculations with your actual raw sensor reads
          // For example: float cable1 = analogRead(A0) * (5.0 / 1023.0);
//          float cable1 = 12.45 + (random(-5, 5) / 10.0); 
          float analog0 = analogRead(A0) * (5.0 / 1023.0);
          float analog1 = analogRead(A1) * (5.0 / 1023.0);
          float analog2 = analogRead(A2) * (5.0 / 1023.0);
          float analog3 = analogRead(A3) * (5.0 / 1023.0);
          float analog4 = analogRead(A4) * (5.0 / 1023.0);
          float analog5 = analogRead(A5) * (5.0 / 1023.0);
          int digital0 = digitalRead(0);
          int digital1 = digitalRead(1);
          int digital2 = digitalRead(2);
          int digital3 = digitalRead(3);
          int digital4 = digitalRead(4);
          int digital5 = digitalRead(5);
          int digital6 = digitalRead(6);
          int digital7 = digitalRead(7);
          int digital8 = digitalRead(8);
          int digital9 = digitalRead(9);
          float cablefake = 12.45 + (random(-5, 5) / 10.0);
          
          // Print comma-separated values matching agent.py requirements
          client.print(analog0);
          client.print(",");
          client.print(analog1);
          client.print(",");
          client.print(analog2);
          client.print(",");
          client.print(analog3);
          client.print(",");
          client.print(analog4);
          client.print(",");
          client.print(analog5);
          client.print(",");
          client.print(digital0);
          client.print(",");
          client.print(digital1);
          client.print(",");
          client.print(digital2);
          client.print(",");
          client.print(digital3);
          client.print(",");
          client.print(digital4);
          client.print(",");
          client.print(digital5);
          client.print(",");
          client.print(digital6);
          client.print(",");
          client.print(digital7);
          client.print(",");
          client.print(digital8);
          client.print(",");
          client.print(digital9);
          client.print(",");
          client.print(cablefake);
          client.print(",");

  
                    
//          client.println(cable8);

        }
        
        delay(1);
        client.stop(); // Clear network socket for next scan
      }
    }
  }
}
