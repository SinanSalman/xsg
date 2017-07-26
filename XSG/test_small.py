import game

WSG_CONFIG = {'Team_Name': 'small_SC',
              'Weeks': 45,
              'Auto_Decide_Ship_Qty': True,
              'Auto_Decide_Order_Qty': True,
              'Demands':[
                    {'Name':'Client','Demand':[4]*4+[8]*41}
                    ],
              'Stations':[
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
                     'Safety_Stock':0,
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
                     'Safety_Stock':0,
                     'Production_Min':[],
                     'Production_Max':[]}
                     ],
              'Connections': [
                    {'supp':'Wholesaler','cust':'Retailer'},
                    {'supp':'Retailer','cust':'Client'},
                    ]
              }

G = game.Game(config=WSG_CONFIG)
G.Run()
G.Report()
G.Plots()
