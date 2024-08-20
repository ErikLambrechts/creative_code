
mod vector;

use vector::Vector;

use whiskers::prelude::*;


mod fish;
use fish::Fish;

#[sketch_app]
struct FishPondSketch {
    #[param(slider, min = 3, max = 1500)]
    num_points: usize,

    #[param(slider, min = 0.0, max = 0.2)]
    matching_factor: f64,

    #[param(slider, min = 0.0, max = 0.2)]
    separation_factor: f64,

    #[param(slider, min = 0.0, max = 0.2)]
    centering_factor: f64,

    #[param(slider, min = 0.0, max = 500.0)]
    visual_range: f64,

    #[param(slider, min = 0.0, max = 100.0)]
    min_distance: f64,

    #[param(slider, min = 0.0, max = 20.0)]
    max_speed: f64,

    #[param(slider, min = 0.0, max = 200.0)]
    repelling_factor: f64,

    #[param(slider, min = 0.0, max = 200.0)]
    repelling_margin: f64,

    weight: bool,
    stride: bool,

    #[skip]
    fishs: Vec<Fish>,

    #[skip]
    fish: Fish,

    #[skip]
    heigth: f64,

    #[skip]
    width: f64,

    #[skip]
    last_time: f64,
}

impl Default for FishPondSketch {
    fn default() -> Self {
        let rng = rand::thread_rng();
        let num_fish = 40; // Number of fish to generate
        let mut fishs = Vec::new();

        for _ in 0..num_fish {
            fishs.push(Fish::random());
        }

        let fish = Fish::random();

        Self {
            num_points: 10,
            fishs,
            fish,
            matching_factor: 0.1,
            separation_factor: 0.2,
            centering_factor: 0.1,
            visual_range: 200.0,
            min_distance: 50.0,
            max_speed: 20.0,
            repelling_factor: 50.0,
            repelling_margin: 150.0,
            heigth: 500.0,
            width: 500.0,
            last_time: 0.0,
    weight: true,
    stride: true,
        }
    }
}
impl FishPondSketch {
    fn boids_update(&mut self, ctx: &mut Context) {
        let dt = ctx.time - self.last_time;
        self.last_time = ctx.time;

        let mut new_fishs_positions = Vec::new();
        let mut new_fishs_velocities = Vec::new();
        let mut new_fishs_accelerations = Vec::new();

        for fish in &self.fishs {
            let mut matching = Vector::new(0.0, 0.0);
            let mut centering = Vector::new(0.0, 0.0);
            let mut seperation = Vector::new(0.0, 0.0);

            let mut matching_w = Vector::new(0.0, 0.0);
            let mut centering_w = Vector::new(0.0, 0.0);
            let mut seperation_w = Vector::new(0.0, 0.0);

            let mut nr_fish_in_neighbourhood = 0;
            let mut weight_neighbourhood = 0.0;
            for other_fish in &self.fishs {
                if fish as *const _ != other_fish as *const _ {
                    let distance = fish.get_position().distance(&other_fish.get_position());

                    if distance < self.visual_range {
                        if fish
                            .velocity
                            .dot(&(other_fish.get_position() - fish.get_position()))
                            > 0.0
                        {
                            matching += other_fish.velocity;
                            centering += other_fish.get_position();
                            nr_fish_in_neighbourhood += 1;

                            matching_w += other_fish.velocity * other_fish.weight;
                            centering_w += other_fish.get_position() * other_fish.weight;
                            weight_neighbourhood += other_fish.weight;
                        }
                    }

                    if fish.get_position().distance(&other_fish.center()) < self.min_distance {
                        seperation += fish.get_position() - other_fish.center();
                        seperation_w += (fish.get_position() - other_fish.center()) * other_fish.weight;
                        seperation += fish.get_position() - other_fish.get_position();
                        seperation_w += (fish.get_position() - other_fish.get_position()) * other_fish.weight;
                    }
                }
            }

            if nr_fish_in_neighbourhood > 0 {
                matching = (matching / nr_fish_in_neighbourhood as f64 - fish.velocity)
                    * self.matching_factor;
                centering = (centering / nr_fish_in_neighbourhood as f64 - fish.get_position())
                    * self.centering_factor;
            }
            seperation = (seperation) * self.separation_factor;

            if weight_neighbourhood > 0.0 {
                let total_weight = self.fishs.iter().map(|fish| fish.weight).sum::<f64>();
                matching_w = (matching_w / weight_neighbourhood /fish.weight- fish.velocity) * self.matching_factor;
                centering_w = (centering_w / weight_neighbourhood /fish.weight- fish.get_position()) * self.centering_factor;
                seperation_w = (seperation_w / total_weight/ fish.weight) * self.separation_factor;
            }

            let edge_repulsion_force = self.edge_repulsion(fish);

            let mut acceleration = matching + centering + seperation + edge_repulsion_force;

            if self.weight {
                acceleration = matching_w + centering_w + seperation_w + edge_repulsion_force;
            }

            let mut velocity = fish.velocity + acceleration * dt;

            // limit the velocity
            let max_velocity = self.max_speed * 10.0 / (fish.weight + 2.0);
            if velocity.lenght() > max_velocity  {
                velocity *= max_velocity / velocity.lenght();
            }

            new_fishs_positions.push(fish.get_position() + velocity * dt);
            new_fishs_velocities.push(velocity);
            new_fishs_accelerations.push(acceleration);
        }

        for (fish, new_position) in self.fishs.iter_mut().zip(new_fishs_positions.iter()) {
            fish.set_position(*new_position);
        }
        for (fish, new_velocity) in self.fishs.iter_mut().zip(new_fishs_velocities.iter()) {
            fish.velocity = *new_velocity;
        }
        for (fish, new_accelaration) in self.fishs.iter_mut().zip(new_fishs_accelerations.iter()) {
            fish.acceleration = *new_accelaration;
        }
    }

    fn edge_repulsion(&self, fish: &Fish) -> Vector {
        let mut repeling_x = Vector::new(0.0, 0.0);
        let mut repeling_y = Vector::new(0.0, 0.0);
        let margin = self.repelling_margin;
        let factor = self.repelling_factor;
        let fish_x = fish.get_position().x();
        let fish_y = fish.get_position().y();
        if fish_x < margin {
            repeling_x = Vector::new(factor * (1.0 - fish_x / margin), 0.0);
        }
        if fish_x > self.width - margin {
            repeling_x = Vector::new(-factor * (1.0 - (self.width - fish_x) / margin), 0.0);
        }
        if fish_y < margin {
            repeling_y = Vector::new(0.0, factor * (1.0 - fish_y / margin));
        }
        if fish_y > self.heigth - margin {
            repeling_y = Vector::new(0.0, -factor * (1.0 - (self.heigth - fish_y) / margin));
        }
        repeling_x + repeling_y
    }
}

impl App for FishPondSketch {
    fn update(&mut self, sketch: &mut Sketch, ctx: &mut Context) -> anyhow::Result<()> {
        // sketch.color(Color::DARK_RED);

        // let points = (0..self.num_points)
        //     .map(|_| ctx.rng_point(50.0..sketch.width() - 50.0, 50.0..sketch.height() - 50.0))
        //     .collect::<Vec<_>>();

        // for pts in &points {
        //     sketch.circle(pts.x(), pts.y(), 1.);
        // }

        // sketch.catmull_rom(
        //     points,
        //     1.0,
        // );

        self.heigth = sketch.height();
        self.width = sketch.width();
        self.boids_update(ctx);

        self.fishs.iter_mut().for_each(|fish| {
            fish.draw(sketch);
            sketch.color(Color::DARK_BLUE);
        });

        // self.fish.draw(sketch);

        Ok(())
    }
}

fn main() -> Result {
    FishPondSketch::runner()
        .with_page_size_options(PageSize::A5H)
        .with_layout_options(LayoutOptions::Center)
        .run()
}
