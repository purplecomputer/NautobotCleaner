#Angelo.Poggi

from config import nautobot_url, nautobot_token, device_platform_connection,device_username,device_password
import pynautobot
import napalm
import gevent
from gevent import monkey

class NautobotCleaner:
    def __init__(self,device):
        '''creates a connection to nautobot and device during instantiation of class'''
        self.pynb = pynautobot.api(nautobot_url, token=nautobot_token)
        try:
            self.device = self.pynb.dcim.devices.get(name=str(device))
        except Exception as e:
            raise Exception(e)
        #grab the platform to find the driver
        self.device_os = device_platform_connection[str(self.device.platform)]['os']
        self.driver = napalm.get_network_driver(self.device_os)
        self.device_init = self.driver(
            hostname=str(self.device.name),
            username=str(device_username),
            password=str(device_password),
            optional_args={
                'secret': str(device_password)
            }
        )

    def getvlans(self):
        '''Queries device info and grabs VLAN'''
        #give me that data
        self.device_init.open()
        return self.device_init.get_vlans()


    def nautobotvlanimport(self,group,vlans):
        '''dumps them vlans into them groups and links it to the SVI created'''
        #did you give me good data?
        if not isinstance(vlans, dict):
            raise("Vlans is not a dict")

        #Check that group exsists & create it if it dont
        vlangroup = self.pynb.ipam.vlan_groups.get(name=str(group))
        if vlangroup is None:
            vlangroup = self.pynb.ipam.vlan_groups.create(
                name=str(group)
            )

        for vid,vidinfo in vlans.items():
            vlan = self.pynb.ipam.vlans.get(
                vid=str(vid),
                group_id=vlangroup.id
            )
            if vlan is None:
                vlan = self.pynb.ipam.vlans.create(
                    name=str(vid),
                    vid=vid,
                    group=str(vlangroup.id),
                    site=self.device.site.id,
                    status='active'
                )
            #Tie vlan to the interface
            for interfaces in vidinfo['interfaces']:
                interface = self.pynb.dcim.interfaces.get(
                    name=str(interfaces),
                    device_id = self.device.id
                )
                print(interface.mode)
                if interface is None:
                    print("interface not on device - skipping")
                    continue
                elif interface.mode == None:
                    '''if the interface exsist but has no vlans or mode set
                    update and link curent vlan to vlan we are
                    set the interface as access'''
                    print('setting int as untagged')
                    interface.update(
                        mode = 'Access',
                        untagged_vlan= vlan.id
                    )
                elif interface.mode == 'Access' and interface.untagged_vlan is None:
                    '''if the interface exsists and was set untagged by network importer w/ no vlans'''
                    print('linking vlan to untagged int')
                    interface.update(
                        mode = 'Access',
                        untagged_vlans = vlan.id
                    )
                elif interface.mode == 'Access' and interface.untagged_vlan is not None:
                    '''if the interface exsists and it currently has an untagged vlan'''
                    print('int has more than one vlan configured - setting to tagged')
                    interface.update(
                        mode = 'Tagged',
                        tagged_vlans = vlan.id
                    )
                elif interface.mode == 'Tagged':
                    '''if interface exsist and already has more than two vlans
                    update with additional vlan tag'''
                    print('adding additional vlan to tagged int')
                    interface.update(
                        tagged_vlans = vlan.id
                    )



if __name__ == "__main__":
    nbc = NautobotCleaner('dsc121.gsc.webair.net')
    vlan_data = nbc.getvlans()
    nbc.nautobotvlanimport('ds121', vlan_data)

