import game

TEST_CONFIG = {'Team_Name': 'root_beer',
               'Weeks': 45,
               'Auto_Decide_Ship_Qty': True,
               'Auto_Decide_Order_Qty': True,
               'Demands':[
                    {'Name':'Consumer','Demand':[]}
                    ],
               'Stations':[
                    {'Name':'Manufacturer',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':5,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':4,
                     'Safety_Stock':4,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'Distributor',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':5,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':4,
                     'Safety_Stock':4,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'Wholesaler',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':5,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':4,
                     'Safety_Stock':4,
                     'Production_Min':[],
                     'Production_Max':[]},
                    {'Name':'Retailer',
                     'Player':'CPU',
                     'Holding_Cost':1,
                     'Backorder_Cost':2,
                     'Transport_Cost':5,
                     'Transport_Size':5,
                     'Delay_Shipping':2,
                     'Delay_Ordering':2,
                     'Initial_Queue_Quantity':4,
                     'Initial_Inventory':4,
                     'Safety_Stock':4,
                     'Production_Min':[],
                     'Production_Max':[]}
                     ],
               'Connections': [
                    {'supp':'Manufacturer','cust':'Distributor'},
                    {'supp':'Distributor','cust':'Wholesaler'},
                    {'supp':'Wholesaler','cust':'Retailer'},
                    {'supp':'Retailer','cust':'Consumer'}
                    ]
               }

G = game.Game(config=TEST_CONFIG)
G.Run()
G.Report()
G.Plots()
