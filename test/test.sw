

struct Holder[T] {
    number: T
}


fn main() -> int {
    let a: Holder[int] = Holder[int](425);
    return a.number;
}