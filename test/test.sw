import io


struct List[T] {
    arr: Array[T]

    fn ::new(size: int, func: (int) -> T) -> List[T] {
        return List[T](Array[T](size, func));
    }

    fn ::get(self, index: int) -> T {
        return self.arr.get(index);
    }
}


fn main() -> int {
    let li := List[int]::new(10, |i| i);

    return li.get(3);
}