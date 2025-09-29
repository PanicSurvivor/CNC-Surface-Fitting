G90          ; absolute positioning
G21          ; units in millimeters

G0  Z5
G0  X50.000 Y10.000    ; move above start point
G01 Z-0.50 F600        ; plunge to cut depth

; star outline (center ~ (50,50), within 0..100 mm)
G01 X59.405 Y37.056
G01 X88.042 Y37.639
G01 X65.217 Y54.944
G01 X73.511 Y82.361
G01 X50.000 Y66.000
G01 X26.489 Y82.361
G01 X34.783 Y54.944
G01 X11.958 Y37.639
G01 X40.595 Y37.056
G01 X50.000 Y10.000     ; close shape

G0  Z5
G0  X0 Y0
M30