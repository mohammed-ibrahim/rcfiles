#!/bin/python

import math
import os
import random
import re
import sys

# https://www.hackerrank.com/challenges/torque-and-development/problem

def roads_and_lib(n, c_lib, c_road, cities):
    if c_lib <= c_road:
        return n * c_lib

    neighbour_mapping = {}
    dis_groups = {}
    already_visited = set()

    for k in cities:
        src = k[0]
        dest = k[1]

        if src not in neighbour_mapping:
            neighbour_mapping[src] = set()
        neighbour_mapping[src].add(dest)

        if dest not in neighbour_mapping:
            neighbour_mapping[dest] = set()
        neighbour_mapping[dest].add(src)

    for i in range(n):
        city_id = i + 1
        current_group_id = city_id

        if city_id in already_visited:
            continue

        already_visited.add(city_id)
        if current_group_id not in dis_groups:
            dis_groups[current_group_id] = set()

        dis_groups[current_group_id].add(city_id)

        queue = []
        queue.append(city_id)

        while len(queue) > 0:
            current_element = queue.pop()
            dis_groups[current_group_id].add(current_element)
            already_visited.add(current_element)

            if current_element not in neighbour_mapping:
                continue

            for neighbour_city_id in neighbour_mapping[current_element]:
                dis_groups[current_group_id].add(neighbour_city_id)

                if neighbour_city_id not in already_visited:
                    queue.append(neighbour_city_id)

    total_number_of_lib_required = len(dis_groups)
    cost_of_building_all_libs = total_number_of_lib_required * c_lib

    total_cost_of_roads = 0

    for key in dis_groups:
        total_cost_of_roads += c_road * (len(dis_groups[key]) - 1)
    
    return cost_of_building_all_libs + total_cost_of_roads

