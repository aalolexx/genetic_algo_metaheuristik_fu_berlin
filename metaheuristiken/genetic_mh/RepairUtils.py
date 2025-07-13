def repair_possible_solution(possible_solution):
    """
    Fix overflown PRs by redistributing routes to underutilized PRs with available capacity.
    """
    # Count current PR usage
    pr_usage = {pr["id"]: 0 for pr in possible_solution.pr_list}
    for route in possible_solution.routes:
        pr_usage[route.PR] += 1

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
                "distance": int(edge["distance_km"]) * 1000  # convert to meters
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
                    pr_usage[route.PR] -= 1  # remove from old
                    route.PR = pr_id
                    pr_usage[pr_id] += 1
                    break  # move to next route

    return possible_solution
