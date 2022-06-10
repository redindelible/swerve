import std::putc


fn call_thrice(func: () -> int) -> () {
    func();
    func();
    func();
}


fn main() -> int {
    let a := 0;
    call_thrice(|| { a = a + 1; });
    return a;
}