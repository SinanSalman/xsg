import game

WSG_CONFIG = {'Team_Name': 'WSG_test',
              'Weeks': 45,
              'Auto_Decide_Ship_Qty': True,
              'Auto_Decide_Order_Qty': True,
              'Demands':[
                    {'Name':'LumberClient','Demand':[4]*4+[8]*41},
                    {'Name':'PaperClient','Demand':[4]*4+[8]*41}
                    ],
              'Stations':[
                    {'Name':'LumberRetailer',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':0,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,  # no effect if station is an 'endnode'
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':12,
                     'Safety_Stock':40,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'PaperRetailer',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':0,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,  # no effect if station is an 'endnode'
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':12,
                     'Safety_Stock':40,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'LumberWholesaler',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':0,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,  # no effect if station is an 'endnode'
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':12,
                     'Safety_Stock':40,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'PaperWholesaler',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':0,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,  # no effect if station is an 'endnode'
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':12,
                     'Safety_Stock':40,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'PaperMill',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':0,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,  # no effect if station is an 'endnode'
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':12,
                     'Safety_Stock':40,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'SawMill',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':0,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,  # no effect if station is an 'endnode'
                     'Initial_Queue_Quantity':8,
                     'Initial_Inventory':24,
                     'Safety_Stock':85,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'Forest',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':0,
                     'Transport_Size':5,
                     'Delay_Shipping':1,
                     'Delay_Ordering':0,  # no effect if station is an 'endnode'
                     'Initial_Queue_Quantity':7,
                     'Initial_Inventory':12,
                     'Safety_Stock':35,
                     'Production_Min':[7,7,7,6,6,6,6,6,6,6,4,4,4,4,0,0,6,6,6,6,4,4,4,4,4,4,6,6,6,6,6,6,6,6,6,6,6,6,6,6,4,4,4,4,4],
                     'Production_Max':[18,18,18,24,24,24,24,24,24,24,26,26,26,26,0,0,28,28,28,28,26,26,26,26,26,26,24,24,24,24,24,24,24,24,24,24,24,24,24,24,26,26,26,26,26]},
                     ],
              'Connections': [
                    {'supp':'Forest','cust':'SawMill'},
                    {'supp':'SawMill','cust':'LumberWholesaler'},
                    {'supp':'LumberWholesaler','cust':'LumberRetailer'},
                    {'supp':'LumberRetailer','cust':'LumberClient'},
                    {'supp':'SawMill','cust':'PaperMill'},
                    {'supp':'PaperMill','cust':'PaperWholesaler'},
                    {'supp':'PaperWholesaler','cust':'PaperRetailer'},
                    {'supp':'PaperRetailer','cust':'PaperClient'}
                    ]
              }

G = game.Game(config=WSG_CONFIG)
G.Run()
G.Report()
G.WSG_Inv_PO_Report()  # compare inventory and PO outputs
G.Plots()