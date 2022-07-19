import io::putchar

struct List[T] : ops::Index[T], ops::Trace[T] {
    _buffer: _array[T]
    _len: int
    _buffer_size: int

    fn ::new(len: int, fill: (int) -> T) -> List[T] {
        putchar(40);
        let li := List[T](_array[T](len), 0, len);
        putchar(33);
        let i := 0;
        while (i < len) {
            putchar(i + 48);
            let item := fill(i);
            li.push(fill(i));
            putchar(i + 48);
            i += 1;
        }
        putchar(41);
        return li;
    }

    fn ::new_empty() -> List[T] {
        return List[T](_array[T](1), 0, 1);
    }

    fn ::len(self) -> int {
        return self._len;
    }

    fn get(self, index: int) -> T {
        return self._buffer.get(index);
    }

    fn set(self, index: int, item: T) -> () {
        return self._buffer.set(index, item);
    }

    fn trace(self, trace: (T) -> T) -> () {
        let i := 0;
        while (i < self._len) {
            let item := self._buffer.get(i);
            let moved := trace(item);
            self._buffer.set(i, moved);
            i += 1;
        }
    }

    fn ::_resize(self, new_size: int) -> () {
        let buf := _array[T](new_size);
        let i := 0;
        while (i < self._len) {
            buf.set(i, self._buffer.get(i));
            i += 1;
        }
        self._buffer = buf;
        self._buffer_size = new_size;
    }

    fn ::push(self, item: T) -> T {
        putchar(self._buffer_size + 48);
        if (self._buffer_size <= self._len) {
            self._resize(self._buffer_size * 2);
        }
        putchar(33);
        self._buffer.set(self._len, item);
        putchar(33);
        self._len += 1;
        return item;
    }

    fn ::pop(self, index: int) -> T {
        let item := self._buffer.get(index);
        self._len -= 1;
        let i := index;
        while (i < self._len) {
            self._buffer.set(i, self._buffer.get(i+1));
        }
        if (self._buffer_size >= self._len * 4) {
            self._resize(self._buffer_size / 2);
        }
        return item;
    }
}