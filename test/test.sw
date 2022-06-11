

struct DiscountNamespace {
    fn ::rand_int() -> int {
        # 100% natural and free-range random number
        return 4;
    }
}

fn main() -> int {
    return DiscountNamespace().rand_int();
}