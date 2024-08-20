use itertools::izip;
use rand::Rng;
use whiskers::prelude::*;

use crate::vector::Vector;

#[derive(serde::Deserialize, serde::Serialize)]
// add a struct representing a fish that can be updated and drawn
pub struct Fish {
    spine: Vec<Vector>,
    width: Vec<f64>,
    pub weight: f64,
    segment_lenght: f64,
    pub velocity: Vector,
    pub acceleration: Vector,
    distance: f64,
}

impl Fish {
    // Method to create a new Fish instance
    pub fn new(spine: Vec<Vector>, width: Vec<f64>, weight: f64) -> Self {
        Fish {
            spine,
            width,
            weight,
            segment_lenght : weight / 9.0,
            velocity: Vector::new(0.0, 0.0),
            acceleration: Vector::new(0.0, 0.0),
            distance: 0.0,
        }
    }

    pub fn random() -> Self {
        let mut rng = rand::thread_rng();
        let spine: Vec<Vector> = (0..30).map(|_| Vector::random()).collect();
        let weight = (rng.gen_range(-1.0..3.0) as f64).powi(2) + 1.0;
        let width: Vec<f64> = (0..30)
            .map(|_| rng.gen_range(1.0..10.0) * (weight / 6.0))
            .collect();
        Fish::new(spine, width, weight)
    }

    pub fn draw(&mut self, sketch: &mut Sketch) {
        self.update_spline_shape();
        // Draw the fish
        // draw the spine
        sketch.color(Color::RED);
        let spine = self
            .spine
            .iter()
            .map(|v| (Point::from(*v)))
            .collect::<Vec<Point>>();
        sketch.color(Color::RED);

        sketch.add_path(&spine);

        // generate a list agles between the spine segments
        let mut angles = self
            .spine
            .windows(3)
            .map(|w| (w[1] - w[0]).angle(&(w[1] - w[2])))
            .collect::<Vec<f64>>();

        angles.push(std::f64::consts::PI);

        // run over the spine segements, wide and angles and generate list of points
        let mut points_l = Vec::new();
        let mut points_r = Vec::new();

        let normal = (self.spine[1] - self.spine[0])
            .rotate(std::f64::consts::PI / 2.0)
            .normalize();
        let p1 = self.spine[0] + normal * self.width[0];
        let p2 = self.spine[0] - normal * self.width[0];
        points_l.push(p1);
        points_r.push(p2);
        izip!(
            self.spine.windows(2),
            self.width.iter().skip(1),
            angles.iter(),
        )
        .for_each(|(segement, width, angle)| {
            let width = *width;
            let angle = angle;
            let normal = (segement[1] - segement[0]).rotate(angle / 2.0).normalize();
            let p1 = segement[1] + normal * (width) * angle.signum();
            let p2 = segement[1] - normal * (width) * angle.signum();
            points_l.push(p1);
            points_r.push(p2);
        });

        let side_r = points_r
            .iter()
            .map(|v| (Point::from(*v)))
            .collect::<Vec<Point>>();
        let side_l = points_l
            .iter()
            .map(|v| (Point::from(*v)))
            .collect::<Vec<Point>>();

        sketch.color(Color::DARK_BLUE);
        sketch.add_path(&side_l);
        sketch.add_path(&side_r);
    }

    fn update_spline_shape(&mut self) {
        for i in 1..self.spine.len() {
            self.update_constraint_spline_segement_lenght(i);
            self.update_constraint_spline_segement_angle(i);
        }

        let speed_increase = if self.velocity.dot(&self.acceleration) > 0.0 {
            self.acceleration.lenght().max(0.1)
        } else {
            0.0
        };
        let nr_tail_segemnetds = 15;
        let tail_index_offset = self.spine.len() - nr_tail_segemnetds;
        for i in 0..nr_tail_segemnetds {
            let stride = {
                (((i as f64) / ((nr_tail_segemnetds - 1) as f64 * 10.0)).exp() - 1.0) / std::f64::consts::E
                    * speed_increase
                    * ((-(i as f64) * self.segment_lenght - self.distance) * std::f64::consts::PI * self.velocity.lenght() / 10.0 / (self.segment_lenght * nr_tail_segemnetds as f64)).cos()
            };

            let normal = (self.spine[tail_index_offset+ i] - self.spine[tail_index_offset + i - 1])
                .rotate(std::f64::consts::FRAC_PI_2)
                .normalize();
            self.spine[tail_index_offset + i] =
                self.spine[tail_index_offset + i] + normal * stride * 0.01;
        }

        for i in 1..self.spine.len() {
            self.update_constraint_spline_segement_lenght(i);
        }
    }

    fn update_constraint_spline_segement_lenght(&mut self, i: usize) {
        // update the spine such that they are at a distance from each other
        self.spine[i] = self.spine[i - 1]
            + (self.spine[i] - self.spine[i - 1])
                * (self.segment_lenght/ (self.spine[i] - self.spine[i - 1]).lenght());
    }

    fn update_constraint_spline_segement_angle(&mut self, i: usize) {
        // limit the angle between the spine segments
        if i < self.spine.len() - 1 {
            let segement_0 = self.spine[i - 1] - self.spine[i];
            let segement_1 = self.spine[i + 1] - self.spine[i];
            let angle = segement_0.angle(&segement_1);

            let min_angle = 160.0 / 180.0 * std::f64::consts::PI;
            if angle.abs() < min_angle {
                let angle = min_angle * angle.signum();
                let new_segment_1 = segement_0.rotate(angle);

                self.spine[i + 1] = self.spine[i] + new_segment_1;
            }
        }
    }

    pub fn get_position(&self) -> Vector {
        self.spine[0]
    }

    pub fn set_position(&mut self, position: Vector) {
        self.distance += (position - self.spine[0]).lenght();
        self.spine[0] = position;
    }

    pub fn center(&self) -> Vector {
        let mut center = Vector::new(0.0, 0.0);
        for point in &self.spine {
            center = center + *point;
        }
        center / self.spine.len() as f64
    }
}
