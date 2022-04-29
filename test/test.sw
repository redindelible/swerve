import std::{io, path}

struct LinkedList[T] {
    item: T
    next: Option

    def ::new(item: T) -> LinkedList {
        return new(item, None);
    }
}