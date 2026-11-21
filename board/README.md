# Electronic chessboard

Senses where the pieces are so moves can be recorded. The chess clock (`../clock/`) was the
stepping stone for this.

## Starting idea (from the clock notes)
- Hall-effect sensors under each square, magnets in the pieces.
- Raspberry Pi Pico as the controller. Not yet decided against staying on the Nano.

## Status
Planning. Nothing built yet.

## Open questions
- What should the board do with a move: show it, log it, send it to an app or a chess site?
- Detect only "a piece is here", or also which piece?
- Board size, and how many sensors to read (64 squares needs multiplexing on either chip).
- Does it connect to the clock?
