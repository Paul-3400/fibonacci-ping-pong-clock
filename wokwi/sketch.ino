/*
 * 🏓 Fibonacci Ping-Pong-Ball-Uhr – Wokwi-Prototyp
 *
 * Board:    Seeed XIAO ESP32-S3 (Prototyp-Ersatz für den Raspberry Pi Zero WH)
 * Anzeige:  40x WS2812B NeoPixel im 5x8-Schnecken-Raster hochkant
 *           (1 LED pro Ping-Pong-Ball), Fibonacci-Felder A(5) B(3) C(2) D(1) E(1)
 *           Feld A (5x5) oben | B (3x3) unten links | C (2x2) unten rechts
 *           D (Zeile 5, Spalte 3 / np28) | E (Zeile 5, Spalte 4 / np29)
 * Klartext: TM1637 – im Wokwi-Sim 4-stellig (HH:MM); Ziel: 6-stellig (HH:MM:SS)
 * Zeit:     NTP über WLAN (Wokwi-GUEST, pool.ntp.org), Zeitzone Europe/Zurich
 *
 * Mapping: LED-Index = Zeile*5 + Spalte (5 Spalten × 8 Zeilen)
 *
 * Die fünf Taster der Ziel-Uhr sind im Prototyp nicht enthalten –
 * die Demo-Variante mit Tastern liegt im Ordner wokwidemo/.
 *
 * Beim Start leuchtet jedes Feld kurz nacheinander (Self-Test) –
 * damit lassen sich Verdrahtung und Feld-Mapping in einem Durchgang prüfen.
 *
 * Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 20.10.2026
 * Lizenz: GNU GPL v2 – abgeleitet von der Arduino-Fibonacci-Uhr
 *          von Philippe Chretien (https://github.com/pchretien/fibo)
 *          Layout-Anordnung inspiriert durch Nerdiy (https://www.nerdiy.de/fibonacciClock)
 */

#include <WiFi.h>
#include <time.h>
#include <Adafruit_NeoPixel.h>
#include <TM1637Display.h>

// ---------- Pins (XIAO ESP32-S3) ----------
// D3 = GPIO4: NeoPixel-Daten | D4 = GPIO5: TM1637 CLK | D5 = GPIO6: TM1637 DIO
#define LED_PIN 4
#define TM_CLK  5
#define TM_DIO  6
#define NUM_LEDS 40

// Zeitzone Europe/Zurich: CET/CEST mit EU-Umstellregeln
#define TZ_INFO "CET-1CEST-2,M3.5.0,M10.5.0/3"

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);
TM1637Display display(TM_CLK, TM_DIO);

// ---------- Farben (wie in der Bauanleitung) ----------
const uint32_t C_HOURS = Adafruit_NeoPixel::Color(255, 0, 0);  // rot
const uint32_t C_MIN   = Adafruit_NeoPixel::Color(0, 255, 0);  // gruen
const uint32_t C_BOTH  = Adafruit_NeoPixel::Color(0, 0, 255);  // blau

// ---------- Fibonacci-Felder (Mapping: LED-Index = Zeile*5 + Spalte) ----------
// A: Zeilen 0-4, Spalten 0-4 (25 LEDs) | B: Zeilen 5-7, Spalten 0-2 (9)
// C: Zeilen 6-7, Spalten 3-4 (4)        | D: Zeile 5, Spalte 3 (np28)
// E: Zeile 5, Spalte 4 (np29)
const uint8_t FIELD_VALUE[5] = {5, 3, 2, 1, 1};
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
    for (uint8_t c = 3; c < 5; c++) fieldLeds[2][n++] = r * 5 + c;
  fieldCount[2] = n;
  fieldLeds[3][0] = 5 * 5 + 3;                       // D: Zeile 5, Spalte 3 (np28)
  fieldCount[3] = 1;
  fieldLeds[4][0] = 5 * 5 + 4;                       // E: Zeile 5, Spalte 4 (np29)
  fieldCount[4] = 1;
}

// Alle gueltigen Fibonacci-Kombinationen fuer 1..12, portiert aus der
// Original-Firmware (setBits). Feldindizes 0-4, '|' trennt Alternativen.
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

// Waehlt per Zufall eine gueltige Kombination, liefert die Feldindizes zurueck
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
  int mu = mm / 5;          // 5-Minuten-Schritte
  if (mu == 0) mu = 12;     // Minute 0 => 12 in Fibonacci-Darstellung

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

// Ein Feld kurz aufleuchten lassen
void pulse(uint8_t f, uint32_t col) {
  for (uint8_t i = 0; i < fieldCount[f]; i++)
    strip.setPixelColor(fieldLeds[f][i], col);
  strip.show();
}

// Self-Test beim Start: prueft Verdrahtung und Feld-Mapping in einem Durchgang
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
  strip.setBrightness(90);  // ~35%: 40 LEDs schonen (am Aufbau waere Vollelweiss ~2.4 A)
  strip.show();             // alle aus

  display.setBrightness(7);
  display.clear();

  Serial.println("Fibonacci Ping-Pong-Ball-Uhr (Prototyp, Schnecken-Layout) startet...");
  selfTest();

  Serial.println("Verbinde WLAN (Wokwi-GUEST)...");
  WiFi.begin("Wokwi-GUEST", "");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(100);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WLAN ok, IP: ");
    Serial.println(WiFi.localIP());
    Serial.println("NTP-Sync: pool.ntp.org (Europe/Zurich)...");
    configTzTime(TZ_INFO, "pool.ntp.org");
  } else {
    Serial.println("WLAN fehlgeschlagen - laufe ohne NTP weiter.");
  }
}

int lastSlot = -1;  // wechselt alle 5 Minuten
int lastSec  = -1;

void loop() {
  struct tm t;
  if (getLocalTime(&t, 50)) {
    // Fibonacci-Anzeige nur bei 5-Minuten-Wechsel neu wuerfeln
    int slot = t.tm_hour * 12 + t.tm_min / 5;
    if (slot != lastSlot) {
      lastSlot = slot;
      updateFibonacci(t.tm_hour, t.tm_min);
      Serial.printf("Zeit %02d:%02d -> Fibonacci neu gesetzt\n", t.tm_hour, t.tm_min);
    }
    // TM1637: jede Sekunde, Doppelpunkt blinkt
    if (t.tm_sec != lastSec) {
      lastSec = t.tm_sec;
      uint8_t dots = (t.tm_sec % 2) ? 0x40 : 0x00;
      display.showNumberDecEx(t.tm_hour * 100 + t.tm_min, dots, true);
    }
  } else {
    // Noch keine Zeit: '----' anzeigen und NTP gelegentlich erneut versuchen
    const uint8_t dash[4] = {SEG_G, SEG_G, SEG_G, SEG_G};
    display.setSegments(dash);
    static unsigned long lastTry = 0;
    if (millis() - lastTry > 5000) {
      lastTry = millis();
      if (WiFi.status() != WL_CONNECTED) WiFi.begin("Wokwi-GUEST", "");
      configTzTime(TZ_INFO, "pool.ntp.org");
    }
  }
  delay(200);
}
