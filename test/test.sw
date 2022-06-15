import io


struct List[T] : ops::Index[T] {
    arr: _array[T]
    len: int
    cap: int

    fn ::new(size: int, func: (int) -> T) -> List[T] {
        let arr := _array[T](size);
        let i := 0;
        while (i < size) {
            arr.set(i, func(i));
            i = i + 1;
        }
        return List[T](arr, size, size);
    }

    fn ::new_empty() -> List[T] {
        let arr := _array[T](1);
        return List[T](arr, 0, 1);
    }

    fn ::resize(self) -> () {
        let new_arr := _array[T](self.cap * 2);
        let i := 0;
        while (i < self.len) {
            new_arr.set(i, self.arr.get(i));
            i += 1;
        }
        self.arr = new_arr;
        self.cap = self.cap * 2;
    }

    fn ::append(self, item: T) -> () {
        if (self.len + 1 > self.cap) {
            self.resize();
        }
        self.arr.set(self.len, item);
        self.len += 1;
    }

    fn get(self, index: int) -> T {
        return self.arr.get(index);
    }
}


fn main() -> int {
    let li := List[int]::new_empty();
    li.append(1);
    li.append(2);
    li.append(3);

    let indexable: ops::Index[int] = li;

    return indexable[2];
}