# Fuzzing IoT parser using fuzztest

## Go to `tools/fuzztest`

```
$ cd ../../tools/fuzztest/
```

## Run unit/property based tests

```
$ cd fuzztest/build/
./iot_parser_fuzztest
```

## Run specific fuzz test

```
cd fuzztest/build_fuzz/
./iot_parser_fuzztest --fuzz=IoTParserTest.FuzzMqttTopicParsing
```

## Example output


Tests:
```
[==========] Running 10 tests from 1 test suite.
[----------] Global test environment set-up.
[----------] 10 tests from IoTParserTest
[ RUN      ] IoTParserTest.ValidMqttParsing
[       OK ] IoTParserTest.ValidMqttParsing (0 ms)
[ RUN      ] IoTParserTest.ValidJsonExtraction
[       OK ] IoTParserTest.ValidJsonExtraction (0 ms)
[ RUN      ] IoTParserTest.ValidHttpParsing
[       OK ] IoTParserTest.ValidHttpParsing (0 ms)
[ RUN      ] IoTParserTest.FuzzMqttTopicParsing
```

Fuzzing:
```
=================================================================
=== Fuzzing stats

Elapsed time: 291.793196ms
Total runs: 16984
Edges covered: 192
Total edges: 49237
Corpus size: 24
Max stack used: 4192

=================================================================
=== BUG FOUND!

/home/david/repos/esp-network-examples/fuzz-me/fuzztest/iot_parser_fuzztest.cc:55: Counterexample found for IoTParserTest.FuzzMqttTopicParsing.
The test fails with input:
argument 0: "\000\000\000\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\001 "

=================================================================
=== Regression test draft

TEST(IoTParserTest, FuzzMqttTopicParsingRegression) {
  FuzzMqttTopicParsing(
    std::string("\000\000\000\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\001 ", 69)
  );
}
```
