"""Optional network analysis interfaces."""


def network_edges(frame, *, max_edges):
    if frame.limit(max_edges + 1).count() > max_edges:
        raise ValueError("Network exceeds the configured driver-side edge budget")
    return frame


def communities(edges, *, max_edges):
    # TODO: Pass a bounded graph to NetworkX, with a fixed seed and weight policy.
    raise NotImplementedError("Community detection is pending")
