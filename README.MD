# Nautobot Cleaner

### what it does?

Cleaner isnt the best word, but it helps to import data that network importer does not do well in a multi-tenant enviroment.

### How it works?

Uses a mix of Napalm and Netmiko to parse vlan information and create it in Nautobot

### How to use?

Instantiate the class and pass in selected devices and vlan group


```python
from importdevicevlans import NautobotCleaner

nbc = NautobotCleaner()
nbc.importdevicevlans(selected_devices=[
    'device1-fqdn',
    'device2-fqdn',
],
    group='vlan-group')
```
```mermaid
graph TD
start
yes
no
q1['Is device IOSXE?']
q2['Is device layer 2?']

start-->q1
start-->q2

q1-->no
no-->a1['Pull VLANS from device DB']
a1-->a2['reverse getvlan dict']
a2-->a3['create vlans, assign to group and link to interface']
a3-->a4['link VLAN to SVI and prefix']
a4-->a5['Parse port channels and link vlans']
a5-->a6['Link Import IPv6']

q1-->yes
yes-->b1['parse only port channels']
b1-->b2['create vlans, assign to group and link to interface']
b2-->b3['link VLAN to SVI and prefix']
b3-->b4['Import IPv6']

q2-->c1['Pull VLANS from device DB']
c1-->c2['reverse getvlan dict']
c2-->c3['create vlans, assign to group and link to interface']
c3-->c4['link VLAN to SVI and prefix']
```