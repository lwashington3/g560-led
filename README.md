# Logitech G560 Gaming Speakers LED control

Allows you to control the LED lighting of your G560 Gaming Speakers programmatically.
Inspired by and based on [g810-led](https://github.com/MatMoul/g810-led) and
[g203-led](https://github.com/smasty/g203-led) and [g403-led](https://github.com/stelcheck/g403-led).

## Requirements

- Python 3.5+
- PyUSB 1.0.2+
- **Root privileges**

## Installation

1. Clone the repository: `git clone https://github.com/smasty/g203-led.git`
2. Prepare _virtualenv_: `virtualenv ./env`
3. Install dependencies: `env/bin/pip install -r requirements.txt`
4. Run (as root) the script for your model:
    - `sudo ./g203-led.py solid 00FFFF`
    - `sudo ./g403-led.py solid 00FFFF`
    - `sudo ./g560-led.py solid 00FFFF`

Note that the g560 has four independent lights: currently this script will set all
to the same color.

## Usage

Make sure to use the script for your mouse model. The example below uses the `g560-led` script.

```text
Usage:
    g560-led solid {color} - Solid color mode
    g560-led cycle [{rate} [{brightness}]] - Cycle through all colors
    g560-led breathe {color} [{rate} [{brightness}]] - Single color breathing
    g560-led intro {on|off} - Enable/disable startup effect / **NOT SUPPORTED**

Arguments:
    Color: RRGGBB (RGB hex value)
    Rate: 100-60000 (Number of milliseconds. Default: 10000ms)
    Brightness: 0-100 (Percentage. Default: 100%)
```
