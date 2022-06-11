


fn main() -> int {
    let a := 0;

    let func: () -> () = || { a += 1; };

    func();

    return a;
}