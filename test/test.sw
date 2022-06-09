

struct Holder[T, K] {
    number: T
    other_number: K
}


fn fibo(n: int) -> int {
    return n;
}


fn main() -> int {
    let a: Holder[int, int] = Holder[int, int](425, 32);
    return fibo(a.number) + a.other_number;
}