import random
import numpy as np
from scipy.spatial import distance_matrix
from shapely import Point
from shapely.ops import nearest_points
from .maze import Maze


class OrganicGrowthMaze(Maze):
    def __init__(self, nr_points, fixed_points, boundary_polygon):
        self.k_spring = 5  # spring stiffness
        self.rest_length = 0.1  # rest length of the springs
        self.k_repulsion = 3.5  # repulsion stiffness for non-connected nodes
        self.min_distance = 0.20  # minimal distance between unconnected nodes
        self.dt = 0.10  # time step
        self.num_iterations = 1500  # number of iterations
        self.k_bend = 0.0

        self.nr_points = nr_points
        self.fixed_points = fixed_points
        self.bounding_polygon = boundary_polygon
        self.bounding_polygon_buffer = self.bounding_polygon.buffer(-self.min_distance)

        self.name = "Organic Growth Maze"
        self.init_nodes()

    # Initialize the spring-mass system
    def init_nodes(self):
        nodes = (
            np.random.rand(self.nr_points, 2) * 3 - 1.5
        )  # Random positions in a [-2, 2] square
        velocities = np.zeros_like(nodes)  # Initially, no velocity
        fixed_nodes = {idx: pos for idx, pos in self.fixed_points.items()}

        # Set fixed points to their positions
        for idx, pos in fixed_nodes.items():
            nodes[idx] = pos

        self.nodes = nodes
        self.velocities = velocities
        self.fixed_nodes = fixed_nodes
        self.connections = [(i, i + 1) for i in range(self.nr_points - 1)]

    def simulate(self, num_iterations, dt):

        self.nodes += self.contour_force()  # Initial correction

        for iteration in range(num_iterations):
            self.update_distance_matrix()

            forces = np.zeros_like(self.nodes)
            forces += self.connection_force()
            forces += self.reple_force()
            if iteration % 10 == 9:
                forces += self.contour_force()

            self.update_positions(forces, dt)

            self.add_node(iteration)
            print(f"Iteration {iteration}/{num_iterations}")

    def update_distance_matrix(self):
        self.distance_matrix = distance_matrix(self.nodes, self.nodes)

    def add_node(self, iteration):
        if iteration % 2 == 0 and iteration < 700 and iteration > 30:
            connection = random.choices(self.connections)[0]
            start = connection[0]
            end = connection[1]
            new_point = (self.nodes[start] + self.nodes[end]) / 2
            self.nodes = np.vstack([self.nodes, new_point])
            self.velocities = np.vstack([self.velocities, np.zeros(2)])
            self.connections.remove(connection)
            self.connections.append([len(self.nodes) - 1, start])
            self.connections.append([len(self.nodes) - 1, end])


    def contour_force(self):
        forces = np.zeros_like(self.nodes)
        for i, p in enumerate(self.nodes):
            point = Point(p)
            if not self.bounding_polygon.contains(point):
                    # Reflect the node back to the polygon
                # nearest_point = bounding_polygon.exterior.interpolate(bounding_polygon.exterior.project(point))
                nearest_point = nearest_points(self.bounding_polygon, point)[0]
                forces[i] += (np.array(nearest_point.coords[0]) - p) * self.k_repulsion # Show the final result
        return forces

    # Compute spring forces between connected nodes
    def spring_force(self, node1, node2):
        displacement = node2 - node1
        distance = np.linalg.norm(displacement)
        force_magnitude = self.k_spring * (distance - self.rest_length)
        return force_magnitude * displacement / (distance)

    # Compute repulsive forces to maintain a minimum distance between non-connected nodes
    def repulsive_force(self, node1, node2):
        displacement = node2 - node1
        distance = np.linalg.norm(displacement)
        if distance < self.min_distance:
            force_magnitude = self.k_repulsion * (self.min_distance - distance)
            return -force_magnitude * displacement / (distance + self.min_distance)
        return np.array([0.0, 0.0])

    def connection_force(self):
        forces = np.zeros_like(self.nodes)
        # Apply spring forces
        for i, j in self.connections:
            f = self.spring_force(self.nodes[i], self.nodes[j])
            forces[i] += f
            forces[j] -= f
        return forces

    def reple_force(self):
        forces = np.zeros_like(self.nodes)
        num_nodes = self.nodes.shape[0]
        # Apply repulsive forces for non-connected nodes

        force_magnitude = self.k_repulsion * (self.min_distance - self.distance_matrix)

        x1, x2 = np.meshgrid(self.nodes[:, 0], self.nodes[:, 0])
        d_x = x1 - x2
        y1, y2 = np.meshgrid(self.nodes[:, 1], self.nodes[:, 1])
        d_y = y1 - y2
        displacement = np.stack([d_x, d_y], axis=2)
        distance = np.linalg.norm(displacement, axis=2)

        force_matrix = np.einsum(
            "ij,ijk,ij->ijk",
            1 / (distance + self.min_distance),
            displacement,
            -force_magnitude,
        )

        force_matrix[self.distance_matrix > self.min_distance] = 0
        # TODO cleaner way to do this
        for i in range(num_nodes):
            force_matrix[i, i, :] = 0
        for i, j in self.connections:
            force_matrix[i, j, :] = 0
            force_matrix[j, i, :] = 0

        forces = force_matrix.sum(axis=1)
        forces = np.nan_to_num(forces, 0)
        return forces

    # Update the position of the nodes with Verlet integration
    def update_positions(self, forces, dt):
        # Verlet integration: x(t+dt) = x(t) + v(t) * dt + 0.5 * a(t) * dt^2
        self.nodes += self.velocities * dt + 0.5 * forces * dt**2
        self.velocities += forces * dt

        self.velocities *= 0.9  # Damping to prevent infinite oscillations
        self.velocities = np.clip(
            self.velocities, -1, 1
        )  # Limit the velocity to prevent instability

        # Apply fixed nodes
        for idx, pos in self.fixed_nodes.items():
            self.nodes[idx] = pos
