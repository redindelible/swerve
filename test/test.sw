import io::putchar


struct List[T] {
    arr: Array[T]

    fn get(self, index: int) -> T {
        return self.arr.get(index);
    }
}


fn main() -> int {
    let a := List[int](Array[int](10, |i| i * 3));

    return a.get(2);
}