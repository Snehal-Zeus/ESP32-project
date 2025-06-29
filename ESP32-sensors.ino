#include <Wire.h>
#include <LiquidCrystal.h>
#include <Adafruit_ADXL345_U.h>

// LCD (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(33, 32, 14, 27, 26, 25);

// ADXL345
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(123);

// Pins
#define FLAME_SENSOR_PIN 13
#define GAS_SENSOR_PIN 34
#define TRIG_PIN 18
#define ECHO_PIN 19
#define FLOW_SENSOR_PIN 23
#define BUZZER_PIN 12
#define LED_WARNING 4
#define LED_CRITICAL 5

// Flow
volatile int flowPulseCount = 0;
unsigned long lastFlowMillis = 0;
float flowRate = 0.0;

void IRAM_ATTR countFlowPulse() {
  flowPulseCount++;
}

void setup() {
  Serial.begin(115200);
  lcd.begin(16, 2);
  lcd.print("Disaster Monitor");

  pinMode(FLAME_SENSOR_PIN, INPUT);
  pinMode(GAS_SENSOR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_WARNING, OUTPUT);
  pinMode(LED_CRITICAL, OUTPUT);

  // Blink test for LEDs
  digitalWrite(LED_WARNING, HIGH);
  digitalWrite(LED_CRITICAL, HIGH);
  delay(1000);
  digitalWrite(LED_WARNING, LOW);
  digitalWrite(LED_CRITICAL, LOW);

  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), countFlowPulse, RISING);

  if (!accel.begin()) {
    Serial.println("No ADXL345 found");
    while (1);
  }

  accel.setRange(ADXL345_RANGE_2_G);
  delay(2000); // MQ2 warm-up time
}

void loop() {
  bool warning = false;
  bool critical = false;

  // 1. Flame
  bool flameDetected = digitalRead(FLAME_SENSOR_PIN) == LOW;

  // 2. Gas
  int gasLevel = analogRead(GAS_SENSOR_PIN);
  int gasStatus = (gasLevel > 2000) ? 2 : (gasLevel > 1500) ? 1 : 0;

  // 3. Ultrasonic
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  float distance = duration * 0.034 / 2.0;
  float distanceToWater = (distance < 2 || distance > 400) ? -1 : distance;
  bool floodingDetected = (distanceToWater < 90 && distanceToWater > 0);

  // 4. Flow Rate
  unsigned long currentMillis = millis();
  if (currentMillis - lastFlowMillis >= 1000) {
    flowRate = (flowPulseCount / 7.5); // L/min approx
    flowPulseCount = 0;
    lastFlowMillis = currentMillis;
  }

  if (flowRate > 10.0) {
    critical = true;
  } else if (flowRate > 5.0) {
    warning = true;
  }

  // 5. Earthquake
  sensors_event_t event;
  accel.getEvent(&event);
  float accel_x = event.acceleration.x;
  float accel_y = event.acceleration.y;
  float accel_z = event.acceleration.z;
  float accMag = sqrt(accel_x * accel_x + accel_y * accel_y + accel_z * accel_z);
  float quakeMagnitude = abs(accMag - 9.8);
  quakeMagnitude = constrain(quakeMagnitude, 0, 5);
  bool earthquakeDetected = quakeMagnitude > 1.5;

  // Set warning and critical flags
  if (flameDetected) critical = true;
  if (gasStatus == 2) critical = true;
  else if (gasStatus == 1) warning = true;

  if (distanceToWater > 0) {
    if (distanceToWater < 30) critical = true;
    else if (distanceToWater < 60) warning = true;
  }

  if (earthquakeDetected) critical = true;

  // Outputs
  digitalWrite(LED_WARNING, warning ? HIGH : LOW);
  digitalWrite(LED_CRITICAL, critical ? HIGH : LOW);

  if (critical) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(2000);
    digitalWrite(BUZZER_PIN, LOW);
  } else if (warning) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(1000);
    digitalWrite(BUZZER_PIN, LOW);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }

  // LCD Display
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Gas:"); lcd.print(gasStatus);
  lcd.print(" Fire:"); lcd.print(flameDetected);

  lcd.setCursor(0, 1);
  if (distanceToWater > 0) {
    lcd.print("Dist:"); lcd.print((int)distanceToWater); lcd.print("cm");
  } else {
    lcd.print("Dist:ERR ");
  }
  lcd.setCursor(9, 1);
  lcd.print("F:"); lcd.print((int)flowRate);

  // Serial Monitor Output (human-readable logs)
  Serial.print("Raw Gas Level: "); Serial.println(gasLevel);
  Serial.println(flowRate > 10 ? "Flow Critical." : flowRate > 5 ? "Flow Warning." : "Flow Normal.");

  Serial.print("Flame: "); Serial.print(flameDetected);
  Serial.print(", Gas: "); Serial.print(gasLevel);
  Serial.print(", Dist: "); Serial.print(distanceToWater, 2); Serial.print(" cm");
  Serial.print(", Flow: "); Serial.print(flowRate, 2);
  Serial.print(", Quake: "); Serial.println(quakeMagnitude, 2);

  Serial.print("Warning: "); Serial.print(warning);
  Serial.print(", Critical: "); Serial.println(critical);

  // CSV Serial Output (for logging)

  Serial.print(accel_x); Serial.print(",");
  Serial.print(accel_y); Serial.print(",");
  Serial.print(accel_z); Serial.print(",");
  Serial.print(gasLevel); Serial.print(",");
  Serial.print(gasStatus); Serial.print(",");
  Serial.print(flameDetected); Serial.print(",");
  Serial.print(floodingDetected); Serial.print(",");
  Serial.print(distanceToWater); Serial.print(",");
  Serial.print(earthquakeDetected); Serial.print(",");
  Serial.print(quakeMagnitude); Serial.print(",");
  Serial.println(flowRate);

  delay(1000);
}
