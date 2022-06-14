import io::putchar


trait Index[T] {
    fn get(self, index: int) -> T;
    fn len(self) -> int;
}


struct List[T] : Index[T] {
    arr: Array[T]

    fn get(self, index: int) -> T {
        return self.arr.get(index);
    }

    fn len(self) -> int {
        return 0;
    }
}


fn main() -> int {
    let a: Index[int] = List[int](Array[int](10, |i| i * 3));

    return a.len();
}