#include "pymatching/fill_match/flooder/detector_node.h"

#include "pymatching/fill_match/flooder/graph_fill_region.h"

namespace pm {

int32_t DetectorNode::compute_wrapped_radius() const {
    if (reached_from_source == nullptr) {
        return 0;
    }
    int32_t total = 0;
    auto r = region_that_arrived;
    while (r != region_that_arrived_top) {
        total += r->radius.y_intercept();
        r = r->blossom_parent;
    }
    return total - radius_of_arrival;
}

Varying32 DetectorNode::local_radius() const {
    if (region_that_arrived_top == nullptr) {
        return Varying32{0};
    }
    return region_that_arrived_top->radius + compute_wrapped_radius();
}

bool DetectorNode::has_same_owner_as(const DetectorNode &other) const {
    return region_that_arrived_top == other.region_that_arrived_top;
}

void DetectorNode::reset() {
    observables_crossed_from_source = 0;
    reached_from_source = nullptr;
    radius_of_arrival = 0;
    region_that_arrived = nullptr;
    region_that_arrived_top = nullptr;
    accumulated_radius_cached = 0;
    node_event_tracker.clear();
}

size_t DetectorNode::index_of_neighbor(DetectorNode *target) const {
    for (size_t k = 0; k < neighbors.size(); k++) {
        if (neighbors[k] == target) {
            return k;
        }
    }
    throw std::invalid_argument("Failed to find neighbor.");
}

}  // namespace pm
