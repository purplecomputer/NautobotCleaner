#Angelo.Poggi - Angelo.Poggi@opti9tech.com
#(c) Opti9 Tech

from importdevicevlans import NautobotCleaner
import pprint

if __name__ == "__main__":
    nbc = NautobotCleaner()
    # nbc.importdevicevlans(selected_devices=[
    #     'tgb090.chi.webair.net',
    #     'tgb091.chi.webair.net',
    #     'es0.chi.webair.net',
    #     'es1.chi.webair.net',
    # ],
    #     group='chi-l3')
    nbc.importdevicevlans(selected_devices=['cs1-l2.chi.webair.net'],
                          group='chi-l2')


