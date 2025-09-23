---
marp: true
theme: default
paginate: true
header: 'Basic intro into fuzz-testing'
footer: '0xFFFFE - Fuzzing Fundamentals For Firmware Engineers'
style: |
  h4 {
    font-size: 1.2em;
  }
  pre {
    font-size: 0.8em;
  }
  img {
    width: 30%;
    height: auto;
    float: right;
  }
---

# Practical intro into fuzz-testing

![fuzzing](fuzz-intro.jpg)

**20-minute crash course on dynamic testing for firmware**

---

# What is Fuzzing?

> **Dynamic testing technique** that feeds random/malformed input to find crashes, vulnerabilities, and edge cases

## Why Embedded Engineers Should Care
- **Robustness**: Find subtle bugs before deployment
- **Security**: Discover vulnerabilities in protocol stacks
- **Edge Cases**: Uncover hard-to-reproduce issues
- **CI Integration**: Automated testing for continuous quality

---

## Fuzzing Approaches

### Black-box (radamsa)

### Grey box fuzzers

* Coverage guided (AFL++)
* State guided, protocol fuzzers (AFLNet)
* LLM enhanced

### White box fuzzers (angr)

---

# Fuzzing Approaches - Examples

| Approach | Tool | Method | Pros | Cons |
|----------|------|--------|------|------|
| **Black-box** | radamsa | Random input mutation | Simple, fast setup | Limited coverage |
| **Grey-box** | AFL++ | Feedback-driven exploration | High effectiveness, finds complex bugs | Requires instrumentation |
| **White-box** | angr | Path analysis without execution | Works on binaries, deep analysis | Limited, research-focused |

---

# Example 1: Hello World with radamsa
## Black-box fuzzing - Getting started

```bash
./fuzz.sh
# 1000 runs, 6 errors found
# AddressSanitizer: SEGV on format string vulnerability
```

**Key Takeaways:**
- ✅ **Simple setup** - minimal configuration
- ✅ **Quick results** - found format string bug
- ✅ **Use sanitizers** - AddressSanitizer caught the crash
- ⚠️ **Limited depth** - mutation-based only

---

# Example 2: LWIP DHCP with AFL++
## Grey-box fuzzing - Real-world impact

```bash
make fuzz MODE=dhcp_client
# Found crashes in network stack
# Reproducible with standard GCC
```

**Key Takeaways:**
- ✅ **High effectiveness** - found real bugs in production code
- ✅ **Coverage-guided** - explores complex code paths
- ✅ **Reproducible** - crashes work without instrumentation
- ✅ **CI-ready** - can be automated

---

# Example 3: IoT Parser with Fuzztest
## Property-based testing integration

```cpp
TEST(IoTParserTest, FuzzMqttTopicParsing) {
  // Combines unit tests + fuzzing
  // 16,984 runs, 192 edges covered
  // Found buffer overflow in 69-byte input
}
```

**Key Takeaways:**
- ✅ **Test integration** - works with existing unit tests
- ✅ **Property-based** - validates invariants
- ✅ **Fast feedback** - 291ms for 16K runs
- ✅ **Regression tests** - auto-generates test cases

---

# Example 4: Firmware Binary with angr
## White-box analysis - Research frontier

```python
# Symbolic execution of firmware binary
# Path analysis without execution
# Limited but powerful for specific cases
```

**Key Takeaways:**
- ✅ **Binary analysis** - no source code needed
- ✅ **Deep exploration** - symbolic path solving
- ⚠️ **Limited scope** - research tool, not production
- ⚠️ **Complex setup** - requires expertise

---

# My Quick Recommendations

## 🚀 **For Fast Results**: AFL++
- Minimal setup, maximum impact
- Coverage-guided exploration
- Works great with embedded protocols

## 🔍 **For Test Integration**: Fuzztest
- Combines with unit testing
- Property-based validation
- Perfect for CI/CD pipelines

---

# Embedded-Specific Considerations

## Environment Options
- **Host testing**: Fast, easy debugging
- **QEMU emulation**: Hardware-like behavior
- **Hardware-in-loop**: Real target validation

## Target Selection
- **Protocol stacks**: DHCP, mDNS, MQTT
- **Parsers**: JSON, HTTP, custom formats
- **Network services**: Servers, clients


---

# Getting Started Workflow

- Start with simple parsers or protocol handlers
- Compile on host
- Setup fuzz target
- Run in CI

---

# CI Integration Strategy

## Continuous Fuzzing Pipeline
```yaml
fuzz_job:
  - Build with AFL++ instrumentation
  - Run fuzzer for 15-60 minutes
  - Check for crashes and timeouts
  - Fail the job if any + upload artifacts
```

---


# Key Takeaways

## **AFL++**

## **Fuzztest**

## **CI integration**

---

# Resources & Next Steps

## 📚 **Learn More**
- **0xFFFFE Repository**: https://github.com/your-repo
- **AFL++ Documentation**: https://github.com/AFLplusplus/AFLplusplus
- **Fuzztest Guide**: https://github.com/google/fuzztest

---

## 🛠️ **Try It Yourself**
1. Clone the 0xFFFFE repository
2. Start with `examples/00_radamsa_hello`
3. Progress to `examples/02_afl_lwip_dhcp`
4. Experiment with `examples/05_fuzztest_iotparser`

---

# Thank You!

**Fuzzing is not just for security professionals**  
**Every embedded engineer should be aware of these techniques**
**0xFFFFE - Fuzzing Fundamentals For Firmware Engineers**
