#include <SoftwareSerial.h>
#include <Servo.h>

class Robot {
  public:
    SoftwareSerial btSerial;
    Servo servo1;
    Servo servo2;
    Servo servo3;
    Servo servo4;
    Servo servo5;
    int lastPosition[5] = {175, 90, 90, 90, 90};  // Array para almacenar las últimas posiciones de los servos
    int delayTime = 2;  // Retraso inicial para el movimiento del servo
    int servoPin1;
    int servoPin2;
    int servoPin3;
    int servoPin4;
    int servoPin5;
  
  public:
    Robot(int btRxPin, int btTxPin, int servoPin1, int servoPin2, int servoPin3, int servoPin4, int servoPin5) : btSerial(btRxPin, btTxPin), servo1(), servo2(), servo3(), servo4(), servo5() {
      this->servoPin1 = servoPin1;
      this->servoPin2 = servoPin2;
      this->servoPin3 = servoPin3;
      this->servoPin4 = servoPin4;
      this->servoPin5 = servoPin5;
    }
    
    void begin() {
      btSerial.begin(115200);
      Serial.begin(115200);
      servo1.attach(this->servoPin1);
      servo2.attach(this->servoPin2);
      servo3.attach(this->servoPin3);
      servo4.attach(this->servoPin4);
      servo5.attach(this->servoPin5);
      servo1.write(175);
      servo2.write(90);
      servo3.write(90);
      servo4.write(90);
      servo5.write(90);

    }
    
    void processCommands() {
      if (btSerial.available()) {

        String input = btSerial.readStringUntil('\n');
        int servoNumber = 0;
        int angle = 0;
        String servoNumberString = input.substring(0, input.indexOf(':'));
        String angleString = input.substring(input.indexOf(':') + 1);
        Serial.println(input);

        if (isInteger(servoNumberString) && isInteger(angleString)) {
           servoNumber = input.substring(0, input.indexOf(':')).toInt();
            angle = input.substring(input.indexOf(':') + 1).toInt();
            if (servoNumber > 1 && servoNumber < 6) {
              moveServo(servoNumber, angle);
            }
        } else {
          managerOption(input);
        }
        Serial.println("OK");
        btSerial.println("OK");
      }
    }

  private:
    bool isInteger(const String& str) {
      if (str.length() == 0) {
        return false;
      }

      for (size_t i = 0; i < str.length(); i++) {
        if (!isDigit(str.charAt(i))) {
          return false;
        }
      }

      return true;
    }

  private:
    void abrir() {
      moveServo(1, 170);  // Mover el servo1 a 170 grados
    }
  private:
    void cerrar() {
      moveServo(1, 143);  // Mover el servo1 a 150 grados
    }

  private:
    void managerOption(String order) {
      Serial.println(order);
      if (order == "open") {
        abrir();
      } else if (order == "close") {
        cerrar();
      }else if (order == "V1"){
        delayTime = 2;
       }else if (order == "V2"){
        delayTime = 10;
       }else if (order == "V3"){
        delayTime = 15;
       }
       else if (order == "V4"){
        delayTime = 25;
       }
       else if (order == "V5"){
        delayTime = 40;
       }
    }
    
  private:
    void moveServo(int servoNumber, int angle) {
      Servo* servo = nullptr;
      
      switch (servoNumber) {
        case 1:
          servo = &servo1;
          break;
        case 2:
          servo = &servo2;
          break;
        case 3:
          servo = &servo3;
          break;
        case 4:
          servo = &servo4;
          break;
        case 5:
          servo = &servo5;
          break;
      }
      
      if (servo != nullptr) {
        int lastAngle = lastPosition[servoNumber - 1];  // Obtener la última posición del servo
        int increment = (angle > lastAngle) ? 1 : -1;  // Determinar si se debe incrementar o decrementar el ángulo
        int currentAngle = lastAngle;
        unsigned long previousMillis = millis();
        unsigned long interval = delayTime;  // Intervalo de tiempo entre cada incremento de ángulo
        // Realizar el movimiento gradual del servo
         while (currentAngle != angle) {
            unsigned long currentMillis = millis();
            if (currentMillis - previousMillis >= interval) {
              currentAngle += increment;
              servo->write(currentAngle);
              previousMillis = currentMillis;
            }
          }


        lastPosition[servoNumber - 1] = angle;  // Almacenar la última posición del servo
      }
    }
};

Robot robot(10, 11, 2, 3, 4, 5, 6);  // Configura los pines del HC-05 y los servos

void setup() {
  robot.begin();
}

void loop() {
  robot.processCommands();
}
