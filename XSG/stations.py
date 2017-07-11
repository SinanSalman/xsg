class Station():
    """ A station class for game stations in the supply chain game

    Attributes:

    Methods:

    """
    __Default_MAX_ORDER = 999

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
        initial_values=4,
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
        if initial_values < 1:
            initial_values = 1

        # ensuring production_min and production_max is valid
        if production_min == []:
            production_min = [0]*game.weeks
        if production_max == []:
            production_max = [self.__Default_MAX_ORDER]*game.weeks
        a = len(production_min)
        b = len(production_max)
        if a > b:
            print("warning - production_min has more values then production_max, filling missing values with {:}}".format(self.__Default_MAX_ORDER))
            production_max.append([self.__Default_MAX_ORDER]*(a-b))
        if a < b:
            print("warning - production_max has more values then production_min, filling missing values with 0")
            production_max.append([0]*(b-a))

        from queue import Queue
        self.game = game
        self.station_name = name
        self.station_player = player
        self.holding_cost = holding_cost
        self.backorder_cost = backorder_cost
        self.transport_cost = transport_cost
        self.transport_size = transport_size
        self.weeklycost_inventory = []
        self.weeklycost_backorder = []
        self.weeklycost_transport = []
        self.KPI_fullfillment_rate = []
        self.KPI_truck_utilization = []
        self.KPI_total_cost = []
        self.queue_receive = Queue(maxsize=delay_shipping)
        self.queue_transmit = Queue(maxsize=delay_ordering)
        self.inventory = initial_values
        self.safety_stock = safety_stock
        self.backorder = 0
        self.current_order = 0
        self.outstanding_orders_to_supplier = 0
        self.customer = None
        self.supplier = None
        self.production_max = production_max
        self.production_min = production_min

        for i in range(delay_shipping):
            self.queue_receive.put(initial_values)
        for i in range(delay_ordering):
            self.queue_transmit.put(initial_values)

    def receive_po(self,po):
        self.current_order = po

    def receive_product(self,shipment):
        self.queue_receive.put(shipment)

    def decide_order(self,player_order=0):
        if self.game.config_auto_decide_order_qty:
            order = max(0,self.backorder + self.safety_stock - self.inventory - self.outstanding_orders_to_supplier)
        else:
            order = player_order
        return order

    def decide_shipment(self,player_shipment=0):
        if self.game.config_auto_decide_ship_qty:
            shipment = min(self.backorder,self.inventory)
        else:
            shipment = min(player_shipment,self.inventory)
        return shipment

    def limit_production(self,week,order):
        return min(max(order,self.production_min[week]),self.production_max[week])

    def process(self,week):
        from math import ceil
        # receive products + increase inventory
        received_product = self.queue_receive.get()
        self.inventory += received_product
        self.outstanding_orders_to_supplier -= received_product
        # receive orders, decide shipment, calculate backorder, inventory
        self.backorder += self.current_order
        shipment = self.decide_shipment()  # player shipment decision goes here
        self.inventory -= shipment
        self.backorder -= shipment
        # ship product & calculate transport needs
        self.customer.receive_product(shipment)
        trucks = ceil(shipment/self.transport_size)
        # decide on PO
        order = self.limit_production(week,self.decide_order())  # player order decision goes here
        self.outstanding_orders_to_supplier += order
        if self.supplier is None:
            self.queue_receive.put(order)
        else:
            self.supplier.receive_po(self.queue_transmit.get())
            self.queue_transmit.put(order)
        # calculate costs, KPI
        self.weeklycost_inventory.append(self.holding_cost*self.inventory)
        self.weeklycost_backorder.append(self.backorder_cost*self.backorder)
        self.weeklycost_transport.append(self.transport_cost*trucks)
        self.KPI_fullfillment_rate.append(shipment/(self.backorder+shipment))
        self.KPI_truck_utilization.append((shipment/self.transport_size)/trucks)
        self.KPI_total_cost.append(self.weeklycost_inventory[-1] + self.weeklycost_backorder[-1] + self.weeklycost_transport[-1])


class Demand():
    """ A class defining demand in the supply chain game

    Attributes:

    Methods:

    """

    def __init__(
        self,
        game,
        demand=[]
    ):
        if demand == []:
            demand = [4]*5 + [8]*(game.weeks-5)
        self.demand = demand
        self.game = game
        self.station_name = "Demand"
        self.station_player = "CPU"
        self.customer = None
        self.supplier = None
        self.received_product = 0
        self.outstanding_orders_to_supplier = 0
        self.KPI_fullfillment_rate = []

    def receive_product(self,shipment):
        self.received_product += shipment
        self.outstanding_orders_to_supplier -= shipment
        if self.outstanding_orders_to_supplier == 0:
            self.KPI_fullfillment_rate.append(1)
        else:
            self.KPI_fullfillment_rate.append(self.received_product/self.outstanding_orders_to_supplier)

    def process(self,week):
        self.outstanding_orders_to_supplier += self.demand[week]
        self.supplier.receive_po(self.demand[week])


def connect_stations(A: Station, B: Station):
    A.customer = B
    B.supplier = A
