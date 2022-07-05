import io::putchar

struct Holder[T] {
    item: T
}


fn main() -> int {
    let h := Holder[Holder[int]](Holder[int](3));

    h.item = Holder[int](5);

    putchar(h.item.item + 48);

    return 0;
}