# Chess system

A custom electronic chessboard, built in steps. Each project has its own folder with a
`README.md` (notes, wiring, status) and, where relevant, a `BOM.md` (parts list).

| Folder | Project | Status |
|---|---|---|
| [`clock/`](clock/README.md) | Two-player chess clock on an Arduino Nano | Working; battery power planned |
| [`board/`](board/README.md) | Electronic chessboard that senses piece moves | Planning |

## Layout inside each project
- `firmware/`: one folder per sketch (Arduino needs the folder name to match the `.ino`).
- `power/`, `case/`, `docs/`: schematics, printed parts and design notes.
- Only `.ino` and `.md` files are tracked in git. CAD files (Blender, STL, KiCad) stay local.
