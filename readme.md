# PyMirror Modules

This is my collection of modules for PyMirror.

### ghost

Scare the kids. This moduel will haunt your mirror every day at midnight.

Sample config:

```
[ghost]
source = modules/ghost/ghost.py
top = 0
left = 0
width = -1
height = -1
scare_frame_counter = 3
```

### skanetrafiken (work in progress)

Display the bus schedule of the local bus service here in the south of Sweden. This is work in progress as it currently is hard coded on showing buses that leaves the place where I live...

Sample config:

```
[skanetrafiken]
source = pymirror-modules/skanetrafiken.py
top = 20
left = 0
width = -1
height = 115
text_size = 40
# number of minutes you need to get to the bus
min_bus_time = 15
```

### skolmaten

If you live in Sweden and have an interest in today's special in the school canteen, this is a module for you.

Sample config:

```
[skolmaten]
source = pymirror-modules/skolmaten.py
top = -200
left = 0
width = -1
height = 80
text_size = 30
# Name of school
school_name = nyvangskolan
```

### spacepeeps

Keep track of the number of people in space.

Sample config:

```
[spacepeeps]
source = modules/spacepeeps/spacepeeps.py
top = -130
left = 550
width = 100
height = 120
text_size = 120
```

### temperature

Read outside temperature from a Swedish Transport Authority weather station of yout choice. Not very useful if you don't live in Sweden.

Sample config:

```
[temperature]
source = modules/temperature/temperature.py
top = -130
left = 10
width = 300
height = 75
# ID of Trafikverket's weather station to pull data from. Can be found by some reverse engineering.
station_id = 1208
```

### time

Display local time.

Sample config:

```
[time]
source = modules/time.py
top = -130
left = -290
width = 290
height = 75
```

### weather

Display weather forecast as predicted by SMHI (Swedish national weather service). Requires you to specify location of mirror in the global PyMirror config:

```
latitude = 57.133123
longitude = 17.1321
```

Sample config:

```
[weather]
source = pymirror-modules/weather/weather.py
top = 200
left = 0
width = -1
height = 100
text_size = 40
# Don't display hours 02..05 as we're asleep then :)
skip_night = True
```
