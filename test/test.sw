

fn main() -> int {
    let arr := array[int](8, |i| i * 2);

    arr.set(3, arr.get(3) * 2);

    return arr.get(3);
}