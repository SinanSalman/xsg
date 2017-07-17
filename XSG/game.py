import stations


def currency(value):
    return '{:>8}'.format('${:.2f}'.format(value))


def percent(value):
    return '{:>8}'.format('{:.1f}%'.format(value*100))


def combine_weekly(D):
    if len(D) > 1:
        return [sum(y) for y in zip(*D.values())]
    else:
        return list(D.values())[0]


class Game(object):
    """ A game class for the X Supply Game

    Attributes:

    Methods:

    """
    def __init__(self,config):
        self.team_name = config['Team_Name']
        self.weeks = config['Weeks']
        self.config_auto_decide_ship_qty = config['Auto_Decide_Ship_Qty']
        self.config_auto_decide_order_qty = config['Auto_Decide_Order_Qty']
        self.network_stations = {}
        self.network_demands = []

        for x in config['Stations']:
            self.network_stations[x['Name']] = stations.Station(game=self,name=x['Name'],player=x['Player'],holding_cost=x['Holding_Cost'],backorder_cost=x['Backorder_Cost'],transport_cost=x['Transport_Cost'],transport_size=x['Transport_Size'],delay_shipping=x['Delay_Shipping'],delay_ordering=x['Delay_Ordering'],initial_values=x['Initial_Values'],safety_stock=x['Safety_Stock'],production_min=x['Production_Min'],production_max=x['Production_Max'])
        for x in config['Demands']:
            self.network_stations[x['Name']] = stations.Demand(game=self,name=x['Name'],demand=x['Demand'])
            self.network_demands.append(x['Name'])
        for x in config['Connections']:
            stations.connect_stations(self.network_stations[x['supp']], self.network_stations[x['cust']])
        for x in self.network_stations.values():  # handle end nodes
            x.check_endnode()

        self.network_walk = self.GenerateNetworkWalk()

        self.KPI_customer_satisfaction = [0] * self.weeks
        self.KPI_green_score = [0] * self.weeks
        self.KPI_cost = {'inventory':[0] * self.weeks, 'backorder':[0] * self.weeks, 'transport':[0] * self.weeks, 'total':[0] * self.weeks}
        # self.connections_status = {'station':1}

    def GenerateNetworkWalk(self):
        netwalk = self.network_demands.copy()  # start with demand nodes
        all_stations = [x.station_name for x in self.network_stations.values()]
        DONE = False
        while not DONE:
            tmp = [x for x in all_stations if x not in netwalk]
            for x in tmp:
                customers = [y.station_name for y in self.network_stations[x].customers]
                if set(customers).issubset(netwalk):
                    netwalk.append(x)
            if tmp == []:
                DONE = True
        return netwalk

    def Run(self):
        for week in range(self.weeks):
            n = 0
            for node_name in self.network_walk:
                node = self.network_stations[node_name]
                node.process(week)
                if node_name not in self.network_demands:
                    n += 1
                    self.KPI_customer_satisfaction[week] += node.KPI_fullfillment_rate[week]
                    self.KPI_green_score[week] += node.KPI_truck_utilization[week]
                    self.KPI_cost['inventory'][week] += node.KPI_weeklycost_inventory[week]
                    self.KPI_cost['backorder'][week] += node.KPI_weeklycost_backorder[week]
                    self.KPI_cost['transport'][week] += node.KPI_weeklycost_transport[week]
                    self.KPI_cost['total'][week] += node.KPI_total_cost[week]
            if n > 0:
                self.KPI_customer_satisfaction[week] /= n
                self.KPI_green_score[week] /= n

            # compare against demand KPIs

    def Report(self):
        print('\n{:20}'.format('Details'))
        print('*'*20)
        for x in self.network_stations.values():
            print('\n       Station: {:20}'.format(x.station_name))
            print('        Player: {:20}'.format(x.station_player))
            if type(x) is stations.Demand:
                print('     Suppliers: {:}'.format(', '.join([str(y.station_name) for y in x.suppliers])))
                print(' WK ' + '{:>8} '.format('  Demand') + ' '.join(['{:>8}'.format(' inbound') for y in x.inbound.keys()]))
                for week in range(self.weeks):
                    print('{:3} {:8} '.format(week+1,x.demand[week]) + ' '.join(['{:8}'.format(y[week]) for y in x.inbound.values()]))
            else:
                print('  Holding cost: {:}'.format(x.holding_cost))
                print('Backorder cost: {:}'.format(x.backorder_cost))
                print('Transport cost: {:}'.format(x.transport_cost))
                print('Transport size: {:}'.format(x.transport_size))
                print('  Safety stock: {:}'.format(x.safety_stock))
                print('Shipping delay: {:}'.format(x.delay_shipping))
                print('Ordering delay: {:}'.format(x.delay_ordering))
                print('     Customers: {:}'.format(', '.join([str(y.station_name) for y in x.customers])))
                print('     Suppliers: {:}'.format(', '.join([str(y.station_name) for y in x.suppliers])))
                print('Production min: {:}'.format(x.production_min))
                print('Production max: {:}'.format(x.production_max))
                print('{:} {:} {:} {:} {:} {:} {:} {:} '.format(' Wk','Invntroy','Bk.Order','transprt',' Total.$','fullfill','TruckUtl','Invntroy') +
                      ' '.join(['{:>8}'.format('OutStand') for y in x.outstanding_orders_to_suppliers.keys()]) + ' ' +
                      ' '.join(['{:>8}'.format('Bk.Order') for y in x.backorder.keys()]) + ' ' +
                      ' '.join(['{:>8}'.format('recvedPO') for y in x.receivedPO.keys()]) + ' ' +
                      ' '.join(['{:>8}'.format('  sentPO') for y in x.sentPO.keys()]) + ' ' +
                      ' '.join(['{:>8}'.format(' inbound') for y in x.inbound.keys()]) + ' ' +
                      ' '.join(['{:>8}'.format('outbound') for y in x.outbound.keys()]))
                for week in range(self.weeks):
                    print('{:3} {:} {:} {:} {:} {:} {:} {:8d} '.format(week+1,currency(x.KPI_weeklycost_inventory[week]),currency(x.KPI_weeklycost_backorder[week]),currency(x.KPI_weeklycost_transport[week]),currency(x.KPI_total_cost[week]),percent(x.KPI_fullfillment_rate[week]),percent(x.KPI_truck_utilization[week]),x.inventory[week]) +
                          ' '.join(['{:>8}'.format(y[week]) for y in x.outstanding_orders_to_suppliers.values()]) + ' ' +
                          ' '.join(['{:>8}'.format(y[week]) for y in x.backorder.values()]) + ' ' +
                          ' '.join(['{:>8}'.format(y[week]) for y in x.receivedPO.values()]) + ' ' +
                          ' '.join(['{:>8}'.format(y[week]) for y in x.sentPO.values()]) + ' ' +
                          ' '.join(['{:>8}'.format(y[week]) for y in x.inbound.values()]) + ' ' +
                          ' '.join(['{:>8}'.format(y[week]) for y in x.outbound.values()]))

        # print('{:20}'.format('Demands:'))
        # print('*'*20)
        # print(' WK ' + ' '.join(['{:>20}'.format(x) for x in self.network_demands]))
        # for week in range(self.weeks):
        #     print('{:3} '.format(week+1) + ' '.join(['{:20}'.format(self.network_stations[x].demand[week]) for x in self.network_demands]))

        print('\n{:20}'.format('Summary'))
        print('*'*20)
        print('{:} {:} {:} {:} {:} {:} {:}'.format(' Wk','C.Satisf','GreenScr','Invntory','Bk.Order','transprt',' Total.$'))
        for i in range(self.weeks):
            print('{:3} {:} {:} {:} {:} {:} {:}'.format(i+1,percent(self.KPI_customer_satisfaction[i]),percent(self.KPI_green_score[i]),currency(self.KPI_cost['inventory'][i]),currency(self.KPI_cost['backorder'][i]),currency(self.KPI_cost['transport'][i]),currency(self.KPI_cost['total'][i])))

        print('\nX-Supply Game Report')
        print('*'*25)
        print('{:>25} {:}'.format('Team name:',self.team_name))
        print('{:>25} {:d}'.format('# of weeks:',self.weeks))
        print('{:>25} {:}'.format('Auto decide ship qty:',self.config_auto_decide_ship_qty))
        print('{:>25} {:}'.format('Auto decide order qty:',self.config_auto_decide_order_qty))
        print('{:>25} {:}'.format('Customer satisfaction:',percent(sum(self.KPI_customer_satisfaction)/self.weeks)))
        print('{:>25} {:}'.format('Green score:',percent(sum(self.KPI_green_score)/self.weeks)))
        print('{:>25} {:}'.format('Inventory cost:',currency(sum(self.KPI_cost['inventory'])/self.weeks)))
        print('{:>25} {:}'.format('Backorder cost:',currency(sum(self.KPI_cost['backorder'])/self.weeks)))
        print('{:>25} {:}'.format('Transport cost:',currency(sum(self.KPI_cost['transport'])/self.weeks)))
        print('{:>25} {:}'.format('Total cost:',currency(sum(self.KPI_cost['total'])/self.weeks)))

    def Plots(self):
        import matplotlib.pyplot as plt
        weeks = range(1,self.weeks+1)

        data = ['outstanding_orders_to_suppliers','backorder','receivedPO','sentPO','backorder','backorder']

        for d in data:
            fig, ax = plt.subplots(figsize=(10, 5))
            lns = []
            for y in self.network_walk:
                x = self.network_stations[y]
                if type(x) is not stations.Demand:
                    lns += ax.plot(weeks,combine_weekly(getattr(x,d)),'-',label=x.station_name)
            ax.set_xlabel("Weeks")
            ax.set_ylabel("Units")
            ax.grid()
            labs = [l.get_label() for l in lns]
            ax.legend(lns, labs, loc="upper left")
            plt.title(d)
            plt.show()

# Trucksize = 15
#
# a=['Retailer Deliveries','Distributor Deliveries','Manufacturer Deliveries','Refinery Deliveries','Well Deliveries']
#
# E = df['Demand']*5 - sum([df[x] for x in a])
# E1 = [max(x,0) for x in E]
# fig, ax = plt.subplots(figsize=(16, 5))
# ax.plot(df['Week'],E,'-',label=y)
# ax.plot(df['Week'],E1,'-',label=y)
# ax.set_xlabel(\"Weeks\")
# ax.set_ylabel(\"Units\")
# ax.grid()
# plt.title(\"OSG Excess Deliveries\")
# plt.show()
#
# E1 = [ceil(max(x,0)/Trucksize) for x in E]
# fig, ax = plt.subplots(figsize=(16, 5))
# ax.plot(df['Week'],E1,'-',label=y)
# ax.set_xlabel(\"Weeks\")
# ax.set_ylabel(\"Trucks\")
# ax.set_yticks([0,1,2,3,4,5])
# ax.grid()
# plt.title(\"OSG Excess Deliveries (with truck capacity = {:} units)\".format(Trucksize))
# plt.show()"
