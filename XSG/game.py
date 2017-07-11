import stations


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

        S = {}
        for x in config['Stations']:
            S[x['Name']] = stations.Station(game=self,name=x['Name'],player=x['Player'],holding_cost=x['Holding_Cost'],backorder_cost=x['Backorder_Cost'],transport_cost=x['Transport_Cost'],transport_size=x['Transport_Size'],delay_shipping=x['Delay_Shipping'],delay_ordering=x['Delay_Ordering'],initial_values=x['Initial_Values'],safety_stock=x['Safety_Stock'],production_min=x['Production_Min'],production_max=x['Production_Max'])
        S['Demand'] = stations.Demand(game=self, demand=config['Demand'])
        for x in config['Connections']:
            stations.connect_stations(S[x['supp']], S[x['cust']])
        self.network_demand = S['Demand']

        self.KPI_customer_satisfaction = 0
        self.KPI_green_score = 0
        self.KPI_cost = {'inventory':0, 'backorder':0, 'transport':0, 'total':0}
        # self.connections_status = {'station':1}

    def Run(self):
        n = 0
        for week in range(self.weeks):
            node = self.network_demand
            while node is not None:
                node.process(week)
                if node.station_name != 'Demand':
                    n += 1
                    self.KPI_customer_satisfaction += node.KPI_fullfillment_rate[-1]
                    self.KPI_green_score += node.KPI_truck_utilization[-1]
                    self.KPI_cost['inventory'] += node.weeklycost_inventory[-1]
                    self.KPI_cost['backorder'] += node.weeklycost_backorder[-1]
                    self.KPI_cost['transport'] += node.weeklycost_transport[-1]
                    self.KPI_cost['total'] += node.KPI_total_cost[-1]
                node = node.supplier
        self.KPI_customer_satisfaction /= n
        self.KPI_green_score /= n

    def Report(self):
        print('X-Supply Game Report')
        print('*'*30)
        print('{:30}\t{:}'.format('Team name:',self.team_name))
        print('{:30}\t{:}'.format('# of weeks:',self.weeks))
        print('{:30}\t{:}'.format('Auto decide ship qty:',self.config_auto_decide_ship_qty))
        print('{:30}\t{:}'.format('Auto decide order qty:',self.config_auto_decide_order_qty))
        print('{:30}'.format('Weekly demand:'))
        print(str([*zip(range(1,self.weeks+1),self.network_demand.demand)]).replace('), (','\n').replace('[(','').replace(')]',''))
        print('{:30}\t{:3.1f}%'.format('Customer satisfaction:',self.KPI_customer_satisfaction*100))
        print('{:30}\t{:3.1f}%'.format('Green score:',self.KPI_green_score*100))
        print('{:30}\t${:d}'.format('Inventory cost:',self.KPI_cost['inventory']))
        print('{:30}\t${:d}'.format('Backorder cost:',self.KPI_cost['backorder']))
        print('{:30}\t${:d}'.format('Transport cost:',self.KPI_cost['transport']))
        print('{:30}\t${:d}'.format('Total cost:',self.KPI_cost['total']))
