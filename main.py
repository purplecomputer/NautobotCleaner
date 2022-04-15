#Angelo.Poggi

from config import nautobot_url, nautobot_token, device_platform_connection,device_username,device_password
import pynautobot
import napalm
import pprint
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

    def _formatnapalmvlandict(self, group,vlans):
        newdict = {}
        #find the group cause you'll need it later
        # Check that group exsists & create it if it dont
        vlangroup = self.pynb.ipam.vlan_groups.get(name=str(group))
        if vlangroup is None:
            vlangroup = self.pynb.ipam.vlan_groups.create(
                name=str(group)
            )
        if not isinstance(vlans, dict):
            raise Exception("vlan arg must be a dictionary")
        for k, v in vlans.items():
            vlanid = self.pynb.ipam.vlans.get(
                vid=str(k),
                vlan_group=vlangroup.id
            )
            if vlanid is None:
                vlanid = self.pynb.ipam.vlans.create(
                    name=str(k),
                    vid=k,
                    group=str(vlangroup.id),
                    site=self.device.site.id,
                    status='active',
                    description=j['name']
                )
            for j in v['interfaces']:
                if j in newdict:
                    #if the key is already there add the vlan
                    newdict[j].append(vlanid.id)
                else:
                    newdict[j] = [vlanid.id]
        return(newdict)

    def nautobotvlanimport(self,group,vlans):
        '''dumps them vlans into them groups and links it to the SVI created'''

        #did you give me good data?
        if not isinstance(vlans, dict):
            raise("Vlans is not a dict")

        #convert the Dict to something thats easier to use here
        vlans = self._formatnapalmvlandict(group,vlans)
        #vlangroup = self.pynb.ipam.vlan_groups.get(name=str(group))

        for interface,vlan in vlans.items():
            '''query interface object'''
            interfaceQuery = self.pynb.dcim.interfaces.get(
                name=str(interface),
                device_id=self.device.id
            )
            if interfaceQuery is None:
                print(f'Interface: {interface} does not match SOT list - Skipping!')
                continue
            if len(vlan) == 1:
                if interfaceQuery.mode.value == None:
                    '''if the interface exsist but has no vlans or mode set
                    update and link curent vlan to vlan we are
                    set the interface as access'''
                    print('setting int as untagged')
                    interface.update({
                        'mode' : 'access',
                        'untagged_vlan' : vlan[0]
                    })
                elif interfaceQuery.untagged_vlan is None:
                    '''if the interfaceQuery exsists and was set untagged by network importer w/ no vlans'''
                    print('linking vlan to untagged int')
                    interfaceQuery.update({
                        'untagged_vlan' :  vlan[0]
                    })
                else:
                    '''if logic doesnt match just set the mode to access and link VLAN'''
                    print('nothing matches, setting as access w/ ID')
                    interfaceQuery.update({
                        'mode':          'access',
                        'untagged_vlan': vlan[0]
                    })
            else:
                '''If vlan dict value list is longer than 1'''
                interfaceQuery.update({
                    'mode' : 'tagged',
                    'tagged_vlans' : vlan
                })

if __name__ == "__main__":
    nbc = NautobotCleaner('dsc121.gsc.webair.net')
    vlan_data = nbc.getvlans()
    #test = nbc._formatnapalmvlandict('ds121', vlan_data)
    #pprint.pprint(test)
    nbc.nautobotvlanimport('ds121', vlan_data)

