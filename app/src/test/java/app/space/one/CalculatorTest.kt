package app.space.one

import org.junit.Assert.assertEquals
import org.junit.Test

class CalculatorTest {
    @Test fun respectsOperatorPrecedence() = assertEquals("14", evaluate("2+3*4"))
    @Test fun supportsGrouping() = assertEquals("20", evaluate("(2+3)*4"))
    @Test fun decimalArithmeticIsExact() = assertEquals("0.3", evaluate("0.1+0.2"))
    @Test fun supportsUnaryMinus() = assertEquals("-10", evaluate("10*-1"))
    @Test fun divisionUsesDeterministicPrecision() = assertEquals("1", evaluate("1/3*3"))
}
