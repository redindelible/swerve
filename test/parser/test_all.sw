
struct StructNoGeneric {
    look: StructNoGeneric

    fn ::static() -> StructNoGeneric {

    }

    fn ::not_as_static(self) -> P {
        let k := self;
        if (k > 0) {
            return self;
        }
    }
}

struct GenericStruct[K, V] {
    a: K
    v: V
}


fn main() -> int {
    let a : int = 0;

    return 0;
}