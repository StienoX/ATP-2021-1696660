
#include <hwlib.hpp>

//#define CATCH_CONFIG_MAIN
//#define CATCH_CONFIG_NO_POSIX_SIGNALS
//#include <catch2/catch.hpp>

unsigned int fib_cpp (unsigned int x) {
    if (x == 0 || x == 1) {
        return 1;
    } else {
        return fib_cpp(x - 2) + fib_cpp(x - 1);
    }
}

unsigned int odd_cpp(unsigned int n);

unsigned int even_cpp(unsigned int n) {
    if (n == 0) {
        return 1;
    } else {
        return odd_cpp(n-1);
    }
}

unsigned int odd_cpp(unsigned int n) {
    if (n == 0) {
        return 0;
    } else {
        return even_cpp(n-1);
    }
}

int expression_cpp(int j) {
    return (8 + 2 - 3 + 1 - 2 - (4 + 5)) * j;
}

// Pascal functions. See pascal.txt for implementation. (is the same as the cpp functions above)
extern "C" unsigned int fib(unsigned int);
extern "C" unsigned int even(unsigned int);
extern "C" unsigned int odd(unsigned int);
extern "C" int expression(int);

extern "C" int xpr_var_plus_var(int);
extern "C" int xpr_var_times_var(int);
extern "C" int xpr_var_sub_var(int);

extern "C" int xpr_var_plus_const(int);
extern "C" int xpr_var_sub_const(int);
extern "C" int xpr_var_times_const(int);

extern "C" int xpr_const_plus_const();
extern "C" int xpr_const_sub_const();
extern "C" int xpr_const_times_const();


// Getting catch2 reference errors when using with hwlib. I don't how to fix these. So I will not be using Catch but instead be running the tests from the main() function

/*
TEST_CASE( "odd_cpp implementation compared to odd pascal implementation", "[odd, odd_cpp]" ) {
    REQUIRE( odd_cpp(1) == odd(1));
    REQUIRE( odd_cpp(2) == odd(2));
    REQUIRE( odd_cpp(3) == odd(3));
    REQUIRE( odd_cpp(4) == odd(4));
    REQUIRE( odd_cpp(5) == odd(5));
    REQUIRE( odd_cpp(6) == odd(6));
    REQUIRE( odd_cpp(7) == odd(7));
    REQUIRE( odd_cpp(8) == odd(8));
    REQUIRE( odd_cpp(9) == odd(9));
    REQUIRE( odd_cpp(12241) == odd(12241));
}

TEST_CASE( "even_cpp implementation compared to even pascal implementation", "[even, even_cpp]" ) {
    REQUIRE( even_cpp(1) == even(1));
    REQUIRE( even_cpp(2) == even(2));
    REQUIRE( even_cpp(3) == even(3));
    REQUIRE( even_cpp(4) == even(4));
    REQUIRE( even_cpp(5) == even(5));
    REQUIRE( even_cpp(6) == even(6));
    REQUIRE( even_cpp(7) == even(7));
    REQUIRE( even_cpp(8) == even(8));
    REQUIRE( even_cpp(9) == even(9));
    REQUIRE( even_cpp(12241) == even(12241));
}

TEST_CASE( "expression_cpp implementation compared to expression pascal implementation", "[expression, expression_cpp]" ) {
    REQUIRE( expression_cpp(1) == expression(1));
    REQUIRE( expression_cpp(2) == expression(2));
    REQUIRE( expression_cpp(3) == expression(3));
    REQUIRE( expression_cpp(4) == expression(4));
    REQUIRE( expression_cpp(5) == expression(5));
    REQUIRE( expression_cpp(6) == expression(6));
    REQUIRE( expression_cpp(7) == expression(7));
    REQUIRE( expression_cpp(8) == expression(8));
    REQUIRE( expression_cpp(9) == expression(9));
    REQUIRE( expression_cpp(12241) == expression(12241));
}

TEST_CASE( "fib_cpp implementation compared to fib pascal implementation", "[fib, fib_cpp]" ) {
    REQUIRE( fib_cpp(1) == fib(1));
    REQUIRE( fib_cpp(2) == fib(2));
    REQUIRE( fib_cpp(3) == fib(3));
    REQUIRE( fib_cpp(4) == fib(4));
    REQUIRE( fib_cpp(5) == fib(5));
    REQUIRE( fib_cpp(6) == fib(6));
    REQUIRE( fib_cpp(7) == fib(7));
    REQUIRE( fib_cpp(8) == fib(8));
    REQUIRE( fib_cpp(9) == fib(9));
    //higher numbers take a really long time to compute. (or do not compute at all)
}
*/


int main() {

    // kill the watchdog
    WDT->WDT_MR = WDT_MR_WDDIS;
   
    // wait for the terminal to start on the PC side
    hwlib::wait_ms( 500 );

    unsigned int lst[] = {1,2,3,4,5,6,7,8,9,20,1235};
    unsigned int rslt_odd[] = {0,0};
    unsigned int rslt_even[] = {0,0};
    unsigned int rslt_expression[] = {0,0};
    unsigned int rslt_fib[] = {0,0};
    unsigned int rslt_simple_expressions[] = {0,0};
    
    // test basic expression:
    rslt_simple_expressions[xpr_const_plus_const() == 8] += 1;      // 4 + 4
    rslt_simple_expressions[xpr_const_times_const() == 16] += 1;    // 4 * 4
    rslt_simple_expressions[xpr_const_sub_const() == 0] += 1;       // 4 - 4

    rslt_simple_expressions[xpr_var_plus_const(4) == 8] += 1;       // var + 4
    rslt_simple_expressions[xpr_var_times_const(4) == 16] += 1;     // var * 4 
    rslt_simple_expressions[xpr_var_sub_const(4) == 0] += 1;        // var - 4

    rslt_simple_expressions[xpr_var_plus_var(4) == 8] += 1;         // var + var
    rslt_simple_expressions[xpr_var_times_var(4) == 16] += 1;       // var * var
    rslt_simple_expressions[xpr_var_sub_var(4) == 0] += 1;          // var - var


    // tests the following value's (1,2,3,4,5,6,7,8,9,20,1235) inside the functions: odd, even, fib and expression
    for (unsigned int i = 0; i < 11; i++) {
        rslt_odd[odd(lst[i]) == odd_cpp(lst[i])] += 1;
        rslt_even[even(lst[i]) == even_cpp(lst[i])] += 1;
        rslt_expression[expression(lst[i]) == expression_cpp(lst[i])] += 1;
        if (i < 10) // skipping high number due long computation time (or running out of stack space)
            rslt_fib[fib(lst[i]) == fib_cpp(lst[i])] += 1;
    }
    hwlib::cout << hwlib::endl;
    hwlib::cout << "Done" << hwlib::endl;
    hwlib::cout << "Basic expressions test: "   << rslt_simple_expressions[1]   << " out of " << rslt_simple_expressions[1] + rslt_simple_expressions[0]    << " completed successfully" << hwlib::endl;
    hwlib::cout << "Odd Unit test: "            << rslt_odd[1]                  << " out of " << rslt_odd[1] + rslt_odd[0]                                  << " completed successfully" << hwlib::endl;
    hwlib::cout << "Even Unit test: "           << rslt_even[1]                 << " out of " << rslt_even[1] + rslt_even[0]                                << " completed successfully" << hwlib::endl;
    hwlib::cout << "Expression Unit test: "     << rslt_expression[1]           << " out of " << rslt_expression[1] + rslt_expression[0]                    << " completed successfully" << hwlib::endl;
    hwlib::cout << "Fib Unit test: "            << rslt_fib[1]                  << " out of " << rslt_fib[1] + rslt_fib[0]                                  << " completed successfully" << hwlib::endl;

    return 0;
}

