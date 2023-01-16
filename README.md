# Netcam
Application to visualize Raspberry pi cameras over a local network.

![Example of four cameras visualized concurrently](cover.jpg)

## Usage
Firstly, the file `pi_server.py` must be run in all Rasperries having a camera
module in the network. Right now, it only works with the legacy driver. Support
for libcamera will be considered once its Python API becomes stable.

Secondly, the `test_visualization.py` can be run to visualize the streams from the
Raspberry pi cameras. Running with no arguments, prompts us to introduce a list
of IP directions corresponding to the ones of the cameras, as well as the
geometry in which we wish to visualize them. If invoked with an argument,
it will be taken as the name of the JSON configuration file, containing
the following two fields
```json
{
    "geometry": ["n", "m"]
    "dirs"    : ["ip_0", "ip_1", "...", "ip_n*m"]
}
```
which are just the geometry and IP directions of our cameras.

## API support
The basic camera control over IP is done through the class `CameraWatcher`.
It allows to connect to `n` cameras and "watch" them simultaneously, receiving
images from each one of them. The basic workflow with this class is as follows
```python
from src import CameraWatcher

# We connect to a single camera at (host, port)
cams = CameraWatcher(1)
# We set a shutter speed, if needed, to maintain a constant illumination between shots
cams.watch_camera(("192.168.1.83", 8000), shutter_speed=33)

# We get the image of camera 0, which returns a IOBytes with a JPEG encoded image
img_buffer = cams.get_image(0)

# We can directly save the image to disk
with open("test.jpeg", "wb") as f:
    f.write(img_buffer.read())
```

