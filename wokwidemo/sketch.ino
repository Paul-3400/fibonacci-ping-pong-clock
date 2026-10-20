/*
 * 🏓 Fibonacci Ping-Pong-Ball-Uhr – Wokwi-DEMO (Schnecken-Layout, 5 Taster)
 *
 * Demo-Variante für Demonstrationszwecke. Das Raster steht hochkant als
 * "sich oeffnende Fibonacci-Schnecke" (5 Spalten x 8 Zeilen):
 *
 *      Feld A (Wert 5, 25 Baelle): Zeilen 0-4, Spalten 0-4  (oben, volle Breite)
 *      Feld B (Wert 3,  9 Baelle): Zeilen 5-7, Spalten 0-2  (unten links)
 *      Feld C (Wert 2,  4 Baelle): Zeilen 6-7, Spalten 3-4  (unten rechts,
 *                                  np33, np34, np38, np39)
 *      Feld D (Wert 1,  1 Ball):   Zeile 5,   Spalte 3      (np28)
 *      Feld E (Wert 1,  1 Ball):   Zeile 5,   Spalte 4      (np29)
 *
 * Die Schnecke oeffnet sich vom Zentrum (D/E, Zeile 5) nach aussen:
 * D -> E -> C (darunter) -> B (links) -> A (oben).
 * Mapping: LED-Index = Zeile*5 + Spalte
 *
 * Taster:
 *   Taster 1 (D0/GPIO1):  Felder A-E durchschalten
 *   Taster 2 (D1/GPIO2):  Handbetrieb - +1 Minute
 *   Taster 3 (D6/GPIO43): Handbetrieb - +5 Minuten
 *   Taster 4 (D7/GPIO44): Handbetrieb - +1 Stunde
 *   Taster 5 (D8/GPIO7):  Normalbetrieb - NTP-Zeit, Fibonacci-Anzeige
 *
 * Handbetrieb = Zeitversatz (Offset) zur NTP-Zeit; die Uhr laeuft dabei
 * weiter. Taster 5 setzt den Offset zurueck. Ohne NTP-Sync laeuft eine
 * virtuelle Uhr ab 12:00:00.
 *
 * Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 20.10.2026
 * Lizenz: GNU GPL v2 - abgeleitet von der Arduino-Fibonacci-Uhr
 *          von Philippe Chretien (https://github.com/pchretien/fibo)
 *          Layout-Anordnung inspiriert durch Nerdiy (https://www.nerdiy.de/fibonacciClock)
 */

#include <WiFi.h>
#include <time.h>
#include <Adafruit_NeoPixel.h>
#include <TM1637Display.h>

// ---------- Pins (XIAO ESP32-S3) ----------
#define LED_PIN 4
#define TM_CLK  5
#define TM_DIO  6
#define NUM_LEDS 40

// Taster (alle gegen GND, INPUT_PULLUP, gedrueckt = LOW)
#define BTN_FIELD 1    // D0/GPIO1  - Taster 1
#define BTN_MIN   2    // D1/GPIO2  - Taster 2
#define BTN_MIN5  43   // D6/GPIO43 - Taster 3
#define BTN_HOUR  44   // D7/GPIO44 - Taster 4
#define BTN_NORM  7    // D8/GPIO7  - Taster 5

#define TZ_INFO "CET-1CEST-2,M3.5.0,M10.5.0/3"

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);
TM1637Display display(TM_CLK, TM_DIO);

// ---------- Farben ----------
const uint32_t C_HOURS = Adafruit_NeoPixel::Color(255, 0, 0);    // rot
const uint32_t C_MIN   = Adafruit_NeoPixel::Color(0, 255, 0);    // gruen
const uint32_t C_BOTH  = Adafruit_NeoPixel::Color(0, 0, 255);    // blau
const uint32_t C_WHITE = Adafruit_NeoPixel::Color(255, 255, 255);

// ---------- Fibonacci-Felder im Schnecken-Layout ----------
// Mapping: LED-Index = Zeile*5 + Spalte (5 Spalten x 8 Zeilen, hochkant)
// A: 5x5 oben | B: 3x3 unten links | C: 2x2 unten rechts (unter D/E)
// D: Zeile 5, Spalte 3 (np28) | E: Zeile 5, Spalte 4 (np29)
const uint8_t FIELD_VALUE[5] = {5, 3, 2, 1, 1};   // A, B, C, D, E
uint8_t fieldLeds[5][25];
uint8_t fieldCount[5];

void buildFields() {
  uint8_t n = 0;
  for (uint8_t r = 0; r < 5; r++)                    // A: Zeilen 0-4, Spalten 0-4
    for (uint8_t c = 0; c < 5; c++) fieldLeds[0][n++] = r * 5 + c;
  fieldCount[0] = n;
  n = 0;
  for (uint8_t r = 5; r < 8; r++)                    // B: Zeilen 5-7, Spalten 0-2
    for (uint8_t c = 0; c < 3; c++) fieldLeds[1][n++] = r * 5 + c;
  fieldCount[1] = n;
  n = 0;
  for (uint8_t r = 6; r < 8; r++)                    // C: Zeilen 6-7, Spalten 3-4
    for (uint8_t c = 3; c < 5; c++) fieldLeds[2][n++] = r * 5 + c;   // np33, np34, np38, np39
  fieldCount[2] = n;
  fieldLeds[3][0] = 5 * 5 + 3;                       // D: Zeile 5, Spalte 3 (np28)
  fieldCount[3] = 1;
  fieldLeds[4][0] = 5 * 5 + 4;                       // E: Zeile 5, Spalte 4 (np29)
  fieldCount[4] = 1;
}

// Alle gueltigen Fibonacci-Kombinationen fuer 1..12 (setBits-Portierung)
const char* COMBINATIONS[13] = {
  NULL,             // Index 0 unbenutzt
  "0|1",            // 1
  "2|01",           // 2
  "3|02|12",        // 3
  "03|13|012",      // 4
  "4|23|013",       // 5
  "04|14|023|123",  // 6
  "24|014|0123",    // 7
  "34|024|124",     // 8
  "034|134",        // 9
  "234|0134",       // 10
  "0234|1234",      // 11
  "01234"           // 12
};

uint8_t pickCombination(uint8_t value, uint8_t* out) {
  if (value < 1) value = 1;
  if (value > 12) value = 12;
  const char* table = COMBINATIONS[value];
  uint8_t count = 1;
  for (const char* p = table; *p; p++)
    if (*p == '|') count++;
  uint8_t pick = random(count);
  const char* s = table;
  for (uint8_t i = 0; i < pick; i++) {
    while (*s && *s != '|') s++;
    if (*s == '|') s++;
  }
  uint8_t n = 0;
  while (*s && *s != '|')
    out[n++] = *s++ - '0';
  return n;
}

// Setzt die 40 LEDs gemaess Stunde/Minute (Zufallszerlegung wie im Original)
void updateFibonacci(int hh, int mm) {
  int h12 = hh % 12;
  if (h12 == 0) h12 = 12;
  int mu = mm / 5;
  if (mu == 0) mu = 12;

  uint8_t hc[5], mc[5];
  uint8_t hn = pickCombination(h12, hc);
  uint8_t mn = pickCombination(mu, mc);

  uint8_t bits[5] = {0, 0, 0, 0, 0};  // Bit 1 = Stunde, Bit 2 = Minute
  for (uint8_t i = 0; i < hn; i++) bits[hc[i]] |= 0x01;
  for (uint8_t i = 0; i < mn; i++) bits[mc[i]] |= 0x02;

  for (uint8_t f = 0; f < 5; f++) {
    uint32_t col = 0;
    if (bits[f] == 0x01)      col = C_HOURS;
    else if (bits[f] == 0x02) col = C_MIN;
    else if (bits[f] == 0x03) col = C_BOTH;
    for (uint8_t i = 0; i < fieldCount[f]; i++)
      strip.setPixelColor(fieldLeds[f][i], col);
  }
  strip.show();
}

// ---------- Demo-Zustand ----------
enum DemoMode { MODE_NORMAL, MODE_MANUAL, MODE_FIELD };
DemoMode mode = MODE_NORMAL;
int8_t fieldIdx = -1;
long timeOffset = 0;
const unsigned long virtualBase = 12UL * 3600UL;

bool ntpFresh() {
  return time(NULL) > 1700000000L;
}

void getNow(int &h, int &m, int &s) {
  if (ntpFresh()) {
    time_t now = time(NULL) + timeOffset;
    struct tm t;
    localtime_r(&now, &t);
    h = t.tm_hour; m = t.tm_min; s = t.tm_sec;
  } else {
    unsigned long secs = virtualBase + millis() / 1000 + (unsigned long)timeOffset;
    h = (secs / 3600) % 24;
    m = (secs / 60) % 60;
    s = secs % 60;
  }
}

// ---------- Taster ----------
const uint8_t BTN_PIN[5] = {BTN_FIELD, BTN_MIN, BTN_MIN5, BTN_HOUR, BTN_NORM};
bool lastState[5] = {false, false, false, false, false};
unsigned long lastMs[5] = {0, 0, 0, 0, 0};

void pulse(uint8_t f, uint32_t col) {
  for (uint8_t i = 0; i < fieldCount[f]; i++)
    strip.setPixelColor(fieldLeds[f][i], col);
  strip.show();
}

// TM1637 zeigt Feld-Buchstabe + Wert, z.B. "C 2"
void showField(int idx) {
  static const uint8_t LETTERS[5] = {0x77, 0x7C, 0x39, 0x5E, 0x79};  // A b C d E
  uint8_t segs[4] = {LETTERS[idx], 0, display.encodeDigit(FIELD_VALUE[idx]), 0};
  display.setSegments(segs);
}

void renderFieldMode() {
  strip.clear();
  pulse(fieldIdx, C_WHITE);
  showField(fieldIdx);
}

void onButton(uint8_t btn) {
  switch (btn) {
    case 1:  // Felder durchschalten
      if (mode != MODE_FIELD) { mode = MODE_FIELD; fieldIdx = -1; }
      fieldIdx = (fieldIdx + 1) % 5;
      renderFieldMode();
      Serial.printf("Taster 1: Feld %c - Wert %d, %d LEDs\n",
                    'A' + fieldIdx, FIELD_VALUE[fieldIdx], fieldCount[fieldIdx]);
      break;
    case 2:  // +1 Minute
      mode = MODE_MANUAL;
      timeOffset += 60;
      Serial.println("Taster 2: Handbetrieb, +1 Minute");
      break;
    case 3:  // +5 Minuten
      mode = MODE_MANUAL;
      timeOffset += 300;
      Serial.println("Taster 3: Handbetrieb, +5 Minuten");
      break;
    case 4:  // +1 Stunde
      mode = MODE_MANUAL;
      timeOffset += 3600;
      Serial.println("Taster 4: Handbetrieb, +1 Stunde");
      break;
    case 5:  // Normalbetrieb
      mode = MODE_NORMAL;
      timeOffset = 0;
      configTzTime(TZ_INFO, "pool.ntp.org");
      Serial.println("Taster 5: Normalbetrieb (NTP-Zeit, Offset zurueckgesetzt)");
      break;
  }
}

void handleButtons() {
  for (uint8_t i = 0; i < 5; i++) {
    bool cur = (digitalRead(BTN_PIN[i]) == LOW);
    if (cur && !lastState[i] && millis() - lastMs[i] > 150) {
      lastMs[i] = millis();
      onButton(i + 1);
    }
    lastState[i] = cur;
  }
}

// ---------- Self-Test ----------
void selfTest() {
  const uint32_t cols[5] = {
    Adafruit_NeoPixel::Color(255, 0, 0),    // A rot
    Adafruit_NeoPixel::Color(0, 255, 0),    // B gruen
    Adafruit_NeoPixel::Color(0, 0, 255),    // C blau
    Adafruit_NeoPixel::Color(255, 255, 0),  // D gelb
    Adafruit_NeoPixel::Color(255, 0, 255)   // E magenta
  };
  for (uint8_t f = 0; f < 5; f++) {
    pulse(f, cols[f]);
    delay(400);
  }
  strip.clear();
  strip.show();
}

void setup() {
  Serial.begin(115200);
  randomSeed((uint32_t)micros());
  buildFields();

  strip.begin();
  strip.setBrightness(90);
  strip.show();

  display.setBrightness(7);
  display.clear();

  const uint8_t BTN_PIN_LOCAL[5] = {BTN_FIELD, BTN_MIN, BTN_MIN5, BTN_HOUR, BTN_NORM};
  for (uint8_t i = 0; i < 5; i++) pinMode(BTN_PIN_LOCAL[i], INPUT_PULLUP);

  Serial.println("Fibonacci Ping-Pong-Ball-Uhr (DEMO, Schnecken-Layout) startet...");
  selfTest();

  Serial.println("Verbinde WLAN (Wokwi-GUEST)...");
  WiFi.begin("Wokwi-GUEST", "");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 8000) {
    delay(100);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("NTP-Sync: pool.ntp.org (Europe/Zurich)...");
    configTzTime(TZ_INFO, "pool.ntp.org");
  } else {
    Serial.println("Kein WLAN - virtuelle Uhr ab 12:00 aktiv.");
  }
}

int lastSlot = -1;
int lastSec  = -1;

void loop() {
  handleButtons();

  int h, m, s;
  getNow(h, m, s);

  if (mode == MODE_FIELD) {
    lastSlot = -1;
    lastSec = -1;
  } else {
    int slot = h * 12 + m / 5;
    if (slot != lastSlot) {
      lastSlot = slot;
      updateFibonacci(h, m);
    }
    if (s != lastSec) {
      lastSec = s;
      uint8_t dots = (s % 2) ? 0x40 : 0x00;
      display.showNumberDecEx(h * 100 + m, dots, true);
    }
  }

  static unsigned long lastNtpTry = 0;
  if (!ntpFresh() && millis() - lastNtpTry > 10000) {
    lastNtpTry = millis();
    if (WiFi.status() != WL_CONNECTED) WiFi.begin("Wokwi-GUEST", "");
    configTzTime(TZ_INFO, "pool.ntp.org");
  }

  delay(50);
}
