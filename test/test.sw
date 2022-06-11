

struct Holder[T] {
    val: T

    fn ::get(self) -> T {
        return self.val;
    }

    fn ::set(self, value: T) -> () {
        self.val = value;
    }
}



fn main() -> int {
    let a := Holder[int](3);
    a.set(8);

    return a.get();
}