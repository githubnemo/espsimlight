# ESP simlight

ESP simlight is a tool to, given a layout file, run arbitrary Python code
to simulate your addressable light effect lambda!

No more endless experimentation in ESPHome and wasting the flash of your
hardware away. Speed up your iteration cycles with the hot-reloading
visualizer that is called **ESP simlight**.

Example video:

https://raw.githubusercontent.com/githubnemo/espsimlight/master/assets/example.webm

## Installation

    poetry install

## Running

There are examples you can test:

	espsimlight examples/desklamp.shape examples/running_light.py

Try editing `running_light.py` while the simulation is running.

The shape file is just an ASCII file with all the
