fn for_f(i:int, high:int, body: (int) -> int) -> () {
    body(i);
    if (i < high - 1) {
        i = i + 1;
        for_f(i, high, body);
    }
}


fn main() -> int {
    let a: int = 0;

    for_f(0, 10, |x| a = a + x);

    return a;
}