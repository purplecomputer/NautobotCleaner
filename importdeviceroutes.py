
from netmiko import ConnectHandler
from config import nautobot_url, nautobot_token, device_platform_connection,device_username,device_password
import pynautobot
import ipaddress

class NautobotCleanerRoutes():
    def __init__(self):
        self.pynb = pynautobot.api(nautobot_url, token=nautobot_token)

    def _isIP(self, network):
        try:
            ipaddress.ip_network(network)
            return True
        except:
            return False

    def _getstaticroutes(self, device):
        '''uses netmiko and NTC textfsm tempalte to pull static routes'''
        print(f'Import prefix from routing table for {device}')
        device_object = self.pynb.dcim.devices.get(name=str(device))
        # device_os = device_platform_connection[str(device.platform)]['os']
        net_connect = ConnectHandler(
            device_type='cisco_ios',
            host=str(device),
            username=str(device_username),
            password=str(device_password),
            secret=str(device_password)
        )
        net_connect.find_prompt()
        output = net_connect.send_command('show ip route static',use_textfsm=True)
        for data in output:
            '''If Null0 set as conatiner'''
            prefix_join = f'''{data['network']}/{data['mask']}'''
            prefix_check = self._isIP(prefix_join)
            print(f'Import prefix {prefix_join}')
            if prefix_check != True:
                continue
            if data['nexthop_if'] == 'Null0':
                prefix_object = self.pynb.ipam.prefixes.get(
                    prefix=str(prefix_join),
                    site_id=device_object.site.id,
                    #tenant_id = device_object.tenant.id
                )
                if prefix_object is None:
                    self.pynb.ipam.prefixes.create(
                        prefix= str(prefix_join),
                        status='container',
                        site=device_object.site.id,
                        #tenant=device_object.tenant.id
                    )
                else:
                    prefix_object.update({
                        'prefix':str(prefix_join),
                        'status':'container',
                        'site':device_object.site.id,
                        'tenant':device_object.tenant.id
                    })
            else:
                '''Else logic if next hop is not Null0'''
                prefix_object = self.pynb.ipam.prefixes.get(
                    prefix=str(prefix_join),
                    #status='container',
                    site_id=device_object.site.id,
                    #tenant_id=device_object.tenant.id
                )
                if prefix_object is None:
                    self.pynb.ipam.prefixes.create(
                        prefix=str(prefix_join),
                        status='active',
                        site=device_object.site.id,
                        #tenant=device_object.tenant.id
                    )
                else:
                    prefix_object.update({
                        'prefix': str(prefix_join),
                        'status': 'active',
                        'site':   device_object.site.id,
                        'tenant': device_object.tenant.id
                    })



if __name__ == "__main__":
    nbc = NautobotCleanerRoutes()
    nbc._getstaticroutes('es0.chi.webair.net')
    nbc._getstaticroutes('es1.chi.webair.net')
    nbc._getstaticroutes('es1.sg.webair.net')

