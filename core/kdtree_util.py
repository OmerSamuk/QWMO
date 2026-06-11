from scipy.spatial import KDTree
import numpy as np


def build_kdtree(positions):
    return KDTree(positions)


def query_radius(kdtree, point, radius):
    indices = kdtree.query_ball_point(point, radius)
    return indices


def query_pairs(kdtree, radius):
    pairs = kdtree.query_pairs(radius)
    return list(pairs)
