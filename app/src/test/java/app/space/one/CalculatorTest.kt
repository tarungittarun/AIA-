package app.space.one

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class CalculatorTest {
    @Test fun respectsOperatorPrecedence() = assertEquals("14", evaluate("2+3*4"))
    @Test fun supportsGrouping() = assertEquals("20", evaluate("(2+3)*4"))
    @Test fun decimalArithmeticIsExact() = assertEquals("0.3", evaluate("0.1+0.2"))
    @Test fun divisionKeepsExactIntermediateValues() = assertEquals("1", evaluate("1/3*3"))
    @Test fun supportsUnaryMinus() = assertEquals("-10", evaluate("10×−"))
    @Test fun trailingAdditionRepeatsTheLeftValue() = assertEquals("10", evaluate("5+"))
    @Test fun implicitMultiplicationWorks() = assertEquals("14", evaluate("2(5+2)"))
    @Test fun powerIsRightAssociative() = assertEquals("512", evaluate("2^3^2"))
    @Test fun additionPercentUsesAccumulatedLeft() = assertEquals("242", evaluate("200+10%+10%"))
    @Test fun multiplicationPercentIsPlainPercent() = assertEquals("20", evaluate("200×10%"))
    @Test fun standalonePercentDividesByOneHundred() = assertEquals("0.5", evaluate("50%"))
    @Test fun equalsBalancesOpenParentheses() = assertEquals("25", evaluate("(2+3"))
    @Test fun factorialSupportsZero() = assertEquals("1", evaluate("0!"))
    @Test fun invalidDivisionIsRejected() {
        assertThrows(IllegalArgumentException::class.java) { evaluate("1/0") }
    }
    @Test fun expressionLengthIsBounded() {
        assertThrows(IllegalArgumentException::class.java) { evaluate("1".repeat(513)) }
    }
}
