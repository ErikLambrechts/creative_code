import random
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points

# Constants
k_spring = 5  # spring stiffness
rest_length = 0.1  # rest length of the springs

k_repulsion = 3.5  # repulsion stiffness for non-connected nodes
min_distance = 0.20  # minimal distance between unconnected nodes
dt = 0.10  # time step
num_iterations = 1500  # number of iterations
k_bend=0.0


# Define the torus shape using two concentric circles (outer and inner boundary)
def create_torus(inner_radius, outer_radius, resolution=100):
    theta = np.linspace(0, 2 * np.pi, resolution)
    outer_circle = [(outer_radius * np.cos(t), outer_radius * np.sin(t)) for t in theta]
    inner_circle = [(inner_radius * np.cos(t), inner_radius * np.sin(t)) for t in theta]
    return Polygon(outer_circle + inner_circle[::-1])

# Initialize the spring-mass system
def init_nodes(num_points, fixed_points):
    nodes = np.random.rand(num_points, 2) * 4 - 2  # Random positions in a [-2, 2] square
    velocities = np.zeros_like(nodes)  # Initially, no velocity
    fixed_nodes = {idx: pos for idx, pos in fixed_points.items()}
    
    # Set fixed points to their positions
    for idx, pos in fixed_nodes.items():
        nodes[idx] = pos
    
    return nodes, velocities, fixed_nodes

# Compute spring forces between connected nodes
def spring_force(node1, node2, rest_length, k_spring):
    displacement = node2 - node1
    distance = np.linalg.norm(displacement)
    force_magnitude = k_spring * (distance - rest_length)
    return force_magnitude * displacement / (distance )

# Compute repulsive forces to maintain a minimum distance between non-connected nodes
def repulsive_force(node1, node2, min_distance, k_repulsion):
    displacement = node2 - node1
    distance = np.linalg.norm(displacement)
    if distance < min_distance:
        force_magnitude = k_repulsion * (min_distance - distance)
        return -force_magnitude * displacement / (distance + min_distance)
    return np.array([0.0, 0.0])

from scipy.spatial import distance_matrix
def reple_force(nodes, connections, min_distance, k_repulsion):
    forces = np.zeros_like(nodes)
    num_nodes = nodes.shape[0]
    # Apply repulsive forces for non-connected nodes

    distance_m = distance_matrix(nodes, nodes)
    force_magnitude = k_repulsion * (min_distance - distance_m)

    x1, x2 = np.meshgrid(nodes[:, 0], nodes[:, 0])
    d_x = x1 - x2
    y1, y2 = np.meshgrid(nodes[:, 1], nodes[:, 1])
    d_y = y1 - y2
    displacement = np.stack([d_x, d_y], axis=2) 
    distance = np.linalg.norm(displacement, axis=2)

    force_matrix = np.einsum('ij,ijk,ij->ijk', 1/(distance + min_distance), displacement, -force_magnitude)    

    force_matrix[distance_m > min_distance] = 0
    # TODO
    for i in range(num_nodes):
        force_matrix[i,i,:] = 0
    for i,j in connections:
        force_matrix[i,j,:] = 0
        force_matrix[j,i,:] = 0
    
    forces = force_matrix.sum(axis=1)
    forces = np.nan_to_num(forces ,0)
    return forces

    

# Update the position of the nodes with Verlet integration
def update_positions(nodes, velocities, forces, dt, fixed_nodes):
    # Verlet integration: x(t+dt) = x(t) + v(t) * dt + 0.5 * a(t) * dt^2
    nodes += velocities * dt + 0.5 * forces * dt**2
    velocities += forces * dt

    velocities *= 0.9  # Damping to prevent infinite oscillations
    velocities = np.clip(velocities, -1, 1)  # Limit the velocity to prevent instability
    # Apply fixed nodes
    for idx, pos in fixed_nodes.items():
        nodes[idx] = pos

    return nodes, velocities
# Simulate the spring-mass system
def simulate(nodes, velocities, connections, fixed_nodes, bounding_polygon, num_iterations, dt):
    bounding_polygon_buffer = bounding_polygon.buffer(-min_distance)
    
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots(figsize=(6, 6))
    
    nodes += contour_force(nodes, bounding_polygon_buffer)  # Initial correction

    ax.clear()  # Clear the previous plot
    plot_system(nodes, connections, bounding_polygon, ax)
    plt.pause(0.10)  # Brief pause to update the plot

    for iteration in range(num_iterations):
        forces = np.zeros_like(nodes)
        
        # Apply spring forces
        for i, j in connections:
            f = spring_force(nodes[i], nodes[j], rest_length, k_spring)
            forces[i] += f
            forces[j] -= f
        
            
        forces += reple_force(nodes, connections, min_distance, k_repulsion)

            # Keep nodes inside the polygon by reflecting them back
        if iteration < 20 or iteration > 10:
            forces += contour_force(nodes, bounding_polygon_buffer, k_repulsion)

            # for a,b,c in bending_triplets:
            #     forceA, forceB, forceC = bending_force(nodes[a], nodes[b], nodes[c], k_bend)
            #     forces[a] += forceA
            #     forces[b] += forceB
            #     forces[c] += forceC
        # Update positions and velocities
        nodes, velocities = update_positions(nodes, velocities, forces, dt, fixed_nodes)
        
        # Plot every 10 iterations
        if iteration % 25 == 24:
            ax.clear()  # Clear the previous plot
            plot_system(nodes, connections, bounding_polygon, ax, iteration)
            plt.pause(0.1)  # Brief pause to update the plot
         
        if iteration % 2 == 0 and iteration < 500 and iteration >30:
            connection = random.choices(connections)[0]
            start = connection[0]
            end = connection[1]
            new_point = (nodes[start] + nodes[end]) / 2
            nodes = np.vstack([nodes, new_point])
            velocities = np.vstack([velocities, np.zeros(2)])
            connections.remove(connection)
            connections.append([len(nodes) - 1, start])
            connections.append([len(nodes) - 1, end])
    
    plt.ioff()  # Turn off interactive mode
    plt.show() 

def countour_fource(nodes, bounding_polygon, num_nodes):
    forces = np.zeros_like(nodes)
    for i in range(num_nodes):
        point = Point(nodes[i])
        if not bounding_polygon.contains(point):
                # Reflect the node back to the polygon
            # nearest_point = bounding_polygon.exterior.interpolate(bounding_polygon.exterior.project(point))
            nearest_point = nearest_points(bounding_polygon, point)[0]
            forces[i] += np.array(nearest_point.coords[0]) - nodes[i] # Show the final result
    return forces

def contour_force(nodes, bounding_polygon, k_repulsion=1):
    forces = np.zeros_like(nodes)
    for i, p in enumerate(nodes):
        point = Point(p)
        if not bounding_polygon.contains(point):
                # Reflect the node back to the polygon
            # nearest_point = bounding_polygon.exterior.interpolate(bounding_polygon.exterior.project(point))
            nearest_point = nearest_points(bounding_polygon, point)[0]
            forces[i] += (np.array(nearest_point.coords[0]) - p) * k_repulsion # Show the final result
    return forces

# Visualize the nodes and connections
def plot_system(nodes, connections, bounding_polygon, ax, iteration=None):
    x, y = nodes[:, 0], nodes[:, 1]
    
    # Plot polygon
    x_poly, y_poly = bounding_polygon.exterior.xy
    ax.fill(x_poly, y_poly, color='lightgrey', alpha=0.5)

    # Plot nodes
    ax.scatter(x, y, c='blue')

    # Plot connections
    for i, j in connections:
        ax.plot([x[i], x[j]], [y[i], y[j]], 'k-')
    
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    if iteration is not None:
        ax.set_title(f"Iteration: {iteration}")

# Main
def main():
    # Create torus-like bounding polygon
    torus_polygon = create_torus(inner_radius=0.5, outer_radius=1.5)
    
    # Number of points
    num_points = 20
    branch_points = 20
    
    # Fix two points on either side of the torus
    fixed_points = {0: (-1.4, 0), num_points - 1: (1.4, 0)}
    
    # Initialize nodes and velocities
    nodes, velocities, fixed_nodes = init_nodes(num_points + 3 * branch_points, fixed_points)
    nodes, velocities, fixed_nodes = init_nodes(num_points, fixed_points)

    # Define connections (a chain plus some branches)
    connections = [(i, i+1) for i in range(num_points-1)]
    
    # Adding 3 branches of 20 nodes each at different points
    # branch_starts = [10, 30, 40]  # points where branches start
    # for start in branch_starts:
    #     for i in range(branch_points - 1):
    #         connections.append((num_points + start + i, num_points + start + i + 1))
    #     connections.append((start, num_points + start))  # Connect branch to the main chain
    
    # Simulate the system
    simulate(nodes, velocities, connections, fixed_nodes, torus_polygon, num_iterations, dt)

if __name__ == "__main__":
    main()
