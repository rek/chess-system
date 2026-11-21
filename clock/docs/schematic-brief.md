Build a battery-powered two-player chess clock on an Arduino Nano. The hardware below is already working on a breadboard. Keep the parts and pin assignments exactly as listed. I want a clean wiring diagram, a parts list, and, if you can make one, a PCB layout (Gerber or KiCad export) so I can replace the loose wires with a board.

PARTS (already owned)
- Arduino Nano clone: ATmega328P, 5V logic, 16 MHz, CH340 USB chip, old bootloader (FQBN arduino:avr:nano:cpu=atmega328old).
- MAX7219 4-digit 7-segment display module. It has two 5-pin header rows (VCC, GND, DIN or DOUT, LOAD/CS, CLK). The rows are wired in parallel except DIN on the input row and DOUT on the output row. The module has decimal points but no colon.
- 4 momentary push buttons: Player 1, Player 2, Start/Pause, Mode.
- Seeed LiPo Rider Plus: LiPo charger plus 5V boost converter, USB-C charging, built-in on/off switch.
- 600 mAh single-cell LiPo battery (3.7V nominal).

PIN MAP (do not change)
- Display VCC -> Nano 5V
- Display GND -> Nano GND
- Display DIN -> D11 (hardware SPI MOSI)
- Display LOAD/CS -> D10
- Display CLK -> D13 (hardware SPI SCK)
- Mode button -> D2 to GND
- Start/Pause button -> D3 to GND
- Spare button (front panel, no function yet) -> D4 to GND
- Player 2 button -> D5 to GND
- Player 1 button -> D6 to GND
- Buttons use the Nano's internal pull-ups (INPUT_PULLUP), so no external resistors.

POWER
- LiPo -> Rider Plus battery connector.
- Rider 5V out -> Nano 5V pin. Rider GND -> Nano GND.
- The Rider's switch is the clock's power switch.
- Feeding the 5V pin bypasses the Nano's regulator. The Rider should be switched off whenever the Nano's USB is plugged in.
- Expected draw is about 80 mA.

PLANNED ADDITIONS (please include in the design, on free pins)
- Piezo buzzer that sounds when a player runs out of time.
- Two LEDs, one per player, showing whose turn it is (with current-limiting resistors).
- Optional second MAX7219 display, daisy-chained from the first display's DOUT so it needs no extra Nano pins (one display per player).

PHYSICAL LAYOUT
- 3D-printed case. The Player 1 and Player 2 buttons sit at opposite ends of the top, roughly 15-20 cm apart. The display sits in the middle. Start and Mode are small buttons near the display.
- The board should either have connectors (JST-XH or similar) for the off-board buttons, display and power, or be shaped as the top panel with the buttons and display mounted directly on it. Show me both if you can.
- Prefer through-hole parts and socketed modules (Nano and display plug in) so I can hand-solder and swap parts.

CLOCK BEHAVIOUR (firmware already written; reproduce it if you generate code)
- States: READY, RUNNING, PAUSED, FLAGGED.
- READY: Mode cycles presets 10 min, 5 min, 3+2, 5+3, 15+10, 1 min. After a change it shows the increment for 1 second as "--05". Pressing a player button starts the OPPONENT's clock. Start begins Player 1's clock.
- RUNNING: pressing your own button ends your turn, adds the increment, and starts the opponent's clock. Start pauses. Holding Mode shows the other player's time.
- PAUSED: the display blinks slowly. Start resumes.
- FLAGGED: the player at zero blinks "00.0". Sound the buzzer here once it is added.
- Hold Start for 1.5 s at any time to reset.
- Display format "MM.SS" (the decimal point stands in for the colon). Under 1 minute it shows "SS.t" with tenths. The far-left decimal point lights when Player 1's time is shown, the far-right one for Player 2.
- Button debounce 25 ms. Display brightness 4 of 15. The MAX7219 is driven directly over SPI (no library) in decode mode.

WHAT I WANT BACK
1. A wiring diagram with every connection, including the buzzer, the two LEDs and the second display.
2. A parts list with values (LED resistors, buzzer type, connectors).
3. A PCB layout or a KiCad/Gerber export, if you support it. If you don't, say so plainly.
4. Anything in my design you think is wrong or risky.
