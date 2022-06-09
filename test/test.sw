import std::putc


struct Holder[T] {
    a: T
}


fn collatz(num: int) -> int {
    let times := 0;
    while (num != 1) {
        if (num % 2 == 0) {
            num = num / 2;
        } else {
            num = num * 3 + 1;
            times += 1;
        }
    }
    return times;
}


fn main() -> int {
    let val := Holder[int](collatz(15));
    val.a += 1;
    return val.a;
}