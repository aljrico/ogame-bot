OGame Bot
=========

Automates OGame expeditions and farm attacks using Playwright.

Quick start
-----------

Follow these steps one by one. Don't skip any!

### Step 1: Install uv (the package manager)

If you don't have `uv` installed yet, open your terminal and run the install
command for your system:

**Mac / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** (open PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then close and reopen your terminal so the `uv` command becomes available.

### Step 2: Clone the project and install dependencies

```bash
git clone <repo-url>
cd ogame-bot
uv sync
uv run playwright install
```

`uv sync` installs all the Python packages the bot needs. The second command
installs the browser that the bot will use to play OGame for you.

### Step 3: Create your personal config files

The bot needs to know **which planet** to launch from and **which ships** to
send. Example config files are included -- you just need to copy them and fill
in your own values.

> **Only want expeditions?** If you don't care about farm attacks and just want
> to send expeditions, you only need `config/expeditions.json`. You can skip
> creating the farming config entirely -- just make sure to always run the bot
> with `--expeditions-only` (shown in Step 4).

Run these commands to create your config files (skip the farming one if you
only want expeditions):

**Mac / Linux:**
```bash
cp config/expeditions.example.json config/expeditions.json
cp config/farming.example.json config/farming.json      # optional, only for farming
```

**Windows** (Command Prompt or PowerShell):
```cmd
copy config\expeditions.example.json config\expeditions.json
copy config\farming.example.json config\farming.json      &REM optional, only for farming
```

Now open `config/expeditions.json` in any text editor. It looks like this:

```json
{
  "planet": "YourPlanet",
  "ships": {
    "Segador": 1,
    "Explorador": 1,
    "Destructor": 1,
    "Sonda de Espionaje": 1,
    "Nave grande de carga": 500
  }
}
```

Change the values to match your game:

- **`planet`**: Replace `"YourPlanet"` with the name of your planet in OGame
  (exactly as it appears in the game, e.g. `"Homeworld"`).
- **`ships`**: Set the number next to each ship type to however many you want
  to send per expedition. The ship names must match what you see in OGame
  (they depend on your language setting).

Then do the same for `config/farming.json`:

```json
{
  "planet": "YourPlanet",
  "ships": {
    "Nave pequeña de carga": 100
  },
  "targets": [
    [1, 1, 1],
    [1, 1, 2]
  ]
}
```

- **`planet`**: Same as above -- the planet you want to attack from.
- **`ships`**: The ships to send on each farm attack.
- **`targets`**: A list of coordinates to attack. Each target is written as
  `[galaxy, system, position]`. You can add as many as you want.

Your config files are personal and won't be uploaded if you push code -- they
are excluded from git on purpose.

### Step 4: Run the bot

```bash
uv run python main.py
```

The first time you run it, a browser window will open and you'll need to log in
to OGame manually. After that, the bot remembers your session.

To run **only expeditions** (skip farm attacks):

```bash
uv run python main.py --expeditions-only
```

Configuration
-------------

Environment variables (optional, loaded via `.env`):

- `CHROME_USER_DATA_DIR`: custom Chrome profile directory
- `OGAME_LANGUAGE`: language code (default `es_ES`)
- `HEADLESS`: `true` or `false` (default `false`)
- `SLOW_MO`: delay between actions in ms (default `50`)
- `EXPEDITIONS_CONFIG`: path to expeditions JSON (default `config/expeditions.json`)
- `FARMING_CONFIG`: path to farming JSON (default `config/farming.json`)

Example `.env`
--------------

```bash
OGAME_LANGUAGE=es_ES
HEADLESS=false
SLOW_MO=50
# CHROME_USER_DATA_DIR=/Users/yourname/Library/Application Support/Google/Chrome
```

Cron example
------------

```bash
0 * * * * cd /Users/alejandrojimenezrico/Code/ogame-bot && /usr/bin/env -i HOME=/Users/alejandrojimenezrico PATH=/usr/bin:/bin:/usr/local/bin uv run python main.py >> /tmp/ogame-bot.log 2>&1
```

Windows scheduled task example
------------------------------

Create a task that runs every 2 hours (replace the repo path with yours):

```bat
schtasks /Create /SC HOURLY /MO 2 /TN "OGameBot" /TR "C:\Windows\System32\cmd.exe /c cd /d C:\path\to\ogame-bot && uv run python main.py >> %TEMP%\ogame-bot.log 2>&1"
```

Run it once immediately:

```bat
schtasks /Run /TN "OGameBot"
```

Notes
-----

- The default Chrome profile is stored at `~/.ogame-bot/chrome-profile`. Do not share it.
- Use a dedicated bot profile to avoid mixing with your main browser session.
