

struct Holder[T, K] {
    number: T
    other_number: K
}


fn main() -> int {
    let a: Holder[int, int] = Holder[int, int](425, 32);
    return a.number + a.other_number;
}