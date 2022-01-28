
unsigned int fib (unsigned int x) {
    if (x == 0 || x == 1) {
        return 1;
    } else {
        return fib(x - 2) + fib(x - 1);
    }
}

unsigned int even(unsigned int n) {
    if (n == 0) {
        return 1;
    } else {
        return odd(n-1);
    }
}

unsigned int odd(unsigned int n) {
    if (n == 0) {
        return 0;
    } else {
        return even(n-1);
    }
}


int main(void) {
    return 0;
}