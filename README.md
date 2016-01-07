# smarthome-yamaha
Plugin to control Yamaha RX-V and RX-S receivers, e.g.: Power On / Off, select input, set volume and mute.

## Notes
This plugin is still under development, but for myself in daily use. I use the plugin to switch on the Yamaha RX-S600 and RX-V475 series and to change the input. Depending on the input I also adapt the volume which works fine for me. Mute is unused in my logics.

Feel free to comment, send me compatible devices and to fill issues.

As far as I know all RX-V4xx, RX-V5xx, RX-V6xx, RX-V7xx and RX-Sxxx series share the same API, so they should be ok with this plugin.


## Prerequisite
The following python packages need to be installed on your system:

- requests
- lxml

Those packages can be installed using:

<pre>
# Debian based
sudo apt-get install python3-lxml python3-requests

#Arch Linux
sudo pacman -S python-lxml python-requests

# Fedora
sudo dnf install python3-lxml python3-requests
</pre>

## Installation
<pre>
cd smarthome.py directory
cd plugins
git clone https://github.com/rthill/yamaha.git
</pre>

### plugin.conf
<pre>
[yamaha]
    class_name = Yamaha
    class_path = plugins.yamaha
</pre>

### items.conf

<pre>
[mm]
    [[gf]]
        [[[living]]]
            [[[[yamaha]]]]
                yamaha_host = 192.168.178.186
                [[[[[power]]]]]
                    type = bool
                    yamaha_cmd = power
                    enforce_updates = True
                [[[[[volume]]]]]
                    type = num
                    yamaha_cmd = volume
                    enforce_updates = True
                [[[[[mute]]]]]
                    type = bool
                    yamaha_cmd = mute
                    enforce_updates = True
                [[[[[input]]]]]
                    type = str
                    yamaha_cmd = input
                    enforce_updates = True
                [[[[[state]]]]]
                    type = str
                    yamaha_cmd = state
</pre>

### Example CLI usage
<pre>
> up mm.gf.living.yamaha.power=True
> up mm.gf.living.yamaha.input=AV4 
> up mm.gf.living.yamaha.volume=-600 # This is equivalent for -60.0dB
> up mm.gf.living.yamaha.input=HDMI1
> up mm.gf.living.yamaha.mute=True
> up mm.gf.living.yamaha.mute=False
> up mm.gf.living.yamaha.power=False
</pre>
