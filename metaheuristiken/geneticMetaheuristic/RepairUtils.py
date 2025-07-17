import random

def repair_possible_solution(possible_solution):
    """
    Fix overflown PRs by redistributing routes to underutilized PRs with available capacity.
    Also tries to fix the street capacity overflow
    """
    # ------
    #  Repair PR Distribution

    # Count current PR usage
    pr_usage = {pr["id"]: 0 for pr in possible_solution.pr_list}
    for route in possible_solution.routes:
        pr_usage[route.PR] += route.group_size

    # Identify overflown and underused PRs
    pr_capacity = {pr["id"]: pr["capacity"] for pr in possible_solution.pr_list}
    overflown_prs = {pr_id for pr_id, usage in pr_usage.items() if usage > pr_capacity[pr_id]}
    underused_prs = {pr_id for pr_id, usage in pr_usage.items() if usage < pr_capacity[pr_id]}

    # Preprocess a map from each RA to available PRs with distances
    ra_to_pr_edges = {}
    for edge in possible_solution.edges_list:
        if edge["to"] in underused_prs:
            ra_to_pr_edges.setdefault(edge["from"], []).append({
                "to": edge["to"],
                "distance": float(edge["distance_km"]) * 1000  # convert to meters
            })

    # Reassign routes from overflown PRs
    for route in possible_solution.routes:
        if route.PR in overflown_prs:
            ra_id = route.RA
            candidates = ra_to_pr_edges.get(ra_id, [])
            if not candidates:
                continue  # no valid PRs available

            # Sort by distance to minimize extra travel
            candidates.sort(key=lambda x: x["distance"])
            for candidate in candidates:
                pr_id = candidate["to"]
                if pr_usage[pr_id] < pr_capacity[pr_id]:
                    # Reassign route
                    route.set_pr(pr_id, candidate["distance"])
                    pr_usage[route.PR] -= route.group_size  # remove from old
                    route.PR = pr_id
                    pr_usage[pr_id] += route.group_size
                    break  # move to next route


    # ------
    #  Repair Street Capacity Overflow
    attempt = 0
    max_attempts = 5
    while attempt < max_attempts:
        amount_overflow, overflow_sum, norm_time, last_time = possible_solution.get_street_overflows()
        if overflow_sum == 0:
            break  # Repaired successfully

        # Sort clusters by size (largest first)
        clusters = sorted(possible_solution.cluster_mapper.clusters, key=lambda c: c.size, reverse=True)

        for cluster in clusters:
            # Try delaying this cluster's start time slightly
            cluster.start_time += random.randrange(0, 200)

        attempt += 1

    return possible_solution
