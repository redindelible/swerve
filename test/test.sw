

struct Holder[T, K] {
    number: T
    other_number: K
}


fn fibo(n: int) -> int {
    if (n < 2) {
        return n;
    } else {
        return 2;
    }
}


fn main() -> int {
    let a: Holder[int, int] = Holder[int, int](425, 32);
    return fibo(a.number) + a.other_number;
}