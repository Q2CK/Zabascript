fn fibonacci(n) {
    if(n == 0 || n == 1) {
        return n;
    }
    else(True) {
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
}

fn main() {
    print(fibonacci(10));
}