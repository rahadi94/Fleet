from Fleet_sim.Zone import Zone

z = 0
zones = list()
for hex in demand_table['h3_hexagon_id_start'].values:
    z += 1
    demand = 1 / (demand_table[demand_table['h3_hexagon_id_start'] == hex] \
                  .drop('h3_hexagon_id_start', axis=1) * 10)
    zone = Zone(z, hex, demand)
    zones.append(zone)
