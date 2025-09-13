package app;

public class SanityTest {
    public static void main(String[] args) {
        if (2 + 2 != 4) {
            throw new RuntimeException("Math is broken");
        }
    }
}
