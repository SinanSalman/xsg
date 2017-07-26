# todo:
# check for circuler reference + network connections

from queue import Queue
from math import floor, ceil


def week_sum(D,week):
    return sum([x[week] for x in D.values()])


def keywithmaxval(d,week):
    """ return the dictionary key with the max value in WEEK """
    v = [x[week] for x in d.values()]
    k = list(d.keys())
    return k[v.index(max(v))]


def keywithminval(d,week):
    """ return the dictionary key with the min value in WEEK """
    v = [x[week] for x in d.values()]
    k = list(d.keys())
    return k[v.index(min(v))]


class Station():
    """ A station class for game stations in the supply chain game

    Attributes:

    Methods:

    """

    __MAX_NODE_SUPPLIERS = 2
    __MAX_NODE_CUSTOMERS = 2
    __Default_MAX_ORDER = 999
    __Order_Method = 'WSG'  # XSG or WSG
    __Quick_Backorder_Recover = False  # True or False

    def __init__(
        self,
        game,
        name,
        player,
        holding_cost=1,
        backorder_cost=2,
        transport_cost=5,
        transport_size=5,
        delay_shipping=2,
        delay_ordering=2,
        initial_queue_quantity=4,
        initial_inventory=8,
        safety_stock=4,
        production_min=[],
        production_max=[]
    ):
        # must have at least one week delay for the game logic to work (b/c queues)
        if delay_shipping < 1:
            delay_shipping = 1
        if delay_ordering < 1:
            delay_ordering = 1
        # trnasport size cannot be zero or negative
        if transport_size < 1:
            transport_size = 1
        # initial values must be positive nonzero integers
        if initial_queue_quantity < 1:
            initial_queue_quantity = 1
        if initial_inventory < 1:
            initial_inventory = 1

        # ensuring production_min and production_max is valid
        if production_min == []:
            production_min = [0] * game.weeks
        if production_max == []:
            production_max = [self.__Default_MAX_ORDER]*game.weeks
        a = len(production_min)
        b = len(production_max)
        if a > b:
            print("warning - in {:}, production_min has more values then production_max, filling missing values with {:}}".format(name,self.__Default_MAX_ORDER))
            production_max.extend([self.__Default_MAX_ORDER]*(a-b))
        if a < b:
            print("warning - in {:}, production_max has more values then production_min, filling missing values with 0".format(name))
            production_max.extend([0]*(b-a))

        self.game = game
        self.station_name = name
        self.station_player = player
        self.holding_cost = holding_cost
        self.backorder_cost = backorder_cost
        self.transport_cost = transport_cost
        self.transport_size = transport_size
        self.safety_stock = safety_stock
        self.delay_shipping = delay_shipping
        self.delay_ordering = delay_ordering
        self.initial_queue_quantity = initial_queue_quantity
        self.initial_inventory = initial_inventory
        self.production_max = production_max
        self.production_min = production_min
        self.KPI_weeklycost_inventory = [0] * game.weeks
        self.KPI_weeklycost_backorder = [0] * game.weeks
        self.KPI_weeklycost_transport = [0] * game.weeks
        self.KPI_total_cost = [0] * game.weeks
        self.KPI_fullfillment_rate = [0] * game.weeks
        self.KPI_truck_utilization = [0] * game.weeks
        self.inventory = [initial_inventory] + [0] * (game.weeks-1)

        self.backorder = {}
        self.outstanding_orders_to_suppliers = {}
        self.receivedPO = {}
        self.sentPO = {}
        self.inbound = {}
        self.outbound = {}
        self.queue_receive = {}
        self.queue_transmit = {}
        self.customers = []
        self.suppliers = []
        self.n_customers = 0
        self.n_suppliers = 0

    def add_customer(self,customer):
        assert len(self.customers) < self.__MAX_NODE_CUSTOMERS, 'Too many customer connections per node({:}), max is {:}, check game settings data (Connections)'.format(self.station_name,self.__MAX_NODE_CUSTOMERS)
        self.customers.extend([customer])
        self.n_customers += 1
        self.backorder[customer.station_name] = [0] * self.game.weeks
        self.receivedPO[customer.station_name] = [0] * self.game.weeks
        self.outbound[customer.station_name] = [0] * self.game.weeks

    def add_supplier(self,supplier):
        assert len(self.suppliers) < self.__MAX_NODE_SUPPLIERS, 'Too many supplier connections per node ({:}), max is {:}, check game settings data (Connections)'.format(self.station_name,self.__MAX_NODE_SUPPLIERS)
        self.suppliers.extend([supplier])
        self.n_suppliers += 1
        self.outstanding_orders_to_suppliers[supplier.station_name] = [0] * self.game.weeks
        self.sentPO[supplier.station_name] = [0] * self.game.weeks
        self.inbound[supplier.station_name] = [0] * self.game.weeks
        self.queue_receive[supplier.station_name] = Queue(maxsize=self.delay_shipping)
        self.queue_transmit[supplier.station_name] = Queue(maxsize=self.delay_ordering)
        for i in range(self.delay_shipping):
            self.queue_receive[supplier.station_name].put(self.initial_queue_quantity)
            self.outstanding_orders_to_suppliers[supplier.station_name][0] += self.initial_queue_quantity
        for i in range(self.delay_ordering):
            self.queue_transmit[supplier.station_name].put(self.initial_queue_quantity)
            self.outstanding_orders_to_suppliers[supplier.station_name][0] += self.initial_queue_quantity

    def check_endnode(self):
        if len(self.suppliers) == 0:
            self.outstanding_orders_to_suppliers['endnode'] = [0] * self.game.weeks
            self.sentPO['endnode'] = [0] * self.game.weeks
            self.inbound['endnode'] = [0] * self.game.weeks
            self.queue_receive['endnode'] = Queue(maxsize=self.delay_shipping)
            for i in range(self.delay_shipping):
                self.queue_receive['endnode'].put(self.initial_queue_quantity)
                self.outstanding_orders_to_suppliers['endnode'][0] += self.initial_queue_quantity

    def receive_po(self,name,po,week):
        self.receivedPO[name][week] += po

    def receive_product(self,name,shipment):
        self.queue_receive[name].put(shipment)

    def decide_order(self,week):
        backorders = week_sum(self.backorder,week)
        outstanding_orders = week_sum(self.outstanding_orders_to_suppliers,week)
        if self.__Quick_Backorder_Recover:
            total_order = max(0,backorders + self.safety_stock - self.inventory[week] - round(outstanding_orders/2))  # use half the outstanding orders to help recover from backorders faster
        else:
            total_order = max(0,backorders + self.safety_stock - self.inventory[week] - outstanding_orders)
        total_order = self.limit_production(total_order,week)
        order = {}
        if self.n_suppliers == 0:
            order['endnode'] = total_order
        elif outstanding_orders > 0:
            for k,v in self.outstanding_orders_to_suppliers.items():
                order[k] = floor((1 - v[week]/outstanding_orders) * total_order)  # award more orders to suppliers with lower outstanding orders
        else:
            for k,v in self.outstanding_orders_to_suppliers.items():
                order[k] = floor(total_order/self.n_suppliers)  # award orders to suppliers equaly
        remainder = total_order - sum(order.values())
        if remainder > 0:
            order[keywithminval(self.outstanding_orders_to_suppliers,week)] += remainder
        return order

    def decide_shipment(self,week):
        backorders = week_sum(self.backorder,week)
        total_shipment = min(backorders,self.inventory[week])
        shipment = {}
        if total_shipment > 0:  # also means backorders is not zero
            for k,v in self.backorder.items():
                shipment[k] = floor(v[week]/backorders * total_shipment)  # ship more to customers with more backorders
        else:
            for k,v in self.backorder.items():
                shipment[k] = 0
        remainder = total_shipment - sum(shipment.values())
        if remainder > 0:
            shipment[keywithmaxval(self.backorder,week)] += remainder
        return shipment

    def limit_production(self,value,week):
        return min(max(value,self.production_min[week]),self.production_max[week])

    def process(self,week):
        supplier_names = [z.station_name for z in self.suppliers]
        customer_names = [z.station_name for z in self.customers]
        if supplier_names == []:
            supplier_names = ['endnode']

        if week > 0:
            self.inventory[week] = self.inventory[week-1]
            for x in customer_names:
                self.backorder[x][week] = self.backorder[x][week-1]
            for x in supplier_names:
                self.outstanding_orders_to_suppliers[x][week] = self.outstanding_orders_to_suppliers[x][week-1]

        if self.__Order_Method == 'WSG':  # decide on PO (using XSG logic)
            order = self.decide_order(week)

        # receive products
        for x in supplier_names:
            self.inbound[x][week] = self.queue_receive[x].get()
            self.outstanding_orders_to_suppliers[x][week] -= self.inbound[x][week]

        # adjust inventory, calculate backorder, decide shipment
        self.inventory[week] += week_sum(self.inbound,week)
        for x in customer_names:
            self.backorder[x][week] += self.receivedPO[x][week]
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

        if self.__Order_Method == 'XSG':  # decide on PO (using XSG logic)
            order = self.decide_order(week)

        if supplier_names == ['endnode']:
            self.queue_receive['endnode'].put(order['endnode'])  # skipping queue_transmit
            self.sentPO['endnode'][week] = order['endnode']
            self.outstanding_orders_to_suppliers['endnode'][week] += order['endnode']
        else:
            for x in self.suppliers:
                x.receive_po(self.station_name,self.queue_transmit[x.station_name].get(),week)
                self.queue_transmit[x.station_name].put(order[x.station_name])
                self.sentPO[x.station_name][week] = order[x.station_name]
                self.outstanding_orders_to_suppliers[x.station_name][week] += order[x.station_name]

        # calculate costs, KPI
        backorders = week_sum(self.backorder,week)
        shipments = sum(shipment.values())
        self.KPI_weeklycost_inventory[week] = self.holding_cost*self.inventory[week]
        self.KPI_weeklycost_backorder[week] = self.backorder_cost*backorders
        self.KPI_weeklycost_transport[week] = self.transport_cost*trucks
        self.KPI_total_cost[week] = self.KPI_weeklycost_inventory[week] + self.KPI_weeklycost_backorder[week] + self.KPI_weeklycost_transport[week]
        if (backorders+shipments) > 0:
            self.KPI_fullfillment_rate[week] = shipments/(backorders+shipments)
        else:
            self.KPI_fullfillment_rate[week] = 1
        if trucks > 0:
            self.KPI_truck_utilization[week] = (shipments/self.transport_size)/trucks
        else:
            self.KPI_truck_utilization[week] = 1


class Demand():
    """ A class defining demand in the supply chain game

    Attributes:

    Methods:

    """

    __MAX_NODE_SUPPLIERS = 2

    def __init__(
        self,
        game,
        name,
        demand=[]
    ):
        if demand == []:
            demand = [4]*5 + [8]*(game.weeks-5)
        self.demand = demand
        self.game = game
        self.station_name = name
        self.station_player = "CPU"
        self.inbound = {}
        self.customers = []
        self.suppliers = []
        self.n_customers = 0
        self.n_suppliers = 0

    def add_supplier(self,supplier):
        assert len(self.suppliers) < self.__MAX_NODE_SUPPLIERS, 'Too many supplier connections per node ({:}), max is {:}, check game settings data (Connections)'.format(self.station_name,self.__MAX_NODE_SUPPLIERS)
        self.suppliers.extend([supplier])
        self.n_suppliers += 1
        self.inbound[supplier.station_name] = []

    def check_endnode(self):
        pass  # provided only for compatibility with station class interface

    def receive_product(self,name,shipment):
        self.inbound[name].append(shipment)

    def process(self,week):
        for x in self.suppliers:
            x.receive_po(self.station_name,self.demand[week],week)


def connect_stations(A: Station, B: Station):
    A.add_customer(B)
    B.add_supplier(A)
