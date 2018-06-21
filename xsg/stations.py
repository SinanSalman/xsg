from collections import deque
from math import floor, ceil, inf
import time
import logging
from flask import flash

logger = logging.getLogger(__name__)

def week_sum(D,week):
    """ return a week's sum from a dictionary of lists of weekly values """
    return sum([x[week] for x in D.values()])


def dict_key_with_min_val(d,week):
    """ return the dictionary key with the min value for a given week """
    v = [x[week] for x in d.values()]
    k = list(d.keys())
    return k[v.index(min(v))]


def dict_key_with_max_val(d,week):
    """ return the dictionary key with the max value for a given week """
    v = [x[week] for x in d.values()]
    k = list(d.keys())
    return k[v.index(max(v))]


class Station():
    """ A station class for game stations in the supply chain game

    Attributes:

    Methods:

    """

    __player_name_counter = 1
    __MAX_NODE_SUPPLIERS = 4  # limited to 4 for display interface design purposes
    __MAX_NODE_CUSTOMERS = 4  # limited to 4 for display interface design purposes
    __Default_PlayerInput_MAX = inf  # used when no maximum is set

    def __init__(self,game,config):
        self.game = game
        if config['name'] == 'MyWorkshop':
            raise ValueError(game.team_name + ': keyword \'MyWorkshop\' is reserved and cannot be used as a station name')
        self.station_name = config['name']

        # set default values
        self.player_name = 'player' + str(Station.__player_name_counter)
        Station.__player_name_counter += 1
        self.holding_cost = 1
        self.backorder_cost = 2
        self.transport_cost = 5
        self.transport_size = 5
        self.safety_stock = 4
        self.delay_shipping = 2
        self.delay_ordering = 2
        self.initial_queue_quantity = 4
        self.initial_inventory = 4
        self.auto_decide_order_qty = True
        self.auto_decide_ship_qty = True

        # initialize variables
        self.kpi_weeklycost_inventory = [0] * game.weeks
        self.kpi_weeklycost_backorder = [0] * game.weeks
        self.kpi_weeklycost_transport = [0] * game.weeks
        self.kpi_total_cost = [0] * game.weeks
        self.kpi_fulfilment_rate = [0] * game.weeks
        self.kpi_truck_utilization = [0] * game.weeks
        self.kpi_shipment_trucks = [0] * game.weeks

        self.backorder = {}
        self.outstanding_orders_to_suppliers = {}
        self.received_po = {}
        self.sent_po = {}
        self.inbound = {}
        self.outbound = {}
        self.queue_receive = {}
        self.queue_transmit = {}
        self.customers = []
        self.suppliers = []

        self.player_order = []
        self.player_shipment = []
        self.player_action_timestamp = []
        self.last_communication_time = 0
        self.week_turn_completed = -1

        self.order_min = [0] * game.weeks
        self.order_max = [self.__Default_PlayerInput_MAX]*game.weeks
        self.ship_min = [0] * game.weeks
        self.ship_max = [self.__Default_PlayerInput_MAX]*game.weeks

        # setting available config values
        for k,v in config.items():
            if k.lower() in ['transport_size','delay_shipping','delay_ordering','initial_queue_quantity','initial_inventory']:
                setattr(self,k.lower(),max(v,1))  # value must not be less than 1 for logic to work; delays b/c of queues
            elif k.lower() in ['player_name','order_min','order_max','ship_min','ship_max']:
                if v:  # ignore empty values, and keep defaults
                    setattr(self,k.lower(),v)
            else:
                setattr(self,k.lower(),v)

        self.inventory = [self.initial_inventory] + [0] * (game.weeks-1)

        # ensuring order/ship min/max arrays cover all weeks
        attr_list = ['order_min','order_max','ship_min','ship_max']
        for k in attr_list:
            v = getattr(self,k)
            v_len = len(v)
            fil = 0
            if k[-3:] == 'max':
                fil = self.__Default_PlayerInput_MAX
            if v_len < game.weeks:
                msg = "Warning - in {:}, {:} has too few values to cover for game weeks ({:} out of {:}), filling missing values with {:}".format(
                    game.team_name + ':' + self.station_name, k, v_len, game.weeks, fil)
                logger.warning(msg)
                flash(msg)
                v.extend([fil]*(game.weeks-v_len))
        # ensuring order/ship min <= max for all weeks
        for w in range(game.weeks):
            if self.order_min[w] > self.order_max[w]:
                msg = "Warning - {:} has order_min > order_max for week {:}, replacing order_min with {:}".format(
                    game.team_name + ':' + self.station_name, w+1, 0)
                logger.warning(msg)
                flash(msg)
                self.order_min[w] = 0
            if self.ship_min[w] > self.ship_max[w]:
                msg = "Warning - {:} has ship_min > ship_max for week {:}, replacing ship_min with {:}".format(
                    game.team_name + ':' + self.station_name, w+1, 0)
                logger.warning(msg)
                flash(msg)
                self.ship_min[w] = 0
        # preparing limits for display in player screen
        self.ordering_limits = list(zip(range(1,game.weeks+1),self.order_min,self.order_max))
        self.shipping_limits = list(zip(range(1,game.weeks+1),self.ship_min,self.ship_max))

    def reset(self):
        # initialize variables
        self.kpi_weeklycost_inventory = [0] * self.game.weeks
        self.kpi_weeklycost_backorder = [0] * self.game.weeks
        self.kpi_weeklycost_transport = [0] * self.game.weeks
        self.kpi_total_cost = [0] * self.game.weeks
        self.kpi_fulfilment_rate = [0] * self.game.weeks
        self.kpi_truck_utilization = [0] * self.game.weeks
        self.kpi_shipment_trucks = [0] * self.game.weeks

        self.player_order = []
        self.player_shipment = []
        self.player_action_timestamp = []
        self.last_communication_time = 0
        self.week_turn_completed = -1

        self.inventory = [self.initial_inventory] + [0] * (self.game.weeks-1)

        for c in self.customers:
            self.backorder[c.station_name] = [0] * self.game.weeks
            self.received_po[c.station_name] = [0] * self.game.weeks
            self.outbound[c.station_name] = [0] * self.game.weeks

        for s in self.suppliers:
            self.outstanding_orders_to_suppliers[s.station_name] = [0] * self.game.weeks
            self.sent_po[s.station_name] = [0] * self.game.weeks
            self.inbound[s.station_name] = [0] * self.game.weeks
            self.queue_receive[s.station_name] = deque()
            self.queue_transmit[s.station_name] = deque()
            for i in range(self.delay_shipping):
                self.queue_receive[s.station_name].append(self.initial_queue_quantity)
                self.outstanding_orders_to_suppliers[s.station_name][0] += self.initial_queue_quantity
            for i in range(self.delay_ordering):
                self.queue_transmit[s.station_name].append(self.initial_queue_quantity)
                self.outstanding_orders_to_suppliers[s.station_name][0] += self.initial_queue_quantity

        if len(self.suppliers) == 0:  # an end_node?
            self.outstanding_orders_to_suppliers['MyWorkshop'] = [0] * self.game.weeks
            self.sent_po['MyWorkshop'] = [0] * self.game.weeks
            self.inbound['MyWorkshop'] = [0] * self.game.weeks
            self.queue_receive['MyWorkshop'] = deque()
            for i in range(self.delay_shipping):
                self.queue_receive['MyWorkshop'].append(self.initial_queue_quantity)
                self.outstanding_orders_to_suppliers['MyWorkshop'][0] += self.initial_queue_quantity

    def get_config(self):
        data = {}
        for x in ['name','player_name','auto_decide_ship_qty','auto_decide_order_qty','holding_cost','backorder_cost',
                  'transport_cost','transport_size','delay_shipping','delay_ordering','initial_queue_quantity','initial_inventory',
                  'safety_stock','order_min','order_max','ship_min','ship_max']:
            data[x] = getattr(self,x,'')
        return data

    def add_customer(self,customer):
        if len(self.customers) == self.__MAX_NODE_CUSTOMERS:
            raise ValueError('Too many customer connections per node({:}:{:}), max is {:}, check game ({:}) settings data (Connections)'.format(self.game.team_name,self.station_name,self.__MAX_NODE_CUSTOMERS,self.game.team_name))
        self.customers.extend([customer])
        self.backorder[customer.station_name] = [0] * self.game.weeks
        self.received_po[customer.station_name] = [0] * self.game.weeks
        self.outbound[customer.station_name] = [0] * self.game.weeks

    def add_supplier(self,supplier):
        if len(self.suppliers) == self.__MAX_NODE_SUPPLIERS:
            raise ValueError('Too many supplier connections per node ({:}:{:}), max is {:}, check game ({:}) settings data (Connections)'.format(self.game.team_name,self.station_name,self.__MAX_NODE_SUPPLIERS,self.game.team_name))
        self.suppliers.extend([supplier])
        self.outstanding_orders_to_suppliers[supplier.station_name] = [0] * self.game.weeks
        self.sent_po[supplier.station_name] = [0] * self.game.weeks
        self.inbound[supplier.station_name] = [0] * self.game.weeks
        self.queue_receive[supplier.station_name] = deque()
        self.queue_transmit[supplier.station_name] = deque()
        for i in range(self.delay_shipping):
            self.queue_receive[supplier.station_name].append(self.initial_queue_quantity)
            self.outstanding_orders_to_suppliers[supplier.station_name][0] += self.initial_queue_quantity
        for i in range(self.delay_ordering):
            self.queue_transmit[supplier.station_name].append(self.initial_queue_quantity)
            self.outstanding_orders_to_suppliers[supplier.station_name][0] += self.initial_queue_quantity

    def check_endnode(self):
        if len(self.suppliers) == 0:  # an end_node?
            self.outstanding_orders_to_suppliers['MyWorkshop'] = [0] * self.game.weeks
            self.sent_po['MyWorkshop'] = [0] * self.game.weeks
            self.inbound['MyWorkshop'] = [0] * self.game.weeks
            self.queue_receive['MyWorkshop'] = deque()
            for i in range(self.delay_shipping):
                self.queue_receive['MyWorkshop'].append(self.initial_queue_quantity)
                self.outstanding_orders_to_suppliers['MyWorkshop'][0] += self.initial_queue_quantity

    def touch(self):
        self.last_communication_time = time.time()

    def set_player_order_and_shipment(self,week,order,shipment):
        if self.week_turn_completed < week:
            for k in order.keys():
                if order[k] < 0:
                    msg = 'Error - player passed negative order value; using zeros instead.({:}:{:}/sup:{:}/wk:{:}/po:{:})'.format(self.game.team_name,self.station_name,k,week,order[k])
                    logger.error(msg)
                    flash(msg)
                    order[k] = 0
            for k in shipment.keys():
                if shipment[k] < 0:
                    msg = 'Error - player passed negative shipment value; using zeros instead.({:}:{:}/cus:{:}/wk:{:}/shp:{:})'.format(self.game.team_name,self.station_name,k,week,shipment[k])
                    logger.error(msg)
                    flash(msg)
                    shipment[k] = 0
            orders_sum = sum(order.values())
            shipments_sum = sum(shipment.values())
            totaldemand = week_sum(self.received_po,week) + week_sum(self.backorder,week)
            if orders_sum > self.order_max[week] or orders_sum < self.order_min[week]:
                msg = 'Warning - player passed order value(s) that is out of ordering limits.({:}:{:}/wk:{:}/sum.po:{:})'.format(self.game.team_name,self.station_name,week,orders_sum)
                logger.warning(msg)
                flash(msg)
            if (shipments_sum > self.ship_max[week] or shipments_sum < self.ship_min[week]) and shipments_sum > 0:
                msg = 'Warning - player passed ship value(s) that is out of shipping limits.({:}:{:}/wk:{:}/sum.shp:{:})'.format(self.game.team_name,self.station_name,week,shipments_sum)
                logger.warning(msg)
                flash(msg)
            if self.ship_min[week] > self.inventory[week] and shipments_sum > 0:
                msg = 'Error - player inventory is below shipping mimumum limit, must ship 0 units for this week; using zeros instead.({:}:{:}/wk:{:}/sum.shp:{:})'.format(self.game.team_name,self.station_name,week,shipments_sum)
                logger.warning(msg)
                flash(msg)
                for k in shipment.keys():
                    shipment[k] = 0
                shipments_sum = 0
            if self.ship_min[week] > totaldemand and shipments_sum > 0:
                msg = 'Error - total customer(s) demand (POs+BackOrders) is below the shipping mimumum limit, must ship 0 units for this week; using zeros instead.({:}:{:}/wk:{:})'.format(self.game.team_name,self.station_name,week)
                logger.warning(msg)
                flash(msg)
                for k in shipment.keys():
                    shipment[k] = 0
                shipments_sum = 0
            if shipments_sum > self.inventory[week] or shipments_sum < 0:
                msg = 'Error - player passed shipment value(s) that is out of inventory limits, using zeros instead.({:}:{:}/wk:{:}/sum.shp:{:})'.format(self.game.team_name,self.station_name,week,shipments_sum)
                logger.error(msg)
                flash(msg)
                for k in shipment.keys():
                    shipment[k] = 0
            for k,v in shipment.items():
                if v > (self.received_po[k][week] + self.backorder[k][week]):
                    msg = 'Error - player passed shipment value that is greater than the requested amount (PO+backorder). Defaulting to zero instead.({:}:{:}/cus:{:}/wk:{:}/shp:{:})'.format(self.game.team_name,self.station_name,k,week,v)
                    logger.error(msg)
                    flash(msg)
                    shipment[k] = 0
            self.player_order.append(order)
            self.player_shipment.append(shipment)
            self.player_action_timestamp.append(time.time())
            self.week_turn_completed += 1
            return True
        else:
            msg = 'Warning - player sent multiple orders/shipments for the same week. Most recent data ignored.({:}:{:}/wk:{:})'.format(self.game.team_name,self.station_name,week)
            logger.warning(msg)
            flash(msg)
            return False

    def limit_ordering(self,value,week):
        return min(max(value,self.order_min[week]),self.order_max[week])

    def limit_shipping(self,value,week):
        if self.ship_min[week] > self.inventory[week]:
            return 0
        value = min(value,self.inventory[week])
        return min(max(value,self.ship_min[week]),self.ship_max[week])

    def decide_order(self,week):
        if self.auto_decide_order_qty:
            backorders = week_sum(self.backorder,week)
            outstanding_orders = week_sum(self.outstanding_orders_to_suppliers,week)
            if self.game.quick_backorder_recovery:
                total_order = max(0,backorders + self.safety_stock - self.inventory[week] - round(outstanding_orders/2))  # use half the outstanding orders to help recover from backorders faster
            else:
                total_order = max(0,backorders + self.safety_stock - self.inventory[week] - outstanding_orders)
            total_order = self.limit_ordering(total_order,week)
            order = {}
            n_suppliers = len(self.suppliers)
            if n_suppliers == 0:
                order['MyWorkshop'] = total_order
            elif n_suppliers == 1:
                order[self.suppliers[0].station_name] = total_order
            elif outstanding_orders > 0:  # award more orders to suppliers with lower outstanding orders
                ratio = {}
                for k,v in self.outstanding_orders_to_suppliers.items():
                    ratio[k] = 1 - (v[week]/outstanding_orders)
                ratiosum = sum(ratio.values())
                for k,v in self.outstanding_orders_to_suppliers.items():
                    ratio[k] /= ratiosum  # to normalize ratio values
                    order[k] = floor(ratio[k] * total_order)
            else:
                for k,v in self.outstanding_orders_to_suppliers.items():
                    order[k] = floor(total_order/n_suppliers)  # award orders to suppliers equaly
            remainder = total_order - sum(order.values())
            if remainder > 0:
                order[dict_key_with_min_val(self.outstanding_orders_to_suppliers,week)] += remainder
            return order
        else:
            return self.player_order[week]

    def decide_shipment(self,week):
        if self.auto_decide_ship_qty:
            backorders = week_sum(self.backorder,week)
            total_shipment = self.limit_shipping(backorders,week)
            shipment = {}
            if total_shipment > 0:  # also means backorders is not zero
                for k,v in self.backorder.items():
                    shipment[k] = floor(v[week]/backorders * total_shipment)  # ship more to customers with more backorders
            else:
                for k,v in self.backorder.items():
                    shipment[k] = 0
            remainder = total_shipment - sum(shipment.values())
            if remainder > 0:
                shipment[dict_key_with_max_val(self.backorder,week)] += remainder
            return shipment
        else:
            return self.player_shipment[week]

    def receive_po(self,name,po,week):
        self.received_po[name][week] = po

    def receive_product(self,name,shipment):
        self.queue_receive[name].append(shipment)

    def initialize_week(self,week):
        supplier_names = [z.station_name for z in self.suppliers]
        customer_names = [z.station_name for z in self.customers]
        if supplier_names == []:
            supplier_names = ['MyWorkshop']
        # carry over values from previous week
        if week > 0:
            self.inventory[week] = self.inventory[week-1]
            for x in customer_names:
                self.backorder[x][week] = self.backorder[x][week-1]
            for x in supplier_names:
                self.outstanding_orders_to_suppliers[x][week] = self.outstanding_orders_to_suppliers[x][week-1]
        # receive product
        for x in supplier_names:
            self.inbound[x][week] = self.queue_receive[x].popleft()
        # transmit POs
        for x in self.suppliers:
            x.receive_po(self.station_name,self.queue_transmit[x.station_name].popleft(),week)
        # adjust outstanding_orders and inventory
        for x in supplier_names:
            self.outstanding_orders_to_suppliers[x][week] -= self.inbound[x][week]
        self.inventory[week] += week_sum(self.inbound,week)

    def process(self,week):
        supplier_names = [z.station_name for z in self.suppliers]
        customer_names = [z.station_name for z in self.customers]
        if supplier_names == []:
            supplier_names = ['MyWorkshop']

        if self.game.auto_order_method == 'WSG':  # decide on PO (using WSG auto-order logic)
            order = self.decide_order(week)

        # adjust backorder
        for x in customer_names:
            self.backorder[x][week] += self.received_po[x][week]

        # decide shipment
        shipment = self.decide_shipment(week)  # player shipment decision goes here
        self.inventory[week] -= sum(shipment.values())
        for x in customer_names:
            self.backorder[x][week] -= shipment[x]

        # ship product & calculate transport needs
        trucks = 0
        for x in self.customers:
            x.receive_product(self.station_name,shipment[x.station_name])
            trucks += ceil(shipment[x.station_name]/self.transport_size)
            self.outbound[x.station_name][week] = shipment[x.station_name]

        if self.game.auto_order_method == 'XSG':  # decide on PO (using XSG auto-order logic)
            order = self.decide_order(week)

        if supplier_names == ['MyWorkshop']:
            self.queue_receive['MyWorkshop'].append(order['MyWorkshop'])  # skipping queue_transmit
            self.sent_po['MyWorkshop'][week] = order['MyWorkshop']
            self.outstanding_orders_to_suppliers['MyWorkshop'][week] += order['MyWorkshop']
        else:
            for x in self.suppliers:
                self.queue_transmit[x.station_name].append(order[x.station_name])
                self.sent_po[x.station_name][week] = order[x.station_name]
                self.outstanding_orders_to_suppliers[x.station_name][week] += order[x.station_name]

        # calculate costs, KPI
        backorders = week_sum(self.backorder,week)
        shipments = sum(shipment.values())
        self.kpi_weeklycost_inventory[week] = self.holding_cost*self.inventory[week]
        self.kpi_weeklycost_backorder[week] = self.backorder_cost*backorders
        self.kpi_weeklycost_transport[week] = self.transport_cost*trucks
        self.kpi_total_cost[week] = self.kpi_weeklycost_inventory[week] + self.kpi_weeklycost_backorder[week] + self.kpi_weeklycost_transport[week]
        self.kpi_shipment_trucks[week] = trucks
        if (backorders+shipments) > 0:
            self.kpi_fulfilment_rate[week] = shipments/(backorders+shipments)
        else:
            self.kpi_fulfilment_rate[week] = 1
        if trucks > 0:
            self.kpi_truck_utilization[week] = (shipments/self.transport_size)/trucks
        else:
            self.kpi_truck_utilization[week] = 1


class Demand():
    """ A class defining demand in the supply chain game

    Attributes:

    Methods:

    """

    __MAX_NODE_SUPPLIERS = 4

    def __init__(self,game,config):
        self.game = game
        self.station_name = config['name']
        self.player_name = 'Demand'

        # set default values
        self.demand = [4]*5 + [8]*(game.weeks-5)

        # initialize variables
        self.inbound = {}
        self.customers = []
        self.suppliers = []

        # setting available config values
        for k,v in config.items():
            setattr(self,k.lower(),v)

        self.last_communication_time = 0  # provided only for compatibility with station class interface

    def reset(self):
        for s in self.suppliers:
            self.inbound[s.station_name] = [0] * self.game.weeks

    def get_config(self):
        data = {}
        for x in ['name','demand']:
            data[x] = getattr(self,x,'')
        return data

    def add_supplier(self,supplier):  # its okay to have multiple suppliers to the same demand point; they all will receive identical demand, and each will need to satisfy the full demand on its own
        if len(self.suppliers) == self.__MAX_NODE_SUPPLIERS:
            raise ValueError('Too many supplier connections per node ({:}), max is {:}, check game ({:}) settings data (Connections)'.format(self.station_name,self.__MAX_NODE_SUPPLIERS,self.game.team_name))
        self.suppliers.extend([supplier])
        self.inbound[supplier.station_name] = []

    def receive_product(self,name,shipment):
        self.inbound[name].append(shipment)

    def initialize_week(self,week):
        for x in self.suppliers:  # transmit POs
            x.receive_po(self.station_name,self.demand[week],week)

    # the below functions are only provided for compatibility with station class interface
    def check_endnode(self):
        pass

    def process(self,week):
        pass


def connect_stations(A: Station, B: Station):
    if type(A) is Demand :
        raise ValueError('Demand point ({:}) cannot have customers. Check game ({:}) settings data (Connections)'.format(A.station_name, A.game.team_name))
    else:
        A.add_customer(B)
        B.add_supplier(A)
