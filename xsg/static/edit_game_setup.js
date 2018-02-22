var schema_demand = {
  "type": "object",
  // "uniqueItems": true,
  "properties": {
    "name": {
      "type": "string",
      "title": "Demand point name",
      "required": true
    },
    "demand": {
      "type": "string",
      "title": "Weekly demand"
    }
  }
}

var schema_station = {
  "type": "object",
  // "uniqueItems": true,
  "properties": {
    "name": {
      "type": "string",
      "title": "Sation name",
      "required": true
    },
    "player_name": {
      "type": "string",
      "title": "Player name"
    },
    "auto_decide_ship_qty": {
      "type": "boolean",
      "title": "Auto-decide shipments"
    },
    "auto_decide_order_qty": {
      "type": "boolean",
      "title": "Auto-decide orders"
    },
    "holding_cost": {
      "type": "number",
      "title": "Holding cost",
      "minimum": 0
    },
    "backorder_cost": {
      "type": "number",
      "title": "Backorder cost",
      "minimum": 0
    },
    "transport_cost": {
      "type": "number",
      "title": "Transport cost",
      "minimum": 0
    },
    "transport_size": {
      "type": "integer",
      "title": "Transport size",
      "minimum": 1
    },
    "delay_shipping": {
      "type": "integer",
      "title": "Shipping delay",
      "minimum": 1
    },
    "delay_ordering": {
      "type": "integer",
      "title": "Ordering delay",
      "minimum": 1
    },
    "initial_queue_quantity": {
      "type": "number",
      "title": "Queues initial quantity",
      "minimum": 0
    },
    "initial_inventory": {
      "type": "number",
      "title": "Initial Inventory",
      "minimum": 0
    },
    "safety_stock": {
      "type": "number",
      "title": "Safety stock",
      "minimum": 0
    },
    "production_min": {
      "type": "string",
      "title": "Weekly production minimum"
    },
    "production_max": {
      "type": "string",
      "title": "Weekly production maximum"
    }
  }
}

var schema_connection = {
  "type": "object",
  // "uniqueItems": true,
  "properties": {
    "supp": {
      "type": "string",
      "title": "Supplier",
      "required": true
    },
    "cust": {
      "type": "string",
      "title": "Customer",
      "required": true
    }
  }
}

var schema = {
  "title": "GAME SETUP",
  "type": "object",
  "properties": {
    "team_name": {
      "type": "string",
      "title": "Game name",
      "required": true
    },
    "admin_password": {
      "type": "string",
      "title": "Admin password",
      "required": true
    },
    "play_password": {
      "type": "string",
      "title": "Player password",
      "required": true
    },
    "weeks": {
      "type": "integer",
      "title": "Length (weeks)",
      "required": true,
      "minimum": 1
    },
    "expiry": {
      "type": "number",
      "title": "Game expiry (days)",
      "minimum": 0.0007
    },
    "turn_time": {
      "type": "integer",
      "title": "Turn time (seconds)",
      "minimum": 1
    },
    "quick_backorder_recovery": {
      "type": "string",
      "title": "Target zero backorders in auto-ordering",
      "readonly": true
    },
    "auto_order_method": {
      "type": "string",
      "title": "Auto order method",
      "readonly": true
    },
    "demands": {
      "type": "array",
      "title": "Demand points",
      "items": schema_demand
    },
    "stations": {
      "type": "array",
      "title": "Network stations",
      "items": schema_station
    },
    "connections": {
      "type": "array",
      "title": "Network connections",
      "items": schema_connection
    }
  }
}

var options = {
  "form": {
    "attributes": {
      "action": $SCRIPT_ROOT + '/change_game_settings',
      "method": "post",
    },
    "buttons": {
      "back": {
        "title": "Cancel",
        "click": function() {
          if (confirm("Are you sure? press [OK] to abort new game creation or [Cancle] to return.")) {
            window.location.href = $SCRIPT_ROOT + '/delete_game?next=index&game_name=' + SETUP.team_name;
          }
        }
      },
      "submit": {
        "title": "Save Setup",
        "click": function() {
          this.refreshValidationState(true);
          if (!this.isValid(true)) {
            this.focus();
            return;
          }
          $.ajax({
            url: $SCRIPT_ROOT + '/change_game_settings',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify(this.getValue(), null, "  "),
            success: function(data) {
              $("#msg").text(data.msg);
              $("#msg")[0].style.display = 'block'
              if ($("#msg").text() == 'Game setup saved.') {
                setTimeout(function () {window.location.href = $SCRIPT_ROOT + '/index'}, 1000);  // redirect to main menu after 1 second
              }
            },
            fail: function(data) {
              alert("Error: unable to send data to server.");
            }
          })
        }
      }
    }
  },
  "fields": {
    "team_name": {
      "placeholder": "Unique game ID"
    },
    "admin_password": {
      "placeholder": "Pasword to administer game"
    },
    "play_password": {
      "placeholder": "Password to join game"
    },
    "weeks": {
      "placeholder": "Number of weeks to be played; e.g. 45 weeks"
    },
    "expiry": {
      "placeholder": "Number of days after which the game will automatically expire; e.g. 120 days"
    },
    "turn_time": {
      "placeholder": "Number of seconds a player has to make decisions; e.g. 90 seconds or -1 to disable timer"
    },
    "quick_backorder_recovery": {},
    "auto_order_method": {},
    "demands": {
      "toolbarSticky": true,
      "fields": {
        "item": {
          "fields": {
            "name": {
              "placeholder": "Unique demand point ID; e.g. customer, client1, client2, etc."
            },
            "demand": {
              "placeholder": "Array of weekly demand; e.g. 5, 6, 4, 5, 8",
              "type": "textarea",
              "rows": 2
            }
          }
        }
      }
    },
    "stations": {
      "toolbarSticky": true,
      "fields": {
        "item": {
          "fields": {
            "name": {
              "placeholder": "Unique station ID; e.g. Mfg, Retail1, Retail2, etc."
            },
            "player_name": {
              "placeholder": "Default player name; e.g. cpu"
            },
            "auto_decide_ship_qty": {},
            "auto_decide_order_qty": {},
            "holding_cost": {
              "placeholder": "Cost per unit held for a week; default = $1"
            },
            "backorder_cost": {
              "placeholder": "Cost of unfulfilling a unit order for one week = $2"
            },
            "transport_cost": {
              "placeholder": "Cost per truck; default = $5/truck"
            },
            "transport_size": {
              "placeholder": "Truck capacity; default = 5 units/truck"
            },
            "delay_shipping": {
              "placeholder": "Shipping time delay; default = 2 weeks"
            },
            "delay_ordering": {
              "placeholder": "Ordering process time delay; default = 2 weeks"
            },
            "initial_queue_quantity": {
              "placeholder": "Initial units placed in queues positions at week 1; default = 4 units"
            },
            "initial_inventory": {
              "placeholder": "Initial units in inventory at week 1; default = 4 units"
            },
            "safety_stock": {
              "placeholder": "Safety stock level, used in auto-ordering logic; default = 4 units"
            },
            "production_min": {
              "placeholder": "Array of minimum production limits; e.g. 10, 10, 20, 30, 10",
              "type": "textarea",
              "rows": 2
            },
            "production_max": {
              "placeholder": "Array of maximum production limits; e.g. 20, 20, 40, 50, 20",
              "type": "textarea",
              "rows": 2
            }
          }
        }
      }
    },
    "connections": {
      "toolbarSticky": true,
      "fields": {
        "item": {
          "fields": {
            "supp": {
              "placeholder": "Unique Supplier ID; see stations"
            },
            "cust": {
              "placeholder": "Unique Customer ID; see demand points and stations"
            }

          }
        }
      }
    }
  }
}

var view = {
  "parent": "bootstrap-edit",
  "displayReadonly": true,
  "horizontal": true,
  "templates": {
    "3c": '<div class="row">' + '{{#if options.label}}<h2>{{options.label}}</h2><span></span>{{/if}}' + '{{#if options.helper}}<p>{{options.helper}}</p>{{/if}}' + '<div id="column-1" class="col-md-6"> </div>' + '<div id="column-2" class="col-md-6"> </div>' + '<div id="column-3" class="col-md-12"> </div>' + '<div class="clear"></div>' + '</div>',
  },
  "layout": {
    "template": "3c",
    "bindings": {
      "team_name": "column-1",
      "admin_password": "column-1",
      "play_password": "column-1",
      "weeks": "column-2",
      "expiry": "column-2",
      "turn_time": "column-2",
      "quick_backorder_recovery": "column-1",
      "auto_order_method": "column-2",
      "demands": "column-3",
      "stations": "column-3",
      "connections": "column-3"
    }
  }
}

$(document).ready(function() {
  $("#msg")[0].style.display = 'none'
  $("#form").alpaca({
    "data": SETUP,
    "schema": schema,
    "options": options,
    "view": view
  });
})
