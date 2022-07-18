
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


fn main() -> int {
    let li := List[int]::new(10, |i| i * 2);
    print_number(li[6]);
    return 0;
}