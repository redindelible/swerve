import "std/std.sw"::putc


struct Holder[T, K] {
    number: T
    other_number: K
}


fn fibo(n: int) -> int {
    if (n < 2) {
        return n;
    } else {
        return fibo(n-1) + fibo(n-2);
    }
}


fn call(func: (int) -> int, arg: int) -> int {
    return func(arg);
}


fn main() -> int {
    let a := Holder[int, int](22, 32);
    return call(fibo, a.number);
}