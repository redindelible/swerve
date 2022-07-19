
import io::putchar
import list::List


fn print_number(n: int) -> () {
    if (n == 0) {
        putchar(48);
    } else {
        let digits := List[int]::new_empty();
        while (n > 0) {
            digits.push(n % 10);
            n = n / 10;
        }
        let i := digits.len() - 1;
        while (i >= 0) {
            putchar(digits[i] + 48);
            i -= 1;
        }
    }
}


struct Holder[T] {
    item: T
}


fn main() -> int {
    let li := List[int]::new(10, |i| i * 2);
    let item := li[6];
    print_number(item);

    let li2 := List[Holder[int]]::new(10, |i| Holder[int](li[i]));
    print_number(li2[6].item);
    return 0;
}