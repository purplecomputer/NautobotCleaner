#Angelo.Poggi

from config import nautobot_url, nautobot_token, device_platform_connection,device_username,device_password
import pynautobot
import napalm

class NautobotCleaner:
    def __init__(self,device):
        '''creates a connection to nautobot on instance'''
        self.pynb = pynautobot.api(nautobot_url, token=nautobot_token)
        try:
            self.device = self.pynb.dcim.devices.get(name=device)
        except Exception as e:
            raise(e)
            return None
        #grab the platform to find the driver
        self.device_os = device_platform_connection[str(device.platform)]['os']
        self.driver = napalm.get_network_driver(self.device_os)
        try:
            self.device_init = self.driver(
                hostname = str(self.device.name),
                username = str(device_username),
                password = str(device_password),
                optional_args={
                    'secret' : str(device_password)
                }

            )
            #knock knock, hello!?
            self.deviceconnection = self.device_init.open()
        except Exception as e:
            raise Exception(e)
        return self.deviceconnection

    def getvlans(self,device):
        '''Queries device info and grabs VLAN'''
        #give me that data
        return self.deviceconnection.get_vlans()


    def nautobotvlanimport(self,group,vlans):
        '''dumps them vlans into them groups and links it to the SVI created'''
        #did you give me good data?
        if not isinstance(vlans, dict):
            raise("Vlans is not a dict")

        #Check that group exsists & creat it if it dont
        vlangroup = self.pynb.ipam.vlan_groups.get(name=str(group))
        if vlangroup is None:
            vlangroup = self.pynb.ipam.vlan_groups.create(
                name=str(group))


        for vid,vidinfo in vlans.items():
            vlan = self.pynb.ipam.vlans.get(
                name=str(vid),
                group=vlangroup.id
            )
            if vlan is None:
                vlan = self.pynb.ipam.vlans.create(
                    name=str(vid),
                    group=str(group),
                    site=self.device.site
                )
            #Tie vlan to the interface
            for interfaces in vidinfo['interfaces']:
                interface = self.pynb.dcim.interfaces.get(
                    name=str(interfaces),
                    device_id = self.device.id
                )
                #PSUDO CODE
                '''
                Will probably come across interfaces with the same vlan i.e tagged
                create the interface object
                if the interface exsist but has no vlans
                    update and link curent vlan to vlan we are
                    set the interface as access
                if the interface exsists and has one vlan already
                    update interface to tagged
                    take exsisitng vland id and one you are wokring on and add it to interface
                if interface exsist and already has more than two vlans
                    update with additional vlan tag
                '''
                if interface is None:
                    print("interface not on device - skipping")
                else:
                    interface.update(
                        ''
                    )


if __name__ == "__main__":
    test = NautobotCleaner()
    print(test.getvlans("dsc121.gsc.webair.net"))

