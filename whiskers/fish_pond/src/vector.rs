    use whiskers::prelude::Point;

    use rand::Rng;
    use std::ops::{Add, AddAssign, Div, Mul, MulAssign, Sub};
    #[derive(Clone, Copy, Debug, serde::Deserialize, serde::Serialize)]
    pub struct Vector(Point);

    impl Vector {
        pub fn x(&self) -> f64 {
            self.0.x()
        }

        pub fn y(&self) -> f64 {
            self.0.y()
        }

        pub fn lenght(&self) -> f64 {
            self.0.distance(&Point::new(0.0, 0.0))
        }

        pub fn dot(&self, other: &Self) -> f64 {
            self.x() * other.x() + self.y() * other.y()
        }

        pub fn angle(&self, other: &Self) -> f64 {
            let dot = self.dot(other);
            let det = self.x() * other.y() - self.y() * other.x();
            det.atan2(dot)
        }

        pub fn rotate(&self, angle: f64) -> Self {
            Vector::new(
                self.x() * angle.cos() - self.y() * angle.sin(),
                self.x() * angle.sin() + self.y() * angle.cos(),
            )
        }

        pub fn new(x: f64, y: f64) -> Self {
            Vector(Point::new(x, y))
        }

        pub fn distance(&self, other: &Self) -> f64 {
            self.0.distance(&other.0)
        }

        pub fn normalize(&self) -> Self {
            let lenght = self.lenght();
            if lenght == 0.0 {
                return *self;
            }
            *self / lenght
        }

        pub fn random() -> Self {
            let mut rng = rand::thread_rng();
            Vector::new(rng.gen_range(0.0..100.0), rng.gen_range(0.0..100.0))
        }
    }

    impl From<Vector> for Point {
        fn from(vector: Vector) -> Self {
            vector.0
        }
    }

    impl Add for Vector {
        type Output = Self;

        fn add(self, other: Self) -> Self {
            Vector::new(self.x() + other.x(), self.y() + other.y())
        }
    }

    impl Sub for Vector {
        type Output = Self;

        fn sub(self, other: Self) -> Self {
            Vector::new(self.x() - other.x(), self.y() - other.y())
        }
    }

    impl Mul<f64> for Vector {
        type Output = Self;

        fn mul(self, scalar: f64) -> Self {
            Vector::new(self.x() * scalar, self.y() * scalar)
        }
    }

    impl Div<f64> for Vector {
        type Output = Self;

        fn div(self, scalar: f64) -> Self {
            Vector::new(self.x() / scalar, self.y() / scalar)
        }
    }

    impl AddAssign for Vector {
        fn add_assign(&mut self, other: Self) {
            *self = *self + other;
        }
    }

    impl MulAssign<f64> for Vector {
        fn mul_assign(&mut self, scalar: f64) {
            *self = self.mul(scalar);
        }
    }

