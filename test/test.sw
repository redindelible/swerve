
struct Holder[T] {
    val: T
}


fn to_holder[T](item: T) -> Holder[T] {
    return Holder[T](item);
}


fn main() -> int {
    return to_holder[int](1).val;
}