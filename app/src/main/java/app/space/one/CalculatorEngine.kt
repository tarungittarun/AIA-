package app.space.one

import java.math.BigDecimal
import java.math.BigInteger
import java.math.MathContext
import java.math.RoundingMode
import kotlin.math.*

/** Exact rational calculator core. Expressions are parsed once; formatted text is never reused as state. */
internal object CalculatorEngine {
    private const val MAX_LENGTH = 512
    private val mc = MathContext(34, RoundingMode.HALF_EVEN)

    fun liveAnswer(source: String, degrees: Boolean = true): String {
        val value = source.trim().replace('−', '-').replace('×', '*').replace('÷', '/')
        if (value.isEmpty() || value.last() in charArrayOf('+', '-', '*', '/', '^', '.')) return ""
        return runCatching { evaluate(source, degrees) }.getOrDefault("")
    }

    fun evaluate(source: String, degrees: Boolean = true): String {
        require(source.length <= MAX_LENGTH) { "Expression is too long" }
        var normalized = source.trim().replace('−', '-').replace('×', '*').replace('÷', '/').replace(',', '.').replace("√(", "sqrt(")
        require(normalized.isNotEmpty()) { "Enter an expression" }
        // Equals closes open groups and follows the specified trailing-operator repeat behavior.
        val opens = normalized.count { it == '(' } - normalized.count { it == ')' }
        if (opens > 0) normalized += ")".repeat(opens)
        if (normalized.last() in charArrayOf('+', '-', '*', '/')) {
            val last = normalized.last()
            if (last == '-' && normalized.dropLast(1).lastOrNull() in listOf('*', '/', '^', '(')) {
                normalized += "1"
            } else {
                val left = normalized.dropLast(1).trimEnd()
                val rhs = Regex("(?:\\d+(?:\\.\\d*)?|\\.\\d+|\\))$").find(left)?.value
                    ?: left.substringAfterLast('+').substringAfterLast('-').substringAfterLast('*').substringAfterLast('/').trim()
                normalized += if (rhs.isBlank() || rhs == ")") "1" else rhs
            }
        }
        return Parser(normalized, degrees).parse().render()
    }

    private data class Value(val number: NumberValue, val percent: Boolean = false)

    private data class NumberValue(val exact: Rational?, val approximate: BigDecimal? = null, val isPi: Boolean = false) {
        fun decimal(): BigDecimal = exact?.decimal() ?: approximate!!
        fun render(): String {
            val d = decimal().stripTrailingZeros()
            if (d.signum() == 0) return "0"
            val abs = d.abs()
            return if (abs >= BigDecimal("1e15") || abs < BigDecimal("1e-9")) d.round(MathContext(10, RoundingMode.HALF_EVEN)).toString()
            else d.toPlainString()
        }
        operator fun unaryMinus() = exact?.let { NumberValue(-it) } ?: NumberValue(null, decimal().negate(mc))
        fun plus(b: NumberValue) = if (exact != null && b.exact != null) NumberValue(exact + b.exact) else approx(decimal().add(b.decimal(), mc))
        fun minus(b: NumberValue) = if (exact != null && b.exact != null) NumberValue(exact - b.exact) else approx(decimal().subtract(b.decimal(), mc))
        fun times(b: NumberValue) = if (exact != null && b.exact != null) NumberValue(exact * b.exact) else approx(decimal().multiply(b.decimal(), mc))
        fun div(b: NumberValue): NumberValue {
            require(b.decimal().signum() != 0) { "Cannot divide by zero" }
            return if (exact != null && b.exact != null) NumberValue(exact / b.exact) else approx(decimal().divide(b.decimal(), mc))
        }
        fun pow(b: NumberValue): NumberValue {
            val exponent = b.exact
            if (exact != null && exponent != null && exponent.denominator == BigInteger.ONE && exponent.numerator.abs() < BigInteger.valueOf(10000)) {
                val n = exponent.numerator.toInt()
                return if (n >= 0) NumberValue(exact.pow(n)) else NumberValue(Rational.ONE / exact.pow(-n))
            }
            val x = decimal().toDouble(); val y = b.decimal().toDouble()
            require(x >= 0 || y % 1.0 == 0.0) { "Invalid exponent domain" }
            return approx(BigDecimal.valueOf(x.pow(y)).round(mc))
        }
        companion object {
            val ZERO = NumberValue(Rational.ZERO)
            val ONE = NumberValue(Rational.ONE)
            fun literal(s: String) = NumberValue(Rational.fromDecimal(s.toBigDecimal()))
            fun approx(d: BigDecimal) = NumberValue(null, d.round(mc))
            fun transcend(x: Double): NumberValue {
                require(x.isFinite()) { "Result is outside the supported range" }
                return approx(BigDecimal.valueOf(x))
            }
        }
    }

    private data class Rational(val numerator: BigInteger, val denominator: BigInteger) {
        operator fun plus(b: Rational) = of(numerator * b.denominator + b.numerator * denominator, denominator * b.denominator)
        operator fun minus(b: Rational) = of(numerator * b.denominator - b.numerator * denominator, denominator * b.denominator)
        operator fun times(b: Rational) = of(numerator * b.numerator, denominator * b.denominator)
        operator fun div(b: Rational): Rational { require(b.numerator != BigInteger.ZERO) { "Cannot divide by zero" }; return of(numerator * b.denominator, denominator * b.numerator) }
        operator fun unaryMinus() = of(-numerator, denominator)
        fun pow(n: Int): Rational = if (n == 0) ONE else if (n > 0) of(numerator.pow(n), denominator.pow(n)) else of(denominator.pow(-n), numerator.pow(-n))
        fun decimal() = BigDecimal(numerator).divide(BigDecimal(denominator), mc)
        companion object {
            val ZERO = Rational(BigInteger.ZERO, BigInteger.ONE)
            val ONE = Rational(BigInteger.ONE, BigInteger.ONE)
            fun of(n: BigInteger, d: BigInteger): Rational {
                require(d != BigInteger.ZERO) { "Cannot divide by zero" }
                val sign = if (d.signum() < 0) BigInteger.valueOf(-1) else BigInteger.ONE
                val nn = n * sign; val dd = d * sign; val gcd = nn.gcd(dd)
                return Rational(nn / gcd, dd / gcd)
            }
            fun fromDecimal(d: BigDecimal): Rational {
                val x = d.stripTrailingZeros(); val scale = x.scale().coerceAtLeast(0)
                return of(x.movePointRight(scale).toBigIntegerExact(), BigInteger.TEN.pow(scale))
            }
        }
    }

    private class Parser(input: String, private val degrees: Boolean) {
        private val s = input.replace("π", "pi")
        private var p = 0
        fun parse(): NumberValue {
            val v = expression()
            require(p == s.length) { "Unexpected input at ${p + 1}" }
            return if (v.percent) v.number.div(NumberValue.literal("100")) else v.number
        }
        private fun expression(): Value {
            var a = term()
            while (peek('+') || peek('-')) {
                val op = s[p++]
                val b = term()
                val right = if (b.percent) a.number.times(b.number).div(NumberValue.literal("100")) else b.number
                a = Value(if (op == '+') a.number.plus(right) else a.number.minus(right))
            }
            return a
        }
        private fun term(): Value {
            var a = power()
            while (true) {
                skipSpaces()
                val explicit = peek('*') || peek('/')
                val implicit = !explicit && startsPrimary()
                if (!explicit && !implicit) return a
                val op = if (explicit) s[p++] else '*'
                val b = power()
                val bn = if (b.percent) b.number.div(NumberValue.literal("100")) else b.number
                a = Value(if (op == '/') a.number.div(bn) else a.number.times(bn))
            }
        }
        private fun power(): Value {
            var a = unary()
            if (take('^')) a = Value(a.number.pow(power().number))
            return a
        }
        private fun unary(): Value {
            if (take('+')) return unary()
            if (take('-')) return Value(-unary().number)
            return postfix()
        }
        private fun postfix(): Value {
            var a = primary()
            while (true) {
                if (take('%')) a = Value(a.number, true)
                else if (take('!')) {
                    val n = a.number.decimal().stripTrailingZeros().toBigIntegerExact()
                    require(n.signum() >= 0 && n <= BigInteger.valueOf(169)) { "Factorial requires an integer from 0 to 169" }
                    var f = BigInteger.ONE
                    for (i in 2..n.toInt()) f *= BigInteger.valueOf(i.toLong())
                    a = Value(NumberValue(Rational.of(f, BigInteger.ONE)))
                } else return a
            }
        }
        private fun primary(): Value {
            skipSpaces()
            if (take('(')) { val v = expression(); require(take(')')) { "Missing closing parenthesis" }; return v }
            if (p < s.length && s[p].isLetter()) {
                val name = readName().lowercase()
                if (name == "pi") return Value(NumberValue(null, BigDecimal.valueOf(Math.PI), isPi = true))
                if (name == "e") return Value(NumberValue.transcend(Math.E))
                require(take('(')) { "Function needs parentheses" }
                val argument = expression().number
                val x = argument.decimal().toDouble()
                require(take(')')) { "Missing closing parenthesis" }
                val angle = if (degrees) Math.toRadians(x) else x
                val v = when (name) {
                    "sin" -> if (argument.isPi) 0.0 else sin(angle)
                    "cos" -> if (argument.isPi) -1.0 else cos(angle)
                    "tan" -> { require(!degrees || abs(x % 180.0 - 90.0) > 1e-12) { "Tangent is undefined at this angle" }; tan(angle) }
                    "asin" -> asin(x).let { if (degrees) Math.toDegrees(it) else it }
                    "acos" -> acos(x).let { if (degrees) Math.toDegrees(it) else it }
                    "atan" -> atan(x).let { if (degrees) Math.toDegrees(it) else it }
                    "ln" -> ln(x); "log" -> log10(x); "sqrt", "√" -> sqrt(x)
                    else -> error("Unknown function: $name")
                }
                require(v.isFinite()) { "Function input is outside its domain" }
                return Value(NumberValue.transcend(v))
            }
            val start = p
            var dot = false
            while (p < s.length && (s[p].isDigit() || (s[p] == '.' && !dot))) { if (s[p] == '.') dot = true; p++ }
            require(start != p) { "Expected a number" }
            val raw = s.substring(start, p)
            require(raw != ".") { "Invalid number" }
            return Value(NumberValue.literal(raw))
        }
        private fun startsPrimary(): Boolean = p < s.length && (s[p] == '(' || s[p].isDigit() || s[p] == '.' || s[p].isLetter() || s[p] == 'π')
        private fun readName(): String { val start = p; while (p < s.length && s[p].isLetter()) p++; return s.substring(start, p) }
        private fun skipSpaces() { while (p < s.length && s[p].isWhitespace()) p++ }
        private fun peek(c: Char): Boolean { skipSpaces(); return p < s.length && s[p] == c }
        private fun take(c: Char): Boolean { if (peek(c)) { p++; return true }; return false }
    }
}

internal fun evaluate(source: String): String = CalculatorEngine.evaluate(source)
