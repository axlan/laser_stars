# laser_stars
Project for drawing on glow in the dark stars with a laser

Tool for drawing simple patterns: `python3 -m laser_stars.line_drawer` this saves on exit to out/line_draw.mvs

Tool for running pattern file: `python3 -m laser_stars.run_controller configs/simulator1.json movements/heart.mvs`

## Todo
 * Improve servo control firmware (jerky movement / servos move one after other / sub-degree resolution)
 * Add recording mode that uses long exposure like recording instead of tracking line https://www.pyimagesearch.com/2017/08/14/long-exposure-with-opencv-and-python/
 * Modify hardware for blue laser
 * Scale and position laser based on vision and markers on ceiling
 * Light up stars

## Dependancies
`sudo apt-get install python3-opencv`

## Reference Projects

https://github.com/AnumSheraz/OpenCV-laser-tracking-gun

https://github.com/bradmontgomery/python-laser-tracker

## Hardware Notes

Laser:
 * Wavelength :405nm
 * Power output: 20mW 
 * Laser Shape:Dot 
 * Operating Voltage:DC3V-5V
 * Operating Current: <50mA 
 * Operating temperature: 0 - 30 °C
 * Beam Effect: 120 dergee Line Effect.
 * Duty Circle:10 minutes on and 1 seconds off.
 * Size:13mm(D)*42(L) mm
 * Packing:1PCS


DF05BB Servo:
 * Voltage: +4.8-6.0 V
 * Current: 160mA (4.8V)
 * Torque Size: 3.5kg · cm (4.8V); 5.1kg · cm (6.0V)
 * No load speed: 0.17 seconds / 60 degrees (4.8V); 0.4 sec / 60 degrees (6.0V)
 * Operating temperature: 0 ℃ ~ 60 ℃
 * Dead Set: 20us
 * Size: 40.2 X 20.2 X 43.2mm
 * Weight: 42g
 * brown or black = ground (GND, battery negative terminal)
 * red = servo power (Vservo, battery positive terminal)
 * orange, yellow, white, or blue = servo control signal line
