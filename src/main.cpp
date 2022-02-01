
#include <hwlib.hpp>
#include <catch.hpp>

//#define CATCH_CONFIG_MAIN

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

unsigned int expression_cpp(unsigned int j) {
    return 8 * j - 3 + j * 2 * (4 + 5);
}

extern "C" unsigned int expression(unsigned int);

int main () {
    // kill the watchdog
    WDT->WDT_MR = WDT_MR_WDDIS;
   
    // wait for the terminal to start on the PC side
    hwlib::wait_ms( 500 );
    
    for (unsigned int i = 0; i < 10; i++) {
        hwlib::cout << i << " " << fib(i) << " " << fib_cpp(i) << hwlib::endl;
    }
    hwlib::cout << expression(5) << " " << expression_cpp(5) << hwlib::endl;
    hwlib::cout << "check" << hwlib::endl;
    return 0;
}
