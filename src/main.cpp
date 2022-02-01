
#include <hwlib.hpp>
#include <catch.hpp>


unsigned int fib_cpp (unsigned int x) {
    if (x == 0 || x == 1) {
        return 1;
    } else {
        return fib_cpp(x - 2) + fib_cpp(x - 1);
    }
}

extern "C" unsigned int fib(unsigned int);

unsigned int odd_cpp(unsigned int n);

unsigned int even_cpp(unsigned int n) {
    if (n == 0) {
        return 1;
    } else {
        return odd_cpp(n-1);
    }
}

extern "C" unsigned int even(unsigned int);

unsigned int odd_cpp(unsigned int n) {
    if (n == 0) {
        return 0;
    } else {
        return even_cpp(n-1);
    }
}

extern "C" unsigned int odd(unsigned int);

int main () {
    hwlib::cout << "Hello World!" << hwlib::endl;
    return 0;
}
